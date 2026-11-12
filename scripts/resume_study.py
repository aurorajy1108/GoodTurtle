#!/usr/bin/env python3
"""Continue a stopped single-batch study in a new archive-preserving directory."""
import argparse
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from turtle_loop.engine import (dump, saved_player_note_recovery, saved_grader_reason_recovery,
                                saved_player_json_recovery, saved_host_transport_recovery,
                                saved_player_auto_recovery)
from turtle_loop.host_context import RUNTIME_VERSION
from scripts.study_20261102 import collect_costs
from turtle_loop.dialogue_recovery import saved_dialogue_action_recovery
from turtle_loop.player_format import saved_untyped_player_correction
from turtle_loop.transport_recovery import saved_transport_recovery
from turtle_loop.host_output_recovery import saved_host_output_recovery


def format_overlay_policy(current,saved):
    """A parser repair cannot silently re-enable a disabled paid formatter."""
    if saved and 'max_codex_calls_per_game' in saved:
        return {**current,'max_codex_calls_per_game':min(current['max_codex_calls_per_game'],
                                                       saved['max_codex_calls_per_game'])}
    return current


def collect_resume_costs(out, batch, gate_reused=False):
    collect_costs(out,[{'name':batch}])
    if gate_reused:
        from turtle_loop.costs import merge_summaries
        cl_cost=json.loads((out/'cost_summary.json').read_text())
        dump(out/'cl_cost_summary.json',cl_cost)
        gate_cost=json.loads((out/'host_gate_archive/cost_summary.json').read_text())
        dump(out/'cost_summary.json',merge_summaries([gate_cost,cl_cost]))


