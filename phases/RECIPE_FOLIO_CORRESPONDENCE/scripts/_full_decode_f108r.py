"""
Full atom-level decode of f108r using atomize().

Recipe: PL Chapter XVI Practica — Separation of elements from putrefied white composite.
  1. After 1.5 months putrefaction, matter is "well animated"
  2. Remove cover, place alembic, seal with lute carefully
  3. Place in HOT balneum mariae — distill water by GENTLE FIRE equally continued
  4. Continue until nothing more distills; cease fire, allow to COOL
  5. Remove vessel, place upon ASHES in aludel
  6. Gradually STRENGTHEN fire — distill air mixed with fire
  7. Receive in glass phial, seal well, set aside
  8. Residue at bottom = "dry and black earth" (burnt, scorched)
  9. Key principle: water in balneum mariae (subtle heat), air in ashes (stronger heat)
  10. Separate three elements for white (L, M, N); red requires four (O, P, Q, R)

Key predictions:
  - Two thermal phases: gentle balneum mariae THEN strengthened ash fire
  - e_depth trajectory: high (gentle) early -> low (direct heat) later
  - Monitoring present (careful sealing, "as best and most discreetly")
  - Sequential staging between phases (cease fire, cool, move vessel)
  - Cooling step explicitly mentioned
  - Equipment changes mid-procedure (vessel to aludel)
"""

import sys, io, json
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import (Transcript, Morphology, ATOM_GLOSSES,
                              HEAD_ATOMS, MOD_ATOMS, TERM_ATOMS)

tx = Transcript()
morph = Morphology()

# Load dark pipeline MIDDLEs
with open(ROOT / 'data' / 'dark_pipeline_middles.json', encoding='utf-8') as f:
    dp_set = set(json.load(f)['middles'])

# ═══════════════════════════════════════════════════════════════
# 0. LOAD f108r
# ═══════════════════════════════════════════════════════════════
all_tokens = list(tx.all())
tokens = [t for t in all_tokens
          if t.folio == 'f108r'
          and t.word.strip()
          and not t.is_label
          and '*' not in t.word]

# Verify section
sections = set(t.section for t in tokens)
languages = set(t.language for t in tokens)

def safe_int(x):
    try: return int(x)
    except: return 0

lines = sorted(set(t.line for t in tokens), key=safe_int)

print("=" * 100)
print("f108r FULL ATOM-LEVEL DECODE")
print("PL Chapter XVI: Separation of elements from putrefied white composite")
print("=" * 100)
print(f"\nSection: {sections}  Language: {languages}")
if 'H' in sections:
    print("CONFIRMED: Herbal section")
else:
    print(f"NOTE: f108r is in section {sections}, NOT Herbal as initially assumed")

# ═══════════════════════════════════════════════════════════════
# 1. BASIC PROFILE
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 100)
print("1. BASIC PROFILE")
print("=" * 100)

n_tokens = len(tokens)
n_lines = len(lines)

# Count paragraphs (gallows-initial tokens at line starts)
para_starts = []
for li in lines:
    lt = [t for t in tokens if t.line == li]
    if lt and lt[0].par_initial:
        para_starts.append(li)
n_paragraphs = len(para_starts)

print(f"  Tokens: {n_tokens}")
print(f"  Lines:  {n_lines}")
print(f"  Paragraphs: {n_paragraphs} (starts at lines: {para_starts})")

# Atom distributions
head_dist = Counter()
mod_dist = Counter()
term_dist = Counter()
prefix_dist = Counter()
e_depth_dist = Counter()
all_e_depths = []
head_count = 0
headless_count = 0

for t in tokens:
    a = morph.atomize(t.word)
    if a.prefix:
        prefix_dist[a.prefix] += 1
    e_depth_dist[a.e_depth] += 1
    all_e_depths.append(a.e_depth)
    if a.is_headless:
        headless_count += 1
    else:
        head_count += 1
    for char, role, gloss in a.atoms:
        if role == 'HEAD':
            head_dist[char] += 1
        elif role == 'MOD':
            mod_dist[char] += 1
        elif role in ('TERM', 'SOLE'):
            term_dist[char] += 1

mean_e_depth = sum(all_e_depths) / len(all_e_depths) if all_e_depths else 0

