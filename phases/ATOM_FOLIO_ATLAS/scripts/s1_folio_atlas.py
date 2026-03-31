"""
S1: Atom-Level Folio Atlas — Profile all 83 Currier B folios.

For each folio, compute via atomize():
  - PREFIX distribution
  - HEAD atom distribution
  - e-depth profile (e0/e1/e2 counts, gentle ratio)
  - dar/dal counts and ratio
  - Dark pipeline inventory (unique MIDDLEs, count)
  - Document type (PROCEDURE/SPECIFICATION/MINIMAL/BALANCED)
  - Paragraph structure (count, t-gallows ratio)
  - chekar presence
  - Monitoring balance (ch%, sh%, gradient direction)

Outputs: JSON atlas + summary table.
"""

import sys, io, json
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology, ATOM_GLOSSES

tx = Transcript()
morph = Morphology()

with open(ROOT / 'data' / 'dark_pipeline_middles.json', encoding='utf-8') as f:
    dp_set = set(json.load(f)['middles'])

all_b = [t for t in tx.currier_b() if t.word.strip() and not t.is_label]
folios = sorted(set(t.folio for t in all_b))

def safe_int(x):
    try: return int(x)
    except: return 0

atlas = {}

for folio in folios:
    toks = [t for t in all_b if t.folio == folio]
    n = len(toks)
    if n < 20:
        continue

    section = toks[0].section
    flines = sorted(set(t.line for t in toks), key=safe_int)
    words = [t.word for t in toks]

    # PREFIX distribution
    pre = Counter()
    heads = Counter()
    e_depths = Counter()

    for t in toks:
        a = morph.atomize(t.word)
        if a.prefix:
            pre[a.prefix] += 1
        for c, role, g in a.atoms:
            if role in ('HEAD', 'SOLE'):
                heads[c] += 1
        e_depths[a.e_depth] += 1

    # dar/dal
    dar_n = words.count('dar')
    dal_n = words.count('dal')
    dar_dal_ratio = dar_n / dal_n if dal_n > 0 else (99.0 if dar_n > 0 else 0.0)

    # Document type
    if dar_n > dal_n and dar_n >= 2:
        doc_type = 'PROCEDURE'
    elif dal_n > dar_n and dal_n >= 2:
        doc_type = 'SPECIFICATION'
    elif dar_n == dal_n and dar_n >= 2:
        doc_type = 'BALANCED'
    elif dar_n + dal_n <= 1:
        doc_type = 'MINIMAL'
    else:
        doc_type = 'LOW'

    # Dark pipeline
    dark_mids = set()
    dark_count = 0
    for t in toks:
        m = morph.extract(t.word)
        if m.middle and m.middle in dp_set:
            dark_mids.add(m.middle)
            dark_count += 1

    # Paragraph structure
    para_gallows = []
    for li in flines:
        lt = [t for t in toks if t.line == li]
        if lt and lt[0].word and lt[0].word[0] in 'tkpf' and len(lt[0].word) > 1:
            para_gallows.append(lt[0].word[0])
    n_paragraphs = len(para_gallows)
    t_gal = para_gallows.count('t')
    t_ratio = t_gal / n_paragraphs if n_paragraphs > 0 else 0

    # e-depth
    e0 = e_depths.get(0, 0)
    e1 = e_depths.get(1, 0)
    e2 = e_depths.get(2, 0)
    gentle_ratio = e2 / (e1 + e2) if (e1 + e2) > 0 else 0

    # chekar
    chekar_n = sum(1 for w in words if w == 'chekar')

    # Monitoring
    ch_total = sum(pre.get(p, 0) for p in ['ch', 'pch', 'tch', 'dch', 'lch', 'fch'])
    sh_total = sum(pre.get(p, 0) for p in ['sh', 'lsh'])
    qo_total = sum(pre.get(p, 0) for p in ['qo', 'ko', 'ke', 'lk'])

    # qokal
    qokal_n = words.count('qokal')

    entry = {
        'folio': folio,
        'n_tokens': n,
        'n_lines': len(flines),
        'section': section,
        'n_paragraphs': n_paragraphs,
        't_gallows_ratio': round(t_ratio, 3),
        'prefix': {k: v for k, v in pre.most_common(10)},
        'qo_pct': round(100 * qo_total / n, 1),
        'ch_pct': round(100 * ch_total / n, 1),
        'sh_pct': round(100 * sh_total / n, 1),
        'ok_pct': round(100 * pre.get('ok', 0) / n, 1),
        'ot_pct': round(100 * pre.get('ot', 0) / n, 1),
        'da_pct': round(100 * pre.get('da', 0) / n, 1),
        'heads': {k: v for k, v in heads.most_common()},
        'k_pct': round(100 * heads.get('k', 0) / n, 1),
        'e_pct': round(100 * heads.get('e', 0) / n, 1),
        'e0': e0, 'e1': e1, 'e2': e2,
        'gentle_ratio': round(gentle_ratio, 3),
        'dar': dar_n, 'dal': dal_n,
        'dar_dal_ratio': round(dar_dal_ratio, 2),
        'doc_type': doc_type,
        'dark_count': dark_count,
        'dark_unique': len(dark_mids),
        'dark_mids': sorted(dark_mids),
        'dark_pct': round(100 * dark_count / n, 1),
        'chekar': chekar_n,
        'qokal': qokal_n,
    }
    atlas[folio] = entry

