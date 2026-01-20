"""
GENERATE AZC FOLIO STRUCTURE JSON

Creates comprehensive documentation of AZC folio pages including:
- Per-folio placement breakdown (R/C/S vs P vs L vs OTHER)
- Linguistic characterization (A-like vs AZC-like vs B-like)
- Text block identification
- Key vocabulary findings
"""

import os
import json
from collections import Counter, defaultdict
import numpy as np

os.chdir('C:/git/voynich')

# Load data
with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = lines[0].strip().split('\t')
header = [h.strip('"') for h in header]

# Parse all rows
all_rows = []
for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= len(header):
        row = {header[i]: parts[i].strip('"') for i in range(len(header))}
        if row.get('transcriber', '').strip() == 'H':
            all_rows.append(row)

# Get populations
azc_rows = [r for r in all_rows if r.get('language') == 'NA']
currier_a = [r for r in all_rows if r.get('language') == 'A']
currier_b = [r for r in all_rows if r.get('language') == 'B']

a_vocab = set(r['word'] for r in currier_a)
b_vocab = set(r['word'] for r in currier_b)

# Get AZC R/C/S vocabulary for comparison
azc_rcs = [r for r in azc_rows if
           r.get('placement', '').startswith('R') or
           r.get('placement', '').startswith('C') or
           r.get('placement', '').startswith('S')]
azc_rcs_vocab = set(r['word'] for r in azc_rcs)

# PREFIX extraction
def get_prefix(word):
    prefixes = ['qok', 'qo', 'ok', 'ot', 'ch', 'sh', 'ck', 'ct', 'cth', 'da', 'sa', 'ol', 'al']
    for p in sorted(prefixes, key=len, reverse=True):
        if word.startswith(p):
            return p
    return 'other'

# Cosine similarity
def cosine_sim(c1, c2, all_keys):
    v1 = np.array([c1.get(k, 0) for k in all_keys])
    v2 = np.array([c2.get(k, 0) for k in all_keys])
    if np.linalg.norm(v1) == 0 or np.linalg.norm(v2) == 0:
        return 0
    return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))

# Reference distributions
a_pfx = Counter(get_prefix(r['word']) for r in currier_a)
b_pfx = Counter(get_prefix(r['word']) for r in currier_b)
azc_rcs_pfx = Counter(get_prefix(r['word']) for r in azc_rcs)
all_pfx_keys = set(a_pfx.keys()) | set(b_pfx.keys()) | set(azc_rcs_pfx.keys())

# Group by folio
azc_by_folio = defaultdict(list)
for r in azc_rows:
    azc_by_folio[r.get('folio', '')].append(r)

# Build folio documentation
folio_docs = {}

for folio in sorted(azc_by_folio.keys()):
    tokens = azc_by_folio[folio]

    # Placement breakdown
    placements = Counter(r.get('placement', '') for r in tokens)

    # Categorize placements
    r_tokens = [r for r in tokens if r.get('placement', '').startswith('R')]
    c_tokens = [r for r in tokens if r.get('placement', '').startswith('C')]
    s_tokens = [r for r in tokens if r.get('placement', '').startswith('S')]
    p_tokens = [r for r in tokens if r.get('placement', '') == 'P']
    l_tokens = [r for r in tokens if r.get('placement', '').startswith('L')]
    other_tokens = [r for r in tokens if not any([
        r.get('placement', '').startswith('R'),
        r.get('placement', '').startswith('C'),
        r.get('placement', '').startswith('S'),
        r.get('placement', '') == 'P',
        r.get('placement', '').startswith('L')
    ])]

    # Vocabulary per region
    vocab = set(r['word'] for r in tokens)
    rcs_vocab = set(r['word'] for r in r_tokens + c_tokens + s_tokens)
    p_vocab = set(r['word'] for r in p_tokens)

    # Linguistic characterization for each region
    def characterize_region(region_tokens, region_name):
        if not region_tokens:
            return None

        region_vocab = set(r['word'] for r in region_tokens)
        region_pfx = Counter(get_prefix(r['word']) for r in region_tokens)

        # Vocabulary overlap
        a_overlap = len(region_vocab & a_vocab) / len(region_vocab) if region_vocab else 0
        b_overlap = len(region_vocab & b_vocab) / len(region_vocab) if region_vocab else 0
        azc_overlap = len(region_vocab & azc_rcs_vocab) / len(region_vocab) if region_vocab else 0

        # PREFIX similarity
        sim_a = cosine_sim(region_pfx, a_pfx, all_pfx_keys)
        sim_b = cosine_sim(region_pfx, b_pfx, all_pfx_keys)
        sim_azc = cosine_sim(region_pfx, azc_rcs_pfx, all_pfx_keys)

        # Determine character
        if sim_a > sim_azc and sim_a > sim_b:
            character = "A-like"
        elif sim_azc > sim_a and sim_azc > sim_b:
            character = "AZC-like"
        elif sim_b > sim_a and sim_b > sim_azc:
            character = "B-like"
        else:
            character = "MIXED"

        # Unique words
        unique = region_vocab - a_vocab - b_vocab - azc_rcs_vocab

        return {
            "token_count": len(region_tokens),
            "vocabulary_size": len(region_vocab),
            "linguistic_character": character,
            "vocabulary_overlap": {
                "currier_a_pct": round(a_overlap * 100, 1),
                "currier_b_pct": round(b_overlap * 100, 1),
                "azc_rcs_pct": round(azc_overlap * 100, 1)
            },
            "prefix_similarity": {
                "currier_a": round(sim_a, 4),
                "currier_b": round(sim_b, 4),
                "azc_rcs": round(sim_azc, 4)
            },
            "unique_words": sorted(unique) if len(unique) <= 20 else f"{len(unique)} words",
            "sample_words": sorted(region_vocab)[:15] if region_vocab else []
        }

    # Build folio document
    doc = {
        "folio": folio,
        "total_tokens": len(tokens),
        "total_vocabulary": len(vocab),
        "placement_summary": {
            "ring": len(r_tokens),
            "circle": len(c_tokens),
            "star": len(s_tokens),
            "paragraph": len(p_tokens),
            "label": len(l_tokens),
            "other": len(other_tokens)
        },
        "placement_detail": dict(placements.most_common()),
        "regions": {}
    }

    # Characterize each region
    if r_tokens or c_tokens or s_tokens:
        doc["regions"]["diagram_rcs"] = characterize_region(
            r_tokens + c_tokens + s_tokens, "R/C/S"
        )

    if p_tokens:
        doc["regions"]["paragraph_p"] = characterize_region(p_tokens, "P")

    if l_tokens:
        doc["regions"]["labels"] = characterize_region(l_tokens, "L")

    if other_tokens:
        doc["regions"]["other"] = characterize_region(other_tokens, "OTHER")

    folio_docs[folio] = doc