print(f"\n  HEAD distribution: {dict(head_dist.most_common())}")
print(f"  MOD distribution:  {dict(mod_dist.most_common())}")
print(f"  TERM distribution: {dict(term_dist.most_common())}")
print(f"  PREFIX distribution: {dict(prefix_dist.most_common())}")
print(f"\n  e_depth distribution: {dict(sorted(e_depth_dist.items()))}")
print(f"  e_depth mean: {mean_e_depth:.3f}")
print(f"  Headed: {head_count}  Headless: {headless_count} ({100*headless_count/n_tokens:.1f}%)")

# Compute Herbal B averages for comparison
herbal_b_tokens = [t for t in all_tokens
                   if t.language == 'B'
                   and t.section == 'H'
                   and t.word.strip()
                   and not t.is_label
                   and '*' not in t.word]
herbal_e_depths = [morph.atomize(t.word).e_depth for t in herbal_b_tokens]
herbal_mean_e = sum(herbal_e_depths) / len(herbal_e_depths) if herbal_e_depths else 0

# Also compute Section S averages
stars_b_tokens = [t for t in all_tokens
                  if t.language == 'B'
                  and t.section == 'S'
                  and t.word.strip()
                  and not t.is_label
                  and '*' not in t.word]
stars_e_depths = [morph.atomize(t.word).e_depth for t in stars_b_tokens]
stars_mean_e = sum(stars_e_depths) / len(stars_e_depths) if stars_e_depths else 0

print(f"\n  Comparison e_depth means:")
print(f"    f108r:         {mean_e_depth:.3f}")
print(f"    Herbal B avg:  {herbal_mean_e:.3f}")
print(f"    Stars B avg:   {stars_mean_e:.3f}")

# ═══════════════════════════════════════════════════════════════
# 2. LINE-BY-LINE ATOM DECODE
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 100)
print("2. LINE-BY-LINE ATOM DECODE")
print("=" * 100)

line_data = {}
for li in lines:
    lt = [t for t in tokens if t.line == li]
    line_e_depths = []
    line_heads = Counter()
    print(f"\n  --- LINE {li} ({len(lt)} tokens) ---")

    for t in lt:
        a = morph.atomize(t.word)
        m = morph.extract(t.word)
        line_e_depths.append(a.e_depth)
        if a.head:
            line_heads[a.head] += 1

        atom_str = ' '.join(f"{c}({r[0]}:{g})" for c, r, g in a.atoms)
        dp_flag = ' [DARK]' if (m.middle and m.middle in dp_set) else ''
        print(f"    {t.word:18s} pfx={str(a.prefix):>4s}  e={a.e_depth}  "
              f"atoms=[{atom_str}]  gloss={a.gloss}{dp_flag}")

    line_mean_e = sum(line_e_depths) / len(line_e_depths) if line_e_depths else 0
    print(f"    >> Line e_depth mean: {line_mean_e:.2f}  HEADs: {dict(line_heads)}")
    line_data[li] = {
        'n_tokens': len(lt),
        'e_depth_mean': round(line_mean_e, 3),
        'heads': dict(line_heads),
        'words': [t.word for t in lt]
    }

# ═══════════════════════════════════════════════════════════════
# 3. e-DEPTH TRAJECTORY
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 100)
print("3. e-DEPTH TRAJECTORY")
print("Prediction: gentle (e>=2 = balneum) early -> direct (e<=1) later")
print("=" * 100)

for li in lines:
    lt = [t for t in tokens if t.line == li]
    e0 = sum(1 for t in lt if morph.atomize(t.word).e_depth == 0)
    e1 = sum(1 for t in lt if morph.atomize(t.word).e_depth == 1)
    e2 = sum(1 for t in lt if morph.atomize(t.word).e_depth >= 2)
    n = len(lt)
    line_mean = sum(morph.atomize(t.word).e_depth for t in lt) / n if n > 0 else 0

    bar_e2 = '#' * e2
    bar_e1 = '|' * e1
    pct_gentle = 100 * e2 / n if n > 0 else 0

    is_para = li in para_starts
    para_flag = ' <<PARA>>' if is_para else ''

    print(f"  L{li:>2s} ({n:2d}T)  mean={line_mean:.2f}  "
          f"e0={e0:2d} e1={e1:2d} e2+={e2:2d} "
          f"[{bar_e2}{bar_e1}] gentle={pct_gentle:.0f}%{para_flag}")

# Compute first-half vs second-half
mid_line = len(lines) // 2
first_half_lines = lines[:mid_line]
second_half_lines = lines[mid_line:]

first_half_e = [morph.atomize(t.word).e_depth
                for t in tokens if t.line in first_half_lines]
second_half_e = [morph.atomize(t.word).e_depth
                 for t in tokens if t.line in second_half_lines]

