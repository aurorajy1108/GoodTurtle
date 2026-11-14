import json,pathlib,sys,re
D=json.loads((pathlib.Path(__file__).parent/'extracted.json').read_text())
REPL=[('the student\'s','S\'s'),('the student','S'),('your courses','YC'),('the courses','TC'),('course selection','CS'),('course-selection','CS'),('course registration','CR'),('course enrollment','CE'),('enrollment','EN'),('academic courses','AC'),('academic classes','AC'),('university','U'),('University of Hong Kong','HKU'),('Did you','D you'),('Did the','D the'),('Were the','W the'),('Was the','W the'),('Did another person','D another'),('another person','another'),('the other person','OP'),('because','bc'),('disappear','vanish'),('removed','rm'),('the disappearance','the vanishing'),('something','sth'),('such as','e.g.'),('rather than','vs'),('rather','vs'),('in a way that','so'),('physically','phys'),('course','c'),('courses','cs')]
def ab(s):
 for x,y in REPL:s=s.replace(x,y)
 return s.replace('\n',' ')
for n in map(int,sys.argv[1:]):
 g=D[n];print('\nGAME',n,g['game_id'])
 for s in g['submissions']:
  print(str(s['submission'])+('F' if s['type']=='final' else ''),{'yes':'Y','no':'N','yes and no':'M','irrelevant':'I'}[s['actual_label']],ab(s['question']))
  if s['evaluation']:
   e=s['evaluation'];print(' E',e.get('partial_score'),'; '.join(c['id']+'='+str(c['credit'])+' '+ab(c.get('reason','')) for c in e.get('checkpoints',[])))
