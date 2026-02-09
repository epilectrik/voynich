"""
06_line_final_material_slot.py - Line-Final Material Slot Test

Tests whether line-final position is a structural "material slot" enriched
for rare/unique MIDDLEs.

Method:
1. Classify each token as LINE_FINAL (last in its line) vs LINE_OTHER
2. Compute enrichment of rare middles (<15 folios) and folio-unique middles (1 folio)
3. Confound control: line length bins (short/medium/long)
4. Confound control: suffix pattern check (line-final suffixes like -y, -ly, -am)
5. Zone distribution (setup/process/finish)
"""

import json
import sys
from collections import defaultdict, Counter
from scipy import stats

sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology

# ============================================================
# LOAD DATA
# ============================================================
tx = Transcript()
morph = Morphology()

# Collect all Currier B tokens (H-only, no labels, no uncertain, no empty)
b_tokens = list(tx.currier_b())
print(f"Total Currier B tokens: {len(b_tokens)}")

# ============================================================
# PRE-COMPUTE: MIDDLE extraction for all tokens
# ============================================================
token_data = []  # list of dicts with token info + morphology
for t in b_tokens:
    m = morph.extract(t.word)
    mid = m.middle if m and m.middle and m.middle != '_EMPTY_' else None
    suffix = m.suffix if m else None
    token_data.append({
        'token': t,
        'middle': mid,
        'suffix': suffix,
        'folio': t.folio,
        'line': t.line,
        'line_final': t.line_final,
        'par_initial': t.par_initial,
    })

tokens_with_middle = [td for td in token_data if td['middle'] is not None]
print(f"Tokens with valid MIDDLE: {len(tokens_with_middle)}")

# ============================================================
# PRE-COMPUTE: folio count per MIDDLE
# ============================================================
middle_folios = defaultdict(set)
for td in tokens_with_middle:
    middle_folios[td['middle']].add(td['folio'])

middle_folio_count = {mid: len(folios) for mid, folios in middle_folios.items()}

# Classify rarity
RARE_THRESHOLD = 15
for td in tokens_with_middle:
    fc = middle_folio_count.get(td['middle'], 0)
    td['is_rare'] = fc < RARE_THRESHOLD
    td['is_unique'] = fc == 1

print(f"Unique MIDDLEs: {len(middle_folio_count)}")
print(f"Rare MIDDLEs (<{RARE_THRESHOLD} folios): {sum(1 for v in middle_folio_count.values() if v < RARE_THRESHOLD)}")
print(f"Folio-unique MIDDLEs (1 folio): {sum(1 for v in middle_folio_count.values() if v == 1)}")

# ============================================================
# PRE-COMPUTE: line length for each (folio, line)
# ============================================================
line_tokens = defaultdict(int)
for td in token_data:
    line_tokens[(td['folio'], td['line'])] += 1

for td in tokens_with_middle:
    td['line_length'] = line_tokens[(td['folio'], td['line'])]

# ============================================================
# PRE-COMPUTE: paragraph numbering for zone classification
# ============================================================
# Assign paragraph numbers within each folio using par_initial markers
current_folio = None
current_para = 0
folio_para_map = {}  # (folio, line) -> para_num

for td in token_data:
    if td['folio'] != current_folio:
        current_folio = td['folio']
        current_para = 0
    if td['par_initial']:
        current_para += 1
    folio_para_map[(td['folio'], td['line'])] = current_para

# Count paragraphs per folio
folio_para_count = defaultdict(int)
for (fol, _), para in folio_para_map.items():
    folio_para_count[fol] = max(folio_para_count[fol], para)

# Classify zone: setup (first para), finish (last para), process (middle)
for td in tokens_with_middle:
    para = folio_para_map.get((td['folio'], td['line']), 0)
    total_paras = folio_para_count.get(td['folio'], 1)
    if para <= 1:
        td['zone'] = 'setup'
    elif para >= total_paras and total_paras > 1:
        td['zone'] = 'finish'
    else:
        td['zone'] = 'process'