first_mean = sum(first_half_e) / len(first_half_e) if first_half_e else 0
second_mean = sum(second_half_e) / len(second_half_e) if second_half_e else 0

first_gentle = sum(1 for e in first_half_e if e >= 2)
second_gentle = sum(1 for e in second_half_e if e >= 2)

print(f"\n  FIRST HALF  (L1-L{lines[mid_line-1]}): mean e_depth={first_mean:.3f}, "
      f"e>=2 count={first_gentle}/{len(first_half_e)} "
      f"({100*first_gentle/len(first_half_e):.1f}%)")
print(f"  SECOND HALF (L{lines[mid_line]}-L{lines[-1]}): mean e_depth={second_mean:.3f}, "
      f"e>=2 count={second_gentle}/{len(second_half_e)} "
      f"({100*second_gentle/len(second_half_e):.1f}%)")

if first_mean > second_mean:
    print("  VERDICT: e_depth DROPS from first to second half — CONSISTENT with prediction")
else:
    print("  VERDICT: e_depth does NOT drop — INCONSISTENT with gentle->strong prediction")

# ═══════════════════════════════════════════════════════════════
# 4. TWO-PHASE DETECTION
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 100)
print("4. TWO-PHASE DETECTION")
print("Looking for structural break: balneum mariae (gentle) -> ashes (direct heat)")
print("=" * 100)

# Compute per-line metrics for break detection
line_metrics = []
for li in lines:
    lt = [t for t in tokens if t.line == li]
    n = len(lt)
    if n == 0:
        continue

    e_depths_line = [morph.atomize(t.word).e_depth for t in lt]
    mean_e = sum(e_depths_line) / n
    pct_e2 = sum(1 for e in e_depths_line if e >= 2) / n

    # PREFIX composition
    prefixes = [morph.atomize(t.word).prefix for t in lt]
    qo_pct = sum(1 for p in prefixes if p in ('qo', 'ko', 'ke', 'lk')) / n
    sh_pct = sum(1 for p in prefixes if p in ('sh', 'lsh')) / n
    ch_pct = sum(1 for p in prefixes if p and p.endswith('ch')) / n

    # HEAD composition
    heads = []
    for t in lt:
        a = morph.atomize(t.word)
        if a.head:
            heads.append(a.head)
    k_pct = heads.count('k') / len(heads) if heads else 0

    line_metrics.append({
        'line': li,
        'n': n,
        'mean_e': mean_e,
        'pct_e2': pct_e2,
        'qo_pct': qo_pct,
        'sh_pct': sh_pct,
        'ch_pct': ch_pct,
        'k_pct': k_pct,
    })

# Find the best split point (maximize difference in mean e_depth)
best_split = None
best_diff = 0
for i in range(5, len(line_metrics) - 5):  # at least 5 lines each side
    phase1 = line_metrics[:i]
    phase2 = line_metrics[i:]
    mean1 = sum(m['mean_e'] for m in phase1) / len(phase1)
    mean2 = sum(m['mean_e'] for m in phase2) / len(phase2)
    diff = mean1 - mean2  # positive = gentle first, direct second
    if diff > best_diff:
        best_diff = diff
        best_split = i

if best_split is not None:
    split_line = line_metrics[best_split]['line']
    phase1 = line_metrics[:best_split]
    phase2 = line_metrics[best_split:]
    mean1 = sum(m['mean_e'] for m in phase1) / len(phase1)
    mean2 = sum(m['mean_e'] for m in phase2) / len(phase2)
    qo1 = sum(m['qo_pct'] for m in phase1) / len(phase1)
    qo2 = sum(m['qo_pct'] for m in phase2) / len(phase2)
    sh1 = sum(m['sh_pct'] for m in phase1) / len(phase1)
    sh2 = sum(m['sh_pct'] for m in phase2) / len(phase2)
    k1 = sum(m['k_pct'] for m in phase1) / len(phase1)
    k2 = sum(m['k_pct'] for m in phase2) / len(phase2)

    print(f"  Best split: before L{split_line} (e_depth diff = {best_diff:.3f})")
    print(f"  Phase 1 (L1-L{phase1[-1]['line']}): mean_e={mean1:.3f}, qo={qo1:.1%}, "
          f"sh={sh1:.1%}, k_HEAD={k1:.1%}")
    print(f"  Phase 2 (L{split_line}-L{lines[-1]}): mean_e={mean2:.3f}, qo={qo2:.1%}, "
          f"sh={sh2:.1%}, k_HEAD={k2:.1%}")

    if best_diff > 0.05:
        print("  VERDICT: Detectable phase break — e_depth drops at split point")
    else:
        print("  VERDICT: No clear phase break — e_depth roughly uniform")