def prepare(source, out, repair_player_note=False, repair_grader_reason=False, repair_player_json=False,
            recover_host_transport=False, auto_player_format=False, recover_dialogue_action=False, correct_untyped_player=False, recover_transport=False, complete_grader_coverage=False, recover_host_output=False, renew_read_window=None):
    source,out=Path(source).resolve(),Path(out).resolve()
    wrapper=None
    if (source/'run_manifest.json').exists() and (source/'study/study_plan.json').exists():
        wrapper=source
        wrapper_status=json.loads((wrapper/'status.json').read_text())
        gate=json.loads((wrapper/'host_gate/summary.json').read_text())
        if (wrapper_status.get('phase')!='continual' or not wrapper_status.get('host_gate_passed')
                or gate.get('dry_run') or type(gate.get('planned_calls')) is not int or gate['planned_calls']<1
                or gate.get('passed')!=gate.get('planned_calls')
                or gate.get('completed_calls')!=gate.get('planned_calls') or gate.get('errors')):
            raise ValueError('Verified wrapper must have a passed, complete Host gate and a stopped CL phase')
        source=wrapper/'study'
    if sum((repair_player_note,repair_grader_reason,repair_player_json,recover_host_transport,auto_player_format,recover_dialogue_action,correct_untyped_player,recover_transport,complete_grader_coverage,recover_host_output))>1:
        raise ValueError('Select one saved-response recovery mode at a time')
    repair_any=repair_player_note or repair_grader_reason or repair_player_json or recover_host_transport or auto_player_format or recover_dialogue_action or correct_untyped_player or recover_transport or complete_grader_coverage or recover_host_output
    if renew_read_window and not recover_transport:raise ValueError('Read-window renewal requires --recover-transport')
    renewed=None
    if out.exists() or source in out.parents or (wrapper and wrapper in out.parents):
        raise ValueError('Use a new output directory outside the original study')
    status=wrapper_status if wrapper else json.loads((source/'status.json').read_text())
    if status['status'] not in ('stopped_on_error','interrupted','error'):
        raise ValueError('Source study must be stopped')
    plan=json.loads((source/'study_plan.json').read_text())
    if len(plan['jobs'])!=1:
        raise ValueError('Resume each single-batch study separately')
    old_hashes=json.loads((source/'snapshot_hashes.json').read_text())
    for name,sha in old_hashes.items():
        if hashlib.sha256((source/'runtime_snapshot'/name).read_bytes()).hexdigest()!=sha:
            raise ValueError('Original frozen snapshot changed: '+name)
    # Preserve the original host/context policy. The explicit note-repair flag
    # permits only the recorded controller/transport overlay below.
    old_engine=(source/'runtime_snapshot/turtle_loop/engine.py').read_text()
    old_experiments=(source/'runtime_snapshot/turtle_loop/experiments.py').read_text()
    if 'def restore(' not in old_engine or '--resume' not in old_experiments:
        raise ValueError('This frozen study predates resume support; use its archived compatible recovery code. '
                         'Current host/context changes cannot be mixed into an old game.')
    recovery_details=None
    preserved_completed=[]
    if repair_any:
        batch=source/plan['jobs'][0]['name']
        rows=json.loads((batch/'experiment_runs.json').read_text())
        preserved_completed=[r['run_dir'] for r in rows if r['status']=='completed']
        stopped=[r for r in rows if r['status']!='completed']
        if len(stopped)!=1:
            raise ValueError('Saved-response recovery requires exactly one stopped solo game')
        game=batch/stopped[0]['run_dir']
        turns=[]
        for line in (game/'trajectory.jsonl').read_text().splitlines():
            e=json.loads(line)
            if e['event']=='submission':turns.append({k:e[k] for k in ('index','type','text','forced')})
            elif e['event'] in ('host_feedback','evaluation'):
                turns[e['submission']-1]['label']=e['label']
                if e['event']=='evaluation':turns[e['submission']-1]['grade']={k:v for k,v in e.items() if k not in ('event','timestamp','submission','raw')}
        calls=[json.loads(x) for x in (game/'api_calls.jsonl').read_text().splitlines()]
        if renew_read_window:
            from turtle_loop.transport_recovery import new_read_retry_window
            if (game/'transport_read_window.json').exists():raise ValueError('This game already has an explicit read-window renewal')
            renewed=new_read_retry_window(calls,renew_read_window)
        args=(json.loads((game/'result.json').read_text()),calls,turns,json.loads((game/'config.json').read_text()))
        if args[0].get('evaluation_versions',{}).get('runtime_context_version') != RUNTIME_VERSION:
            raise ValueError('Recovery overlay would change the frozen runtime context protocol. '
                             'Use the archived compatible recovery code for this old study; new experiments use a fresh batch.')
        recovery=(saved_host_output_recovery(*args,game) if recover_host_output else
                  saved_grader_reason_recovery(*args,json.loads((game/'puzzle_private.json').read_text()),missing_coverage=True) if complete_grader_coverage else
                  saved_transport_recovery(*args,game,renewed_window=renewed) if recover_transport else
                  saved_untyped_player_correction(*args) if correct_untyped_player else
                  saved_dialogue_action_recovery(*args,game) if recover_dialogue_action else
                  saved_player_auto_recovery(*args) if auto_player_format else
                  saved_host_transport_recovery(*args) if recover_host_transport else
                  saved_player_note_recovery(*args) if repair_player_note else
                  saved_player_json_recovery(*args) if repair_player_json else
                  saved_grader_reason_recovery(*args,json.loads((game/'puzzle_private.json').read_text())))
        if not recovery:
            raise ValueError('No supported saved DeepSeek recovery matches this archive')
        recovery_details={'run_dir':stopped[0]['run_dir'],'preserved_submissions':len(turns),
                          'source_response_id':recovery.get('response_id'),
                          'kind':'host_output' if recover_host_output else 'missing_grader_coverage' if complete_grader_coverage else 'exact_transport' if recover_transport else 'untyped_player_correction' if correct_untyped_player else 'saved_dialogue_action' if recover_dialogue_action else 'auto_player_format' if auto_player_format else 'host_transport' if recover_host_transport else 'player_note' if repair_player_note else 'question_quote' if repair_player_json else 'grader_reason'}
        if 'verified_pre_send_attempts' in recovery:
            recovery_details['verified_pre_send_attempts']=recovery['verified_pre_send_attempts']
        if recover_host_transport or recover_dialogue_action or correct_untyped_player or recover_transport or complete_grader_coverage or recover_host_output:
            recovery_details.update(recovery)
        elif repair_player_note or repair_player_json or auto_player_format:
            recovery_details.update(pending_submission=len(turns)+1,action=recovery['action'])
            if repair_player_note:recovery_details['removed_fields']=['text_note']
            else:recovery_details['format_recovery']=recovery['format_recovery']
        else:
            recovery_details.update(recovered_submission=turns[-1]['index'],grade=recovery['grade'],removed_fields=recovery['removed_fields'])
    shutil.copytree(source,out,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    if wrapper:
        shutil.copytree(wrapper/'host_gate',out/'host_gate_archive',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        shutil.copy2(wrapper/'run_manifest.json',out/'original_verified_run_manifest.json')
    if complete_grader_coverage:
        dump(out/plan['jobs'][0]['name']/recovery_details['run_dir']/'grader_coverage_completion.json',recovery)
    if recover_transport:
        dump(out/plan['jobs'][0]['name']/recovery_details['run_dir']/'transport_recovery.json',recovery)
        if renewed:dump(out/plan['jobs'][0]['name']/recovery_details['run_dir']/'transport_read_window.json',renewed)
    if recover_host_transport:
        dump(out/plan['jobs'][0]['name']/recovery_details['run_dir']/'host_transport_recovery.json', recovery)
    if recover_dialogue_action:
        dump(out/plan['jobs'][0]['name']/recovery_details['run_dir']/'dialogue_action_recovery.json',recovery)
    if correct_untyped_player:
        dump(out/plan['jobs'][0]['name']/recovery_details['run_dir']/'player_format_correction.json',recovery)
    snap=out/'runtime_snapshot'
    if recover_host_output:
        dump(out/plan['jobs'][0]['name']/recovery_details['run_dir']/'host_output_recovery.json',recovery)
    changes={}
    if repair_any:
        files=('engine.py','sessions.py','providers.py','action_text.py','player_format.py','coverage.py','transport_recovery.py','codex_client.py','grader.py','host.py','host_output_recovery.py')
        if recover_dialogue_action or recover_transport:files+=('dialogue.py','dialogue_contract.py','dialogue_recovery.py','experiments.py')
        for name in files:
            dest=snap/'turtle_loop'/name
            before=hashlib.sha256(dest.read_bytes()).hexdigest() if dest.exists() else None
            shutil.copy2(ROOT/'turtle_loop'/name,dest)
            changes['turtle_loop/'+name]={'before_sha256':before,
                'after_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
                'reason':('Automatic format recovery; solver actions are not regenerated; auxiliary formatter calls separately audited'
                          if auto_player_format else 'Exact DeepSeek message restoration and one explicit unanswered Host request replay'
                          if recover_host_transport else 'Explicit saved-response repair and exact DeepSeek chat recovery; no model resampling')}
        if auto_player_format:
            for name in ('configs/player_format_repair.json',):
                dest=snap/name
                dest.parent.mkdir(parents=True,exist_ok=True)
                before=hashlib.sha256(dest.read_bytes()).hexdigest() if dest.exists() else None
                saved_policy=json.loads(dest.read_text()) if dest.exists() else None
                dump(dest,format_overlay_policy(json.loads((ROOT/name).read_text()),saved_policy))
                changes[name]={'before_sha256':before,'after_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
                               'reason':'Explicit opt-in to bounded automatic player format recovery; puzzle models/prompts/rubrics unchanged'}
    job=plan['jobs'][0]
    argv=[v.replace(str(source),str(out)) for v in job['argv']]
    if '--resume' not in argv: argv.append('--resume')
    argv[0]=sys.executable
    hashes={str(p.relative_to(snap)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in snap.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    dump(out/'snapshot_hashes.json',hashes)
    dump(out/'study_plan.json',{**plan,'jobs':[{**job,'argv':argv}], 'resumed_from':str(source)})
    record={'source':str(source),'out':str(out),'batch':job['name'],'argv':argv,
            'controller_overlay':changes,'original_snapshot_hashes':old_hashes,
            'saved_action_recovery':recovery_details,
            'preserved_completed_runs':preserved_completed,
            'transport_changes':(['Explicit replay of one unanswered DeepSeek host request; possible duplicate remote charge recorded']
                                 if recover_host_transport else
                                 ['Exact transport replay; all observed role messages retained; original failed attempts remain in accounting'] if recover_transport else
                                 ['Saved-response parser recovery; verified pre-send retries do not become assistant messages; all original attempts remain in accounting'] if repair_any else []),
            'prompt_changes':(['Reuse an existing coverage-completion reply when present; otherwise one isolated request for missing arrays. Original credits, flags and role messages fixed; no fresh full grade.'] if complete_grader_coverage else ['Bounded same-session format correction after an output containing no typed action; max two per game. No valid question is regenerated.'] if correct_untyped_player else ['MAS response_contract lists concrete literal headers; original system prompt files and all past role messages preserved.'] if recover_dialogue_action else []),
            'policy':'Original files retained; histories, quotas, costs and completed games preserved. Models, system prompt files, packs, scoring criteria and order unchanged. Explicit controller/format overlays and any format-correction prompt are recorded; no hidden puzzle hints added.'}
    if wrapper:
        record.update(verified_wrapper=str(wrapper),host_gate_reused=True,
                      host_gate_archive='host_gate_archive',
                      gate_cost_policy='Preserved gate is not rerun; combined cost summary includes its calls exactly once.')
    elif (out/'host_gate_archive/summary.json').exists():
        record.update(host_gate_reused=True,host_gate_archive='host_gate_archive',
                      gate_cost_policy='Inherited archived gate included exactly once; no gate calls repeated.')
    if auto_player_format:
        format_policy=json.loads((snap/'configs/player_format_repair.json').read_text())
        record.update(format_repair_policy=format_policy,
                      experiment_model_profiles_unchanged=True,
                      auxiliary_formatter=('Local-only; no auxiliary model calls' if
                        format_policy['max_codex_calls_per_game']==0 else
                        'Codex format-only; no hidden puzzle context; exact source-value guard'))
    dump(out/'resume_manifest.json',record)
    dump(out/'status.json',{'status':'prepared_resume','resumed_from':str(source),'completed':[],'active':None})
    if record.get('host_gate_reused'):
        collect_resume_costs(out,job['name'],True)
    return record


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--from-study',required=True)
    p.add_argument('--out',required=True)
    p.add_argument('--mode',choices=['plan','run'],default='plan')
    p.add_argument('--repair-player-note',action='store_true',help='Recover one complete saved DeepSeek solo action rejected solely for string text_note; preserve local chat messages and quota')
    p.add_argument('--repair-grader-reason',action='store_true',help='Recover the complete saved DeepSeek grade rejected solely for coverage reason metadata; no new grader call')
    p.add_argument('--repair-player-json',action='store_true',help='Recover a saved complete question with a missing/incorrectly escaped closing quote or one unescaped inner quote pair; no model call')
    p.add_argument('--recover-host-transport',action='store_true',help='Explicitly restore saved DeepSeek solo sessions and replay one unanswered host request. Failed remote attempt may already have been billed; all observed replies and counts are preserved.')
    p.add_argument('--auto-player-format',action='store_true',help='Restore saved Player output, enable fixed-position extraction and bounded verbatim Codex formatting; no puzzle action resampling')
    p.add_argument('--recover-dialogue-action',action='store_true',help='Restore both DeepSeek agents and one explicit saved ACTION NEXT=X wrapper; preserve exact body, handoff, history and quota')
    p.add_argument('--correct-untyped-player',action='store_true',help='Continue the original Player session after complete untyped prose, with a maximum of two explicit format-correction turns per game; no valid action is regenerated')
    p.add_argument('--recover-transport',action='store_true',help='Checked exact replay of pre-send DeepSeek failures or a cancelled pending Host request, including MAS buffers; never rerun completed games')
    p.add_argument('--complete-grader-coverage',action='store_true',help='Complete omitted per-fact evidence for an observed valid grader judgment; freeze all original credits and flags, never regrade the submission')
    p.add_argument('--recover-host-output',action='store_true',help='Recover a unique saved Host label envelope without API, or replay only a saved blank Host request within its total three-attempt limit')
    p.add_argument('--renew-read-window',metavar='REASON',help='Explicit operator-only renewal after three unanswered judging-role read failures; one renewal per game, up to three further failures; requires --recover-transport')
    args=p.parse_args(argv)
    record=prepare(args.from_study,args.out,args.repair_player_note,args.repair_grader_reason,args.repair_player_json,
                   args.recover_host_transport,args.auto_player_format,args.recover_dialogue_action,args.correct_untyped_player,args.recover_transport,args.complete_grader_coverage,args.recover_host_output,args.renew_read_window)
    out=Path(record['out']);batch=record['batch']
    print(json.dumps(record,ensure_ascii=False),flush=True)
    if args.mode=='plan':return 0
    state={'pid':os.getpid(),'status':'running','active':batch,'completed':[], 'mode':'resume',
           'resumed_from':record['source']}
    dump(out/'status.json',state)
    with (out/(batch+'_resume.log')).open('w') as log:
        child=subprocess.Popen(record['argv'],cwd=out/'runtime_snapshot',stdout=log,stderr=subprocess.STDOUT)
        state['child_pid']=child.pid;dump(out/'status.json',state)
        try:
            code=child.wait()
        except KeyboardInterrupt:
            child.send_signal(signal.SIGINT)
            try:child.wait(timeout=15)
            except subprocess.TimeoutExpired:child.terminate();child.wait()
            code=130
    collect_resume_costs(out,batch,record.get('host_gate_reused',False))
    state.update(status='completed' if code==0 else 'interrupted' if code==130 else 'stopped_on_error',
                 active=None,completed=[{'batch':batch,'exit_code':code}])
    dump(out/'status.json',state)
    return code


if __name__=='__main__':raise SystemExit(main())
