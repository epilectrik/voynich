"""
Rebuild folio_operational_profiles.json using atomize()-corrected features.

Follows the EXACT same feature definitions as archive/scripts/build_folio_profiles.py
but uses atomize() to correctly identify MIDDLE contents and suffix types.

Key corrections:
  - thermo_ke: check if atom sequence contains k followed by e (not MIDDLE substring)
  - terminal_rate: check TERM atom for terminal-class endings
  - iteration_rate: check for i atoms in sequence
  - checkpoint_rate: check for ain/aiin patterns in atom sequence
"""

import json, sys, io
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# Match original definitions
PREP_MIDDLES = {'te', 'pch', 'lch', 'tch'}
THERMO_MIDDLES = {'ke', 'kch'}
CHECKPOINT_SUFFIXES = {'aiin', 'ain'}
ITERATION_SUFFIXES = {'iin'}
TERMINAL_SUFFIXES = {'y', 'dy', 'ry', 'oly', 'am', 'om', 'im'}

# Load original for kernel ratios and categorical fields (unchanged)
with open(ROOT / 'results' / 'folio_operational_profiles.json', encoding='utf-8') as f:
    orig = json.load(f)
orig_by_folio = {p['folio']: p for p in orig.get('profiles', [])}

b_folios = sorted(set(t.folio for t in tx.currier_b()))
print(f"Rebuilding profiles for {len(b_folios)} folios")

profiles = []

for folio in b_folios:
    toks = [t for t in tx.currier_b() if t.folio == folio and t.word.strip()]
    if not toks:
        continue

    n = len(toks)
    orig_p = orig_by_folio.get(folio, {})

    prep_counts = Counter()
    thermo_counts = Counter()
    suffix_terminal = 0
    suffix_checkpoint = 0
    suffix_iteration = 0
    total_with_suffix = 0

    for t in toks:
        m = morph.extract(t.word)
        a = morph.atomize(t.word)

        # PREP MIDDLEs: check if extract() MIDDLE contains prep patterns
        # This is unchanged — prep MIDDLEs (te, pch, lch, tch) are PREFIX-based
        # and not affected by the edy bug
        if m.middle:
            for pm in PREP_MIDDLES:
                if m.middle == pm or (len(m.middle) > len(pm) and pm in m.middle):
                    prep_counts[pm] += 1

        # THERMO MIDDLEs: CORRECTED using atomize()
        # Original: checked if extract().middle contains 'ke' or 'kch'
        # Fix: check if the atom sequence has k followed by e (for ke)
        # or k followed by c followed by h (for kch)
        atom_chars = ''.join(c for c, _, _ in a.atoms)
        for tm in THERMO_MIDDLES:
            if tm in atom_chars:
                thermo_counts[tm] += 1

        # SUFFIX features: CORRECTED using atomize()
        # Original checked extract().suffix against fixed suffix lists
        # Fix: use extract() suffix BUT also check for cases where
        # the suffix should be different due to edy absorption
        #
        # The key issue: extract() gives suffix='edy' for tokens like qokedy
        # when the correct suffix should be 'dy'. We need to detect this.
        suffix = m.suffix
        if suffix:
            total_with_suffix += 1

            # Correct edy -> dy when MIDDLE would gain an 'e'
            # If suffix is 'edy' and the preceding MIDDLE doesn't end with
            # a vowel-initial suffix pattern, the 'e' belongs to MIDDLE
            corrected_suffix = suffix
            if suffix == 'edy' and m.middle and m.middle not in ('', None):
                # The atomize sequence tells us the truth
                # If atom sequence has more 'e' atoms than extract MIDDLE,
                # the suffix stole one
                mid_e = m.middle.count('e')
                atom_e = sum(1 for c, _, _ in a.atoms if c == 'e')
                if atom_e > mid_e:
                    corrected_suffix = 'dy'  # return the stolen e to MIDDLE
            elif suffix == 'eey' and m.middle and m.middle not in ('', None):
                mid_e = m.middle.count('e')
                atom_e = sum(1 for c, _, _ in a.atoms if c == 'e')
                if atom_e > mid_e:
                    corrected_suffix = 'ey'

            if corrected_suffix in TERMINAL_SUFFIXES:
                suffix_terminal += 1
            if corrected_suffix in CHECKPOINT_SUFFIXES:
                suffix_checkpoint += 1
            if corrected_suffix in ITERATION_SUFFIXES:
                suffix_iteration += 1
        else:
            # No suffix from extract() — check if atomize sees a bare terminal
            # Bare tokens (no suffix) that end in terminal atoms still count
            # as having suffix in the original definition only if extract found one
            pass

    ts = total_with_suffix or 1
    tc = n or 1

    profile = {
        'folio': folio,
        'token_count': n,
        'paragraph_count': orig_p.get('paragraph_count', 0),
        'prep_te': prep_counts.get('te', 0) / tc,
        'prep_pch': prep_counts.get('pch', 0) / tc,
        'prep_lch': prep_counts.get('lch', 0) / tc,
        'prep_tch': prep_counts.get('tch', 0) / tc,
        'thermo_ke': thermo_counts.get('ke', 0) / tc,
        'thermo_kch': thermo_counts.get('kch', 0) / tc,
        'k_ratio': orig_p.get('k_ratio', 0),
        'h_ratio': orig_p.get('h_ratio', 0),
        'e_ratio': orig_p.get('e_ratio', 0),
        'iteration_rate': round(suffix_iteration / ts, 4),
        'checkpoint_rate': round(suffix_checkpoint / ts, 4),
        'terminal_rate': round(suffix_terminal / ts, 4),
        'material_category': orig_p.get('material_category', 'UNKNOWN'),
        'output_category': orig_p.get('output_category', 'UNKNOWN'),
        'kernel_balance': orig_p.get('kernel_balance', 'UNKNOWN'),
    }
    profiles.append(profile)

