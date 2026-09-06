#!/usr/bin/env bash
# Memory across a restart -- the only honest way to test it is to actually
# stop the process and start a new one.
#
#   bash eval/e2e/restart_memory.sh
set -u
BASE=http://127.0.0.1:8765
fail(){ echo "FAIL: $1"; exit 1; }

curl -sf $BASE/api/status >/dev/null || fail "server not running on $BASE"

python3 - <<'PY' || fail "could not write memory"
import json
from websockets.sync.client import connect
with connect('ws://127.0.0.1:8765/ws') as ws:
    json.loads(ws.recv())
    ws.send(json.dumps({'type':'say','text':'remember I use neovim as my editor'}))
    while True:
        m = json.loads(ws.recv())
        if m.get('type') == 'reply':
            print('  wrote:', m['text'][:60]); break
PY

echo "  now: stop the server, start it again, then run:"
echo "    curl -s $BASE/api/memory | python3 -m json.tool | head -20"
echo "  the editor=neovim fact must still be there."
