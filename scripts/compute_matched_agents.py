#!/usr/bin/env python3
"""TS038 solo/MAS × self-review pilot with common per-repeat solver budgets."""
import argparse
import html
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.matched_self_review import prepare as prepare_solo,read,calls,sha,authorize_recovery
from scripts.supervise_campaign import notify
from turtle_loop.budgeted_agents import SolverBudget,BudgetedAgent
from turtle_loop.dialogue import FreeDialoguePlayer,dialogue_settings
from turtle_loop.engine import Recorder,dump,play
from turtle_loop.costs import merge_summaries
from turtle_loop.providers import Client

CONDITIONS={'solo':(1,False),'solo_review':(1,True),'mas':(2,False),'mas_review':(2,True)}


def prepare(reference,out):
    reference,out=Path(reference).resolve(),Path(out).resolve()
    prepare_solo(reference,out)
    caps=read(out/'plan.json')
    snap=out/'runtime_snapshot'
    inputs=read(snap/'configs/matched_inputs.json')
    inputs['mas_player_prompt']=read(reference/'team/TS038_r01_free_dialogue/prompts.json')['player']
    if 'SHARED DIALOGUE PROTOCOL' not in inputs['mas_player_prompt']:
        raise ValueError('Missing frozen MAS role protocol')
    if 'SHARED DIALOGUE PROTOCOL' in inputs['prompts']['player']:
        raise ValueError('Solo prompt is contaminated with MAS roles')
    dump(snap/'configs/compute_agents_inputs.json',inputs)
    specs=[]
    common_caps={'generation_cap':max(b['generation_cap'] for b in caps['repeats']),
                 'output_token_cap':max(b['output_token_cap'] for b in caps['repeats'])}
    for budget in caps['repeats']:
        for condition,(agents,review) in CONDITIONS.items():
            specs.append({**budget,**common_caps,'condition':condition,'agents':agents,'review':review,
                          'run_dir':f"TS038_r{budget['repeat']:02}_{condition}"})
    random.Random(20261112).shuffle(specs)
    plan={'schema_version':1,'protocol':'compute-agents-2x2-v1','puzzle':'TS038','planned_games':8,
          'repeats':2,'conditions':CONDITIONS,'jobs':specs,'workers':2,
          'per_generation_output_cap':2048,'note_word_target':160,
          'dialogue_policy':dialogue_settings(argparse.Namespace()),
          'reference_study':str(reference),'cap_derivation':caps['repeats'],
          'common_solver_caps':common_caps,
          'matching':'Same available aggregate actor generation/output caps in ALL eight games. Actor A+B and reviews share ONE budget. Actual input/cache/cost need not match.',
          'review_schedule':'Floor differences across external slots 1..99. Only the first solver decision in a slot gets its scheduled private draft/review; no extra review for format corrections or subsequent public discussion.',
          'isolation':'Solo base comes from actual solo; MAS base comes from actual MAS. Two MAS actors have distinct persistent sessions and shared public dialogue; their private reviews are not automatically shared.',
          'limitations':['Budget ceilings are matched, not exact FLOPs or realized token expenditure.',
                         'Two repeats of one puzzle are exploratory.',
                         'Earlier solo_self_review_matched results used a MAS-contaminated base prompt and are excluded from this factorial comparison.']}
    shutil.copy2(ROOT/'scripts/compute_matched_agents.py',snap/'scripts/compute_matched_agents.py')
    dump(snap/'configs/compute_agents_plan.json',plan)
    dump(out/'plan.json',plan)
    dump(out/'snapshot_hashes.json',{str(p.relative_to(snap)):sha(p) for p in snap.rglob('*')
                                    if p.is_file() and '__pycache__' not in p.parts})
    dump(out/'status.json',{'status':'prepared','planned_games':8,'completed_games':0,'active':{}})
    dashboard(out)
    return plan