# ============================================================
# ANALYSIS 1: Basic enrichment - LINE_FINAL vs LINE_OTHER
# ============================================================
final_tokens = [td for td in tokens_with_middle if td['line_final']]
other_tokens = [td for td in tokens_with_middle if not td['line_final']]

n_final = len(final_tokens)
n_other = len(other_tokens)
print(f"\nLINE_FINAL tokens: {n_final}")
print(f"LINE_OTHER tokens: {n_other}")


def compute_enrichment(final_set, other_set, key):
    """Compute rate, odds ratio, and chi-square for a boolean key."""
    n_f = len(final_set)
    n_o = len(other_set)
    rare_f = sum(1 for td in final_set if td[key])
    rare_o = sum(1 for td in other_set if td[key])
    not_rare_f = n_f - rare_f
    not_rare_o = n_o - rare_o

    rate_f = rare_f / n_f if n_f > 0 else 0.0
    rate_o = rare_o / n_o if n_o > 0 else 0.0

    # Odds ratio (with continuity correction to avoid division by zero)
    a, b, c, d = rare_f, not_rare_f, rare_o, not_rare_o
    if b == 0 or c == 0:
        odds_ratio = float('inf') if a > 0 and d > 0 else 0.0
    else:
        odds_ratio = (a * d) / (b * c)

    # Chi-square test (2x2 contingency table)
    table = [[rare_f, not_rare_f], [rare_o, not_rare_o]]
    if min(rare_f, not_rare_f, rare_o, not_rare_o) >= 5:
        chi2, p_val = stats.chi2_contingency(table)[:2]
    elif n_f > 0 and n_o > 0:
        # Use Fisher's exact test for small samples
        _, p_val = stats.fisher_exact(table)
        chi2 = 0.0
    else:
        chi2, p_val = 0.0, 1.0

    return {
        'rate_final': round(rate_f, 4),
        'rate_other': round(rate_o, 4),
        'odds_ratio': round(odds_ratio, 4),
        'chi_square': round(chi2, 4),
        'p_value': round(p_val, 6),
        'n_final_rare': rare_f,
        'n_other_rare': rare_o,
    }


rare_enrich = compute_enrichment(final_tokens, other_tokens, 'is_rare')
unique_enrich = compute_enrichment(final_tokens, other_tokens, 'is_unique')

print(f"\n--- RARE MIDDLE enrichment (<{RARE_THRESHOLD} folios) ---")
print(f"  LINE_FINAL rate: {rare_enrich['rate_final']:.4f} ({rare_enrich['n_final_rare']}/{n_final})")
print(f"  LINE_OTHER rate: {rare_enrich['rate_other']:.4f} ({rare_enrich['n_other_rare']}/{n_other})")
print(f"  Odds ratio: {rare_enrich['odds_ratio']:.4f}")
print(f"  Chi-square: {rare_enrich['chi_square']:.4f}, p={rare_enrich['p_value']:.6f}")

print(f"\n--- FOLIO-UNIQUE MIDDLE enrichment (1 folio) ---")
print(f"  LINE_FINAL rate: {unique_enrich['rate_final']:.4f} ({unique_enrich['n_final_rare']}/{n_final})")
print(f"  LINE_OTHER rate: {unique_enrich['rate_other']:.4f} ({unique_enrich['n_other_rare']}/{n_other})")
print(f"  Odds ratio: {unique_enrich['odds_ratio']:.4f}")
print(f"  Chi-square: {unique_enrich['chi_square']:.4f}, p={unique_enrich['p_value']:.6f}")

# ============================================================
# ANALYSIS 2: Line-length controlled enrichment
# ============================================================
def classify_line_length(length):
    if length <= 4:
        return 'short'
    elif length <= 8:
        return 'medium'
    else:
        return 'long'


