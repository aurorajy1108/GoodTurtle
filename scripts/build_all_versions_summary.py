#!/usr/bin/env python3
"""Refresh the pinned November 14 analysis tables without generating dashboards.

The snapshot preserves the original 168 archive records (167 observations).
New cohorts in results/catalog.json are summarized separately by results_catalog.
"""
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/tables/20261114_all_versions'


def main():
    from scripts.results_catalog import summarize
    rows=json.loads((OUT/'formal_inventory.json').read_text())
    selected=[]
    for r in rows:
        res=json.loads((ROOT/r['path']/'result.json').read_text())
        if (r['status'],r['score'],r['success'],r['submissions'])!=(res['status'],res.get('final_partial_score'),res.get('success'),res['submissions']):
            raise ValueError('Pinned outcome differs: '+r['id'])
        selected.append(r)
    stats=summarize(selected)
    (OUT/'condition_summary.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n')
    for name,data in [('formal_inventory.csv',rows),('condition_summary.csv',stats)]:
        fields=[k for k in data[0] if k!='models']
        with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.DictWriter(f,fields,extrasaction='ignore');w.writeheader();w.writerows(data)
    print(json.dumps({'snapshot_rows':len(rows),'observations':sum(not r['duplicate_of'] for r in rows),
                      'summary_groups':len(stats),'outputs':str(OUT.relative_to(ROOT)),
                      'new_model_calls':0,'dashboard_generated':False}))


if __name__=='__main__':
    import sys
    sys.path.insert(0,str(ROOT))
    main()
