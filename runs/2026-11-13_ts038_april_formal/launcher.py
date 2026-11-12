import argparse,datetime,hashlib,json,os,subprocess,sys
from pathlib import Path
ROOT=Path('/Users/tongmindy/Desktop/COMP1110/gp-comp1110/GoodTurtle')
os.chdir(ROOT);sys.path.insert(0,str(ROOT))
from scripts.run_ts038_smoke import child_environment
from scripts.team_campaign import prepare,execute,verify
reference=ROOT/'runs/api/ts038_april_formal_dry_20261113_parserfix01'
out=ROOT/'runs/api/ts038_april_formal_20261113_parserfix01'
if out.exists():raise SystemExit('Refusing to overwrite formal output')
dry=json.loads((reference/'campaign.json').read_text())
assert json.loads((reference/'status.json').read_text())['status']=='completed'
assert dry['planned_games']==4 and len(dry['jobs'])==1
assert dry['jobs'][0]['id']=='mas-ts038-b' and dry['jobs'][0]['repeat_offset']==2
verify(reference/dry['jobs'][0]['folder']/'runtime_snapshot',dry['jobs'][0]['hashes'])
env=child_environment(ROOT/'.env',Path('/etc/ssl/cert.pem'),'direct',True)
os.environ.update(env)
args=argparse.Namespace(command='start',preset='full',runner='april',tasks='mas-ts038-b',workers=1,
 set1_positive='15',config=str(ROOT/'configs/loop.deepseek.json'),
 dataset=str(ROOT/'data/annotations/turtle50_v4/private.json'),seed=20261111,host_gate='auto',
 on_error='stop',poll_seconds=2,mode='run',out=str(out))
folder,manifest=prepare(args)
job=manifest['jobs'][0]
assert manifest['planned_games']==4 and manifest['host_gate'] is None
assert job['repeat']==2 and job['repeat_offset']==2 and job['conditions']==['solo','free_dialogue']
assert job['hashes']==dry['jobs'][0]['hashes'],'Live inputs differ from verified dry-run'
smoke=ROOT/'runs/api/ts038_smoke_live_20261112_contractfix01'
smoke_hashes=json.loads((smoke/'snapshot_hashes.json').read_text())
semantic_keys=[k for k in job['hashes'] if (k.startswith(('turtle_loop/','prompts/','data/')) and '/web/' not in k)
 or k in ('configs/run.json','configs/host_bindings.json','configs/player_format_repair.json')]
semantic_changes=[k for k in semantic_keys if job['hashes'][k]!=smoke_hashes[k]]
assert semantic_changes==['turtle_loop/engine.py'],'Unexpected changes beyond documented JSON parser fix'
provenance={'purpose':'Formal TS038 April b slot; global repeats 3 and 4; smoke excluded',
 'started_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
 'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
 'git_branch':subprocess.check_output(['git','branch','--show-current'],text=True).strip(),
 'git_status':subprocess.check_output(['git','status','--porcelain'],text=True),
 'dry_run':str(reference),'dry_live_hashes_identical':True,'semantic_files_matching_smoke':len(semantic_keys)-len(semantic_changes),'changes_from_smoke':semantic_changes,'technical_failure_archive':'runs/api/ts038_april_formal_20261113',
 'SSL_CERT_FILE':'/etc/ssl/cert.pem','TURTLE_DEEPSEEK_PROXY_MODE':'direct',
 'protocol_hash':manifest['protocol_hash'],'launcher_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(out/'formal_provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'out':str(out),'task':'mas-ts038-b','runner':'april','global_repeats':[3,4],
 'games':4,'dry_live_inputs_identical':True,'semantic_files_matching_smoke':len(semantic_keys)-len(semantic_changes),'changes_from_smoke':semantic_changes,'technical_failure_archive':'runs/api/ts038_april_formal_20261113'},ensure_ascii=False),flush=True)
raise SystemExit(execute(out,manifest))