# Save JSON
out_path = ROOT / 'phases' / 'ATOM_FOLIO_ATLAS' / 'results' / 'folio_atlas.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(atlas, f, indent=2, ensure_ascii=False)
print(f"Saved atlas: {len(atlas)} folios -> {out_path}")

# Summary table
print(f"\n{'=' * 130}")
print(f"ATOM-LEVEL FOLIO ATLAS: {len(atlas)} Currier B folios")
print(f"{'=' * 130}")

print(f"\n{'Folio':>8s} {'N':>5s} {'Sec':>4s} {'Type':>12s} {'qo%':>5s} {'ch%':>5s} {'sh%':>5s} "
      f"{'k%':>4s} {'e%':>4s} {'g%':>4s} {'dar':>4s} {'dal':>4s} {'d:d':>5s} "
      f"{'dkU':>4s} {'chk':>4s} {'qkl':>4s} {'P':>3s} {'t%':>4s}")
print(f"  {'-'*120}")

for folio in sorted(atlas.keys()):
    e = atlas[folio]
    dd = f"{e['dar_dal_ratio']:.1f}" if e['dar_dal_ratio'] < 50 else 'INF'
    print(f"{e['folio']:>8s} {e['n_tokens']:5d} {e['section']:>4s} {e['doc_type']:>12s} "
          f"{e['qo_pct']:5.1f} {e['ch_pct']:5.1f} {e['sh_pct']:5.1f} "
          f"{e['k_pct']:4.1f} {e['e_pct']:4.1f} {100*e['gentle_ratio']:4.0f} "
          f"{e['dar']:4d} {e['dal']:4d} {dd:>5s} "
          f"{e['dark_unique']:4d} {e['chekar']:4d} {e['qokal']:4d} "
          f"{e['n_paragraphs']:3d} {100*e['t_gallows_ratio']:4.0f}")

# Section summaries
print(f"\n\nSECTION SUMMARIES")
print(f"{'=' * 80}")
for sec in sorted(set(e['section'] for e in atlas.values())):
    sec_folios = [e for e in atlas.values() if e['section'] == sec]
    n_f = len(sec_folios)
    type_ct = Counter(e['doc_type'] for e in sec_folios)
    avg_qo = sum(e['qo_pct'] for e in sec_folios) / n_f
    avg_ch = sum(e['ch_pct'] for e in sec_folios) / n_f
    avg_gentle = sum(e['gentle_ratio'] for e in sec_folios) / n_f
    avg_dark = sum(e['dark_unique'] for e in sec_folios) / n_f
    print(f"\n  Section {sec} ({n_f} folios):")
    print(f"    Types: {dict(type_ct.most_common())}")
    print(f"    Avg: qo={avg_qo:.1f}% ch={avg_ch:.1f}% gentle={100*avg_gentle:.0f}% dark_unique={avg_dark:.1f}")

print(f"\n{'=' * 130}")
print("DONE")
print(f"{'=' * 130}")