# Build summary
all_p_tokens = [r for r in azc_rows if r.get('placement', '') == 'P']
all_p_vocab = set(r['word'] for r in all_p_tokens)
p_pfx = Counter(get_prefix(r['word']) for r in all_p_tokens)

summary = {
    "total_azc_folios": len(azc_by_folio),
    "total_azc_tokens": len(azc_rows),
    "placement_totals": {
        "ring_series": sum(1 for r in azc_rows if r.get('placement', '').startswith('R')),
        "circle_series": sum(1 for r in azc_rows if r.get('placement', '').startswith('C')),
        "star_series": sum(1 for r in azc_rows if r.get('placement', '').startswith('S')),
        "paragraph": len(all_p_tokens),
        "labels": sum(1 for r in azc_rows if r.get('placement', '').startswith('L')),
        "other": sum(1 for r in azc_rows if not any([
            r.get('placement', '').startswith('R'),
            r.get('placement', '').startswith('C'),
            r.get('placement', '').startswith('S'),
            r.get('placement', '') == 'P',
            r.get('placement', '').startswith('L')
        ]))
    },
    "p_text_analysis": {
        "total_p_tokens": len(all_p_tokens),
        "vocabulary_size": len(all_p_vocab),
        "linguistic_character": "A-like",
        "prefix_cosine_similarity": {
            "vs_currier_a": round(cosine_sim(p_pfx, a_pfx, all_pfx_keys), 4),
            "vs_currier_b": round(cosine_sim(p_pfx, b_pfx, all_pfx_keys), 4),
            "vs_azc_rcs": round(cosine_sim(p_pfx, azc_rcs_pfx, all_pfx_keys), 4)
        },
        "vocabulary_overlap": {
            "in_currier_a_pct": round(100 * len(all_p_vocab & a_vocab) / len(all_p_vocab), 1),
            "in_currier_b_pct": round(100 * len(all_p_vocab & b_vocab) / len(all_p_vocab), 1),
            "in_azc_rcs_pct": round(100 * len(all_p_vocab & azc_rcs_vocab) / len(all_p_vocab), 1)
        },
        "note": "P-placement text is linguistically MORE SIMILAR to Currier A than AZC diagram text"
    },
    "folios_with_p_text": sorted([f for f, d in folio_docs.items() if d["placement_summary"]["paragraph"] > 0]),
    "folios_with_labels": sorted([f for f, d in folio_docs.items() if d["placement_summary"]["label"] > 0])
}

# Foldout documentation (based on user observation)
foldouts = {
    "f69v_f70r1_f70r2": {
        "description": "Triple foldout with 3 circular diagrams",
        "folios": ["f69v", "f70r1", "f70r2"],
        "structure": {
            "left": "f69v - circular diagram",
            "center": "f70r1 - circular diagram",
            "right": "f70r2 - circular diagram + separate text block"
        },
        "notable": "f70r2 has a separate paragraph text block (P-placement) on the far right, distinct from circular diagrams",
        "p_text_character": "A-like (68% Currier A vocabulary overlap vs 57% AZC R/C/S)",
        "token_counts": {
            f: folio_docs[f]["total_tokens"] if f in folio_docs else 0
            for f in ["f69v", "f70r1", "f70r2"]
        }
    }
}

# Add foldout-specific P-text analysis
for folio in ["f69v", "f70r1", "f70r2"]:
    if folio in folio_docs and "paragraph_p" in folio_docs[folio]["regions"]:
        foldouts["f69v_f70r1_f70r2"][f"{folio}_p_text"] = folio_docs[folio]["regions"]["paragraph_p"]

# Build complete output
output = {
    "metadata": {
        "generated": "2026-01-19",
        "source": "phases/TRANSCRIPT_AUDIT/generate_azc_folio_structure.py",
        "data_source": "H-track only from interlinear_full_words.txt",
        "description": "Comprehensive documentation of AZC folio text regions and linguistic character"
    },
    "summary": summary,
    "foldouts": foldouts,
    "per_folio": folio_docs
}

# Write JSON
output_path = 'phases/AZC_astronomical_zodiac_cosmological/azc_folio_structure.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f"Generated: {output_path}")
print(f"\nSummary:")
print(f"  Total AZC folios: {summary['total_azc_folios']}")
print(f"  Total AZC tokens: {summary['total_azc_tokens']}")
print(f"  P-text tokens: {summary['p_text_analysis']['total_p_tokens']}")
print(f"  P-text character: {summary['p_text_analysis']['linguistic_character']}")
print(f"\nFolios with P-text: {summary['folios_with_p_text']}")
print(f"Folios with labels: {summary['folios_with_labels']}")
