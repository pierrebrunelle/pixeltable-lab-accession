"""Parallel accessions and assignments, then 8 technicians racing to claim the same work item.

Usage:
    python client_demo.py                             # local service on port 8000
    python client_demo.py https://<your-service-url>  # hosted service; set PIXELTABLE_API_KEY first

Standard library only. If PIXELTABLE_API_KEY is set it is sent as the X-api-key header.
Exits non-zero if any call returns an unexpected status code.
"""
import concurrent.futures as cf
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

BASE = (sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8000').rstrip('/')
API_KEY = os.environ.get('PIXELTABLE_API_KEY')
HERE = Path(__file__).resolve().parent
FAILURES: list[str] = []


def _send(req: urllib.request.Request) -> tuple[int, object]:
    if API_KEY:
        req.add_header('X-api-key', API_KEY)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read()
            if 'json' in (resp.headers.get('Content-Type') or ''):
                return resp.status, json.loads(raw or b'null')
            return resp.status, f'<{len(raw)} bytes {resp.headers.get("Content-Type")}>'
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors='replace')[:300]


def call(method: str, path: str, body: dict | None = None) -> tuple[int, object]:
    data = json.dumps(body).encode() if body is not None else None
    return _send(urllib.request.Request(BASE + path, data=data, method=method,
                                        headers={'Content-Type': 'application/json'}))


def upload(path: str, fields: dict, files: dict) -> tuple[int, object]:
    """multipart/form-data POST: fields are form values, files maps field name -> local file path."""
    boundary = uuid.uuid4().hex
    parts = []
    for k, v in fields.items():
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
    for k, fp in files.items():
        fp = Path(fp)
        ctype = mimetypes.guess_type(fp.name)[0] or 'application/octet-stream'
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"; filename="{fp.name}"\r\n'
                     f'Content-Type: {ctype}\r\n\r\n'.encode() + fp.read_bytes() + b'\r\n')
    body = b''.join(parts) + f'--{boundary}--\r\n'.encode()
    return _send(urllib.request.Request(BASE + path, data=body, method='POST',
                                        headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}))


def check(label: str, code: int, out: object, expect: int = 200):
    print(f'{label:<36} {code}  {json.dumps(out)[:180]}')
    if code != expect:
        FAILURES.append(f'{label}: got {code}, expected {expect}')
    return out


def show(label: str, method: str, path: str, body: dict | None = None, expect: int = 200):
    code, out = call(method, path, body)
    return check(label, code, out, expect)


def parallel(label: str, n: int, fn) -> list:
    with cf.ThreadPoolExecutor(max_workers=min(n, 16)) as pool:
        results = list(pool.map(fn, range(n)))
    codes = sorted({c for c, _ in results})
    print(f'{label:<36} {n} calls, status codes: {codes}')
    if codes != [200]:
        FAILURES.append(f'{label}: status codes {codes}')
    return results


def q(s: str) -> str:
    return urllib.parse.quote(s)


run = uuid.uuid4().hex[:6]
show('triage band (compute)', 'POST', '/urgency', {'priority': 3, 'delayed_min': 25})
parallel('12 parallel sample accessions', 12, lambda i: call('POST', '/samples', {
    'accession_id': f'A-{run}-{i:02d}', 'specimen': 'serum', 'priority': 1 + i % 3,
    'received_at': f'2026-09-28T09:{i:02d}', 'batch_code': f'B-{run}'}))
results = parallel('12 parallel assignments', 12, lambda i: call('POST', '/assignments', {
    'accession_id': f'A-{run}-{i:02d}', 'station_id': 'CHEM-2', 'priority': 1 + i % 3, 'delayed_min': 5 * i,
    'status': 'queued', 'claimed_by': None}))
target = results[0][1].get('id') if isinstance(results[0][1], dict) else None
techs = [f'tech-{n}' for n in range(8)]
parallel('8 techs race to claim one item', 8, lambda i: call('POST', '/assignments/claim',
                                                              {'id': target, 'status': 'claimed', 'claimed_by': techs[i]}))
queue = show('CHEM-2 queue', 'GET', '/stations/queue?station_id=CHEM-2')
winner = [r for r in queue.get('rows', []) if r['id'] == target] if isinstance(queue, dict) else []
print(f'{"claimed by (last writer wins)":<36} {winner[0]["claimed_by"] if winner else None}')
if not winner or winner[0]['claimed_by'] not in techs:
    FAILURES.append('claimed row missing or inconsistent')
show('this run\'s batch', 'GET', f'/batches?batch_code=B-{run}')


if FAILURES:
    print('\nFAILED:', *FAILURES, sep='\n  ')
    sys.exit(1)
print('\nall calls OK')
