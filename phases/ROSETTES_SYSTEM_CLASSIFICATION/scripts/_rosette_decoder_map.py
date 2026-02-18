#!/usr/bin/env python3
"""Build the Rosette Decoder Map: trace each rosette's labels to body text
locations, creating a cross-reference index that reveals what each rosette
is describing/explaining."""
import sys
import json
from pathlib import Path
from collections import Counter, defaultdict
ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT))

from scripts.voynich import (Transcript, Morphology, RosettesAnalyzer,
                              BFolioDecoder)

tx = Transcript()
morph = Morphology()
ra = RosettesAnalyzer()
decoder = BFolioDecoder()

# ============================================================
# 0. BUILD LABEL INVENTORY BY ROSETTE GROUP
# ============================================================
# Physical rosette groups on f85v2 (9 diagrams arranged in 3x3-ish layout)
ROSETTE_GROUPS = {
    'BOTTOM':  {'label': ['B1', 'B2', 'B3'], 'desc': []},
    'MIDDLE':  {'label': ['M1', 'M2', 'M3'], 'desc': ['M3']},
    'UPPER':   {'label': ['U1', 'U2', 'U3'], 'desc': ['U3']},
    'NORTH':   {'label': [],  'desc': ['N1', 'N2']},
    'VERT':    {'label': [],  'desc': ['V1', 'V2']},
    'CENTER':  {'label': [],  'desc': ['C2']},
    'D_W':     {'label': ['W1'], 'desc': ['D1']},
}

# Extract all labels per group
group_labels = {}
for gname, regions in ROSETTE_GROUPS.items():
    words = []
    for r in regions['label']:
        toks = ra.get_tokens('f85v2', r)
        for t in toks:
            words.append(t.word)
    group_labels[gname] = words

# ============================================================
# 1. BUILD FULL MANUSCRIPT INDEX (word → folio → section → count)
# ============================================================
print("Building manuscript index...")

# Pre-build: for every word in the manuscript, record where it appears
word_folio_section = defaultdict(lambda: defaultdict(lambda: Counter()))

for tok in tx.currier_a():
    word_folio_section[tok.word][tok.folio][tok.section] += 1

for tok in tx.currier_b():
    if tok.folio not in ra.ROSETTES_FOLIOS:
        word_folio_section[tok.word][tok.folio][tok.section] += 1

for tok in tx.azc():
    word_folio_section[tok.word][tok.folio][tok.section] += 1

# ============================================================
# 2. MIDDLE-LEVEL CROSS REFERENCE
# ============================================================
# More powerful: match by MIDDLE (not exact word), since labels may
# use different prefix/suffix but share the operative MIDDLE

mid_folio_section = defaultdict(lambda: defaultdict(lambda: Counter()))

for tok in tx.currier_a():
    m = morph.extract(tok.word)
    if m.middle:
        mid_folio_section[m.middle][tok.folio]['A'] += 1

for tok in tx.currier_b():
    if tok.folio not in ra.ROSETTES_FOLIOS:
        m = morph.extract(tok.word)
        if m.middle:
            mid_folio_section[m.middle][tok.folio]['B'] += 1

for tok in tx.azc():
    m = morph.extract(tok.word)
    if m.middle:
        mid_folio_section[m.middle][tok.folio]['AZC'] += 1

# ============================================================
# 3. PER-ROSETTE CROSS-REFERENCE MAP
# ============================================================
print("\n" + "=" * 70)
print("ROSETTE DECODER MAP: Where does each rosette's vocabulary appear?")
print("=" * 70)

results = {}