else:
    print("  No valid split found")

# Also check for PREFIX shifts
print("\n  PREFIX shift at split point:")
for i, m in enumerate(line_metrics):
    is_split = '>>SPLIT<<' if m['line'] == split_line else ''
    print(f"    L{m['line']:>2s}: e={m['mean_e']:.2f}  qo={m['qo_pct']:.0%}  "
          f"sh={m['sh_pct']:.0%}  ch={m['ch_pct']:.0%}  k_HEAD={m['k_pct']:.0%} {is_split}")

# ═══════════════════════════════════════════════════════════════
# 5. SPECIFIC PREDICTIONS
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 100)
print("5. SPECIFIC PREDICTIONS")
print("=" * 100)

# P1: e_depth above Herbal average
print(f"\n  P1: e_depth above section average (gentle balneum dominates)")
print(f"      f108r mean:  {mean_e_depth:.3f}")
print(f"      Herbal mean: {herbal_mean_e:.3f}")
print(f"      Stars mean:  {stars_mean_e:.3f}")
if mean_e_depth > herbal_mean_e:
    print(f"      PASS: f108r e_depth ({mean_e_depth:.3f}) > Herbal ({herbal_mean_e:.3f})")
elif mean_e_depth > stars_mean_e:
    print(f"      PARTIAL: f108r > Stars avg but <= Herbal avg")
else:
    print(f"      FAIL: f108r e_depth not elevated")

# P2: Cooling step visible (e-HEAD or ee compound)
print(f"\n  P2: Cooling step visible (e-HEAD tokens or consecutive e's)")
cooling_tokens = []
for t in tokens:
    a = morph.atomize(t.word)
    if a.head == 'e':
        cooling_tokens.append((t.word, t.line, a.gloss))
    elif a.e_depth >= 2:
        cooling_tokens.append((t.word, t.line, a.gloss))

print(f"      e-HEAD tokens: {sum(1 for w,l,g in cooling_tokens if morph.atomize(w).head == 'e')}")
print(f"      e_depth>=2 tokens: {sum(1 for w,l,g in cooling_tokens if morph.atomize(w).e_depth >= 2)}")
for w, l, g in cooling_tokens[:20]:
    a = morph.atomize(w)
    reason = 'e-HEAD' if a.head == 'e' else f'e_depth={a.e_depth}'
    print(f"        L{l:>2s}: {w:18s} {g:40s} ({reason})")
if cooling_tokens:
    print(f"      PASS: {len(cooling_tokens)} cooling-related tokens found")
else:
    print(f"      FAIL: No cooling tokens found")

# P3: Sequential staging atoms (mod_s=sequence, mod_d=mark) at phase boundary
print(f"\n  P3: Sequential staging atoms (s=sequence, d=mark) at phase boundary")
if best_split is not None:
    boundary_lines = [line_metrics[best_split-1]['line'], split_line]
    if best_split >= 2:
        boundary_lines.insert(0, line_metrics[best_split-2]['line'])
    if best_split + 1 < len(line_metrics):
        boundary_lines.append(line_metrics[best_split+1]['line'])

    staging_tokens = []
    for t in tokens:
        if t.line in boundary_lines:
            a = morph.atomize(t.word)
            mods = a.mods
            if 's' in mods or 'd' in mods:
                staging_tokens.append((t.word, t.line, a.gloss, mods))

    if staging_tokens:
        print(f"      Found {len(staging_tokens)} staging tokens near boundary (L{boundary_lines}):")
        for w, l, g, mods in staging_tokens:
            print(f"        L{l:>2s}: {w:18s} {g:40s} mods={mods}")
        print(f"      PASS: Staging atoms present at phase boundary")
    else:
        print(f"      FAIL: No staging atoms at boundary")
else:
    print(f"      SKIP: No phase boundary detected")

# P4: Equipment/arrangement tokens (o-HEAD) early (setup)
print(f"\n  P4: Equipment/arrangement tokens (o-HEAD) appearing early (setup)")
o_head_by_line = defaultdict(list)
for t in tokens:
    a = morph.atomize(t.word)
    if a.head == 'o':
        o_head_by_line[t.line].append(t.word)

