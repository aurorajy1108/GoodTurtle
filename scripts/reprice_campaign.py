#!/usr/bin/env python3
"""Reprice raw API usage in sidecars; never change frozen experiments or invoices."""
import argparse
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.team_campaign import rows_for
from turtle_loop.costs import account_call,cost_summary,pricing_config
from turtle_loop.engine import dump


def reprice(root,out):
    root=Path(root).resolve();out=Path(out).resolve()
    manifest=json.loads((root/'campaign.json').read_text())
    files={root/'host_gate/api_calls.jsonl'}
    files.update(root/r['run_dir']/'api_calls.jsonl' for r in rows_for(root,manifest))
    book=pricing_config();records=[]
    for file in sorted(files):
        if not file.exists():continue
        for index,line in enumerate(file.read_text().splitlines(),1):
            call=json.loads(line);account=account_call(call,book)
            peak=account['estimated_cost_usd']
            factor=(account.get('price') or {}).get('off_peak_multiplier',1)
            records.append({'source':str(file.relative_to(root)),'call_index':index,'response_id':call.get('response_id'),
                **account,'lower_estimated_cost_usd':None if peak is None else peak*factor,
                'upper_estimated_cost_usd':peak})
    summary=cost_summary(records)
    known=all(r['estimated_cost_usd'] is not None for r in records)
    summary.update({'source_campaign':str(root),'rates_source':'https://api-docs.deepseek.com/quick_start/pricing/',
        'assumption':'DeepSeek peak reference estimate plus half-price off-peak lower bound; no holiday/time-band guess. Actual billed amount unknown.',
        'lower_estimated_cost_usd':sum(r['lower_estimated_cost_usd'] for r in records) if known else None,
        'upper_estimated_cost_usd':sum(r['upper_estimated_cost_usd'] for r in records) if known else None,
        'known_lower_estimated_cost_usd':sum(r['lower_estimated_cost_usd'] for r in records if r['lower_estimated_cost_usd'] is not None),
        'known_upper_estimated_cost_usd':sum(r['upper_estimated_cost_usd'] for r in records if r['upper_estimated_cost_usd'] is not None),
        'recorded_calls':len(records)})
    out.mkdir(parents=True,exist_ok=False)
    dump(out/'pricing_snapshot.json',book);dump(out/'calls.json',records);dump(out/'summary.json',summary)
    return summary


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--campaign',required=True);parser.add_argument('--out',required=True)
    args=parser.parse_args();summary=reprice(args.campaign,args.out)
    print(json.dumps({k:summary[k] for k in ('recorded_calls','lower_estimated_cost_usd','upper_estimated_cost_usd')}))


if __name__=='__main__':main()
