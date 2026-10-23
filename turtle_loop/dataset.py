"""Read the labeled XLSX as data, never execute formulas or workbook instructions."""
import hashlib
import json
import math
import posixpath
import re
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path
from zipfile import ZipFile

NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
REL = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'


def workbook_rows(path):
    """Minimal read-only OOXML reader: inline/shared strings, sparse cells, relationships."""
    with ZipFile(path) as archive:
        strings = []
        if 'xl/sharedStrings.xml' in archive.namelist():
            strings = [''.join(t.text or '' for t in si.findall('.//s:t', NS))
                       for si in ET.fromstring(archive.read('xl/sharedStrings.xml')).findall('s:si', NS)]
        relationships = ET.fromstring(archive.read('xl/_rels/workbook.xml.rels'))
        targets = {r.attrib['Id']: r.attrib['Target'] for r in relationships
                   if r.attrib.get('TargetMode') != 'External'}
        workbook = ET.fromstring(archive.read('xl/workbook.xml'))
        result = {}
        for sheet in workbook.findall('s:sheets/s:sheet', NS):
            target = targets[sheet.attrib[REL]]
            target = target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/' + target)
            if not target.startswith('xl/') or '..' in target.split('/'):
                raise ValueError('Invalid worksheet relationship')
            rows = []
            for row in ET.fromstring(archive.read(target)).findall('s:sheetData/s:row', NS):
                cells = {}
                for cell in row.findall('s:c', NS):
                    column = re.sub(r'\d', '', cell.attrib['r'])
                    value = cell.find('s:v', NS)
                    text = value.text or '' if value is not None else ''
                    if cell.attrib.get('t') == 's':
                        text = strings[int(text)]
                    elif cell.attrib.get('t') == 'inlineStr':
                        text = ''.join(t.text or '' for t in cell.findall('.//s:t', NS))
                    cells[column] = {'value': text, 'formula': cell.find('s:f', NS) is not None}
                rows.append(cells)
            result[sheet.attrib['name']] = rows
        return result


def records(rows, required):
    if not rows:
        raise ValueError('Empty worksheet')
    header = {col: cell['value'] for col, cell in rows[0].items()}
    if not set(required) <= set(header.values()):
        raise ValueError(f'Missing columns: {set(required) - set(header.values())}')
    output = []
    for row in rows[1:]:
        record = {}
        for col, name in header.items():
            cell = row.get(col, {'value': '', 'formula': False})
            if name in required and cell['formula']:
                raise ValueError(f'Formula in authoritative column {name}; provide literal data')
            record[name] = cell['value']
        if any(record.get(k) for k in required):
            output.append(record)
    return output


def validate_dataset(data):
    if not isinstance(data, dict) or data.get('schema_version') != 1 or not data.get('puzzles'):
        raise ValueError('Expected a nonempty schema_version=1 dataset')
    ids = set()
    for puzzle in data['puzzles']:
        pid = puzzle['id']
        if not re.fullmatch(r'[A-Za-z0-9_-]+', pid) or pid in ids:
            raise ValueError(f'Invalid or duplicate puzzle ID: {pid}')
        ids.add(pid)
        if not all(isinstance(puzzle[k], str) and puzzle[k].strip() for k in ('opening', 'answer')):
            raise ValueError(f'{pid}: empty opening/answer')
        requirements = puzzle.get('completion_requirements', [])
        if not isinstance(requirements, list) or any(not isinstance(x, str) or not x.strip() for x in requirements):
            raise ValueError(f'{pid}: invalid completion requirements')
        rubric = puzzle['rubric']
        if not rubric or len({c['id'] for c in rubric}) != len(rubric):
            raise ValueError(f'{pid}: absent or duplicate rubric checkpoints')
        for c in rubric:
            if (type(c['weight']) not in (float, int) or not math.isfinite(c['weight'])
                    or not 0 < c['weight'] <= 1 or not isinstance(c['criterion'], str)
                    or not c['criterion'].strip()):
                raise ValueError(f'{pid}: invalid rubric checkpoint')
        if not math.isclose(sum(c['weight'] for c in rubric), 1, abs_tol=1e-9):
            raise ValueError(f'{pid}: rubric weights must sum to 1')
    return data


def load_dataset(path):
    path = Path(path)
    if path.suffix.lower() == '.json':
        return validate_dataset(json.loads(path.read_text()))
    if path.suffix.lower() != '.xlsx':
        raise ValueError('Dataset must be .xlsx or an imported .json')
    sheets = workbook_rows(path)
    puzzles = records(sheets['逐题标注'], ['puzzle_id', 'problem', 'answer'])
    rubric_rows = records(sheets['Partial Rubric'],
                         ['Puzzle ID', 'Checkpoint', '权重 (0–1)', 'English scoring criterion'])
    rubrics = defaultdict(list)
    for row in rubric_rows:
        rubrics[row['Puzzle ID']].append({
            'id': row['Checkpoint'], 'weight': float(row['权重 (0–1)']),
            'core': row.get('核心事实?') == '是',
            'criterion': row['English scoring criterion'],
            'criterion_zh': row.get('中文得分条件', '')})
    result = []
    for row in puzzles:
        if not row['problem'].strip() and not row['answer'].strip():
            continue
        pid = row['puzzle_id']
        result.append({'id': pid, 'opening': row['problem'], 'answer': row['answer'],
                       'rubric': rubrics.pop(pid, []), 'title': row.get('中文短题名', ''),
                       'story_family': row.get('story_family', ''),
                       'quality_status': row.get('质量状态', ''),
                       'review_notes': row.get('人工复核说明', ''),
                       'source_row': row.get('source_row', ''),
                       'observed_score': None})
    if rubrics:
        raise ValueError(f'Rubric references absent puzzles: {list(rubrics)}')
    return validate_dataset({'schema_version': 1,
                             'source': {'filename': path.name,
                                        'sha256': hashlib.sha256(path.read_bytes()).hexdigest()},
                             'scoring': 'sum(weight * credit); credit in {0, 0.5, 1}; provisional rubric',
                             'puzzles': result})


def overview(data):
    openings = defaultdict(list)
    families = defaultdict(list)
    for p in data['puzzles']:
        openings[p['opening'].strip()].append(p['id'])
        families[p.get('story_family', '')].append(p['id'])
    return {'puzzles': len(data['puzzles']),
            'checkpoints': sum(len(p['rubric']) for p in data['puzzles']),
            'quality_counts': dict(Counter(p.get('quality_status', '') for p in data['puzzles'])),
            'needs_review': [p['id'] for p in data['puzzles'] if p.get('quality_status') == '需要复核'],
            'identical_opening_groups': [v for v in openings.values() if len(v) > 1],
            'shared_families': {k: v for k, v in families.items() if k and len(v) > 1},
            'source': data.get('source'), 'observed_scores': 'null until a final is actually evaluated'}
