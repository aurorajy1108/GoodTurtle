import json,pathlib,sys
O=pathlib.Path(__file__).parent
D=json.loads((O/'extracted.json').read_text())
if sys.argv[1]=='read':
 for n in map(int,sys.argv[2:]):
  g=D[n]; print('\nGAME',n,g['game_id'])
  for s in g['submissions']:
   print(str(s['submission'])+('F' if s['type']=='final' else 'Q'),{'yes':'Y','no':'N','yes and no':'M','irrelevant':'I',None:'?'}[s['actual_label']],s['question'].replace('\n',' '))
   if s['evaluation']:
    e=s['evaluation'];print(' E',e.get('partial_score'),[(c['id'],c['credit'],c.get('reason')) for c in e.get('checkpoints',[])])
elif sys.argv[1]=='list':
 for n,g in enumerate(D): print(n,g['game_id'],len(g['submissions']))
