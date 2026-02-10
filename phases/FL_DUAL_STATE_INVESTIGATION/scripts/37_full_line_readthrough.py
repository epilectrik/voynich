"""
37_full_line_readthrough.py

Systematic readthrough of real B lines through the full model.

For 15 diverse lines, annotate every token:
  - Layer: PREAMBLE / FL-LOW / OL / CENTER / OR / FL-HIGH / CODA
  - Morphology: [ART] + [PFX] + MID + [SFX]
  - Role: from 49-class system
  - FL info: stage, mode (LOW/HIGH)
  - Prefix gloss: sh=monitor, ch=interact, qo=action, ok=check, ot=test

Then compose a line-level interpretation:
  "At state (ACTION=X, OVERSIGHT=Y), monitor Z, do W with parameters..."

Selection criteria for lines:
  - Must have both FL-LOW and FL-HIGH
  - Must have at least 2 gap tokens (OL + OR minimum)
  - Sample across different FL pairs, sections, and folio positions
"""
import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np
from sklearn.mixture import GaussianMixture

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

FL_STAGE_MAP = {
    'ii': ('INITIAL', 0.299), 'i': ('INITIAL', 0.345),
    'in': ('EARLY', 0.421),
    'r': ('MEDIAL', 0.507), 'ar': ('MEDIAL', 0.545),
    'al': ('LATE', 0.606), 'l': ('LATE', 0.618), 'ol': ('LATE', 0.643),
    'o': ('FINAL', 0.751), 'ly': ('FINAL', 0.785), 'am': ('FINAL', 0.802),
    'm': ('TERMINAL', 0.861), 'dy': ('TERMINAL', 0.908),
    'ry': ('TERMINAL', 0.913), 'y': ('TERMINAL', 0.942),
}
STAGE_ORDER = {'INITIAL': 0, 'EARLY': 1, 'MEDIAL': 2, 'LATE': 3, 'FINAL': 4, 'TERMINAL': 5}

# Prefix interpretive glosses (from our investigation)
PREFIX_GLOSS = {
    'sh': 'SENSE',
    'ch': 'INTERACT',
    'qo': 'ACT',
    'ok': 'CHECK',
    'ot': 'TEST',
    'ol': 'LINK',
    'd': 'DIRECT',
    's': 'STABILIZE',
    'NONE': '-',
}

tx = Transcript()
morph = Morphology()
MIN_N = 50

class_map_path = Path(__file__).resolve().parents[3] / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
with open(class_map_path) as f:
    class_data = json.load(f)
token_to_class = class_data['token_to_class']
token_to_role = class_data['token_to_role']

# Role abbreviations
ROLE_ABBREV = {
    'ENERGY_OPERATOR': 'EN',
    'FREQUENT_OPERATOR': 'FQ',
    'CORE_CONTROL': 'CC',
    'AUXILIARY': 'AX',
    'UNKNOWN': 'UK',
}

line_tokens = defaultdict(list)
line_meta = {}
for t in tx.currier_b():
    key = (t.folio, t.line)
    line_tokens[key].append(t)
    if key not in line_meta:
        line_meta[key] = {'section': t.section, 'folio': t.folio, 'line': t.line}

# Fit GMMs
per_middle_positions = defaultdict(list)
for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n <= 1:
        continue
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        if m and m.middle and m.middle in FL_STAGE_MAP:
            per_middle_positions[m.middle].append(idx / (n - 1))

gmm_models = {}
for mid, positions in per_middle_positions.items():
    if len(positions) < MIN_N:
        continue
    X = np.array(positions).reshape(-1, 1)
    gmm = GaussianMixture(n_components=2, random_state=42, n_init=10)
    gmm.fit(X)
    if gmm.means_[0] > gmm.means_[1]:
        gmm_models[mid] = {'model': gmm, 'swap': True}
    else:
        gmm_models[mid] = {'model': gmm, 'swap': False}

# ============================================================
# Analyze all lines, select diverse sample
# ============================================================
analyzed_lines = []

