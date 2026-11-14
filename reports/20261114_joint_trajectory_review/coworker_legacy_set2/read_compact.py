import pathlib,json,sys
D=json.loads((pathlib.Path(__file__).parent/'extracted.json').read_text())
REPL=[('the father\'s','F\'s'),('the father','F'),('The father','F'),('his father','F'),('the daughter\'s','D\'s'),('the daughter','D'),('The daughter','D'),('his daughter','his D'),('daughter','D'),('father','F'),('the kidnapper','K'),('The kidnapper','K'),('kidnapper','K'),('the hostage','H'),('The hostage','H'),('hostage','H'),('the ransom','R'),('The ransom','R'),('ransom','R'),('because','bc'),('regardless of whether','regardless whether'),('regardless of','regardless'),('something','sth'),('someone','sb'),('rather than','vs'),('such as','e.g.'),('before the deadline','before cutoff'),('one hundred million yen','100m yen'),('fifty million yen','50m yen'),('one million yen','1m yen'),('Did the','D the'),('Does the','Does'),('Was the','W the'),('Were the','W the'),('Is the','Is')]
def ab(s):
 for a,b in REPL:s=s.replace(a,b)
 return s.replace('\n',' ')
for i in map(int,sys.argv[1:]):
 g=D[i];print('\nGAME',i,g['game_id'],'PUZZLE',g['puzzle']['id'])
 for s in g['submissions']:
  print(str(s['submission'])+('F' if s['type']=='final' else ''),{'yes':'Y','no':'N','yes and no':'M','irrelevant':'I'}[s['actual_label']],ab(s['question']))
  if s['evaluation']:
   e=s['evaluation'];print(' E',e.get('partial_score'),'complete',e.get('complete'),'full',e.get('full_solution'),'; '.join(c['id']+'='+str(c['credit'])+' '+ab(c.get('reason','')) for c in e.get('checkpoints',[])));print(' R',[(x.get('id'),x.get('status')) for x in e.get('requirement_coverage',[])],ab(e.get('completion_note','')))
