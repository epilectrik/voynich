#!/usr/bin/env python3
"""Registry integrity check — permanent bookkeeping tool (added 2026-09-27).

Detects drift between the constraint registry and the documents that consume it:

1. Status of every constraint number, from the GENERATED table (authoritative) plus INDEX.md:
   LIVE (Tier 0-2), DEMOTED (Tier 3/4 reached by demotion), SPECULATIVE (Tier 3/4 from the start; not
   flagged), TIER1 (falsified / invalidated),
   DEAD (registered in INDEX.md but dropped from the table: struck without a live tier, or
   STATUS:RETRACTED|SUPERSEDED), UNKNOWN (cited but never registered).
2. Citations of DEMOTED / DEAD / UNKNOWN constraints in living documents that the expert agents
   and new sessions consume (contracts, core docs, interpretation layer, agent generator, fits),
   flagged when no annotation (retract / demot / supersed / withdrawn / struck / ~~) is nearby.
3. Closure-banner phrasing that contradicts the standing directive "never declare the program
   exhausted / closed / foreclosed while referents are unrecovered".

Usage:
    python scripts/registry_integrity_check.py              # report to stdout + context/SYSTEM/REGISTRY_INTEGRITY_REPORT.md
    python scripts/registry_integrity_check.py --json out.json

Run it after `python context/generate_constraint_table.py` in the bookkeeping checklist.
Exit code is 0 always (it is a report, not a gate); read the summary counts.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TABLE = ROOT / 'context' / 'CONSTRAINT_TABLE.txt'
INDEX = ROOT / 'context' / 'CLAIMS' / 'INDEX.md'
REPORT = ROOT / 'context' / 'SYSTEM' / 'REGISTRY_INTEGRITY_REPORT.md'

# Living documents: consumed by new sessions and/or embedded in the expert agents.
TARGET_GLOBS = [
    'CLAUDE.md',
    'context/CLAUDE_INDEX.md',
    'context/MODEL_CONTEXT.md',
    'context/PROJECT_SYNTHESIS.md',
    'context/CRAZY_EXPERT_STANCE.md',
    'context/generate_expert_context.py',
    'context/MODEL_FITS/FIT_TABLE.txt',
    'context/CORE/*.md',
    'context/STRUCTURAL_CONTRACTS/*.yaml',
    'context/SPECULATIVE/*.md',
    # added 2026-09-28 (v7.26): entry-level and reference docs that were not scanned before
    'README.md',
    'WHAT_WE_CLAIM.md',
    'context/SYSTEM/STATUS_BRIEF.md',
    'context/SYSTEM/RESEARCH_AGENDA.md',
    'context/ARCHITECTURE/*.md',
    'context/OPERATIONS/*.md',
    'context/METRICS/*.md',
    'context/MAPS/*.md',
    'context/TERMINOLOGY/*.md',
]
ANNOTATION = re.compile(r'retract|demot|supersed|withdrawn|struck|~~|DEAD|invalidat|refuted|correction|scoped|historical|'
                        r'never frame|retired|re-tiered|Tier[ -]?3', re.IGNORECASE)
CITE = re.compile(r'(?<![A-Za-z0-9])C(\d{2,4})(?:\s*[–-]\s*C?(\d{2,4}))?(?![0-9])')
CLOSURE = re.compile(
    r'ANALYSIS CLOSED|Structural work is DONE|structurally closed system|Characterization program COMPLETE|'
    r'STRUCTURALLY EXHAUSTED|\bforeclosed\b|methodology is now saturated|defensible terminal|'
    r'FROZEN STATE|explanatory saturation|cannot be reopened|Definitively rejected',
    re.IGNORECASE)
ANNOT_WINDOW = 160  # characters either side of a citation searched for an annotation


DEMOTION_MARK = re.compile(r'\bDEMOTED\b|Tier\s*[0-2]\s*→\s*[34]|~~[0-2]~~|Registry cascade', re.IGNORECASE)


def demoted_in_index():
    """Numbers whose INDEX tier cell records a demotion ('~~2~~ 3'). A borderline '2/3' cell is not a demotion."""
    out = set()
    row = re.compile(r'^\|[ \t]*(?:~~)?[ \t]*\*{0,2}(\d{2,4})(?:\.[a-z])?\*{0,2}[ \t]*(?:~~)?[ \t]*\|(.*?)\|([^|\n]*)\|',
                     re.MULTILINE)
    for m in row.finditer(INDEX.read_text(encoding='utf-8')):
        cell = m.group(3)
        if '~~' in cell:
            out.add(int(m.group(1)))
    return out


def load_table():
    """LIVE (Tier 0/2), TIER1, DEMOTED (Tier 3/4 reached by demotion), SPECULATIVE (Tier 3/4 from the start;
    not flagged — a citation of a speculative row is not drift). Fixed 2026-09-28 (v7.26): a Tier 0-2 row that
    merely mentions 'DEMOTED' in its text (e.g. a demoted sub-leg) is LIVE, not DEMOTED."""
    demoted = demoted_in_index()
    status = {}
    for line in TABLE.read_text(encoding='utf-8').splitlines():
        parts = line.split('\t')
        if len(parts) < 3 or not parts[0].startswith('C'):
            continue
        num = parts[0][1:].split('.')[0]
        try:
            n = int(num)
        except ValueError:
            continue
        tier, desc = parts[2].strip(), parts[1]
        if tier in ('3', '4'):
            status.setdefault(n, 'DEMOTED' if (n in demoted or DEMOTION_MARK.search(desc)) else 'SPECULATIVE')
        elif tier == '1':
            status.setdefault(n, 'TIER1')
        else:
            status.setdefault(n, 'LIVE')
    return status


def registered_in_index():
    """Numbers registered anywhere in the registry: INDEX.md rows (struck or not) and headings in the
    grouped registry files (struck or not, e.g. '### ~~C476~~ - [RETRACTED]')."""
    nums = set()
    for m in re.finditer(r'^\|\s*(?:~~)?\s*\*{0,2}(\d{2,4})(?:\.[a-z])?\*{0,2}\s*(?:~~)?\s*\|',
                         INDEX.read_text(encoding='utf-8'), re.MULTILINE):
        nums.add(int(m.group(1)))
    for reg in (ROOT / 'context' / 'CLAIMS').glob('*.md'):
        for m in re.finditer(r'^#{2,3}\s*(?:~~)?\s*C(\d{2,4})\b', reg.read_text(encoding='utf-8', errors='replace'),
                             re.MULTILINE):
            nums.add(int(m.group(1)))
    return nums


def classify(n, table_status, registered):
    if n in table_status:
        return table_status[n]
    if n in registered:
        return 'DEAD'
    return 'UNKNOWN'


def iter_targets():
    seen = set()
    for pattern in TARGET_GLOBS:
        for path in sorted(ROOT.glob(pattern)):
            if path.is_file() and path not in seen:
                seen.add(path)
                yield path


def scan(table_status, registered):
    findings = []           # (file, line, number, status, annotated, excerpt)
    closures = []           # (file, line, excerpt)
    for path in iter_targets():
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding='utf-8', errors='replace')
        lines = text.split('\n')
        offsets = []
        pos = 0
        for ln in lines:
            offsets.append(pos)
            pos += len(ln) + 1
        for i, ln in enumerate(lines, 1):
            if CLOSURE.search(ln) and not ANNOTATION.search(ln):
                closures.append((rel, i, ln.strip()[:200]))
            for m in CITE.finditer(ln):
                a = int(m.group(1))
                b = int(m.group(2)) if m.group(2) else a
                if b < a or b - a > 60:       # not a real range
                    b = a
                for n in range(a, b + 1):
                    if n < 70:                # below the registry's numbering
                        continue
                    st = classify(n, table_status, registered)
                    if st in ('LIVE', 'TIER1', 'SPECULATIVE'):
                        continue
                    if st == 'UNKNOWN' and a < n < b:   # unregistered interior of a cited range (e.g. C109-C114)
                        continue
                    start = offsets[i - 1] + max(0, m.start() - ANNOT_WINDOW)
                    end = offsets[i - 1] + min(len(ln), m.end() + ANNOT_WINDOW)
                    annotated = bool(ANNOTATION.search(text[start:end]))
                    findings.append((rel, i, n, st, annotated, ln.strip()[:180]))
    return findings, closures


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', help='also write findings as JSON to this path')
    ap.add_argument('--no-report', action='store_true', help='do not write the markdown report')
    args = ap.parse_args()

    table_status = load_table()
    registered = registered_in_index()
    findings, closures = scan(table_status, registered)

    unannotated = [f for f in findings if not f[4]]
    by_file = defaultdict(Counter)
    for f in unannotated:
        by_file[f[0]][f[3]] += 1
    by_number = Counter((f[2], f[3]) for f in unannotated)

    counts = Counter(table_status.values())
    out = []
    out.append(f"# Registry Integrity Report\n\n**Generated:** {date.today().isoformat()} by "
               f"`scripts/registry_integrity_check.py` (regenerate after every registry change).\n")
    out.append(f"**Generated table:** LIVE (Tier 0/2) {counts['LIVE']}, TIER1 {counts['TIER1']}, "
               f"DEMOTED (Tier 3/4) {counts['DEMOTED']}, SPECULATIVE (Tier 3/4 from the start, not flagged) "
               f"{counts['SPECULATIVE']}; registered numbers in INDEX.md: {len(registered)}; "
               f"dead (registered, not in table): {len(registered - set(table_status))}.\n")
    out.append(f"**Citations of non-live constraints in living docs:** {len(findings)} "
               f"({len(unannotated)} without a nearby annotation).  "
               f"**Unannotated closure-banner lines:** {len(closures)}.\n")
    out.append("\n## Unannotated citations by file\n\n| File | DEMOTED | DEAD | UNKNOWN |\n|---|---|---|---|")
    for rel, c in sorted(by_file.items(), key=lambda kv: -sum(kv[1].values())):
        out.append(f"| {rel} | {c['DEMOTED']} | {c['DEAD']} | {c['UNKNOWN']} |")
    out.append("\n## Most-cited non-live constraints (unannotated)\n\n| Constraint | Status | Citations |\n|---|---|---|")
    for (n, st), k in by_number.most_common(40):
        out.append(f"| C{n} | {st} | {k} |")
    out.append("\n## Closure-banner lines (unannotated)\n")
    for rel, i, ex in closures:
        out.append(f"- `{rel}:{i}` — {ex}")
    out.append("\n## All unannotated citations\n")
    for rel, i, n, st, _, ex in unannotated:
        out.append(f"- `{rel}:{i}` C{n} [{st}] — {ex}")
    report = '\n'.join(out) + '\n'

    head = report.split('\n## All unannotated citations')[0]
    print(head)
    if not args.no_report:
        REPORT.write_text(report, encoding='utf-8')
        print(f"\nFull report: {REPORT.relative_to(ROOT).as_posix()}")
    if args.json:
        Path(args.json).write_text(json.dumps({
            'findings': [dict(zip(('file', 'line', 'constraint', 'status', 'annotated', 'excerpt'), f))
                         for f in findings],
            'closures': [dict(zip(('file', 'line', 'excerpt'), c)) for c in closures]}, indent=1),
            encoding='utf-8')


if __name__ == '__main__':
    sys.exit(main())
