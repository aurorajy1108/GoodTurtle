#!/usr/bin/env python3
"""Monitor assigned studies, resume verified checkpoints, and notify locally."""
import argparse
import copy
import fcntl
import html
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from turtle_loop.engine import dump,now
from turtle_loop.costs import merge_summaries
from turtle_loop.transport_recovery import saved_transport_recovery,digest
from turtle_loop.player_format import saved_untyped_player_correction
from turtle_loop.dialogue_recovery import saved_dialogue_action_recovery
from turtle_loop.engine import saved_player_auto_recovery,saved_grader_reason_recovery
from turtle_loop.host_output_recovery import saved_host_output_recovery


def read(path,default=None):
    try:return json.loads(Path(path).read_text())
    except (OSError,ValueError):return default


def checkpoint(study):
    plan=read(study/'study_plan.json')
    if not plan or len(plan['jobs'])!=1:raise ValueError('Expected one stopped study batch')
    batch=study/plan['jobs'][0]['name']
    rows=read(batch/'experiment_runs.json',[])
    pending=[r for r in rows if read(batch/r['run_dir']/'result.json',r).get('status')!='completed']
    if len(pending)!=1:raise ValueError('Expected exactly one durable stopped game')
    game=batch/pending[0]['run_dir'];previous=read(game/'result.json');config=read(game/'config.json')
    events=[json.loads(l) for l in (game/'trajectory.jsonl').read_text().splitlines()]
    calls=[json.loads(l) for l in (game/'api_calls.jsonl').read_text().splitlines()]
    turns=[]
    for event in events:
        if event['event']=='submission':turns.append({k:event[k] for k in ('index','type','text','forced')})
        elif event['event'] in ('host_feedback','evaluation'):
            turn=turns[event['submission']-1];turn['label']=event['label']
            if event['event']=='evaluation':turn['grade']=event
    return game,previous,calls,turns,config


def choose_recovery(study,renew_read_window=None):
    game,previous,calls,turns,config=checkpoint(study)
    args=(previous,calls,turns,config)
    if renew_read_window:
        from turtle_loop.transport_recovery import new_read_retry_window
        if (game/'transport_read_window.json').exists():raise ValueError('This game already has an explicit read-window renewal')
        window=new_read_retry_window(calls,renew_read_window)
        proof=saved_transport_recovery(*args,game,renewed_window=window)
        if not proof:raise ValueError('Read-window renewal has no verified transport checkpoint')
        return '--recover-transport',{'game':game.name,'preserved_submissions':len(turns),
            'calls_sha256':digest(calls),'possible_duplicate_remote_charge':True,
            'renew_read_window':renew_read_window}
    choices=[('--recover-host-output',lambda:saved_host_output_recovery(*args,game)),
             ('--complete-grader-coverage',lambda:saved_grader_reason_recovery(*args,read(game/'puzzle_private.json'),missing_coverage=True)),
             ('--recover-transport',lambda:saved_transport_recovery(*args,game)),
             ('--auto-player-format',lambda:saved_player_auto_recovery(*args)),
             ('--recover-dialogue-action',lambda:saved_dialogue_action_recovery(*args,game)),
             ('--correct-untyped-player',lambda:saved_untyped_player_correction(*args)),
             ('--repair-grader-reason',lambda:saved_grader_reason_recovery(*args,read(game/'puzzle_private.json')))]
    for flag,check in choices:
        proof=check()
        if proof:return flag,{'game':game.name,'preserved_submissions':len(turns),
                              'calls_sha256':digest(calls),'possible_duplicate_remote_charge':proof.get('possible_duplicate_remote_charge',False)}
    raise ValueError('No verified recovery: '+str(previous.get('error') or previous.get('stop_reason')))


def desktop_notification(title,message):
    script='on run argv\ndisplay notification (item 2 of argv) with title (item 1 of argv)\nend run\n'
    try:
        result=subprocess.run(['/usr/bin/osascript','-',title,message],input=script,text=True,
                              capture_output=True,timeout=15)
        return {'requested':True,'command_succeeded':result.returncode==0,
                'visibility':'Desktop visibility depends on macOS notification permissions and Focus settings.'}
    except (OSError,subprocess.TimeoutExpired):return {'requested':True,'command_succeeded':False}


