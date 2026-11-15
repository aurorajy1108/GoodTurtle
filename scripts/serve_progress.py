#!/usr/bin/env python3
"""Serve a live, read-only experiment dashboard on loopback; no repo-wide file server.

python3 scripts/serve_progress.py --batch runs/api/my_study/team --port 8765
"""
import argparse
import json
import mimetypes
import sys
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.watch_progress import collect


def artifact_path(batches, request_path):
    parts = unquote(request_path).split('/')
    if len(parts) < 4 or parts[1] != 'runs' or not parts[2].isdigit():
        return None
    index = int(parts[2])
    if index >= len(batches) or any(p.startswith('.') for p in parts[3:]):
        return None
    root = batches[index][0].resolve()
    path = root.joinpath(*parts[3:]).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        return None
    if path.suffix not in ('.html', '.json', '.jsonl', '.csv', '.md', '.txt'):
        return None
    return path


class Handler(BaseHTTPRequestHandler):
    def __init__(self, *args, batches, **kwargs):
        self.batches = batches
        super().__init__(*args, **kwargs)

    def do_GET(self):
        route = urlsplit(self.path).path
        if route in ('/', '/index.html'):
            body = (ROOT/'turtle_loop/web/progress.html').read_bytes()
            content_type = 'text/html; charset=utf-8'
        elif route == '/progress.json':
            body = json.dumps(collect(self.batches), ensure_ascii=False, allow_nan=False).encode()
            content_type = 'application/json; charset=utf-8'
        else:
            path = artifact_path(self.batches, route)
            if path is None:
                self.send_error(404)
                return
            body = path.read_bytes()
            content_type = mimetypes.guess_type(str(path))[0] or 'text/plain'
            content_type += '; charset=utf-8'
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch', type=Path, action='append', required=True)
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    batches = [(p.resolve(), '/runs/'+str(i)) for i, p in enumerate(args.batch)]
    if any(not p.is_dir() for p, _ in batches):
        parser.error('Each --batch must be an existing experiment batch directory')
    server = ThreadingHTTPServer(('127.0.0.1', args.port), partial(Handler, batches=batches))
    print(f'GoodTurtle live progress: http://127.0.0.1:{server.server_port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