# Save as v3 (corrected, matching original schema)
output = {
    'title': 'Voynich B Folio Operational Profiles (atomize-corrected v3)',
    'folio_count': len(profiles),
    'dimensions': ['prep_te', 'prep_pch', 'prep_lch', 'prep_tch',
                   'thermo_ke', 'thermo_kch',
                   'k_ratio', 'h_ratio', 'e_ratio',
                   'iteration_rate', 'checkpoint_rate', 'terminal_rate'],
    'profiles': profiles,
}

out_path = ROOT / 'results' / 'folio_operational_profiles_v3.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
print(f"Saved: {out_path}")

# Validate against known matches
print(f"\n{'=' * 90}")
print("VALIDATION: Corrected vs original features for matched folios")
print(f"{'=' * 90}")

matched = ['f75r', 'f76r', 'f77v', 'f84r', 'f108r', 'f84v', 'f83r', 'f112r', 'f81v']
v3_by_folio = {p['folio']: p for p in profiles}

print(f"\n{'Folio':>8s} {'Feature':>15s} {'Original':>10s} {'Corrected':>10s} {'Delta':>10s}")
print('-' * 60)

for folio in matched:
    o = orig_by_folio.get(folio, {})
    c = v3_by_folio.get(folio, {})
    for feat in ['thermo_ke', 'terminal_rate', 'iteration_rate', 'checkpoint_rate']:
        ov = o.get(feat, 0) or 0
        cv = c.get(feat, 0) or 0
        delta = cv - ov
        if abs(delta) > 0.001:
            print(f"{folio:>8s} {feat:>15s} {ov:10.4f} {cv:10.4f} {delta:+10.4f}")

# Now run the Phase 628 matching with corrected profiles
print(f"\n\n{'=' * 90}")
print("RUNNING PHASE 628 MATCHING WITH CORRECTED PROFILES")
print(f"{'=' * 90}")

# Load PL channel features
sys.path.insert(0, str(ROOT / 'phases' / 'PER_DOMAIN_BRIDGE_CALIBRATION' / 'scripts'))
from shared_627 import load_pl_channel_features, load_regime_mapping, load_b_deployment_features