def worker(out,run_dir,resume=False):
    out=Path(out).resolve()
    inputs=read(ROOT/'configs/compute_agents_inputs.json')
    plan=read(ROOT/'configs/compute_agents_plan.json')
    spec=next(s for s in plan['jobs'] if s['run_dir']==run_dir)
    game=out/run_dir
    prompts={**inputs['prompts'],'player':inputs['mas_player_prompt'] if spec['agents']==2 else inputs['prompts']['player']}
    old=read(game/'result.json')
    if old and old['status']=='completed':return 0
    rec=(Recorder.restore(game,inputs['puzzle'],inputs['config'],prompts,echo=True) if resume else
         Recorder(game,inputs['puzzle'],inputs['config'],prompts,echo=True))
    ledger=SolverBudget(rec,spec,spec['review'])
    actors=[BudgetedAgent(inputs['config']['player'],role,ledger,actor) for role,actor in
            ([('player','A'),('partner','B')] if spec['agents']==2 else [('player','A')])]
    player=actors[0]
    if spec['agents']==2:
        # dialogue_system_prompt() uses the frozen files, not a new root prompt.
        from turtle_loop.dialogue import dialogue_system_prompt
        if dialogue_system_prompt()!=inputs['mas_player_prompt']:
            raise ValueError('Frozen MAS prompt changed')
        player=FreeDialoguePlayer(actors[0],actors[1],rec,plan['dialogue_policy'])
        if ledger.forced_final:player.compute_budget_final=True
    clients={r:Client(inputs['config'][r],r,rec.audit) for r in ('host','grader')}
    clients['player']=player
    result=play(inputs['puzzle'],inputs['config'],rec,clients,prompts)
    ledger.save()
    return 0 if result['status']=='completed' else 1


def dashboard(out):
    plan=read(out/'plan.json')
    rows=[]
    for spec in plan['jobs']:
        game=out/spec['run_dir'];result=read(game/'result.json',{})
        rows.append({**{k:spec[k] for k in ('run_dir','condition','agents','review','repeat','generation_cap','output_token_cap')},
                     **result,'solver_compute':read(game/'solver_compute.json',{})})
        if game.exists():
            notes=[c for c in calls(game/'api_calls.jsonl') if c.get('reflection_phase') in ('draft','review') and c.get('status')=='ok']
            (game/'self_review.html').write_text('<!doctype html><meta charset="utf-8"><h1>Private solver reviews</h1>'
                '<a href="trajectory.html">Host trajectory</a> · <a href="shared_dialogue.html">MAS public dialogue</a>'+''.join(
                '<details><summary>'+html.escape(f"Slot {c['reflection_slot']} · {c['reflection_actor']} · {c['reflection_phase']}")+ '</summary><pre style="white-space:pre-wrap">'+html.escape(c['text'])+'</pre></details>' for c in notes))
    dump(out/'experiment_runs.json',rows)
    dump(out/'cost_summary.json',merge_summaries([r['costs'] for r in rows if r.get('costs')]))
    import statistics
    performance=[]
    for condition in CONDITIONS:
        done=[r for r in rows if r['condition']==condition and r.get('status')=='completed']
        scores=[r['final_partial_score'] for r in done if r.get('final_partial_score') is not None]
        performance.append({'condition':condition,'completed':len(done),'expected':2,
            'successes':sum(r['success'] is True for r in done),
            'success_rate':sum(r['success'] is True for r in done)/len(done) if done else None,
            'mean_final_partial_score':statistics.mean(scores) if scores else None,
            'mean_submissions':statistics.mean(r['submissions'] for r in done) if done else None,
            'solver_generations':[r['solver_compute'].get('generations') for r in done],
            'solver_output_tokens':[r['solver_compute'].get('output_tokens') for r in done]})
    contrasts=[]
    for repeat in (1,2):
        local={r['condition']:r for r in rows if r['repeat']==repeat and r.get('status')=='completed'}
        for baseline,treatment in [('solo','solo_review'),('mas','mas_review'),('solo_review','mas_review')]:
            if baseline in local and treatment in local and all(local[c].get('final_partial_score') is not None for c in (baseline,treatment)):
                contrasts.append({'repeat':repeat,'baseline':baseline,'treatment':treatment,
                    'final_score_delta':local[treatment]['final_partial_score']-local[baseline]['final_partial_score'],
                    'note':'Exploratory model grades under equal available budget caps; inspect trajectories and actual token use.'})
    dump(out/'performance.json',{'conditions':performance,'paired_contrasts':contrasts})
    table=''.join('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in (
        r['condition'],r['repeat'],r.get('status','planned'),r.get('submissions',0),r.get('final_partial_score'),
        r['solver_compute'].get('generations',0),r['generation_cap'],r['solver_compute'].get('output_tokens',0),r['output_token_cap']))+
        '<td><a href="'+r['run_dir']+'/trajectory.html">Trajectory</a> · <a href="'+r['run_dir']+'/self_review.html">Reviews</a> · '
        '<a href="'+r['run_dir']+'/shared_dialogue.html">Dialogue</a></td></tr>' for r in rows)
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="30">'
        '<h1>TS038 · solo/MAS × self-review</h1><p>'+html.escape(plan['matching'])+'</p>'
        '<a href="status.json">Status</a> · <a href="plan.json">Plan</a> · <a href="performance.json">Performance</a> · <a href="cost_summary.json">Costs</a> · '
        '<a href="alerts.jsonl">Alerts</a><table border="1"><tr><th>Condition</th><th>Repeat</th><th>Status</th>'
        '<th>Submissions</th><th>Score</th><th>Generations</th><th>Cap</th><th>Output tokens</th><th>Cap</th><th>Inspect</th></tr>'+table+'</table>')
    return rows