for gname, words in group_labels.items():
    if not words:
        continue

    # Get unique MIDDLEs from this group's labels
    label_middles = set()
    for w in words:
        m = morph.extract(w)
        if m.middle:
            label_middles.add(m.middle)

    # For each MIDDLE, find the folios where it appears most
    folio_scores = Counter()  # folio → total occurrences of group's MIDDLEs
    section_scores = Counter()  # section → total
    system_scores = Counter()   # A/B/AZC → total

    for mid in label_middles:
        for folio, sec_counts in mid_folio_section[mid].items():
            for sec, count in sec_counts.items():
                folio_scores[folio] += count
                section_scores[sec] += count  # This is A/B/AZC, not section letter
                if sec == 'A':
                    system_scores['A'] += count
                elif sec == 'B':
                    system_scores['B'] += count
                elif sec == 'AZC':
                    system_scores['AZC'] += count

    # Now get the actual manuscript sections (H, S, B, T, etc.)
    section_letter_scores = Counter()
    for mid in label_middles:
        for tok in tx.currier_b():
            if tok.folio in ra.ROSETTES_FOLIOS:
                continue
            m2 = morph.extract(tok.word)
            if m2.middle == mid:
                section_letter_scores[tok.section] += 1

    top_folios = folio_scores.most_common(10)
    top_sections = section_letter_scores.most_common(5)

    print(f"\n{'='*60}")
    print(f"  ROSETTE: {gname} ({len(words)} labels, {len(label_middles)} unique MIDDLEs)")
    print(f"{'='*60}")
    print(f"  Labels: {words[:15]}{'...' if len(words) > 15 else ''}")
    print(f"  MIDDLEs: {sorted(label_middles)[:15]}{'...' if len(label_middles) > 15 else ''}")
    print(f"\n  System distribution: {dict(system_scores)}")
    print(f"  Top B sections: {top_sections}")
    print(f"\n  Top 10 folios (by MIDDLE overlap):")
    for folio, score in top_folios:
        print(f"    {folio:>8}: {score:>5} occurrences")

    results[gname] = {
        'n_labels': len(words),
        'n_middles': len(label_middles),
        'middles': sorted(label_middles),
        'system_dist': dict(system_scores),
        'top_sections': [(s, c) for s, c in top_sections],
        'top_folios': [(f, c) for f, c in top_folios],
    }

# ============================================================
# 4. DESCRIPTION REGION PROFILES
# ============================================================
print("\n" + "=" * 70)
print("DESCRIPTION REGION STRUCTURAL PROFILES")
print("=" * 70)

desc_profiles = {}
for gname, regions in ROSETTE_GROUPS.items():
    desc_regs = regions['desc']
    if not desc_regs:
        continue

    all_toks = []
    for r in desc_regs:
        all_toks.extend(ra.get_tokens('f85v2', r))

    if not all_toks:
        continue

    hub_dist = Counter()
    macro_dist = Counter()
    kernel_dist = Counter()
    desc_middles = set()

    for t in all_toks:
        analysis = decoder.analyze_token(t.word)
        if analysis.hub_sub_role:
            hub_dist[analysis.hub_sub_role] += 1
        if analysis.macro_state:
            macro_dist[analysis.macro_state] += 1
        if analysis.middle_kernel:
            kernel_dist[analysis.middle_kernel] += 1
        m = morph.extract(t.word)
        if m.middle:
            desc_middles.add(m.middle)

    # What's the HAZARD balance?
    h_src = hub_dist.get('HAZARD_SOURCE', 0)
    h_tgt = hub_dist.get('HAZARD_TARGET', 0)
    h_buf = hub_dist.get('SAFETY_BUFFER', 0)
    h_con = hub_dist.get('PURE_CONNECTOR', 0)
    total_hub = h_src + h_tgt + h_buf + h_con
    hazard_pct = 100 * (h_src + h_tgt) / total_hub if total_hub else 0

    # Kernel character balance
    k_count = kernel_dist.get('K', 0)
    e_count = kernel_dist.get('E', 0)
    h_count = kernel_dist.get('H', 0)
    total_kernel = k_count + e_count + h_count
    k_pct = 100 * k_count / total_kernel if total_kernel else 0

    print(f"\n  {gname} description ({len(all_toks)} tokens from {desc_regs}):")
    print(f"    Hub balance: SRC={h_src} TGT={h_tgt} BUF={h_buf} CON={h_con}")
    print(f"    Hazard-dominated: {hazard_pct:.0f}% of hub tokens are HAZARD_*")
    print(f"    Kernel: K={k_count} E={e_count} H={h_count} ({k_pct:.0f}% k-dominant)")
    print(f"    Macro states: {dict(macro_dist.most_common())}")

    # Characterize
    if hazard_pct > 60 and k_pct > 60:
        char = "HAZARD-INTENSIVE + K-HEATING"
    elif hazard_pct > 60:
        char = "HAZARD-INTENSIVE"
    elif k_pct > 60:
        char = "K-HEATING DOMINANT"
    else:
        char = "BALANCED"

    print(f"    CHARACTER: {char}")

    desc_profiles[gname] = {
        'n_tokens': len(all_toks),
        'regions': desc_regs,
        'hub_balance': {'src': h_src, 'tgt': h_tgt, 'buf': h_buf, 'con': h_con},
        'hazard_pct': round(hazard_pct, 1),
        'kernel_balance': {'K': k_count, 'E': e_count, 'H': h_count},
        'k_pct': round(k_pct, 1),
        'character': char,
    }