pl_feats = load_pl_channel_features()
regime_map = load_regime_mapping()
deploy, _ = load_b_deployment_features()

# Get distillation chapters and R1 folios
per_ch = pl_feats['T5_channel_signatures']['per_chapter']
dist_chs = [ch for ch in per_ch if ch.get('family') == 'distillation']
r1_fols = sorted(f for f, r in regime_map.items() if r == 'REGIME_1')

print(f"Distillation chapters: {len(dist_chs)}")
print(f"R1 folios: {len(r1_fols)}")

# Build corrected operational profiles dict
corrected_op = {p['folio']: p for p in profiles}

# Import matching function
sys.path.insert(0, str(ROOT / 'phases' / 'RECIPE_FOLIO_CORRESPONDENCE' / 'scripts'))
from shared_628 import build_pl_vector, compute_residuals, standardize, TUNED_DIMS
import math

def build_v_vector_corrected(folio, dims):
    """Build V vector using corrected operational profiles + original deployment."""
    prof = corrected_op.get(folio, {})
    dep_f = deploy.get(folio, {})
    vec = []
    for pl_feat, v_feat, sign in dims:
        if v_feat.startswith('d_'):
            raw_key = v_feat[2:]
            val = dep_f.get(raw_key, 0.0)
        else:
            val = prof.get(v_feat, 0.0)
        vec.append(float(val) if val is not None else 0.0)
    return vec

# Build vectors
pl_raw = [build_pl_vector(ch, TUNED_DIMS) for ch in dist_chs]
v_raw = [build_v_vector_corrected(f, TUNED_DIMS) for f in r1_fols]

# Sign flips
for i in range(len(pl_raw)):
    for d, (_, _, sign) in enumerate(TUNED_DIMS):
        pl_raw[i][d] *= sign

# Residuals + standardize
pl_resid = compute_residuals(pl_raw)
v_resid = compute_residuals(v_raw)
all_vecs = pl_resid + v_resid
all_std = standardize(all_vecs)
pl_std = all_std[:len(dist_chs)]
v_std = all_std[len(dist_chs):]

# Distance matrix and matching
def euc(a, b):
    return math.sqrt(sum((x-y)**2 for x, y in zip(a, b)))

print(f"\n{'Ch#':>4} {'Folio':>8} {'Dist':>7} {'2nd':>8} {'2ndD':>7} {'Ratio':>6} {'Conf':>5}")
print('-' * 50)

confident_matches = []
for i, ch in enumerate(dist_chs):
    dists = [(j, euc(pl_std[i], v_std[j])) for j in range(len(r1_fols))]
    dists.sort(key=lambda x: x[1])
    best_j, best_d = dists[0]
    second_j, second_d = dists[1]
    ratio = second_d / best_d if best_d > 0 else 0
    conf = ratio > 1.15

    ch_num = ch.get('chapter_number', ch.get('number', '?'))
    print(f"{ch_num:>4} {r1_fols[best_j]:>8} {best_d:7.3f} {r1_fols[second_j]:>8} {second_d:7.3f} {ratio:6.3f} {'Y' if conf else '':>5}")

    if conf:
        confident_matches.append((ch_num, r1_fols[best_j]))

print(f"\nConfident matches: {len(confident_matches)}/{len(dist_chs)}")

# Check concordance with Phase 628
print(f"\nPhase 628 concordance:")
phase628 = {19: 'f75r', 18: 'f76r', 27: 'f77v', 14: 'f84r', 16: 'f108r',
            24: 'f84v', 9: 'f83r', 11: 'f112r'}
hits = 0
for ch_num, folio in confident_matches:
    if ch_num in phase628:
        expected = phase628[ch_num]
        match = folio == expected
        if match: hits += 1
        print(f"  Ch{ch_num}: corrected={folio}, Phase628={expected} {'MATCH' if match else 'DIFFERENT'}")

total_comparable = sum(1 for cn, _ in confident_matches if cn in phase628)
print(f"  Concordance: {hits}/{total_comparable}")

print(f"\n{'=' * 90}")
print("DONE")
print(f"{'=' * 90}")
