"""
Verify that human-track tokens truly avoid hazard zones.
Previous test found only hazard tokens near hazards (artifacts).
"""

from collections import Counter, defaultdict
from pathlib import Path

project_root = Path(__file__).parent.parent.parent

# ALL hazard tokens (including single chars and variants)
ALL_HAZARD_TOKENS = {
    # PHASE_ORDERING
    'shey', 'aiin', 'al', 'c', 'chol', 'r', 'chedy', 'ee', 'chey', 'l',
    # COMPOSITION_JUMP
    'dy', 'or', 'dal', 'ar',
    # RATE_MISMATCH
    'dar', 'qokaiin',
    # CONTAINMENT_TIMING
    'qo', 'shy', 'ok', 'shol', 'ol', 'shor',
    # ENERGY_OVERSHOOT
    'qokedy',
    # Variants
    "q'o", 'q"o',
}

# High-frequency tokens that are definitely NOT human-track
DEFINITELY_OPERATIONAL = {
    'daiin', 'chedy', 'ol', 'shedy', 'aiin', 'chol', 'chey', 'or', 'dar',
    'qokaiin', 'qokeedy', 'ar', 'qokedy', 'qokeey', 'dy', 'shey', 'dal',
    'okaiin', 'qokain', 'cheey', 'qokal', 'sho', 'cho', 'chy', 'shy',
    'al', 'ol', 'or', 'ar', 'qo', 'ok', 'ot', 'od', 'oe', 'oy',
    'chol', 'chor', 'char', 'shor', 'shal', 'shol', 's', 'o', 'd', 'y',
    'a', 'e', 'l', 'r', 'k', 'h', 'c', 't', 'n', 'p', 'm', 'g', 'f',
    'dain', 'chain', 'shain', 'ain', 'in', 'an', 'dan',
}


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
                # H-only transcriber filter (CRITICAL: avoids 3.2x token inflation)
                transcriber = parts[12].strip('"').strip() if len(parts) > 12 else ''
                if transcriber != 'H':
                    continue
                folio_id = parts[0].split('.')[0] if '.' in parts[0] else parts[0]
                raw_tokens = parts[1].split() if len(parts) > 1 else []
                tokens = [t.strip('"') for t in raw_tokens if t.strip('"')]  # filter empty
                folios[folio_id].extend(tokens)
    return folios


def is_true_human_track(token, token_counts, total_tokens):
    """Strict human-track identification."""
    # Exclude empty/short tokens
    if len(token) < 2:
        return False

    # Exclude hazard tokens and variants
    if token in ALL_HAZARD_TOKENS:
        return False

    # Exclude high-frequency operational tokens
    if token in DEFINITELY_OPERATIONAL:
        return False

    # Exclude very high frequency (top operational layer)
    freq = token_counts.get(token, 0) / total_tokens
    if freq > 0.005:  # Stricter threshold
        return False

    return True


def main():
    print("Verifying Human-Track Absence Near Hazards")
    print("=" * 60)

    folios = load_transcription()

    # Build token counts
    token_counts = Counter()
    total_tokens = 0
    for tokens in folios.values():
        for t in tokens:
            token_counts[t] += 1
            total_tokens += 1

    print(f"Total tokens: {total_tokens}")
    print(f"Unique tokens: {len(token_counts)}")

    # Find TRUE human-track tokens within distance 1-3 of hazard tokens
    true_ht_near_hazards = []

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
                        if is_true_human_track(neighbor, token_counts, total_tokens):
                            true_ht_near_hazards.append((neighbor, offset, token, folio_id))

    print(f"\n{'='*60}")
    print(f"TRUE Human-Track Tokens Near Hazards: {len(true_ht_near_hazards)}")
    print(f"{'='*60}")

    if true_ht_near_hazards:
        print("\nTokens found:")
        ht_counts = Counter(t for t, _, _, _ in true_ht_near_hazards)
        for token, count in ht_counts.most_common(20):
            freq = token_counts[token]
            print(f"  {token}: {count}x near hazards (corpus freq: {freq})")

        print("\nSample contexts:")
        for token, offset, hazard, folio in true_ht_near_hazards[:10]:
            pos = "before" if offset < 0 else "after"
            print(f"  {token} appears {abs(offset)} {pos} '{hazard}' in {folio}")
    else:
        print("\n** NO TRUE HUMAN-TRACK TOKENS FOUND NEAR HAZARDS **")

    # Compare to random baseline
    print(f"\n{'='*60}")
    print("BASELINE: HT tokens near random positions")
    print(f"{'='*60}")

    # Sample random positions and count HT nearby
    import random
    random.seed(42)

    all_tokens_flat = []
    for tokens in folios.values():
        all_tokens_flat.extend(tokens)

    random_positions = random.sample(range(len(all_tokens_flat)), min(1000, len(all_tokens_flat)))

    ht_near_random = 0
    for i in random_positions:
        for offset in range(-3, 4):
            if offset == 0:
                continue
            j = i + offset
            if 0 <= j < len(all_tokens_flat):
                neighbor = all_tokens_flat[j]
                if is_true_human_track(neighbor, token_counts, total_tokens):
                    ht_near_random += 1

    # How many hazard positions did we check?
    hazard_positions = sum(1 for tokens in folios.values() for t in tokens if t in ALL_HAZARD_TOKENS)

    print(f"Hazard positions checked: {hazard_positions}")
    print(f"Random positions checked: {len(random_positions)}")
    print(f"HT found near hazards: {len(true_ht_near_hazards)}")
    print(f"HT found near random: {ht_near_random}")

    hazard_rate = len(true_ht_near_hazards) / hazard_positions if hazard_positions else 0
    random_rate = ht_near_random / len(random_positions) if random_positions else 0

    print(f"\nHT rate near hazards: {hazard_rate:.4f}")
    print(f"HT rate near random: {random_rate:.4f}")
    print(f"Ratio (random/hazard): {random_rate/hazard_rate:.1f}x" if hazard_rate > 0 else "Hazard rate = 0")

    print(f"\n{'='*60}")
    print("CONCLUSION")
    print(f"{'='*60}")

    if len(true_ht_near_hazards) == 0:
        print("""
** HUMAN-TRACK TOKENS COMPLETELY AVOID HAZARD ZONES **

This STRONGLY supports the attentional pacing model:
- Near hazards, attention is demanded
- Operator stops scribbling entirely
- The "sparse HT" from earlier tests were artifacts (hazard tokens near each other)

The SID-05 "suppression near hazards" is not suppression - it's ABSENCE.
Operators don't write simpler marks near hazards; they write NOTHING.
""")
    elif hazard_rate < random_rate * 0.5:
        print(f"""
Human-track tokens are {random_rate/hazard_rate:.1f}x LESS common near hazards than random.
Strong avoidance confirmed.
""")
    else:
        print(f"""
Some human-track tokens found near hazards.
These may be warning markers or special-purpose tokens.
""")


if __name__ == '__main__':
    main()
