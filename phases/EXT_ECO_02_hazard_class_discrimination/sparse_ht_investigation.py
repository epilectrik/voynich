"""
Investigate the sparse human-track tokens found near hazard zones.

If HT = attentional pacing (scribbling during waiting), why ANY near hazards?
Possibilities:
1. Noise (random)
2. Warning markers ("danger here")
3. Transition markers (boundary of hazard zone)
4. Recovery markers (after navigating hazard)
5. Different function entirely

Tests:
1. What ARE these tokens? List them.
2. Do they repeat? (deliberate vs random)
3. Are they morphologically distinctive?
4. Do they appear BEFORE or AFTER hazard tokens?
5. Do they match the IMD "high hazard" tokens?
"""

from collections import Counter, defaultdict
from pathlib import Path

project_root = Path(__file__).parent.parent.parent

# Hazard tokens
BATCH_HAZARD_TOKENS = {
    'shey', 'aiin', 'al', 'c', 'chol', 'r', 'chedy', 'ee', 'chey', 'l',
    'dy', 'or', 'dal', 'ar', 'dar', 'qokaiin',
}

APPARATUS_HAZARD_TOKENS = {
    'qo', 'shy', 'ok', 'shol', 'ol', 'shor', 'qokedy',
}

ALL_HAZARD_TOKENS = BATCH_HAZARD_TOKENS | APPARATUS_HAZARD_TOKENS

# High-frequency operational tokens
OPERATIONAL_TOKENS = {
    'daiin', 'chedy', 'ol', 'shedy', 'aiin', 'chol', 'chey', 'or', 'dar',
    'qokaiin', 'qokeedy', 'ar', 'qokedy', 'qokeey', 'dy', 'shey', 'dal',
    'okaiin', 'qokain', 'cheey', 'qokal', 'sho', 'cho', 'chy', 'shy',
    'al', 'ol', 'or', 'ar', 'qo', 'ok', 'ot', 'od', 'oe', 'oy',
    'chol', 'chor', 'char', 'shor', 'shal', 'shol',
    'dain', 'chain', 'shain', 'rain', 'kain', 'taiin', 'saiin',
    'chkaiin', 'otaiin', 'oraiin', 'okaiin',
}

# IMD "high hazard" tokens from Phase IMD
IMD_HIGH_HAZARD = {'ckhar', 'cthar', 'daraiin', 'okan', 'cphar', 'sairy', 'kos', 'cfhol', 'ydain', 'shoshy'}