length_controlled = {}
for bin_name in ['short', 'medium', 'long']:
    bin_final = [td for td in final_tokens if classify_line_length(td['line_length']) == bin_name]
    bin_other = [td for td in other_tokens if classify_line_length(td['line_length']) == bin_name]

    if len(bin_final) >= 5 and len(bin_other) >= 5:
        re = compute_enrichment(bin_final, bin_other, 'is_rare')
        ue = compute_enrichment(bin_final, bin_other, 'is_unique')
        length_controlled[bin_name] = {
            'n_final': len(bin_final),
            'n_other': len(bin_other),
            'rare_or': re['odds_ratio'],
            'rare_p': re['p_value'],
            'unique_or': ue['odds_ratio'],
            'unique_p': ue['p_value'],
        }
    else:
        length_controlled[bin_name] = {
            'n_final': len(bin_final),
            'n_other': len(bin_other),
            'rare_or': None,
            'rare_p': None,
            'unique_or': None,
            'unique_p': None,
        }

print(f"\n--- LINE LENGTH CONTROLLED ---")
for bin_name, data in length_controlled.items():
    print(f"  {bin_name}: n_final={data['n_final']}, n_other={data['n_other']}, "
          f"rare_OR={data['rare_or']}, rare_p={data['rare_p']}")

# ============================================================
# ANALYSIS 3: Suffix confound control
# ============================================================
# Known line-final suffixes (from C777, C897, and GLOSSING context)
LINE_FINAL_SUFFIXES = {'y', 'ly', 'am', 'dy', 'ry'}

# For line-final tokens WITH rare middles: what % have line-final suffixes?
final_rare = [td for td in final_tokens if td['is_rare']]
final_all = final_tokens
other_rare = [td for td in other_tokens if td['is_rare']]

def line_final_suffix_rate(token_list):
    """Compute fraction of tokens with a known line-final suffix."""
    if not token_list:
        return 0.0
    count = sum(1 for td in token_list if td['suffix'] in LINE_FINAL_SUFFIXES)
    return count / len(token_list)


lf_suffix_rate_rare = line_final_suffix_rate(final_rare)
lf_suffix_rate_all_final = line_final_suffix_rate(final_all)
lf_suffix_rate_other_rare = line_final_suffix_rate(other_rare)
lf_suffix_rate_other_all = line_final_suffix_rate(other_tokens)

# If line-final rare middles have MUCH higher line-final suffix rates than
# line-final tokens overall, the suffix (not the middle) drives the pattern.
# If they are similar, the middle rarity is independent of suffix.
suffix_explains = (lf_suffix_rate_rare > lf_suffix_rate_all_final + 0.10)

print(f"\n--- SUFFIX CONFOUND ---")
print(f"  Line-final suffix rate (LINE_FINAL + rare MIDDLE): {lf_suffix_rate_rare:.4f}")
print(f"  Line-final suffix rate (LINE_FINAL, all):          {lf_suffix_rate_all_final:.4f}")
print(f"  Line-final suffix rate (LINE_OTHER + rare MIDDLE):  {lf_suffix_rate_other_rare:.4f}")
print(f"  Line-final suffix rate (LINE_OTHER, all):           {lf_suffix_rate_other_all:.4f}")
print(f"  Suffix explains rarity enrichment: {suffix_explains}")

# Detailed suffix breakdown for line-final rare middles
suffix_counts_final_rare = Counter(td['suffix'] for td in final_rare)
print(f"\n  Suffix distribution for LINE_FINAL + rare MIDDLE:")
for suf, cnt in suffix_counts_final_rare.most_common(10):
    print(f"    {suf!r}: {cnt} ({100*cnt/len(final_rare):.1f}%)")

# ============================================================
# ANALYSIS 4: Zone distribution
# ============================================================
# Among LINE_FINAL tokens with RARE middles, where do they concentrate?
zone_counts = Counter(td['zone'] for td in final_rare)
zone_total = sum(zone_counts.values())
zone_pcts = {z: round(100 * zone_counts.get(z, 0) / zone_total, 1)
             if zone_total > 0 else 0.0
             for z in ['setup', 'process', 'finish']}

# Baseline zone distribution (all tokens)
zone_baseline = Counter(td['zone'] for td in tokens_with_middle)
zone_baseline_total = sum(zone_baseline.values())
zone_baseline_pcts = {z: round(100 * zone_baseline.get(z, 0) / zone_baseline_total, 1)
                      if zone_baseline_total > 0 else 0.0
                      for z in ['setup', 'process', 'finish']}

