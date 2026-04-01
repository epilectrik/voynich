#!/usr/bin/env python3
"""
s4_a_record_decode.py — Decode individual Currier A records at atom level.

Selects 5 records per cluster (20 total), shows full atom glosses for every
token, then synthesizes cross-cluster patterns.

Phase: CURRIER_A_ATOMS / Script 4
"""

import sys
import os
import json
from collections import Counter, defaultdict

# Windows stdout encoding fix
sys.stdout.reconfigure(encoding='utf-8')

# Run from repo root
os.chdir(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, '.')

from scripts.voynich import Transcript, Morphology

# ---------------------------------------------------------------------------
# Data setup
# ---------------------------------------------------------------------------
tx = Transcript()
morph = Morphology()

# Collect Currier A tokens into records keyed by (folio, line)
records_raw = defaultdict(list)  # (folio, line) -> [Token, ...]

for token in tx.currier_a(h_only=True, exclude_labels=True, exclude_uncertain=True):
    if not token.word.strip():
        continue
    records_raw[(token.folio, token.line)].append(token)

print(f"Loaded {sum(len(v) for v in records_raw.values())} tokens in {len(records_raw)} records")

# ---------------------------------------------------------------------------
# Cluster definitions
# ---------------------------------------------------------------------------
CLUSTERS = {
    1: {
        'name': 'Thermal/Pharma',
        'folios': ['f87r','f87v','f88v','f89r1','f89r2','f89v1','f89v2',
                   'f90r2','f90v1','f90v2','f93v','f96v','f99r','f99v',
                   'f101r1','f101v2','f102r1','f102r2','f102v1','f102v2',
                   'f27r','f51r','f51v','f52v','f53v','f58r','f58v']
    },
    2: {
        'name': 'Arrangement',
        'folios': ['f100r','f100v','f17r','f1v','f24r','f24v','f3r','f3v',
                   'f45v','f52r','f53r','f54r','f6v','f88r','f90r1','f93r','f96r']
    },
    3: {
        'name': 'Stripped-down Herbal',
        'folios': ['f1r','f2r','f2v','f4r','f5v','f6r','f8r','f8v','f9r','f9v',
                   'f10v','f11r','f13v','f15r','f15v','f17v','f18r','f20v','f22r',
                   'f22v','f23r','f23v','f25r','f25v','f28v','f29v','f32r','f32v',
                   'f35r','f35v','f36r','f36v','f37r','f37v','f38r','f38v','f42r',
                   'f44v','f45r','f47r','f54v']
    },
    4: {
        'name': 'Closure-heavy Herbal',
        'folios': ['f10r','f11v','f13r','f14r','f14v','f16r','f16v','f18v',
                   'f19r','f19v','f20r','f21r','f21v','f27v','f28r','f29r',
                   'f30r','f30v','f42v','f44r','f47v','f49r','f49v','f4v',
                   'f56r','f56v','f5r','f7r','f7v']
    }
}

# Build folio -> cluster mapping
folio_to_cluster = {}
for cid, cinfo in CLUSTERS.items():
    for f in cinfo['folios']:
        folio_to_cluster[f] = cid

# ---------------------------------------------------------------------------
# Select 5 records per cluster (mid-length: 5-9 tokens, different folios)
# ---------------------------------------------------------------------------
def select_records(cluster_id, cluster_info, n=5):
    """Select n records from different folios with 5-9 tokens."""
    folios = set(cluster_info['folios'])
    candidates = []
    for (folio, line), toks in records_raw.items():
        if folio in folios:
            n_tok = len(toks)
            if 5 <= n_tok <= 9:
                candidates.append((folio, line, n_tok))

    # Sort for reproducibility
    candidates.sort(key=lambda x: (x[0], x[1]))

    # Pick from different folios
    selected = []
    used_folios = set()
    for folio, line, n_tok in candidates:
        if folio not in used_folios:
            selected.append((folio, line, n_tok))
            used_folios.add(folio)
            if len(selected) >= n:
                break

    # If not enough different folios, allow repeats
    if len(selected) < n:
        for folio, line, n_tok in candidates:
            key = (folio, line)
            if key not in [(s[0], s[1]) for s in selected]:
                selected.append((folio, line, n_tok))
                if len(selected) >= n:
                    break

    return selected


