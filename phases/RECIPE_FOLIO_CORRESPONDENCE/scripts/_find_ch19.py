"""Find the correct PL Ch19 (aqua vitae recipe from Practica)."""
import json

d = json.load(open('phases/PER_DOMAIN_BRIDGE_CALIBRATION/results/pl_channel_features.json'))
chs = d['T5_channel_signatures']['per_chapter']

# Find distillation chapters
dist = [c for c in chs if c.get('family') == 'distillation']
print(f'Distillation chapters: {len(dist)}')
for c in dist:
    hr = c['k_channel']['heat_rate']
    mr = c['h_channel']['monitoring_rate']
    cr = c['e_channel']['correction_rate']
    tr = c['t_channel']['termination_rate']
    cf = c['h_channel']['consistency_frac']
    print(f'  idx={c["chapter_idx"]:3d} num={c["chapter_number"]:3d} '
          f'lines={c["n_lines"]:3d} heat={hr:.3f} mon={mr:.3f} '
          f'corr={cr:.3f} term={tr:.3f} cons={cf:.3f}')

# Also check: what was matched to f75r in Phase 628?
match_data = json.load(open('phases/RECIPE_FOLIO_CORRESPONDENCE/results/recipe_matching.json'))
mt = match_data.get('T4_match_summary', {}).get('match_table', [])
for m in mt:
    if m.get('folio') == 'f75r':
        print(f'\nPhase 628 f75r match:')
        print(json.dumps(m, indent=2))
        ch_idx = m.get('chapter_idx')
        if ch_idx is not None:
            ch = chs[ch_idx]
            print(f'\nMatched chapter full profile:')
            print(json.dumps(ch, indent=2))
