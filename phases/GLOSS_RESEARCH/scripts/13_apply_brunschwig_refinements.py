"""Apply Brunschwig-derived gloss refinements to middle dictionary.

Source: GLOSS_RESEARCH Test 12 (compound differentiation test)
Method: REGIME distribution, positional analysis, bigram context
Evidence: Cross-validated against Brunschwig fire degree -> REGIME mapping

Refinements based on three independent signals:
  1. REGIME enrichment (which fire degree method does this middle correlate with?)
  2. Positional data (where in the line does this middle appear?)
  3. Bigram context (what follows this middle?)
"""
import json
from pathlib import Path

md_path = Path('data/middle_dictionary.json')
md = json.load(open(md_path, encoding='utf-8'))

# Explicit mapping: middle -> (new_gloss, evidence)
refinements = {
    # K-FAMILY: heat method differentiation
    'ke':   ('sustained heat',
             'Peaks R1 (1.6x), not R2. F-BRU-017: sustained equilibration, not gentle fire.'),
    'ck':   ('direct heat',
             'Peaks R3 (direct fire regime). "Hard" is vague; "direct" matches Brunschwig per ignem.'),
    'ksh':  ('ignition check',
             'Earliest k-compound (pos 0.340). Heat + verify at line start = startup verification.'),
    'ka':   ('sustained fire',
             'Latest k-compound (pos 0.643). Peaks R3. Late-stage heat maintenance.'),
    'keo':  ('precision heat, work',
             'Peaks R4 (2.0x). Active heat operation under tight tolerance.'),
    'ko':   ('precision heat-work',
             'Peaks R4 (1.7x). Active heat processing in precision mode.'),
    'kc':   ('heat-seal',
             'Peaks R3 (1.9x). Heat to closure under intense conditions.'),

    # E-FAMILY: cooling duration differentiation
    'ee':   ('extended cool',
             'Peaks R2 (1.5x). Double-e = longer cooling. Balneum marie overnight pattern.'),
    'eeo':  ('extended cool, work',
             'Peaks R2 (1.7x). Extended cooling with active monitoring. Differentiated from ee.'),
    'eey':  ('extended cool',
             'Peaks R3 but double-e length. Same as ee (collapse accepted).'),
    'eeol': ('extended sustain',
             'Peaks R2 (2.1x). Sustained extended cooling = Brunschwig overnight standing.'),
    'eod':  ('standing cool',
             'Peaks R2 (1.4x). Let stand to cool = Brunschwig "overnight to cool".'),
    'eee':  ('deep extended cool',
             'Peaks R2 (2.9x). Triple-e = maximum cooling duration.'),
    'eeeo': ('deep extended cool, open',
             'Peaks R2 (2.4x). Maximum cooling then open vessel.'),
    'ep':   ('precision cool',
             'Peaks R4 (1.7x). Careful controlled cooling under tight tolerance.'),

    # SEAL/LOCK: apparatus operations
    'ok':   ('seal',
             'Peaks R2 (balneum marie = sealed glass vessel in water bath).'),
    'olk':  ('sustain seal',
             'Peaks R2 (1.3x). Maintaining sealed state during water bath.'),

    # Monitoring differentiation
    'che':  ('check cooling',
             'Peaks R2 (2.6x). Verification during cooling phase.'),
    'osh':  ('work-verify',
             'Peaks R2 (2.2x). Verification during active work.'),
    'ockh': ('work, heat-check',
             'Peaks R2 (1.8x). Heat monitoring during work phase.'),
    'tch':  ('transfer-check',
             'Peaks R3 (1.6x). Verification during transfer under intense conditions.'),

    # Hazard differentiation
    'eckh': ('direct heat hazard',
             'Peaks R3 (1.7x). Hazard from direct fire operations.'),
    'cth':  ('precision hazard',
             'Peaks R4 (1.4x). Hazard under precision/tight tolerance.'),
    'hy':   ('acute hazard',
             'Peaks R3 (2.3x). Acute hazard from intense fire.'),
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
md['meta']['brunschwig_refinement'] = 'Brunschwig fire-degree differentiation applied (2026-02-06)'
md['meta']['version'] = '1.6'
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