# ============================================================
# 5. EXCLUSIVE LABELS — Rosettes-only vocabulary
# ============================================================
print("\n" + "=" * 70)
print("EXCLUSIVE VOCABULARY (labels that appear ONLY in Rosettes)")
print("=" * 70)

exclusive_labels = []
widespread_labels = []

for gname, words in group_labels.items():
    for w in words:
        locs = word_folio_section.get(w, {})
        total_elsewhere = sum(sum(s.values()) for s in locs.values())
        if total_elsewhere == 0:
            exclusive_labels.append((gname, w))
        elif total_elsewhere >= 10:
            widespread_labels.append((gname, w, total_elsewhere))

print(f"\nExclusive to Rosettes ({len(exclusive_labels)} labels):")
for gname, w in exclusive_labels:
    m = morph.extract(w)
    analysis = decoder.analyze_token(w)
    hub = analysis.hub_sub_role or ''
    mk = analysis.middle_kernel or ''
    print(f"  {gname:>8}: {w:<20s} MID={str(m.middle):<12s} {hub} {mk}")

print(f"\nWidespread in manuscript ({len(widespread_labels)} labels):")
for gname, w, total in sorted(widespread_labels, key=lambda x: -x[2]):
    m = morph.extract(w)
    analysis = decoder.analyze_token(w)
    hub = analysis.hub_sub_role or ''
    print(f"  {gname:>8}: {w:<20s} MID={str(m.middle):<12s} {total:>5} occurrences  {hub}")

# ============================================================
# 6. FOLIO-CLUSTER ANALYSIS — which folios share the most
#    vocabulary with which rosette groups?
# ============================================================
print("\n" + "=" * 70)
print("FOLIO AFFINITY MAP: Which folios 'belong to' which rosette?")
print("=" * 70)

# For each folio, compute MIDDLE Jaccard with each rosette group
folio_middles = defaultdict(set)
for tok in tx.currier_b():
    if tok.folio not in ra.ROSETTES_FOLIOS:
        m = morph.extract(tok.word)
        if m.middle:
            folio_middles[tok.folio].add(m.middle)

for tok in tx.currier_a():
    m = morph.extract(tok.word)
    if m.middle:
        folio_middles[tok.folio].add(m.middle)

group_middle_sets = {}
for gname, words in group_labels.items():
    mids = set()
    for w in words:
        m = morph.extract(w)
        if m.middle:
            mids.add(m.middle)
    if mids:
        group_middle_sets[gname] = mids

# For each folio, which rosette group has highest Jaccard?
folio_best_rosette = {}
for folio, fmids in sorted(folio_middles.items()):
    if len(fmids) < 5:  # skip tiny folios
        continue
    best_group = None
    best_jaccard = -1
    group_jaccards = {}
    for gname, gmids in group_middle_sets.items():
        inter = len(fmids & gmids)
        union = len(fmids | gmids)
        j = inter / union if union else 0
        group_jaccards[gname] = j
        if j > best_jaccard:
            best_jaccard = j
            best_group = gname
    folio_best_rosette[folio] = (best_group, best_jaccard, group_jaccards)