for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n < 7:
        continue

    all_info = []
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        pos = idx / (n - 1) if n > 1 else 0.5
        mid = m.middle if m else None
        is_fl = mid is not None and mid in FL_STAGE_MAP

        mode = None
        stage = None
        fl_mid = None
        if is_fl and mid in gmm_models:
            info = gmm_models[mid]
            pred = info['model'].predict(np.array([[pos]]))[0]
            if info['swap']:
                pred = 1 - pred
            mode = 'LOW' if pred == 0 else 'HIGH'
            stage = FL_STAGE_MAP[mid][0]
            fl_mid = mid

        prefix = m.prefix if m and m.prefix else 'NONE'
        suffix = m.suffix if m and m.suffix else 'NONE'
        middle = m.middle if m and m.middle else '?'
        art = m.articulator if m and m.articulator else None
        cls = token_to_class.get(t.word, None)
        role = token_to_role.get(t.word, 'UNKNOWN')

        all_info.append({
            'word': t.word, 'idx': idx, 'pos': pos,
            'is_fl': is_fl, 'mode': mode, 'stage': stage, 'fl_mid': fl_mid,
            'prefix': prefix, 'suffix': suffix, 'middle': middle,
            'articulator': art,
            'class': cls, 'role': role,
        })

    low_fls = [a for a in all_info if a['is_fl'] and a['mode'] == 'LOW']
    high_fls = [a for a in all_info if a['is_fl'] and a['mode'] == 'HIGH']
    if not low_fls or not high_fls:
        continue

    low_stage = Counter(f['stage'] for f in low_fls).most_common(1)[0][0]
    high_stage = Counter(f['stage'] for f in high_fls).most_common(1)[0][0]

    max_low_idx = max(f['idx'] for f in low_fls)
    min_high_idx = min(f['idx'] for f in high_fls)

    gap = [a for a in all_info if not a['is_fl']
           and a['idx'] > max_low_idx and a['idx'] < min_high_idx]

    if len(gap) < 2:
        continue

    # Assign layers
    for a in all_info:
        if a['is_fl'] and a['mode'] == 'LOW':
            a['layer'] = 'FL-LOW'
        elif a['is_fl'] and a['mode'] == 'HIGH':
            a['layer'] = 'FL-HIGH'
        elif a['idx'] < min(f['idx'] for f in low_fls):
            a['layer'] = 'PREAMBLE'
        elif a['idx'] > max(f['idx'] for f in high_fls):
            a['layer'] = 'CODA'
        elif a['idx'] == gap[0]['idx']:
            a['layer'] = 'OL'
        elif a['idx'] == gap[-1]['idx']:
            a['layer'] = 'OR'
        elif a['idx'] > gap[0]['idx'] and a['idx'] < gap[-1]['idx']:
            a['layer'] = 'CENTER'
        else:
            a['layer'] = 'FRAME'

    analyzed_lines.append({
        'key': line_key,
        'folio': line_meta[line_key]['folio'],
        'line': line_meta[line_key]['line'],
        'section': line_meta[line_key]['section'],
        'n_tokens': n,
        'low_stage': low_stage,
        'high_stage': high_stage,
        'pair': f"{low_stage}>{high_stage}",
        'n_gap': len(gap),
        'all_info': all_info,
    })

print(f"Lines with full structure: {len(analyzed_lines)}")

# ============================================================
# Select diverse sample
# ============================================================
# Want: different pairs, sections, gap sizes
pair_counts = Counter(al['pair'] for al in analyzed_lines)
section_counts = Counter(al['section'] for al in analyzed_lines)

# Sample strategy: pick lines that cover different pairs and sections
# Prioritize lines with larger gaps (more readable)
selected = []
used_pairs = set()
used_sections = Counter()

# Sort by gap size descending (prefer lines with more content)
candidates = sorted(analyzed_lines, key=lambda x: -x['n_gap'])

# First pass: one line per unique pair (from most common pairs)
for al in candidates:
    if al['pair'] not in used_pairs and len(selected) < 15:
        # Prefer sections we haven't used much
        if used_sections[al['section']] < 3:
            selected.append(al)
            used_pairs.add(al['pair'])
            used_sections[al['section']] += 1

# Fill remaining slots if needed
if len(selected) < 15:
    for al in candidates:
        if al not in selected and len(selected) < 15:
            selected.append(al)

