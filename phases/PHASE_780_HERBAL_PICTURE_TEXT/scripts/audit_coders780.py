#!/usr/bin/env python3
"""PHASE_780 coder transcript audit: every tool call of every coder must be Read on the batch file, the codebook or a
listed image, or Write on the batch's output file. Prints one line per batch and writes results/coder_audit780.json.

  python audit_coders780.py <agents.json> <transcript_dir>
agents.json maps batch name (e.g. A_V_1) to the agent id; transcripts are <transcript_dir>/agent-<id>.jsonl."""
import json
import sys
from pathlib import Path

CODE_DIR = Path('C:/git/voynich/external/phase780_coding')
RES = Path('C:/git/voynich/phases/PHASE_780_HERBAL_PICTURE_TEXT/results')


def norm(p):
    return str(p).replace('\\', '/').lower().replace('c:/users/epilec~1', 'c:/users/epilectrik')


def tool_calls(path):
    calls = []
    for ln in open(path, encoding='utf-8', errors='replace'):
        try:
            d = json.loads(ln)
        except Exception:
            continue
        msg = d.get('message') or {}
        content = msg.get('content') if isinstance(msg, dict) else None
        if not isinstance(content, list):
            continue
        for c in content:
            if isinstance(c, dict) and c.get('type') == 'tool_use':
                calls.append((c.get('name'), c.get('input', {})))
    return calls


def main():
    agents = json.load(open(sys.argv[1]))
    tdir = Path(sys.argv[2])
    out = {}
    prev = json.load(open(RES / 'coder_audit780.json')) if (RES / 'coder_audit780.json').exists() else {}
    for batch, aid in agents.items():
        b = json.load(open(CODE_DIR / f'batch_{batch}.json', encoding='utf-8'))
        allowed_read = {norm(CODE_DIR / f'batch_{batch}.json'), norm(b['codebook'])} | {norm(p) for p in b['images']}
        allowed_write = {norm(b['out'])}
        tp = tdir / f'agent-{aid}.jsonl'
        if not tp.exists():
            out[batch] = {'status': 'NO TRANSCRIPT'}
            continue
        calls = tool_calls(tp)
        bad = []
        for name, inp in calls:
            fp = norm(inp.get('file_path', ''))
            if name == 'Read' and fp in allowed_read:
                continue
            if name == 'Write' and fp in allowed_write:
                continue
            bad.append({'tool': name, 'input': {k: str(v)[:160] for k, v in inp.items()}})
        coded = json.load(open(b['out'], encoding='utf-8')) if Path(b['out']).exists() else {}
        missing = [Path(p).stem for p in b['images'] if Path(p).stem not in coded]
        out[batch] = {'status': 'PASS' if not bad and not missing else 'FAIL', 'n_tool_calls': len(calls),
                      'violations': bad, 'n_images': len(b['images']), 'n_coded': len(coded), 'missing': missing}
        print(f"{batch}: {out[batch]['status']} ({len(calls)} calls, {len(bad)} violations, {len(coded)}/{len(b['images'])} coded)")
        for v in bad[:5]:
            print('   ', v)
    prev.update(out)
    json.dump(prev, open(RES / 'coder_audit780.json', 'w', encoding='utf-8'), indent=1)


if __name__ == '__main__':
    main()