def notify(out,kind,message,desktop=True):
    delivery=desktop_notification('GoodTurtle · '+kind,message) if desktop else {'requested':False}
    event={'timestamp':now(),'kind':kind,'message':message,'delivery':delivery}
    with (out/'alerts.jsonl').open('a') as stream:stream.write(json.dumps(event,ensure_ascii=False)+'\n')
    return event


def job_rows(study,slot):
    plan=read(study/'study_plan.json',{})
    if not plan.get('jobs'):return []
    batch=study/plan['jobs'][0]['name'];rows=[]
    for meta in read(batch/'experiment_runs.json',[]):
        game=batch/meta['run_dir'];result=read(game/'result.json',meta)
        rows.append({'task':slot,'game':game.name,'trajectory':str(game/'trajectory.html'),
                     'study':str(study),**{k:result.get(k) for k in
                     ('status','submissions','final_partial_score','success','error','costs')}})
    return rows


def report(out,state):
    rows=[r for slot,job in state['jobs'].items() for r in job_rows(Path(job['latest_study']),slot)]
    costs=[r['costs'] for r in rows if r.get('costs')]
    gate=read(Path(state['campaign'])/'host_gate/cost_summary.json')
    if gate:costs.append(gate)
    dump(out/'cost_summary.json',merge_summaries(costs))
    dump(out/'experiment_runs.json',rows)
    state.update(updated_at=now(),completed_games=sum(r['status']=='completed' for r in rows))
    dump(out/'status.json',state)
    blocks=''.join('<tr>'+''.join('<td>'+html.escape(str(r[k]))+'</td>' for k in
        ('task','game','status','submissions','final_partial_score'))+'<td><a href="'+
        html.escape(os.path.relpath(r['trajectory'],out),quote=True)+'">Trajectory</a></td></tr>' for r in rows)
    alerts=(out/'alerts.jsonl').read_text() if (out/'alerts.jsonl').exists() else ''
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="30">'
        '<title>GoodTurtle supervised experiments</title><h1>GoodTurtle 自动监督</h1><p>'+html.escape(state['updated_at'])+
        ' · '+html.escape(state['status'])+' · '+str(state['completed_games'])+'/'+str(state['planned_games'])+
        ' completed</p><p><a href="status.json">Status</a> · <a href="alerts.jsonl">Alerts</a> · '
        '<a href="cost_summary.json">Cumulative costs, no duplicate recovery archives</a></p><table border="1">'
        '<tr><th>Task</th><th>Game</th><th>Status</th><th>Submissions</th><th>Score</th><th>View</th></tr>'+blocks+
        '</table><pre>'+html.escape(alerts)+'</pre>')