# Sort selected by pair for readability
selected.sort(key=lambda x: (STAGE_ORDER.get(x['low_stage'], 0),
                              STAGE_ORDER.get(x['high_stage'], 0)))

print(f"Selected {len(selected)} lines for readthrough")
print(f"Pairs covered: {len(set(s['pair'] for s in selected))}")
print(f"Sections: {Counter(s['section'] for s in selected)}")

# ============================================================
# READTHROUGH
# ============================================================
readthrough_results = []

for i, al in enumerate(selected):
    folio = al['folio']
    line = al['line']
    section = al['section']
    low = al['low_stage']
    high = al['high_stage']
    n = al['n_tokens']

    print(f"\n{'='*75}")
    print(f"LINE {i+1}: {folio}.{line} (Section {section}, {n} tokens)")
    print(f"COORDINATE: ACTION={low}, OVERSIGHT={high}")
    print(f"{'='*75}")

    # Print raw line
    raw = ' '.join(a['word'] for a in al['all_info'])
    print(f"\n  RAW: {raw}")

    # Print annotated tokens
    print(f"\n  {'#':>2} {'Layer':<9} {'Word':<14} {'Pfx':<5} {'Mid':<8} {'Sfx':<5} "
          f"{'Role':>4} {'PfxGloss':<9} {'FL':>10}")
    print(f"  {'-'*80}")

    ol_token = None
    or_token = None
    center_tokens = []
    preamble_tokens = []
    coda_tokens = []
    fl_low_tokens = []
    fl_high_tokens = []

    for a in al['all_info']:
        layer = a['layer']
        pfx_gloss = PREFIX_GLOSS.get(a['prefix'], '?')
        role_abbr = ROLE_ABBREV.get(a['role'], '??')
        fl_str = ''
        if a['is_fl'] and a['mode'] and a['stage']:
            fl_str = f"{a['mode']}:{a['stage'][:4]}"
            if a['fl_mid']:
                fl_str = f"{a['fl_mid']}={fl_str}"
        elif a['is_fl']:
            fl_str = f"FL:{a['middle']}"

        art_str = f"{a['articulator']}+" if a['articulator'] else ''

        print(f"  {a['idx']:>2} {layer:<9} {a['word']:<14} "
              f"{a['prefix']:<5} {art_str}{a['middle']:<8} {a['suffix']:<5} "
              f"{role_abbr:>4} {pfx_gloss:<9} {fl_str:>10}")

        if layer == 'OL':
            ol_token = a
        elif layer == 'OR':
            or_token = a
        elif layer == 'CENTER':
            center_tokens.append(a)
        elif layer == 'PREAMBLE':
            preamble_tokens.append(a)
        elif layer == 'CODA':
            coda_tokens.append(a)
        elif layer == 'FL-LOW':
            fl_low_tokens.append(a)
        elif layer == 'FL-HIGH':
            fl_high_tokens.append(a)

    # Compose interpretation
    print(f"\n  INTERPRETATION:")

    # State
    print(f"    STATE: action={low} ({STAGE_ORDER[low]}/5), "
          f"oversight={high} ({STAGE_ORDER[high]}/5)")

    # Preamble
    if preamble_tokens:
        pre_words = [t['word'] for t in preamble_tokens]
        pre_pfx = [PREFIX_GLOSS.get(t['prefix'], '?') for t in preamble_tokens]
        print(f"    PREAMBLE: {' '.join(pre_words)} [{'/'.join(pre_pfx)}]")

    # FL-LOW
    fl_low_mids = [t['fl_mid'] for t in fl_low_tokens if t['fl_mid']]
    print(f"    FL-LOW: {','.join(fl_low_mids)} -> action level {low}")

    # OL (monitor specification)
    if ol_token:
        ol_gloss = PREFIX_GLOSS.get(ol_token['prefix'], '?')
        print(f"    MONITOR: {ol_token['word']} "
              f"[{ol_token['prefix']}+{ol_token['middle']}+{ol_token['suffix']}] "
              f"= {ol_gloss} operation, role={ol_token['role']}")

    # CENTER (body/parameters)
    if center_tokens:
        center_glosses = []
        for ct in center_tokens:
            cg = PREFIX_GLOSS.get(ct['prefix'], '?')
            center_glosses.append(f"{ct['word']}({cg})")
        print(f"    BODY: {', '.join(center_glosses)}")
    else:
        print(f"    BODY: (empty - OL and OR are adjacent)")

    # OR (action specification)
    if or_token:
        or_gloss = PREFIX_GLOSS.get(or_token['prefix'], '?')
        print(f"    ACTION: {or_token['word']} "
              f"[{or_token['prefix']}+{or_token['middle']}+{or_token['suffix']}] "
              f"= {or_gloss} operation, role={or_token['role']}")

    # FL-HIGH
    fl_high_mids = [t['fl_mid'] for t in fl_high_tokens if t['fl_mid']]
    print(f"    FL-HIGH: {','.join(fl_high_mids)} -> oversight level {high}")

    # Coda
    if coda_tokens:
        coda_words = [t['word'] for t in coda_tokens]
        coda_pfx = [PREFIX_GLOSS.get(t['prefix'], '?') for t in coda_tokens]
        print(f"    CODA: {' '.join(coda_words)} [{'/'.join(coda_pfx)}]")

    # One-line summary
    ol_pfx = PREFIX_GLOSS.get(ol_token['prefix'], '?') if ol_token else '?'
    or_pfx = PREFIX_GLOSS.get(or_token['prefix'], '?') if or_token else '?'
    n_center = len(center_tokens)
    summary = (f"At ({low[:4]},{high[:4]}): "
               f"{ol_pfx}({ol_token['word'] if ol_token else '?'}) -> "
               f"{n_center} body tokens -> "
               f"{or_pfx}({or_token['word'] if or_token else '?'})")
    print(f"\n    SUMMARY: {summary}")

    readthrough_results.append({
        'folio': folio,
        'line': line,
        'section': section,
        'pair': al['pair'],
        'low_stage': low,
        'high_stage': high,
        'n_tokens': n,
        'n_gap': al['n_gap'],
        'raw': raw,
        'ol_word': ol_token['word'] if ol_token else None,
        'ol_prefix': ol_token['prefix'] if ol_token else None,
        'or_word': or_token['word'] if or_token else None,
        'or_prefix': or_token['prefix'] if or_token else None,
        'n_center': n_center,
        'n_preamble': len(preamble_tokens),
        'n_coda': len(coda_tokens),
        'summary': summary,
    })