def run(out):
    import fcntl
    out=Path(out).resolve()
    lock=(out/'runner.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    snap=out/'runtime_snapshot';plan=read(out/'plan.json')
    for name,digest in read(out/'snapshot_hashes.json').items():
        if sha(snap/name)!=digest:raise ValueError('Frozen runtime changed: '+name)
    state={'status':'running','pid':os.getpid(),'planned_games':8,'completed_games':0,'active':{},'recoveries':{}}
    pending=[];active={};failed=False
    for spec in plan['jobs']:
        result=read(out/spec['run_dir']/'result.json')
        if result and result['status']=='completed':continue
        if result and not authorize_recovery(out/spec['run_dir']):
            raise ValueError('Unverified stopped game; refusing to resample '+spec['run_dir'])
        pending.append((spec['run_dir'],bool(result)))
    notify(out,'compute-matched pilot started','Eight TS038 games; two concurrent workers; shared solver caps and isolated role sessions.')
    try:
        while pending or active:
            while pending and len(active)<plan['workers']:
                name,resume=pending.pop(0)
                cmd=[sys.executable,str(snap/'scripts/compute_matched_agents.py'),'worker','--out',str(out),'--game',name]
                if resume:cmd.append('--resume')
                log=(out/(name+'.log')).open('a')
                proc=subprocess.Popen(cmd,cwd=snap,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                active[name]=(proc,log);state['active'][name]=proc.pid
            for name,(proc,log) in list(active.items()):
                if proc.poll() is None:continue
                log.close();del active[name];del state['active'][name]
                game=out/name;result=read(game/'result.json',{})
                if not proc.returncode and result.get('status')=='completed':
                    notify(out,'game completed',f"{name}: score {result['final_partial_score']}, submissions {result['submissions']}")
                    continue
                attempts=state['recoveries'].get(name,0)
                recovery=authorize_recovery(game) if result else None
                if recovery and attempts<3:
                    state['recoveries'][name]=attempts+1;pending.append((name,True))
                    notify(out,'verified recovery',f'{name}: {recovery}; original history and budget retained.')
                else:
                    failed=True
                    notify(out,'attention required',name+': '+str(result.get('error','worker failure')))
            rows=dashboard(out)
            state.update(completed_games=sum(r.get('status')=='completed' for r in rows),updated_at=time.time())
            dump(out/'status.json',state)
            if active or pending:time.sleep(10)
        state['status']='requires_attention' if failed else 'completed'
        return int(failed)
    finally:
        for proc,log in active.values():
            if proc.poll() is None:
                os.killpg(proc.pid,2)
                try:proc.wait(timeout=20)
                except subprocess.TimeoutExpired:os.killpg(proc.pid,15)
            log.close()
        if state['status']=='running':state['status']='interrupted'
        state['active']={};dump(out/'status.json',state);dashboard(out);lock.close()


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['prepare','run','worker','status'])
    parser.add_argument('--out',required=True)
    parser.add_argument('--reference',help='Completed frozen TS038 study used only to derive caps and frozen inputs')
    parser.add_argument('--game',help='Internal worker run_dir from plan')
    parser.add_argument('--resume',action='store_true')
    args=parser.parse_args(argv)
    if args.command=='prepare':
        if not args.reference:parser.error('--reference required')
        prepare(args.reference,args.out);print('Prepared 8 games, no API calls.');return 0
    if args.command=='worker':return worker(args.out,args.game,args.resume)
    if args.command=='status':dashboard(Path(args.out));print(json.dumps(read(Path(args.out)/'status.json'),indent=2));return 0
    return run(args.out)


if __name__=='__main__':raise SystemExit(main())
