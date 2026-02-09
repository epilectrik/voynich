"""Apply apparatus-derived gloss refinements to middle dictionary.

Source: GLOSS_RESEARCH Test 16 (apparatus discrimination test)
Method: REGIME enrichment ratios for apparatus-discriminating middles
Evidence: Cross-validated against Brunschwig apparatus protocols (BRSC)

Key finding: R2 (balneum marie) has a coherent seal->heat->pause->cool->open->collect
cycle encoded in discriminating middles. Other REGIMEs have distinct apparatus signatures.

Refinements are conservative: only change glosses where apparatus evidence
provides a more specific reading than the current generic one.
"""
import json
from pathlib import Path

md_path = Path('data/middle_dictionary.json')
md = json.load(open(md_path, encoding='utf-8'))

# Explicit mapping: middle -> (new_gloss, evidence)
refinements = {
    # BALNEUM MARIE apparatus cycle (R2 enriched)
    'eeol':  ('overnight standing',
              'Peaks R2 (8.1x). Brunschwig: "lassen zeston das glas uber nacht zu bekalten" = let stand overnight to cool.'),
    'aii':   ('unseal',
              'Peaks R2 (6.1x). Complement of ok(seal). Open sealed vessel after overnight cooling.'),
    'op':    ('process start',
              'Peaks R2 (3.9x). Initiation of gentle process after setup.'),
    'keeo':  ('sustained heat, extended cool',
              'Peaks R2 (3.2x). Full balneum marie cycle: sustained heating then extended cooling.'),
    'eed':   ('extended discharge',
              'Peaks R2 (3.2x). Extended collection phase in gentle process.'),

    # PER IGNEM apparatus (R3 enriched)
    'te':    ('rapid gather',
              'Peaks R3 (8.5x). Rapid collection under direct fire conditions.'),
    'tch':   ('rapid transfer-check',
              'Peaks R3 (3.4x). Verification during transfer under intense fire.'),
    'eol':   ('sustain output',
              'Peaks R3 (3.1x). Sustain continuous output during active distillation.'),
    'kc':    ('intense heat-seal',
              'Peaks R3 (3.0x). Heat to closure under direct fire. F-BRU-020 OIL_MARKER.'),

    # PRECISION apparatus (R4 enriched)
    'm':     ('precision marker',
              'Peaks R4 (4.7x). Precision operation indicator. Already correctly glossed.'),
    's':     ('precise sequence',
              'Peaks R4 (4.1x). Sequential steps under tight tolerance.'),
    'a':     ('precision attach',
              'Peaks R4 (2.9x). Attachment operation in precision context.'),
    'cph':   ('precision measure',
              'Peaks R4 (2.8x). Measurement under tight tolerance.'),
}

count = 0
log = []

for mid, (new_gloss, evidence) in refinements.items():
    entry = md['middles'].get(mid)
    if not entry:
        continue
    old_gloss = entry.get('gloss') or ''
    if old_gloss != new_gloss:
        entry['gloss'] = new_gloss
        count += 1
        n = entry.get('token_count', 0)
        log.append((mid, old_gloss, new_gloss, n, evidence))

# Update metadata
md['meta']['apparatus_refinement'] = 'Apparatus discrimination refinements applied (2026-02-06)'
md['meta']['version'] = '1.7'
total_glossed = sum(1 for e in md['middles'].values() if e.get('gloss'))
md['meta']['glossed'] = total_glossed

with open(md_path, 'w', encoding='utf-8') as f:
    json.dump(md, f, indent=2, ensure_ascii=False)

print(f"Updated {count} middle glosses\n")
print(f"{'Middle':<14} {'Old':<28} {'New':<28} {'Count':>6}")
print(f"{'-'*14} {'-'*28} {'-'*28} {'-'*6}")
for mid, old, new, n, ev in sorted(log, key=lambda x: -x[3]):
    print(f"{mid:<14} {old:<28} {new:<28} {n:>6}")

print(f"\nEvidence summary:")
for mid, old, new, n, ev in sorted(log, key=lambda x: -x[3]):
    print(f"  {mid:<14} {ev}")

print(f"\nTotal glossed middles: {total_glossed}")