# ============================================================
# PATTERN ANALYSIS across all readthrough lines
# ============================================================
print(f"\n\n{'='*75}")
print("PATTERN ANALYSIS ACROSS ALL READTHROUGH LINES")
print(f"{'='*75}")

# Do OL prefixes cluster by coordinate?
print(f"\n  OL prefix by coordinate pair:")
for r in readthrough_results:
    ol_pfx = r['ol_prefix'] if r['ol_prefix'] else '?'
    or_pfx = r['or_prefix'] if r['or_prefix'] else '?'
    print(f"    {r['pair']:<20} OL={ol_pfx:<6} OR={or_pfx:<6} "
          f"center={r['n_center']}")

# How often does interpretation follow the pattern:
# OL=SENSE/INTERACT, body=mixed, OR=ACT
ol_is_monitor = sum(1 for r in readthrough_results
                     if r['ol_prefix'] in ('sh', 'ch'))
or_is_action = sum(1 for r in readthrough_results
                    if r['or_prefix'] in ('qo',))
n_total = len(readthrough_results)

print(f"\n  OL is monitor (sh/ch): {ol_is_monitor}/{n_total} ({ol_is_monitor/n_total*100:.0f}%)")
print(f"  OR is action (qo):     {or_is_action}/{n_total} ({or_is_action/n_total*100:.0f}%)")

# ============================================================
# SAVE
# ============================================================
result = {
    'n_lines_readthrough': len(readthrough_results),
    'ol_monitor_rate': round(ol_is_monitor / n_total * 100, 1),
    'or_action_rate': round(or_is_action / n_total * 100, 1),
    'lines': readthrough_results,
}

out_path = Path(__file__).resolve().parent.parent / "results" / "37_full_line_readthrough.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nResult written to {out_path}")
