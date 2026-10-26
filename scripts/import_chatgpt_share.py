#!/usr/bin/env python3
"""Extract visible user/assistant messages from a saved public ChatGPT share page.

No JavaScript execution, login cookies, or private API calls. System/hidden/tool
messages are excluded. Output is a source archive, never automatically a host pack.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path


def extract(html, source_url):
    chunks=re.findall(r'streamController\.enqueue\(("(?:\\.|[^"\\])*")\)',html)
    for chunk in chunks:
        try:pool=json.loads(json.loads(chunk))
        except (ValueError,TypeError):continue
        if not isinstance(pool,list) or 'linear_conversation' not in pool:continue
        key='_'+str(pool.index('linear_conversation'))
        refs=[item[key] for item in pool if isinstance(item,dict) and key in item]
        if len(refs)!=1:raise ValueError('Ambiguous public linear conversation')
        memo={}
        def decode(ref):
            if type(ref) is not int:return ref
            if ref<0:return None
            if ref in memo:return memo[ref]
            value=pool[ref]
            if isinstance(value,dict):
                result={};memo[ref]=result
                for k,v in value.items():
                    name=decode(int(k[1:])) if k.startswith('_') and k[1:].isdigit() else k
                    result[name]=decode(v)
                return result
            if isinstance(value,list):
                result=[];memo[ref]=result;result.extend(decode(v) for v in value);return result
            return value
        nodes=decode(refs[0]);messages=[]
        for node in nodes:
            msg=node.get('message') or {}
            role=msg.get('author',{}).get('role');content=msg.get('content') or {}
            if (role not in ('user','assistant') or msg.get('channel') not in (None,'final')
                or content.get('content_type')!='text'
                or msg.get('metadata',{}).get('is_visually_hidden_from_conversation',False)):
                continue
            parts=content.get('parts',[])
            if any(not isinstance(part,str) for part in parts):raise ValueError('Non-text part requires separate review')
            messages.append({'message_id':msg['id'],'role':role,'text':'\n'.join(parts)})
        if not messages:raise ValueError('No visible messages found')
        ids=[m['message_id'] for m in messages]
        if len(ids)!=len(set(ids)):raise ValueError('Duplicate message ID in linear conversation')
        return {'source_url':source_url,'extraction':'public_linear_text_v1',
                'visible_messages':len(messages),'omitted_nonvisible_nodes':len(nodes)-len(messages),'messages':messages}
    raise ValueError('No readable public conversation stream; do not treat login/error page as a chat')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--html',required=True,help='Saved HTML of the user-provided public share page')
    p.add_argument('--source-url',required=True,help='Original share URL for provenance')
    p.add_argument('--out',required=True,help='New normalized messages JSON file')
    args=p.parse_args();raw=Path(args.html).read_bytes();out=Path(args.out)
    if out.exists():p.error('Output already exists; preserve existing archives')
    value=extract(raw.decode('utf-8'),args.source_url)
    value['source_html_sha256']=hashlib.sha256(raw).hexdigest()
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'messages':value['visible_messages'],'output':str(out)}))


if __name__=='__main__':main()