def decode_record(folio, line):
    """Decode all tokens in a record, returning structured data."""
    toks = records_raw.get((folio, line), [])
    tokens = []
    for i, tok in enumerate(toks):
        word = tok.word
        a = morph.atomize(word)
        m = morph.extract(word)
        atom_details = []
        for char, role, gloss_word in a.atoms:
            atom_details.append({
                'char': char,
                'role': role,
                'gloss': gloss_word
            })
        tokens.append({
            'position': i + 1,
            'word': word,
            'prefix': a.prefix,
            'articulator': a.articulator,
            'atoms': atom_details,
            'atom_display': ' '.join(
                f"{ad['char']}({ad['role']}:{ad['gloss']})"
                if ad['role'] != ad['gloss']
                else f"{ad['char']}({ad['role']})"
                for ad in atom_details
            ),
            'gloss': a.gloss,
            'e_depth': a.e_depth,
            'i_depth': a.i_depth,
            'terminal_opacity': a.terminal_opacity,
            'is_headless': a.is_headless,
            'head': a.head,
            'middle': m.middle if m else None,
            'suffix': m.suffix if m else None,
        })
    return tokens


def print_record(folio, line, cluster_id, cluster_name, tokens):
    """Pretty-print a decoded record."""
    print(f"\n{'='*80}")
    print(f"  RECORD: {folio} / line {line}  |  Cluster {cluster_id} ({cluster_name})  |  {len(tokens)} tokens")
    print(f"{'='*80}")

    heads = []
    prefixes = []
    opacities = []

    for t in tokens:
        pos_label = f"  [{t['position']:>2}]"
        art_str = f"[{t['articulator']}]+" if t['articulator'] else ""
        pfx_str = f"{t['prefix']}" if t['prefix'] else "(none)"

        headless_tag = "  HEADLESS" if t['is_headless'] else ""
        print(f"{pos_label}  {t['word']:<16s}  PREFIX={art_str}{pfx_str:<8s}{headless_tag}")
        print(f"        Atoms: {t['atom_display']}")
        print(f"        Gloss: {t['gloss']:<40s}  e={t['e_depth']}  opacity={t['terminal_opacity']}")

        heads.append(t['head'] if t['head'] else '?')
        prefixes.append(t['prefix'] if t['prefix'] else '-')
        opacities.append(t['terminal_opacity'][0] if t['terminal_opacity'] else '?')

    # Record gloss
    gloss_chain = ' -> '.join(t['gloss'] for t in tokens)
    print(f"\n  RECORD GLOSS: {gloss_chain}")

    # Summary
    head_seq = ' '.join(heads)
    pfx_seq = ' '.join(prefixes)
    opacity_seq = ' '.join(opacities)
    print(f"  HEAD sequence:    {head_seq}")
    print(f"  PREFIX sequence:  {pfx_seq}")
    print(f"  Opacity trajectory: {opacity_seq}")

    # Check o->HL pattern
    o_count = heads.count('o')
    has_o_dominance = o_count >= len(heads) * 0.4
    print(f"  o-HEAD count: {o_count}/{len(heads)} {'(o-dominant)' if has_o_dominance else ''}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
all_records = []  # For JSON output
all_prefix_seqs = {}  # cluster -> list of prefix sequences

print("=" * 80)
print("  CURRIER A RECORD DECODE -- Atom-Level Analysis")
print("  20 records (5 per cluster), full atom decomposition")
print("=" * 80)

for cid in sorted(CLUSTERS.keys()):
    cinfo = CLUSTERS[cid]
    print(f"\n\n{'#'*80}")
    print(f"#  CLUSTER {cid}: {cinfo['name']}")
    print(f"#  Folios: {len(cinfo['folios'])}")
    print(f"{'#'*80}")

    selected = select_records(cid, cinfo)
    all_prefix_seqs[cid] = []

    for folio, line, n_tok in selected:
        tokens = decode_record(folio, line)
        print_record(folio, line, cid, cinfo['name'], tokens)

        pfx_seq = [t['prefix'] if t['prefix'] else '-' for t in tokens]
        all_prefix_seqs[cid].append({
            'folio': folio, 'line': line, 'prefix_seq': pfx_seq
        })

        all_records.append({
            'cluster_id': cid,
            'cluster_name': cinfo['name'],
            'folio': folio,
            'line': line,
            'n_tokens': len(tokens),
            'tokens': tokens,
            'record_gloss': ' -> '.join(t['gloss'] for t in tokens),
            'head_sequence': [t['head'] if t['head'] else '?' for t in tokens],
            'prefix_sequence': pfx_seq,
            'opacity_sequence': [t['terminal_opacity'] for t in tokens],
        })


# ---------------------------------------------------------------------------
# SYNTHESIS
# ---------------------------------------------------------------------------
print(f"\n\n{'='*80}")
print("  SYNTHESIS")
print(f"{'='*80}")

# 1. Cluster "feel" comparison
print("\n--- Cluster Character ---\n")
for cid in sorted(CLUSTERS.keys()):
    recs = [r for r in all_records if r['cluster_id'] == cid]
    all_heads = []
    all_pfxs = []
    all_opacities = []
    all_e = []
    headless_count = 0
    total_tokens = 0

    for r in recs:
        for t in r['tokens']:
            all_heads.append(t['head'] if t['head'] else '?')
            all_pfxs.append(t['prefix'] if t['prefix'] else '-')
            all_opacities.append(t['terminal_opacity'])
            all_e.append(t['e_depth'])
            if t['is_headless']:
                headless_count += 1
            total_tokens += 1

    head_counts = Counter(all_heads)
    pfx_counts = Counter(all_pfxs)
    opacity_counts = Counter(all_opacities)
    avg_e = sum(all_e) / len(all_e) if all_e else 0

    print(f"  Cluster {cid} ({CLUSTERS[cid]['name']}):")
    print(f"    Tokens sampled: {total_tokens}")
    print(f"    HEAD distribution: {dict(head_counts.most_common())}")
    print(f"    PREFIX distribution: {dict(pfx_counts.most_common())}")
    print(f"    Opacity distribution: {dict(opacity_counts.most_common())}")
    print(f"    Mean e-depth: {avg_e:.2f}")
    print(f"    Headless tokens: {headless_count}/{total_tokens}")
    print()

# 2. Repeating sub-patterns (2-token and 3-token word sequences)
print("\n--- Repeating Sub-Patterns (by cluster) ---\n")
for cid in sorted(CLUSTERS.keys()):
    recs = [r for r in all_records if r['cluster_id'] == cid]
    bigrams = []
    trigrams = []
    for r in recs:
        words = [t['word'] for t in r['tokens']]
        for i in range(len(words) - 1):
            bigrams.append(f"{words[i]} {words[i+1]}")
        for i in range(len(words) - 2):
            trigrams.append(f"{words[i]} {words[i+1]} {words[i+2]}")

    print(f"  Cluster {cid} ({CLUSTERS[cid]['name']}):")
    bi_counts = Counter(bigrams)
    tri_counts = Counter(trigrams)
    common_bi = [(k, v) for k, v in bi_counts.most_common(5) if v > 1]
    common_tri = [(k, v) for k, v in tri_counts.most_common(5) if v > 1]
    if common_bi:
        print(f"    Repeated bigrams: {common_bi}")
    else:
        print(f"    Repeated bigrams: none (all unique in 5-record sample)")
    if common_tri:
        print(f"    Repeated trigrams: {common_tri}")
    else:
        print(f"    Repeated trigrams: none")
    print(f"    All bigrams ({len(bigrams)}): {bi_counts.most_common(8)}")
    print()

# 3. Cross-cluster repeated bigrams
print("\n--- Cross-Cluster Repeating Bigrams ---\n")
all_bigrams = []
for r in all_records:
    words = [t['word'] for t in r['tokens']]
    for i in range(len(words) - 1):
        all_bigrams.append(f"{words[i]} {words[i+1]}")
cross_bi = Counter(all_bigrams)
repeated_cross = [(k, v) for k, v in cross_bi.most_common(15) if v > 1]
if repeated_cross:
    for bg, ct in repeated_cross:
        print(f"    {bg} (x{ct})")
else:
    print("    No repeated bigrams across all 20 records")

# 4. PREFIX sequences
print(f"\n\n--- PREFIX Sequences by Cluster ---\n")
for cid in sorted(CLUSTERS.keys()):
    print(f"  Cluster {cid} ({CLUSTERS[cid]['name']}):")
    for ps in all_prefix_seqs[cid]:
        seq_str = ' -> '.join(ps['prefix_seq'])
        print(f"    {ps['folio']:>8s} L{ps['line']}: {seq_str}")
    print()

# Cluster-level prefix signature by position
print("--- Cluster PREFIX Signatures (by token position) ---\n")
for cid in sorted(CLUSTERS.keys()):
    recs = [r for r in all_records if r['cluster_id'] == cid]
    pfx_position = defaultdict(lambda: Counter())
    for r in recs:
        for t in r['tokens']:
            pos = t['position']
            pfx = t['prefix'] if t['prefix'] else '-'
            pfx_position[pos][pfx] += 1

    print(f"  Cluster {cid} ({CLUSTERS[cid]['name']}):")
    for pos in sorted(pfx_position.keys()):
        top = pfx_position[pos].most_common(3)
        top_str = ', '.join(f"{p}({c})" for p, c in top)
        print(f"    Position {pos}: {top_str}")
    print()

# 5. Cluster-feel observations
print("\n--- Cluster Feel Observations ---\n")
for cid in sorted(CLUSTERS.keys()):
    recs = [r for r in all_records if r['cluster_id'] == cid]
    all_heads = []
    all_e = []
    all_opacities = []
    all_pfxs = []
    headless_pct = 0
    total = 0
    for r in recs:
        for t in r['tokens']:
            all_heads.append(t['head'] if t['head'] else '?')
            all_e.append(t['e_depth'])
            all_opacities.append(t['terminal_opacity'])
            all_pfxs.append(t['prefix'] if t['prefix'] else '-')
            if t['is_headless']:
                headless_pct += 1
            total += 1

    head_c = Counter(all_heads)
    pfx_c = Counter(all_pfxs)
    opacity_c = Counter(all_opacities)
    avg_e = sum(all_e) / total if total else 0
    o_pct = head_c.get('o', 0) / total * 100 if total else 0
    k_pct = head_c.get('k', 0) / total * 100 if total else 0
    opaque_pct = opacity_c.get('OPAQUE', 0) / total * 100 if total else 0

    name = CLUSTERS[cid]['name']
    print(f"  Cluster {cid} ({name}):")
    print(f"    o-HEAD: {o_pct:.0f}%  k-HEAD: {k_pct:.0f}%  avg e-depth: {avg_e:.2f}  OPAQUE: {opaque_pct:.0f}%")

    if cid == 1:
        note = ("    -> Thermal/Pharma: " +
                ("HIGH e-depth suggests thermal layering (balneum mariae). " if avg_e > 0.5 else "Moderate e-depth. ") +
                ("k-HEAD presence suggests heat processes. " if k_pct > 15 else "") +
                "Look for sustained modification chains.")
    elif cid == 2:
        note = ("    -> Arrangement: Look for structural/organizational patterns. " +
                "PREFIX variety may indicate diverse operational modes.")
    elif cid == 3:
        note = ("    -> Stripped-down Herbal: " +
                ("Low e-depth consistent with simple/bare substance entries. " if avg_e < 0.6 else "Higher e-depth than expected. ") +
                ("High opacity suggests closed/definite items." if opaque_pct > 60 else ""))
    elif cid == 4:
        note = ("    -> Closure-heavy Herbal: " +
                ("High opacity confirms closure emphasis. " if opaque_pct > 60 else "") +
                "Compare with Cluster 3 for herbal sub-differentiation.")

    print(note)
    print()

# 6. Do records within a cluster share structural patterns?
print("\n--- Intra-Cluster Structural Similarity ---\n")
for cid in sorted(CLUSTERS.keys()):
    recs = [r for r in all_records if r['cluster_id'] == cid]
    head_seqs = [' '.join(r['head_sequence']) for r in recs]
    pfx_seqs = [' '.join(r['prefix_sequence']) for r in recs]

    # Check head pattern similarity
    head_patterns = Counter(head_seqs)
    print(f"  Cluster {cid} ({CLUSTERS[cid]['name']}):")
    print(f"    HEAD sequence patterns ({len(set(head_seqs))} unique / {len(head_seqs)} records):")
    for seq in head_seqs:
        print(f"      {seq}")

    # Check if o appears in same positions across records
    o_positions = []
    for r in recs:
        opos = [i+1 for i, h in enumerate(r['head_sequence']) if h == 'o']
        o_positions.append(opos)
    print(f"    o-HEAD positions: {o_positions}")
    print()


# ---------------------------------------------------------------------------
# Save JSON
# ---------------------------------------------------------------------------
output = {
    'description': 'Currier A record-level atom decode, 5 records per cluster',
    'n_records': len(all_records),
    'records': all_records,
    'cluster_summaries': {}
}

for cid in sorted(CLUSTERS.keys()):
    recs = [r for r in all_records if r['cluster_id'] == cid]
    heads = []
    pfxs = []
    e_depths = []
    for r in recs:
        for t in r['tokens']:
            heads.append(t['head'] if t['head'] else '?')
            pfxs.append(t['prefix'] if t['prefix'] else '-')
            e_depths.append(t['e_depth'])
    output['cluster_summaries'][cid] = {
        'name': CLUSTERS[cid]['name'],
        'n_records': len(recs),
        'head_distribution': dict(Counter(heads)),
        'prefix_distribution': dict(Counter(pfxs)),
        'mean_e_depth': sum(e_depths) / len(e_depths) if e_depths else 0,
    }

out_path = 'phases/CURRIER_A_ATOMS/results/s4_a_record_decode.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\nJSON saved to {out_path}")
print(f"Total records decoded: {len(all_records)}")
print("Done.")