print(f"\n--- ZONE DISTRIBUTION (LINE_FINAL + rare MIDDLE) ---")
for z in ['setup', 'process', 'finish']:
    print(f"  {z}: {zone_pcts[z]}% (baseline: {zone_baseline_pcts[z]}%)")

# ============================================================
# VERDICT
# ============================================================
# SUPPORTED if:
# 1. Rare OR > 1.3 AND p < 0.01
# 2. At least one line-length bin also shows OR > 1.2 AND p < 0.05
# 3. Suffix does NOT fully explain the pattern
rare_sig = rare_enrich['odds_ratio'] > 1.3 and rare_enrich['p_value'] < 0.01
length_sig = any(
    data['rare_or'] is not None and data['rare_or'] > 1.2 and data['rare_p'] < 0.05
    for data in length_controlled.values()
)
suffix_ok = not suffix_explains

verdict = "SUPPORTED" if (rare_sig and length_sig and suffix_ok) else "NOT_SUPPORTED"

# Build notes
notes_parts = []
notes_parts.append(f"Rare OR={rare_enrich['odds_ratio']}, p={rare_enrich['p_value']}")
notes_parts.append(f"Unique OR={unique_enrich['odds_ratio']}, p={unique_enrich['p_value']}")

# Note which length bins survived
surviving_bins = [b for b, d in length_controlled.items()
                  if d['rare_or'] is not None and d['rare_or'] > 1.2 and d['rare_p'] < 0.05]
if surviving_bins:
    notes_parts.append(f"Length-controlled signal survives in: {', '.join(surviving_bins)}")
else:
    notes_parts.append("Length-controlled signal does NOT survive in any bin")

if suffix_explains:
    notes_parts.append("Suffix confound: line-final suffixes explain rare MIDDLE enrichment")
else:
    notes_parts.append(f"Suffix confound controlled: rare MIDDLE lf-suffix rate "
                       f"{lf_suffix_rate_rare:.3f} vs baseline {lf_suffix_rate_all_final:.3f}")

notes = "; ".join(notes_parts)

print(f"\n{'='*60}")
print(f"VERDICT: {verdict}")
print(f"{'='*60}")
print(f"Notes: {notes}")

# ============================================================
# SAVE RESULTS
# ============================================================
output = {
    "test": "Line-Final Material Slot",
    "n_line_final": n_final,
    "n_line_other": n_other,
    "rare_rate_final": rare_enrich['rate_final'],
    "rare_rate_other": rare_enrich['rate_other'],
    "rare_odds_ratio": rare_enrich['odds_ratio'],
    "rare_chi_square": rare_enrich['chi_square'],
    "rare_p_value": rare_enrich['p_value'],
    "unique_rate_final": unique_enrich['rate_final'],
    "unique_rate_other": unique_enrich['rate_other'],
    "unique_odds_ratio": unique_enrich['odds_ratio'],
    "unique_chi_square": unique_enrich['chi_square'],
    "unique_p_value": unique_enrich['p_value'],
    "line_length_controlled": {
        bin_name: {
            "n_final": data['n_final'],
            "n_other": data['n_other'],
            "rare_or": data['rare_or'],
            "rare_p": data['rare_p'],
            "unique_or": data['unique_or'],
            "unique_p": data['unique_p'],
        }
        for bin_name, data in length_controlled.items()
    },
    "suffix_confound": {
        "line_final_suffix_rate_rare": round(lf_suffix_rate_rare, 4),
        "line_final_suffix_rate_all": round(lf_suffix_rate_all_final, 4),
        "suffix_explains": suffix_explains
    },
    "zone_distribution": {
        "setup_pct": zone_pcts['setup'],
        "process_pct": zone_pcts['process'],
        "finish_pct": zone_pcts['finish']
    },
    "zone_baseline": {
        "setup_pct": zone_baseline_pcts['setup'],
        "process_pct": zone_baseline_pcts['process'],
        "finish_pct": zone_baseline_pcts['finish']
    },
    "verdict": verdict,
    "notes": notes
}

output_path = 'C:/git/voynich/phases/MIDDLE_MATERIAL_SEMANTICS/results/line_final_material_slot.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {output_path}")
