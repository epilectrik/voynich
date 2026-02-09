"""
07_pp_triangulation.py

PP Triangulation Test

Proper methodology:
- A record = PARAGRAPH (not line)
- Initial RI = ID (material identification)
- Final RI = output
- PP tokens in between = processing pipeline

This test triangulates Brunschwig materials by matching PP token patterns
against Brunschwig instruction sequences.
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology

# Paths
results_dir = Path(__file__).parent.parent / "results"
para_results = Path(__file__).parent.parent.parent / "PARAGRAPH_INTERNAL_PROFILING" / "results"
class_results = Path(__file__).parent.parent.parent / "CLASS_COSURVIVAL_TEST" / "results"

print("="*70)
print("PP TRIANGULATION TEST")
print("="*70)
print("\nMethodology: Match PP token patterns against Brunschwig instructions")

# Load data
print("\nLoading data...")

# A paragraph tokens
with open(para_results / "a_paragraph_tokens.json", encoding='utf-8') as f:
    para_tokens = json.load(f)
print(f"  A paragraphs: {len(para_tokens)}")

# A paragraph profiles (has RI/PP classification)
with open(para_results / "a_paragraph_profiles.json", encoding='utf-8') as f:
    para_profiles = json.load(f)
profiles_by_id = {p['par_id']: p for p in para_profiles['profiles']}
print(f"  Profiles: {len(profiles_by_id)}")

# Token class map (for role assignment)
with open(class_results / "class_token_map.json", encoding='utf-8') as f:
    class_map = json.load(f)
token_to_class = class_map.get('token_to_class', {})
token_to_role = class_map.get('token_to_role', {})
print(f"  Classified tokens: {len(token_to_class)}")

# Brunschwig signatures
with open(results_dir / "brunschwig_signatures.json", encoding='utf-8') as f:
    sig_data = json.load(f)
signatures = sig_data['signatures']
print(f"  Brunschwig recipes: {len(signatures)}")

# Load B folio MIDDLEs for PP identification
# CRITICAL: We need to compare MIDDLEs, not full words
tx = Transcript()
morph = Morphology()

b_middles = set()
for token in tx.currier_b():
    if '*' not in token.word and token.word.strip():
        try:
            m = morph.extract(token.word)
            if m.middle:
                b_middles.add(m.middle)
        except:
            pass
print(f"  B MIDDLE vocabulary: {len(b_middles)} types")

# Classify paragraph tokens as RI vs PP
print("\n" + "="*70)
print("CLASSIFYING PARAGRAPH TOKENS")
print("="*70)

def classify_paragraph_tokens(para_id, tokens):
    """
    Classify tokens in a paragraph by MIDDLE:
    - PP MIDDLEs: appear in B vocabulary (pipeline)
    - RI MIDDLEs: A-specific (identification)

    CRITICAL: Classification is by MIDDLE, not full word.
    e.g., okeoschso has prefix='ok', middle='eoschso'
    If 'eoschso' is A-exclusive, it's RI even though 'ok' appears in B.

    Returns dict with:
    - initial_ri: first RI MIDDLE(s) - the ID
    - final_ri: last RI MIDDLE(s) - the output
    - pp_middles: middle PP MIDDLEs - the processing
    """
    words = [t['word'] for t in tokens]

    # Extract MIDDLEs and classify
    classified = []
    for i, word in enumerate(words):
        try:
            m = morph.extract(word)
            middle = m.middle if m.middle else word  # fallback to word if no MIDDLE
        except:
            middle = word

        is_pp = middle in b_middles
        classified.append({
            'word': word,
            'middle': middle,
            'position': i,
            'is_pp': is_pp,
            'is_ri': not is_pp,
        })

    # Find initial RI (first RI MIDDLEs at start)
    initial_ri = []
    initial_ri_words = []
    for c in classified:
        if c['is_ri']:
            initial_ri.append(c['middle'])
            initial_ri_words.append(c['word'])
        else:
            break  # Stop at first PP

    # Find final RI (last RI MIDDLEs at end)
    final_ri = []
    final_ri_words = []
    for c in reversed(classified):
        if c['is_ri']:
            final_ri.insert(0, c['middle'])
            final_ri_words.insert(0, c['word'])
        else:
            break

    # PP MIDDLEs are everything classified as PP
    pp_middles = [c['middle'] for c in classified if c['is_pp']]
    pp_words = [c['word'] for c in classified if c['is_pp']]

    return {
        'para_id': para_id,
        'total_tokens': len(words),
        'initial_ri': initial_ri,
        'initial_ri_words': initial_ri_words,
        'final_ri': final_ri,
        'final_ri_words': final_ri_words,
        'pp_middles': pp_middles,
        'pp_words': pp_words,
        'ri_count': len([c for c in classified if c['is_ri']]),
        'pp_count': len(pp_middles),
    }

# Classify all paragraphs
classified_paragraphs = []
for para_id, tokens in para_tokens.items():
    classified = classify_paragraph_tokens(para_id, tokens)
    classified_paragraphs.append(classified)

# Summary
print(f"\nClassified {len(classified_paragraphs)} paragraphs")

ri_counts = [p['ri_count'] for p in classified_paragraphs]
pp_counts = [p['pp_count'] for p in classified_paragraphs]

print(f"  Mean RI per paragraph: {np.mean(ri_counts):.1f}")
print(f"  Mean PP per paragraph: {np.mean(pp_counts):.1f}")

# Compute PP role profiles
print("\n" + "="*70)
print("COMPUTING PP ROLE PROFILES")
print("="*70)

# Role mapping from token class
def get_token_role(token):
    """Get role (EN/FL/FQ/CC/AX) for a token."""
    return token_to_role.get(token, 'UNKNOWN')

def compute_pp_role_profile(pp_tokens):
    """Compute role distribution for PP tokens."""
    roles = Counter()
    for token in pp_tokens:
        role = get_token_role(token)
        roles[role] += 1

    total = len(pp_tokens)
    if total == 0:
        return {}

    # Map full role names to short codes
    role_map = {
        'ENERGY_OPERATOR': 'EN',
        'FLOW_OPERATOR': 'FL',
        'FREQUENT_OPERATOR': 'FQ',
        'CORE_CONTROL': 'CC',
        'AUXILIARY': 'AX',
    }

    # Normalize to short codes
    normalized = Counter()
    for role, count in roles.items():
        short = role_map.get(role, 'UNKNOWN')
        normalized[short] += count

    return {
        'EN': normalized.get('EN', 0) / total,
        'FL': normalized.get('FL', 0) / total,
        'FQ': normalized.get('FQ', 0) / total,
        'CC': normalized.get('CC', 0) / total,
        'AX': normalized.get('AX', 0) / total,
        'UNKNOWN': normalized.get('UNKNOWN', 0) / total,
        'total': total,
        'raw_counts': dict(normalized),
    }

# Add role profiles to paragraphs
for para in classified_paragraphs:
    para['pp_role_profile'] = compute_pp_role_profile(para['pp_middles'])

# Show examples
print("\nExample paragraphs with PP profiles:")
for para in classified_paragraphs[:5]:
    if para['pp_count'] > 0 and para['initial_ri']:
        print(f"\n{para['para_id']}:")
        print(f"  Initial RI (ID): {para['initial_ri'][:3]}")
        print(f"  Final RI (output): {para['final_ri'][:3] if para['final_ri'] else 'none'}")
        print(f"  PP tokens: {para['pp_count']}")
        rp = para['pp_role_profile']
        print(f"  PP roles: EN={rp.get('EN',0):.2f}, FL={rp.get('FL',0):.2f}, "
              f"FQ={rp.get('FQ',0):.2f}, CC={rp.get('CC',0):.2f}")

# Match PP profiles against Brunschwig instruction patterns
print("\n" + "="*70)
print("MATCHING PP PROFILES TO BRUNSCHWIG INSTRUCTIONS")
print("="*70)

# Brunschwig instruction pattern predictions
# Based on procedural_steps -> role mapping
BRUNSCHWIG_PATTERNS = {
    'hen (chicken)': {
        'expected_roles': {'CC': 0.28, 'AX': 0.28, 'EN': 0.28, 'FQ': 0.14},
        'signature': 'ESCAPE+AUX dominant',
        'fire_degree': 1,
    },
    'ox blood water': {
        'expected_roles': {'AX': 0.33, 'CC': 0.33, 'FQ': 0.33},
        'signature': 'AUX+CC+FQ balanced',
        'fire_degree': 2,
    },
    'earthworm water': {
        'expected_roles': {'FL': 0.33, 'AX': 0.33, 'FQ': 0.33},
        'signature': 'FLOW+AUX dominant',
        'fire_degree': 1,
    },
    'standard herb': {
        'expected_roles': {'CC': 0.33, 'EN': 0.33, 'FQ': 0.33},
        'signature': 'GATHER+CHOP+DISTILL',
        'fire_degree': 2,
    },
}

def cosine_similarity(vec1, vec2, keys):
    """Compute cosine similarity."""
    v1 = np.array([vec1.get(k, 0) for k in keys])
    v2 = np.array([vec2.get(k, 0) for k in keys])
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(np.dot(v1, v2) / (norm1 * norm2))

def match_pp_to_brunschwig(pp_role_profile, min_pp=5):
    """Match PP role profile against Brunschwig patterns."""
    if pp_role_profile.get('total', 0) < min_pp:
        return None

    roles = ['EN', 'FL', 'FQ', 'CC', 'AX']
    matches = []

    for material, pattern in BRUNSCHWIG_PATTERNS.items():
        similarity = cosine_similarity(pp_role_profile, pattern['expected_roles'], roles)
        matches.append({
            'material': material,
            'similarity': similarity,
            'fire_degree': pattern['fire_degree'],
            'signature': pattern['signature'],
        })

    return sorted(matches, key=lambda x: -x['similarity'])

# Match all paragraphs
print("\nMatching paragraphs to Brunschwig materials...")

matched_paragraphs = []
for para in classified_paragraphs:
    if para['pp_count'] >= 5 and para['initial_ri']:
        matches = match_pp_to_brunschwig(para['pp_role_profile'])
        if matches and matches[0]['similarity'] > 0.5:
            para['brunschwig_matches'] = matches[:3]
            matched_paragraphs.append(para)

print(f"Paragraphs with strong matches: {len(matched_paragraphs)}")

# Show top matches
print("\n" + "="*70)
print("TOP PP TRIANGULATION MATCHES")
print("="*70)

# Sort by best match similarity
matched_paragraphs.sort(key=lambda x: -x['brunschwig_matches'][0]['similarity'])

for para in matched_paragraphs[:20]:
    best = para['brunschwig_matches'][0]
    initial_ri = ', '.join(para['initial_ri'][:2])
    print(f"\n{para['para_id']}: Initial RI = {initial_ri}")
    print(f"  PP tokens: {para['pp_count']}")
    print(f"  Best match: {best['material']} (similarity: {best['similarity']:.3f})")
    print(f"  Pattern: {best['signature']}")

# Aggregate by material
print("\n" + "="*70)
print("MATCHES BY BRUNSCHWIG MATERIAL")
print("="*70)

matches_by_material = defaultdict(list)
for para in matched_paragraphs:
    best = para['brunschwig_matches'][0]
    matches_by_material[best['material']].append({
        'para_id': para['para_id'],
        'initial_ri': para['initial_ri'],
        'similarity': best['similarity'],
    })

for material, matches in sorted(matches_by_material.items(), key=lambda x: -len(x[1])):
    print(f"\n{material}: {len(matches)} paragraphs")
    for m in sorted(matches, key=lambda x: -x['similarity'])[:5]:
        ri = ', '.join(m['initial_ri'][:2])
        print(f"    {m['para_id']}: {ri} ({m['similarity']:.3f})")

# Cross-reference with known eoschso=chicken
print("\n" + "="*70)
print("CROSS-VALIDATION: eoschso=chicken")
print("="*70)

# Note: eoschso is the MIDDLE of token 'okeoschso' in f90r1:6
# We need to find paragraphs containing this MIDDLE

eoschso_paras = [p for p in matched_paragraphs if 'eoschso' in p['initial_ri']]

if eoschso_paras:
    print(f"\nParagraphs with eoschso as initial RI MIDDLE: {len(eoschso_paras)}")
    for para in eoschso_paras:
        best = para['brunschwig_matches'][0]
        print(f"  {para['para_id']}: best match = {best['material']} ({best['similarity']:.3f})")
        print(f"    Full word: {para.get('initial_ri_words', [])}")
        if best['material'] == 'hen (chicken)':
            print("    ^ VALIDATES known mapping!")
else:
    # Search all paragraphs for eoschso in any position
    all_eoschso = []
    for p in classified_paragraphs:
        if 'eoschso' in p['initial_ri']:
            all_eoschso.append(('initial_ri', p))
        elif 'eoschso' in p.get('final_ri', []):
            all_eoschso.append(('final_ri', p))
        elif 'eoschso' in p.get('pp_middles', []):
            all_eoschso.append(('pp_middle', p))

    if all_eoschso:
        print(f"\nParagraphs containing eoschso: {len(all_eoschso)}")
        for position, para in all_eoschso:
            print(f"  {para['para_id']}: eoschso in {position}")
            if position == 'initial_ri':
                print(f"    Word: {para.get('initial_ri_words', [])}")
            elif position == 'final_ri':
                print(f"    Word: {para.get('final_ri_words', [])}")
    else:
        print("\neoschso MIDDLE not found in any paragraph")
        print("Searching transcript directly...")

        # Direct search
        for para_id, tokens in para_tokens.items():
            for t in tokens:
                try:
                    m = morph.extract(t['word'])
                    if m.middle == 'eoschso':
                        print(f"  Found in {para_id}: word={t['word']}, middle=eoschso")
                except:
                    pass

# Summary statistics
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print(f"\nTotal A paragraphs: {len(classified_paragraphs)}")
print(f"Paragraphs with PP >= 5: {len([p for p in classified_paragraphs if p['pp_count'] >= 5])}")
print(f"Paragraphs with strong matches: {len(matched_paragraphs)}")

# Role distribution across all PP
all_pp_roles = Counter()
for para in classified_paragraphs:
    for count, role in [(v, k) for k, v in para['pp_role_profile'].get('raw_counts', {}).items()]:
        all_pp_roles[role] += count

print(f"\nAggregate PP role distribution:")
total_roles = sum(all_pp_roles.values())
for role, count in all_pp_roles.most_common():
    print(f"  {role}: {count} ({100*count/total_roles:.1f}%)")

# Save results
output = {
    'total_paragraphs': len(classified_paragraphs),
    'paragraphs_with_strong_matches': len(matched_paragraphs),
    'matches_by_material': {
        material: [
            {'para_id': m['para_id'], 'initial_ri': m['initial_ri'], 'similarity': m['similarity']}
            for m in matches[:10]
        ]
        for material, matches in matches_by_material.items()
    },
    'top_matches': [
        {
            'para_id': p['para_id'],
            'initial_ri': p['initial_ri'],
            'final_ri': p['final_ri'],
            'pp_count': p['pp_count'],
            'best_material': p['brunschwig_matches'][0]['material'],
            'similarity': p['brunschwig_matches'][0]['similarity'],
        }
        for p in matched_paragraphs[:50]
    ],
    'pp_role_distribution': dict(all_pp_roles),
}

output_path = results_dir / "pp_triangulation.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
print(f"\nSaved to {output_path}")