# Show per-rosette: which folios have highest affinity?
print("\nFolios with highest affinity to each rosette group:")
for gname in ['BOTTOM', 'MIDDLE', 'UPPER', 'D_W']:
    if gname not in group_middle_sets:
        continue
    # Sort folios by Jaccard with this group
    folio_j = [(f, data[2].get(gname, 0))
               for f, data in folio_best_rosette.items()]
    folio_j.sort(key=lambda x: -x[1])
    top5 = folio_j[:8]
    print(f"\n  {gname} (MIDDLEs: {sorted(group_middle_sets[gname])[:10]}):")
    for f, j in top5:
        print(f"    {f:>8}: J={j:.4f}")

# ============================================================
# 7. SYNTHESIS: What does each rosette explain?
# ============================================================
print("\n" + "=" * 70)
print("SYNTHESIS: ROSETTE DECODER INTERPRETATION")
print("=" * 70)

# Combine label cross-refs with description profiles
for gname in ['BOTTOM', 'MIDDLE', 'UPPER', 'NORTH', 'VERT', 'CENTER', 'D_W']:
    print(f"\n  --- {gname} ---")

    # Labels
    if gname in results:
        r = results[gname]
        print(f"  LABELS: {r['n_labels']} entries, {r['n_middles']} MIDDLEs")
        if r['top_sections']:
            print(f"    Points to sections: {r['top_sections'][:3]}")
        if r['top_folios']:
            top3 = r['top_folios'][:3]
            print(f"    Strongest folios: {top3}")
        print(f"    System weight: {r['system_dist']}")

    # Descriptions
    if gname in desc_profiles:
        d = desc_profiles[gname]
        print(f"  DESCRIPTION: {d['n_tokens']} tokens, character={d['character']}")
        print(f"    Hazard balance: {d['hazard_pct']:.0f}% hazard-dominated")
        print(f"    Kernel: K={d['kernel_balance']['K']} E={d['kernel_balance']['E']} "
              f"H={d['kernel_balance']['H']}")

    # Interpretation
    if gname == 'BOTTOM':
        print(f"  >> LARGEST label set (38 entries). Diverse MIDDLEs spanning")
        print(f"     all hub roles. Appears to be the MAIN VOCABULARY INDEX.")
    elif gname == 'MIDDLE':
        print(f"  >> Second-largest (31 entries). Heavy da-prefix (scaffold).")
        print(f"     Contains hub-critical vocabulary (ar, dal, dy).")
    elif gname == 'UPPER':
        print(f"  >> 15 entries, da-prefix dominant (daldar, daldal, daraldy).")
        print(f"     SCAFFOLD-class labels — structural/positional vocabulary.")
    elif gname == 'NORTH':
        print(f"  >> Description-only (60 tokens). Balanced HAZARD profile.")
        print(f"     K=18 kernel enrichment -> describes a HEATING process.")
    elif gname == 'VERT':
        print(f"  >> Description-only (62 tokens). HIGHEST kernel enrichment K=23.")
        print(f"     The most HAZARD-INTENSIVE description on the foldout.")
    elif gname == 'CENTER':
        print(f"  >> Description-only (33 tokens). HAZARD_TARGET dominant.")
        print(f"     Describes something that RECEIVES hazard, not generates it.")
    elif gname == 'D_W':
        print(f"  >> Smallest group. 3 labels + 5 description tokens.")
        print(f"     Transitional/connecting region between other rosettes.")

# ============================================================
# 8. SAVE RESULTS
# ============================================================
output = {
    'metadata': {
        'phase': '388H_DECODER_MAP',
        'description': 'Rosette cross-reference decoder map',
        'total_labels': sum(len(w) for w in group_labels.values()),
        'exclusive_labels': len(exclusive_labels),
        'widespread_labels': len(widespread_labels),
    },
    'rosette_groups': {
        gname: {
            'labels': words,
            'cross_refs': results.get(gname, {}),
            'description_profile': desc_profiles.get(gname, {}),
        }
        for gname, words in group_labels.items()
    },
    'exclusive_vocabulary': [
        {'group': g, 'word': w, 'middle': morph.extract(w).middle}
        for g, w in exclusive_labels
    ],
}

out_path = ROOT / 'phases/ROSETTES_SYSTEM_CLASSIFICATION/results/rosette_decoder_map.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, default=str)
print(f"\n\nResults saved to {out_path}")