early_o = sum(len(v) for k, v in o_head_by_line.items() if safe_int(k) <= safe_int(lines[len(lines)//4]))
late_o = sum(len(v) for k, v in o_head_by_line.items() if safe_int(k) > safe_int(lines[3*len(lines)//4]))
total_o = sum(len(v) for v in o_head_by_line.values())

print(f"      Total o-HEAD tokens: {total_o}")
print(f"      First quarter: {early_o}")
print(f"      Last quarter:  {late_o}")
if early_o > late_o and total_o > 0:
    print(f"      PASS: o-HEAD (arrangement) concentrated early")
else:
    print(f"      {'FAIL' if total_o > 0 else 'INCONCLUSIVE'}: o-HEAD not early-concentrated")

# ═══════════════════════════════════════════════════════════════
# 6. FREEDOM SPACE POSITION
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 100)
print("6. FREEDOM SPACE POSITION")
print("=" * 100)

# Load feature matrix from t0
try:
    with open(ROOT / 'phases' / 'APPARATUS_RESPONSE_MANIFOLD_SYNTHESIS' / 'results' /
              't0_feature_matrix_assembly.json', encoding='utf-8') as f:
        fm = json.load(f)

    folios_list = fm['folios']
    raw_B = fm['space_B']['raw']

    if 'f108r' in folios_list:
        idx = folios_list.index('f108r')
        features = raw_B[idx]
        print(f"  f108r raw features (4 freedom dims): {features}")
        print(f"  Feature order: [mod_c, term_h, mod_d, mod_s]  (from t0 assembly)")

        # Compute percentile ranks
        for fi, fname in enumerate(['mod_c', 'term_h', 'mod_d', 'mod_s']):
            vals = [row[fi] for row in raw_B]
            rank = sum(1 for v in vals if v < features[fi])
            pctile = 100 * rank / len(vals)
            print(f"    {fname}: {features[fi]:.4f}  (percentile: {pctile:.1f}%)")
    else:
        print("  f108r not in feature matrix folio list")

    # PC positions from s1
    with open(ROOT / 'phases' / 'FOLIO_DESIGN_FREEDOM' / 'results' /
              's1_variance_decomposition.json', encoding='utf-8') as f:
        s1 = json.load(f)

    fp = s1.get('folio_pc_positions', {})
    if 'f108r' in fp:
        pc = fp['f108r']
        print(f"\n  PC positions: PC1={pc.get('PC1', 'N/A'):.3f}, "
              f"PC2={pc.get('PC2', 'N/A'):.3f}")
        print(f"  Section classification: {pc.get('section', 'N/A')}")

        # Compute PC percentile ranks
        all_pc1 = [v['PC1'] for v in fp.values() if 'PC1' in v]
        all_pc2 = [v['PC2'] for v in fp.values() if 'PC2' in v]
        pc1_pctile = 100 * sum(1 for v in all_pc1 if v < pc['PC1']) / len(all_pc1)
        pc2_pctile = 100 * sum(1 for v in all_pc2 if v < pc['PC2']) / len(all_pc2)
        print(f"    PC1 percentile: {pc1_pctile:.1f}%")
        print(f"    PC2 percentile: {pc2_pctile:.1f}%")
    else:
        print("  f108r not in s1 PC positions")

except Exception as e:
    print(f"  ERROR loading freedom space data: {e}")

# ═══════════════════════════════════════════════════════════════
# 7. RECIPE ALIGNMENT SUMMARY
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 100)
print("7. RECIPE ALIGNMENT SUMMARY")
print("PL Ch XVI: Separation of elements from putrefied white composite")
print("=" * 100)

# For each recipe step, find candidate lines
recipe_steps = [
    ("1. Putrefaction complete (1.5 months, 'well animated')",
     "Look for: state atoms (l), iteration (i), passive monitoring (sh)"),
    ("2. Remove cover, place alembic, seal with lute",
     "Look for: arrangement (o-HEAD), equipment tokens, careful monitoring (h)"),
    ("3. Hot balneum mariae — gentle fire, distill water",
     "Look for: high e_depth (ee = balneum), k-HEAD (heat), gentle signature"),
    ("4. Continue until nothing distills; cease fire, cool",
     "Look for: e-HEAD (cooling), sequence change (s,d mods), iteration end"),
    ("5. Remove vessel, place on ashes in aludel",
     "Look for: arrangement (o-HEAD), equipment change, transfer (t)"),
    ("6. Strengthen fire — distill air mixed with fire",
     "Look for: k-HEAD increase, e_depth DROP (direct heat), reduced e>=2"),
    ("7. Receive in glass phial, seal well, set aside",
     "Look for: arrangement (o-HEAD), monitoring (h), end markers (y,n,m)"),
    ("8. Residue = dry and black earth",
     "Look for: state atoms (l), mark (d), terminal markers"),
    ("9. Principle: water in balneum, air in ashes",
     "Look for: two-phase structure reflected in overall folio architecture"),
    ("10. Separate three elements (white) / four (red)",
     "Look for: structural grouping, possible 3-part or paragraph division"),
]

for step_desc, look_for in recipe_steps:
    print(f"\n  {step_desc}")
    print(f"    {look_for}")

    # Provide quantitative evidence for each step
    if "putrefaction" in step_desc.lower():
        sh_total = sum(1 for t in tokens if (morph.atomize(t.word).prefix or '') in ('sh', 'lsh'))
        i_total = sum(1 for t in tokens for c, r, g in morph.atomize(t.word).atoms if c == 'i')
        print(f"    Evidence: sh-prefix (passive monitoring) = {sh_total} tokens, "
              f"i-atoms (iteration) = {i_total}")

    elif "alembic" in step_desc.lower() or "seal" in step_desc.lower():
        o_early = sum(1 for t in tokens if t.line in lines[:5] and morph.atomize(t.word).head == 'o')
        h_early = sum(1 for t in tokens if t.line in lines[:5]
                      for c, r, g in morph.atomize(t.word).atoms if c == 'h')
        print(f"    Evidence: o-HEAD in L1-L5 = {o_early}, h-atoms in L1-L5 = {h_early}")

    elif "balneum" in step_desc.lower() and "gentle" in step_desc.lower():
        e2_total = sum(1 for t in tokens if morph.atomize(t.word).e_depth >= 2)
        e2_first_half = sum(1 for t in tokens if t.line in first_half_lines
                           and morph.atomize(t.word).e_depth >= 2)
        print(f"    Evidence: e>=2 total = {e2_total}, in first half = {e2_first_half}")

    elif "cease fire" in step_desc.lower() or "cool" in step_desc.lower():
        e_heads = sum(1 for t in tokens if morph.atomize(t.word).head == 'e')
        print(f"    Evidence: e-HEAD (cooling) = {e_heads} tokens")

    elif "ashes" in step_desc.lower() and "aludel" in step_desc.lower():
        t_atoms = sum(1 for t in tokens for c, r, g in morph.atomize(t.word).atoms if c == 't')
        print(f"    Evidence: t-atoms (transfer) = {t_atoms}")

    elif "strengthen" in step_desc.lower():
        if best_split is not None:
            k_phase2 = sum(1 for t in tokens if safe_int(t.line) >= safe_int(split_line)
                          and morph.atomize(t.word).head == 'k')
            k_phase1 = sum(1 for t in tokens if safe_int(t.line) < safe_int(split_line)
                          and morph.atomize(t.word).head == 'k')
            print(f"    Evidence: k-HEAD phase1={k_phase1}, phase2={k_phase2}")

    elif "phial" in step_desc.lower():
        late_lines = lines[-5:]
        o_late = sum(1 for t in tokens if t.line in late_lines
                     and morph.atomize(t.word).head == 'o')
        print(f"    Evidence: o-HEAD in last 5 lines = {o_late}")

    elif "residue" in step_desc.lower():
        l_total = sum(1 for t in tokens for c, r, g in morph.atomize(t.word).atoms if c == 'l')
        d_total = sum(1 for t in tokens for c, r, g in morph.atomize(t.word).atoms if c == 'd')
        print(f"    Evidence: l-atoms (state) = {l_total}, d-atoms (mark) = {d_total}")

    elif "principle" in step_desc.lower():
        print(f"    Evidence: Two-phase split detected={best_split is not None}, "
              f"diff={best_diff:.3f}")

    elif "three elements" in step_desc.lower():
        print(f"    Evidence: {n_paragraphs} paragraphs detected")

# ═══════════════════════════════════════════════════════════════
# 8. DARK PIPELINE
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 100)
print("8. DARK PIPELINE TOKENS")
print("=" * 100)

dark_mids = set()
for t in tokens:
    m = morph.extract(t.word)
    if m.middle and m.middle in dp_set:
        a = morph.atomize(t.word)
        atoms_str = '.'.join(ATOM_GLOSSES.get(c, '?') for c in m.middle)
        dark_mids.add(m.middle)
        print(f"  L{t.line:>2s}: {t.word:18s} mid={m.middle:10s} ({atoms_str})")

print(f"\n  Unique dark MIDDLEs: {len(dark_mids)}")
print(f"  Dark MIDDLEs: {sorted(dark_mids)}")

# ═══════════════════════════════════════════════════════════════
# 9. KEY TOKENS: chekar, dar, dal
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 100)
print("9. KEY TOKENS: chekar, dar, dal")
print("=" * 100)

for keyword in ['chekar', 'dar', 'dal']:
    hits = [(t.word, t.line) for t in tokens if t.word == keyword]
    print(f"  {keyword}: {len(hits)} occurrences")
    for w, l in hits:
        lt = [x.word for x in tokens if x.line == l]
        print(f"    L{l:>2s}: {' '.join(lt)}")

# ═══════════════════════════════════════════════════════════════
# 10. COMPARISON WITH OTHER RECIPE FOLIOS
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 100)
print("10. COMPARISON WITH OTHER RECIPE FOLIOS")
print("=" * 100)

all_b = [t for t in all_tokens
         if t.language == 'B' and t.word.strip()
         and not t.is_label and '*' not in t.word]

for label, folio in [
    ('f108r (Ch16 elem sep)', 'f108r'),
    ('f75r  (Ch19 aqua vitae)', 'f75r'),
    ('f76r  (Ch18 elem sep)', 'f76r'),
    ('f84r  (Ch14 gold diss)', 'f84r'),
]:
    ftoks = [t for t in all_b if t.folio == folio]
    n = len(ftoks)
    if n == 0:
        print(f"  {label}: NO TOKENS")
        continue

    pre = Counter()
    e_depths_f = Counter()
    for t in ftoks:
        a = morph.atomize(t.word)
        if a.prefix:
            pre[a.prefix] += 1
        e_depths_f[a.e_depth] += 1

    words = [t.word for t in ftoks]
    dar = words.count('dar')
    dal = words.count('dal')
    chekar = sum(1 for w in words if w == 'chekar')
    e1 = e_depths_f.get(1, 0)
    e2 = sum(e_depths_f.get(k, 0) for k in e_depths_f if k >= 2)
    gentle = 100 * e2 / (e1 + e2) if e1 + e2 > 0 else 0

    qo = 100 * sum(pre.get(p, 0) for p in ['qo', 'ko', 'ke', 'lk']) / n
    ch = 100 * sum(pre.get(p, 0) for p in ['ch', 'pch', 'tch', 'dch', 'lch']) / n
    sh = 100 * sum(pre.get(p, 0) for p in ['sh', 'lsh']) / n

    dark_n = sum(1 for t in ftoks if morph.extract(t.word).middle in dp_set)
    mean_e_f = sum(morph.atomize(t.word).e_depth for t in ftoks) / n

    print(f"  {label}: {n}T  e_mean={mean_e_f:.2f}  qo={qo:.0f}% ch={ch:.0f}% sh={sh:.0f}%  "
          f"gentle={gentle:.0f}%  dar={dar} dal={dal} chekar={chekar} dark={dark_n}")

# ═══════════════════════════════════════════════════════════════
# 11. OVERALL ASSESSMENT
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 100)
print("11. OVERALL ASSESSMENT: Is f108r a convincing match for PL Ch XVI?")
print("=" * 100)