def load_transcription():
    trans_path = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'
    folios = defaultdict(list)
    with open(trans_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split('\t')
            if len(parts) >= 2:
                folio_id = parts[0].split('.')[0] if '.' in parts[0] else parts[0]
                raw_tokens = parts[1].split() if len(parts) > 1 else []
                tokens = [t.strip('"') for t in raw_tokens]
                folios[folio_id].extend(tokens)
    return folios


def is_human_track(token, token_counts, total_tokens):
    if token in OPERATIONAL_TOKENS:
        return False
    freq = token_counts.get(token, 0) / total_tokens
    if freq > 0.001:
        return False
    return True


def main():
    print("Investigating Sparse HT Tokens Near Hazards")
    print("=" * 60)

    folios = load_transcription()

    # Build token counts
    token_counts = Counter()
    total_tokens = 0
    for tokens in folios.values():
        for t in tokens:
            token_counts[t] += 1
            total_tokens += 1

    # Find HT tokens within distance 1-3 of hazard tokens
    ht_near_hazards = []
    ht_positions = []  # (token, position relative to hazard: -3 to +3)

    for folio_id, tokens in folios.items():
        for i, token in enumerate(tokens):
            if token in ALL_HAZARD_TOKENS:
                # Check window around hazard
                for offset in range(-3, 4):
                    if offset == 0:
                        continue
                    j = i + offset
                    if 0 <= j < len(tokens):
                        neighbor = tokens[j]
                        if is_human_track(neighbor, token_counts, total_tokens):
                            ht_near_hazards.append(neighbor)
                            ht_positions.append((neighbor, offset, token))

    print(f"\nTotal HT tokens found near hazards: {len(ht_near_hazards)}")

    # 1. What ARE these tokens?
    print("\n" + "=" * 60)
    print("1. WHAT ARE THESE TOKENS?")
    print("=" * 60)

    ht_counts = Counter(ht_near_hazards)
    print(f"\nUnique tokens: {len(ht_counts)}")
    print("\nAll tokens found (with counts):")
    for token, count in ht_counts.most_common():
        in_imd = "** IMD HIGH HAZARD **" if token in IMD_HIGH_HAZARD else ""
        print(f"  {token}: {count} {in_imd}")

    # 2. Do they repeat?
    print("\n" + "=" * 60)
    print("2. DO THEY REPEAT?")
    print("=" * 60)

    repeating = [t for t, c in ht_counts.items() if c > 1]
    singleton = [t for t, c in ht_counts.items() if c == 1]
    print(f"\nRepeating tokens (count > 1): {len(repeating)}")
    print(f"Singleton tokens (count = 1): {len(singleton)}")
    print(f"Repeat ratio: {len(repeating) / len(ht_counts):.1%}" if ht_counts else "N/A")

    if repeating:
        print("\nRepeating tokens:")
        for t in repeating:
            print(f"  {t}: {ht_counts[t]}x")

    # 3. Morphological analysis
    print("\n" + "=" * 60)
    print("3. MORPHOLOGICAL ANALYSIS")
    print("=" * 60)

    lengths = [len(t) for t in ht_near_hazards]
    avg_length = sum(lengths) / len(lengths) if lengths else 0
    print(f"\nMean length: {avg_length:.2f} chars")

    # Common prefixes/suffixes
    prefixes = Counter(t[:2] for t in ht_near_hazards if len(t) >= 2)
    suffixes = Counter(t[-2:] for t in ht_near_hazards if len(t) >= 2)

    print("\nTop prefixes:")
    for p, c in prefixes.most_common(5):
        print(f"  {p}: {c}")

    print("\nTop suffixes:")
    for s, c in suffixes.most_common(5):
        print(f"  {s}: {c}")

    # 4. Position relative to hazard (before vs after)
    print("\n" + "=" * 60)
    print("4. POSITION RELATIVE TO HAZARD")
    print("=" * 60)

    before = sum(1 for _, offset, _ in ht_positions if offset < 0)
    after = sum(1 for _, offset, _ in ht_positions if offset > 0)

    print(f"\nBefore hazard (offset < 0): {before}")
    print(f"After hazard (offset > 0): {after}")
    print(f"Ratio before/after: {before/after:.2f}" if after > 0 else "N/A")

    # By specific offset
    offset_counts = Counter(offset for _, offset, _ in ht_positions)
    print("\nBy offset:")
    for offset in sorted(offset_counts.keys()):
        label = "before" if offset < 0 else "after"
        print(f"  {offset:+d} ({label}): {offset_counts[offset]}")

    # 5. Match with IMD high-hazard tokens
    print("\n" + "=" * 60)
    print("5. IMD HIGH-HAZARD TOKEN MATCH")
    print("=" * 60)

    imd_matches = [t for t in ht_near_hazards if t in IMD_HIGH_HAZARD]
    print(f"\nTokens matching IMD high-hazard set: {len(imd_matches)}")
    if imd_matches:
        print("Matches:", Counter(imd_matches))

    # Check for partial matches (similar morphology)
    print("\nIMD high-hazard tokens for reference:")
    for t in sorted(IMD_HIGH_HAZARD):
        print(f"  {t}")

    # 6. Which hazard tokens do they appear near?
    print("\n" + "=" * 60)
    print("6. WHICH HAZARDS ARE THEY NEAR?")
    print("=" * 60)

    hazard_neighbors = Counter(h for _, _, h in ht_positions)
    print("\nHazard tokens with HT neighbors:")
    for h, c in hazard_neighbors.most_common(10):
        htype = "BATCH" if h in BATCH_HAZARD_TOKENS else "APPARATUS"
        print(f"  {h} ({htype}): {c}")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    print(f"""
Total sparse HT near hazards: {len(ht_near_hazards)}
Unique tokens: {len(ht_counts)}
Repeating tokens: {len(repeating)} ({len(repeating)/len(ht_counts)*100:.0f}% of unique)
Mean length: {avg_length:.1f} chars
Before/After ratio: {before}/{after} = {before/after:.2f if after else 'N/A'}
IMD matches: {len(imd_matches)}
""")

    # Interpretation
    print("=" * 60)
    print("INTERPRETATION")
    print("=" * 60)

    if len(repeating) > len(singleton) * 0.3:
        print("\n>> SIGNAL: Many tokens repeat - suggests deliberate marking, not random noise")
    else:
        print("\n>> No strong repeat signal - could be random/noise")

    if before > after * 1.5:
        print(">> SIGNAL: More tokens BEFORE hazards - possible WARNING markers")
    elif after > before * 1.5:
        print(">> SIGNAL: More tokens AFTER hazards - possible RECOVERY/COMPLETION markers")
    else:
        print(">> No strong positional bias - distributed around hazards")

    if len(imd_matches) > 0:
        print(f">> SIGNAL: {len(imd_matches)} tokens match IMD high-hazard set - supports warning marker hypothesis")


if __name__ == '__main__':
    main()