def supervise(args):
    campaign=Path(args.campaign).resolve();out=Path(args.out).resolve()
    previous_state=None
    manifest=read(campaign/'campaign.json')
    supplied=campaign
    if not manifest:
        previous_state=read(campaign/'status.json',{})
        if previous_state.get('status') not in ('requires_attention','interrupted') or not previous_state.get('campaign'):
            raise ValueError('Expected a stopped campaign or stopped supervisor')
        campaign=Path(previous_state['campaign'])
        manifest=copy.deepcopy(read(campaign/'campaign.json'))
        if manifest:
            for job in manifest['jobs']:
                current=Path(previous_state['jobs'][job['id']]['latest_study'])
                if not (current/'study_plan.json').exists():
                    current=Path(previous_state['jobs'][job['id']]['attempts'][-1]['source'])
                if read(current/'status.json',{}).get('status')=='running':
                    raise ValueError('A previous worker is still running; no duplicate takeover')
                job['folder']=str(current)
    if not manifest:raise ValueError('Expected an existing campaign')
    if read(campaign/'status.json',{}).get('active'):raise ValueError('Original launcher still owns active workers')
    lock=(campaign/'.supervisor.lock').open('a')
    try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:raise ValueError('Another supervisor owns this campaign') from None
    out.mkdir(parents=True,exist_ok=False)
    state={'pid':os.getpid(),'status':'running','campaign':str(campaign),'resumed_supervisor':str(supplied) if previous_state else None,'planned_games':manifest['planned_games'],
           'poll_seconds':args.interval,'max_recoveries_per_slot':args.max_recoveries,'jobs':{},
           'policy':'Verified checkpoint repairs only. Original archives, prompts, answers, scoring and quotas preserved. Unknown errors require review. Costs use each latest archive once.'}
    for job in manifest['jobs']:
        study=campaign/job['folder']
        state['jobs'][job['id']]={'latest_study':str(study),'attempts':[],
            'status':'pending','planned_games':job['planned_games'],'retry_at':time.time()}
        if previous_state:
            state['jobs'][job['id']]['prior_attempts']=previous_state['jobs'][job['id']].get('prior_attempts',[])+previous_state['jobs'][job['id']]['attempts']
    processes={};logs={};pinned={str(p.relative_to(ROOT)):digest(p.read_text()) for p in
        [ROOT/'scripts/resume_study.py',ROOT/'scripts/supervise_campaign.py',ROOT/'configs/player_format_repair.json',*sorted((ROOT/'turtle_loop').glob('*.py'))]}
    dump(out/'controller_hashes.json',pinned)
    notify(out,'监督已启动','每30秒检查；已知断点自动续跑，未知异常暂停告警。',args.notify=='macos')
    try:
        while True:
            changed=any(digest((ROOT/name).read_text())!=sha for name,sha in pinned.items())
            if changed and not state.get('controller_change_notified'):
                state['controller_change_notified']=True
                notify(out,'控制器有更新','现有冻结实验继续运行；后续恢复暂停，需验证新控制器。',args.notify=='macos')
            for slot,job in state['jobs'].items():
                if job['status'] in ('completed','requires_attention'):continue
                if slot in processes:
                    proc=processes[slot];code=proc.poll()
                    if code is None:
                        if not job.get('recovery_notified') and (Path(job['latest_study'])/'study_plan.json').exists():
                            proof=job['attempts'][-1]['checkpoint']
                            folder=next(Path(job['latest_study']).glob('*/'+proof['game']),None)
                            if folder and (folder/'trajectory.jsonl').exists() and any(
                                    e.get('event') in ('transport_recovery_response_observed','saved_grader_coverage_completed') and e.get('source_calls_sha256')==proof['calls_sha256'] for e in
                                    (json.loads(l) for l in (folder/'trajectory.jsonl').read_text().splitlines())):
                                job['recovery_notified']=True
                                notify(out,'已恢复运行',slot+' 已收到恢复后API答复，原轨迹和额度继续保留。',args.notify=='macos')
                        # Alert stalled requests; do not kill/replay an ambiguous call.
                        paths=list(Path(job['latest_study']).glob('*/**/api_calls.jsonl'))
                        latest=max([job['started_at'],*(p.stat().st_mtime for p in paths)])
                        if time.time()-latest>args.stall_seconds and not job.get('stall_notified'):
                            job['stall_notified']=True
                            notify(out,'长时间未更新',slot+' 长时间未更新，请查看正在等待的API请求。',args.notify=='macos')
                        continue
                    logs.pop(slot).close();del processes[slot]
                    job['attempts'][-1]['exit_code']=code
                    if code==0:
                        rows=job_rows(Path(job['latest_study']),slot)
                        if len(rows)==job['planned_games'] and all(r['status']=='completed' for r in rows):
                            job['status']='completed'
                            notify(out,'任务完成',slot+' 已完成全部对局。',args.notify=='macos');continue
                    if code==130:
                        job['status']='requires_attention'
                        notify(out,'已暂停',slot+' 收到中断，不自动撤销暂停。',args.notify=='macos');continue
                    job['status']='pending';job['retry_at']=time.time()+args.cooldown*2**(len(job['attempts'])-1)
                    notify(out,'检测到停止',slot+' 已停止，正在校验保留原轨迹的恢复方案。',args.notify=='macos')
                if time.time()<job['retry_at']:continue
                try:
                    current=Path(job['latest_study']);rows=job_rows(current,slot)
                    if len(rows)==job['planned_games'] and all(r['status']=='completed' for r in rows):
                        job['status']='completed';continue
                    if changed:raise ValueError('Controller changed; existing frozen workers were preserved, but a new repair requires validation')
                    if len(job['attempts'])>=args.max_recoveries:raise ValueError('Bounded recovery limit reached')
                    renewal=getattr(args,'renew_read_window',None) if not job['attempts'] else None
                    flag,proof=choose_recovery(current,renewal) if renewal else choose_recovery(current)
                    if proof['calls_sha256'] in [a['checkpoint']['calls_sha256'] for a in job['attempts']]:
                        raise ValueError('Identical failed checkpoint already attempted; refusing a repair loop')
                    target=out/'continuations'/slot/f"attempt_{len(job['attempts'])+1:02d}"
                    target.parent.mkdir(parents=True,exist_ok=True)
                    log=(out/f"{slot}_{len(job['attempts'])+1:02d}.log").open('w')
                    command=[sys.executable,str(ROOT/'scripts/resume_study.py'),'--from-study',str(current),
                             '--out',str(target),flag,'--mode','run']
                    if renewal:command.extend(['--renew-read-window',renewal])
                    proc=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                    processes[slot]=proc;logs[slot]=log
                    job.update(status='running',latest_study=str(target),pid=proc.pid,started_at=time.time(),stall_notified=False,recovery_notified=False)
                    job['attempts'].append({'out':str(target),'source':str(current),'mode':flag,'checkpoint':proof,'pid':proc.pid})
                    notify(out,'自动续跑',slot+' 从已保存的 '+str(proof['preserved_submissions'])+' 次提交继续。',args.notify=='macos')
                except (ValueError,OSError,KeyError) as exc:
                    job.update(status='requires_attention',error=str(exc))
                    notify(out,'需要处理',slot+'：'+str(exc),args.notify=='macos')
            if all(j['status'] in ('completed','requires_attention') for j in state['jobs'].values()):
                state['status']='completed' if all(j['status']=='completed' for j in state['jobs'].values()) else 'requires_attention'
                report(out,state)
                notify(out,'监督结束','全部完成。' if state['status']=='completed' else '存在无法安全自动恢复的断点，请查看告警。',args.notify=='macos')
                return 0 if state['status']=='completed' else 1
            report(out,state)
            time.sleep(args.interval)
    except BaseException as exc:
        state.update(status='interrupted' if isinstance(exc,KeyboardInterrupt) else 'requires_attention',error=type(exc).__name__+': '+str(exc))
        for proc in processes.values():
            if proc.poll() is None:os.killpg(proc.pid,signal.SIGINT)
        for proc in processes.values():
            try:proc.wait(timeout=30)
            except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGTERM)
        for log in logs.values():log.close()
        report(out,state);notify(out,'监督已停止',state['error'],args.notify=='macos')
        if not isinstance(exc,KeyboardInterrupt):raise
        return 130
    finally:lock.close()


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--campaign',required=True)
    p.add_argument('--out',required=True,help='New supervision directory')
    p.add_argument('--interval',type=int,default=30)
    p.add_argument('--cooldown',type=int,default=60)
    p.add_argument('--max-recoveries',type=int,default=3)
    p.add_argument('--stall-seconds',type=int,default=2700)
    p.add_argument('--notify',choices=['macos','none'],default='macos')
    p.add_argument('--renew-read-window',metavar='REASON',help='Explicit first-checkpoint operator renewal after exhausted read retries; never automatically renewed again')
    a=p.parse_args(argv)
    if not 1<=a.interval<=60 or not 1<=a.max_recoveries<=10 or a.cooldown<0 or a.stall_seconds<60:
        p.error('interval 1..60, max-recoveries 1..10, cooldown >=0, stall-seconds >=60')
    def terminate(*unused):raise KeyboardInterrupt()
    signal.signal(signal.SIGTERM,terminate)
    return supervise(a)


if __name__=='__main__':raise SystemExit(main())