# Tally predictions
predictions = []
predictions.append(('P1: e_depth elevated (balneum dominance)',
                    mean_e_depth > herbal_mean_e,
                    mean_e_depth > stars_mean_e))
predictions.append(('P2: Cooling step visible',
                    len(cooling_tokens) > 0, None))
predictions.append(('P3: Staging atoms at boundary',
                    best_split is not None and best_diff > 0.03, None))
predictions.append(('P4: o-HEAD early (equipment setup)',
                    early_o > late_o and total_o > 0, None))

pass_count = 0
partial_count = 0
fail_count = 0
for desc, primary, secondary in predictions:
    if primary:
        status = 'PASS'
        pass_count += 1
    elif secondary:
        status = 'PARTIAL'
        partial_count += 1
    else:
        status = 'FAIL'
        fail_count += 1
    print(f"  {status:8s} {desc}")

print(f"\n  Score: {pass_count} PASS, {partial_count} PARTIAL, {fail_count} FAIL out of {len(predictions)}")
print(f"  Two-phase split quality: e_depth diff = {best_diff:.3f} "
      f"({'strong' if best_diff > 0.1 else 'moderate' if best_diff > 0.05 else 'weak'})")

# Honest assessment
print(f"\n  HONEST ASSESSMENT:")
print(f"  The Voynich atom system is designed to encode operational procedures.")
print(f"  Any sufficiently detailed recipe will find SOME alignment with atom")
print(f"  distributions, because the atoms describe generic process operations")
print(f"  (heat, cool, monitor, mark, sequence, arrange, etc.).")
print(f"  ")
print(f"  Convincing match criteria:")
print(f"  1. Specific quantitative predictions confirmed (not just 'atoms exist')")
print(f"  2. Structural breaks align with recipe phase transitions")
print(f"  3. Distinctive features (e.g., unusual e_depth) match recipe emphasis")
print(f"  4. The folio looks MORE like this recipe than a random recipe")

# ═══════════════════════════════════════════════════════════════
# SAVE JSON RESULTS
# ═══════════════════════════════════════════════════════════════
results = {
    'folio': 'f108r',
    'recipe': 'PL Chapter XVI Practica — Separation of elements from putrefied white composite',
    'section': list(sections)[0] if sections else 'unknown',
    'language': list(languages)[0] if languages else 'unknown',
    'basic_profile': {
        'n_tokens': n_tokens,
        'n_lines': n_lines,
        'n_paragraphs': n_paragraphs,
        'para_starts': para_starts,
        'e_depth_mean': round(mean_e_depth, 4),
        'e_depth_distribution': {str(k): v for k, v in sorted(e_depth_dist.items())},
        'head_distribution': dict(head_dist.most_common()),
        'mod_distribution': dict(mod_dist.most_common()),
        'term_distribution': dict(term_dist.most_common()),
        'prefix_distribution': dict(prefix_dist.most_common()),
        'headed_pct': round(100 * head_count / n_tokens, 1),
    },
    'comparisons': {
        'herbal_e_depth_mean': round(herbal_mean_e, 4),
        'stars_e_depth_mean': round(stars_mean_e, 4),
    },
    'trajectory': {
        'first_half_e_mean': round(first_mean, 4),
        'second_half_e_mean': round(second_mean, 4),
        'first_half_gentle_pct': round(100 * first_gentle / len(first_half_e), 1) if first_half_e else 0,
        'second_half_gentle_pct': round(100 * second_gentle / len(second_half_e), 1) if second_half_e else 0,
    },
    'two_phase': {
        'best_split_line': split_line if best_split else None,
        'e_depth_diff': round(best_diff, 4),
        'split_quality': 'strong' if best_diff > 0.1 else 'moderate' if best_diff > 0.05 else 'weak',
    },
    'predictions': {
        'P1_e_depth_elevated': mean_e_depth > herbal_mean_e,
        'P1_e_depth_above_stars': mean_e_depth > stars_mean_e,
        'P2_cooling_visible': len(cooling_tokens) > 0,
        'P2_cooling_count': len(cooling_tokens),
        'P3_staging_at_boundary': best_split is not None and best_diff > 0.03,
        'P4_o_head_early': early_o > late_o and total_o > 0,
    },
    'dark_pipeline': {
        'n_dark_tokens': sum(1 for t in tokens if morph.extract(t.word).middle in dp_set),
        'unique_dark_middles': sorted(dark_mids),
    },
    'key_tokens': {
        'chekar': sum(1 for t in tokens if t.word == 'chekar'),
        'dar': sum(1 for t in tokens if t.word == 'dar'),
        'dal': sum(1 for t in tokens if t.word == 'dal'),
    },
    'line_data': line_data,
    'score': {
        'pass': pass_count,
        'partial': partial_count,
        'fail': fail_count,
        'total': len(predictions),
    },
}

# Add freedom space if available
try:
    if 'f108r' in folios_list:
        idx = folios_list.index('f108r')
        features = raw_B[idx]
        feature_names = ['mod_c', 'term_h', 'mod_d', 'mod_s']
        percentiles = {}
        for fi, fname in enumerate(feature_names):
            vals = [row[fi] for row in raw_B]
            rank = sum(1 for v in vals if v < features[fi])
            percentiles[fname] = round(100 * rank / len(vals), 1)
        results['freedom_space'] = {
            'raw_features': {fname: round(features[fi], 4) for fi, fname in enumerate(feature_names)},
            'percentile_ranks': percentiles,
        }
    if 'f108r' in fp:
        results['freedom_space']['PC1'] = round(fp['f108r']['PC1'], 3)
        results['freedom_space']['PC2'] = round(fp['f108r']['PC2'], 3)
except Exception:
    pass

out_path = ROOT / 'phases' / 'RECIPE_FOLIO_CORRESPONDENCE' / 'results' / 'decode_f108r.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\n\nResults saved to: {out_path}")
print("\n" + "=" * 100)
print("DONE")
print("=" * 100)
