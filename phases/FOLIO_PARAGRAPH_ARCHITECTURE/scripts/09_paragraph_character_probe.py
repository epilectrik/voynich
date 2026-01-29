"""
09_paragraph_character_probe.py - Do paragraphs have distinct operational character?

Questions:
1. Do specific tokens concentrate in early vs late paragraphs?
2. Is there "preparation vocabulary" vs "transformation vocabulary"?
3. Can we predict paragraph ordinal from vocabulary?
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
import statistics

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

# Role classes
CC_CLASSES = {10, 11, 12, 17}
EN_CLASSES = {8, 31, 32, 33, 34, 35, 36, 37, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49}
FL_CLASSES = {7, 30, 38, 40}
FQ_CLASSES = {9, 13, 14, 23}

def get_role(cls):
    if cls in CC_CLASSES: return 'CC'
    if cls in EN_CLASSES: return 'EN'
    if cls in FL_CLASSES: return 'FL'
    if cls in FQ_CLASSES: return 'FQ'
    return 'AX'

def main():
    results_dir = Path(__file__).parent.parent / 'results'

    # Load census
    with open(results_dir / 'folio_paragraph_census.json') as f:
        census = json.load(f)

    # Load paragraph tokens
    par_results = Path(__file__).resolve().parents[2] / 'PARAGRAPH_INTERNAL_PROFILING' / 'results'
    with open(par_results / 'b_paragraph_tokens.json') as f:
        tokens_by_par = json.load(f)

    # Load class map
    class_map_path = Path(__file__).resolve().parents[3] / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(class_map_path) as f:
        raw_map = json.load(f)
    class_map = raw_map.get('token_to_class', raw_map)

    print("=== PARAGRAPH CHARACTER PROBE ===\n")

    # Track token occurrences by normalized ordinal position
    # Normalize: early (1-2), middle (3-5), late (6+)
    token_by_phase = defaultdict(lambda: {'early': 0, 'middle': 0, 'late': 0})
    en_token_by_phase = defaultdict(lambda: {'early': 0, 'middle': 0, 'late': 0})

    # Also track by exact ordinal for finer analysis
    token_by_ordinal = defaultdict(lambda: defaultdict(int))

    # Track total tokens per phase for normalization
    phase_totals = {'early': 0, 'middle': 0, 'late': 0}

    for folio_entry in census['folios']:
        pars = folio_entry['paragraphs']
        n_pars = len(pars)

        for i, par_info in enumerate(pars):
            par_id = par_info['par_id']
            tokens = tokens_by_par.get(par_id, [])

            # Determine phase based on relative position
            if n_pars <= 2:
                # For short folios, just use early/late
                phase = 'early' if i == 0 else 'late'
            else:
                rel_pos = i / (n_pars - 1) if n_pars > 1 else 0
                if rel_pos < 0.33:
                    phase = 'early'
                elif rel_pos < 0.67:
                    phase = 'middle'
                else:
                    phase = 'late'

            ordinal = min(i + 1, 6)  # Cap at 6

            for t in tokens:
                word = t['word']
                if not word or '*' in word:
                    continue

                token_by_phase[word][phase] += 1
                token_by_ordinal[word][ordinal] += 1
                phase_totals[phase] += 1

                # Track EN tokens specifically
                if word in class_map and class_map[word] in EN_CLASSES:
                    en_token_by_phase[word][phase] += 1

    # === 1. FIND PHASE-SPECIFIC TOKENS ===
    print("--- PHASE-SPECIFIC TOKENS ---\n")

    # Calculate enrichment scores
    def phase_enrichment(token_phases, phase, totals):
        """How much more common is this token in this phase vs expected?"""
        token_total = sum(token_phases.values())
        if token_total < 10:  # Need enough data
            return 0
        observed = token_phases[phase] / token_total
        expected = totals[phase] / sum(totals.values())
        return observed / expected if expected > 0 else 0

    early_enriched = []
    late_enriched = []

    for token, phases in token_by_phase.items():
        total = sum(phases.values())
        if total < 15:  # Need sufficient occurrences
            continue

        early_enrich = phase_enrichment(phases, 'early', phase_totals)
        late_enrich = phase_enrichment(phases, 'late', phase_totals)

        if early_enrich > 1.5:
            early_enriched.append((token, early_enrich, total, phases))
        if late_enrich > 1.5:
            late_enriched.append((token, late_enrich, total, phases))

    early_enriched.sort(key=lambda x: x[1], reverse=True)
    late_enriched.sort(key=lambda x: x[1], reverse=True)

    print("EARLY-ENRICHED tokens (>1.5x expected in early paragraphs):")
    for token, enrich, total, phases in early_enriched[:15]:
        role = get_role(class_map.get(token, -1)) if token in class_map else 'HT'
        print(f"  {token:15} {role:4} {enrich:.2f}x  (E:{phases['early']:3} M:{phases['middle']:3} L:{phases['late']:3})")

    print(f"\nLATE-ENRICHED tokens (>1.5x expected in late paragraphs):")
    for token, enrich, total, phases in late_enriched[:15]:
        role = get_role(class_map.get(token, -1)) if token in class_map else 'HT'
        print(f"  {token:15} {role:4} {enrich:.2f}x  (E:{phases['early']:3} M:{phases['middle']:3} L:{phases['late']:3})")

    # === 2. EN TOKEN PHASE ANALYSIS ===
    print("\n--- EN TOKEN PHASE DISTRIBUTION ---\n")

    en_early = []
    en_late = []

    for token, phases in en_token_by_phase.items():
        total = sum(phases.values())
        if total < 10:
            continue

        early_enrich = phase_enrichment(phases, 'early', phase_totals)
        late_enrich = phase_enrichment(phases, 'late', phase_totals)

        if early_enrich > 1.3:
            en_early.append((token, early_enrich, total, phases))
        if late_enrich > 1.3:
            en_late.append((token, late_enrich, total, phases))

    en_early.sort(key=lambda x: x[1], reverse=True)
    en_late.sort(key=lambda x: x[1], reverse=True)

    print("EN tokens enriched in EARLY paragraphs:")
    for token, enrich, total, phases in en_early[:10]:
        cls = class_map.get(token, '?')
        print(f"  {token:15} class={cls:2}  {enrich:.2f}x  (n={total})")

    print(f"\nEN tokens enriched in LATE paragraphs:")
    for token, enrich, total, phases in en_late[:10]:
        cls = class_map.get(token, '?')
        print(f"  {token:15} class={cls:2}  {enrich:.2f}x  (n={total})")

    # === 3. ROLE DISTRIBUTION BY PHASE ===
    print("\n--- ROLE DISTRIBUTION BY PHASE ---\n")

    role_by_phase = defaultdict(lambda: {'early': 0, 'middle': 0, 'late': 0})

    for token, phases in token_by_phase.items():
        if token in class_map:
            role = get_role(class_map[token])
        else:
            role = 'HT'
        for phase, count in phases.items():
            role_by_phase[role][phase] += count

    print(f"{'Role':<6} {'Early':>10} {'Middle':>10} {'Late':>10}")
    for role in ['EN', 'FL', 'FQ', 'CC', 'AX', 'HT']:
        phases = role_by_phase[role]
        total = sum(phases.values())
        if total > 0:
            e = phases['early'] / total
            m = phases['middle'] / total
            l = phases['late'] / total
            print(f"{role:<6} {e:>10.1%} {m:>10.1%} {l:>10.1%}")

    # === 4. ORDINAL SIGNATURE TOKENS ===
    print("\n--- ORDINAL-SPECIFIC TOKENS ---\n")

    # Find tokens that strongly prefer specific ordinal
    ordinal_specific = []

    for token, ordinals in token_by_ordinal.items():
        total = sum(ordinals.values())
        if total < 20:
            continue

        # Find most concentrated ordinal
        max_ord = max(ordinals.keys(), key=lambda o: ordinals[o])
        concentration = ordinals[max_ord] / total

        if concentration > 0.4:  # >40% in one ordinal
            ordinal_specific.append((token, max_ord, concentration, total, dict(ordinals)))

    ordinal_specific.sort(key=lambda x: x[2], reverse=True)

    print("Tokens concentrated in specific ordinal positions (>40%):")
    for token, ord_pos, conc, total, ords in ordinal_specific[:20]:
        role = get_role(class_map.get(token, -1)) if token in class_map else 'HT'
        dist = ' '.join(f"{o}:{c:2}" for o, c in sorted(ords.items()))
        print(f"  {token:15} {role:4} ord={ord_pos} ({conc:.0%})  [{dist}]")

    # === 5. PREDICTABILITY TEST ===
    print("\n--- ORDINAL PREDICTABILITY ---\n")

    # Can we predict ordinal from vocabulary?
    # Simple test: what fraction of tokens are ordinal-specific?

    total_tokens = sum(sum(phases.values()) for phases in token_by_phase.values())
    ordinal_specific_tokens = sum(t[3] for t in ordinal_specific)

    print(f"Total tokens analyzed: {total_tokens}")
    print(f"Tokens with ordinal concentration >40%: {len(ordinal_specific)}")
    print(f"Token occurrences in concentrated patterns: {ordinal_specific_tokens} ({ordinal_specific_tokens/total_tokens:.1%})")

    # === 6. VERDICT ===
    print("\n=== VERDICT ===\n")

    n_early = len(early_enriched)
    n_late = len(late_enriched)
    n_ordinal = len(ordinal_specific)

    if n_early > 20 and n_late > 20:
        print("DISTINCT CHARACTER: Many tokens show phase preference")
        print(f"  {n_early} early-enriched, {n_late} late-enriched tokens")
        verdict = "DISTINCT"
    elif n_early > 10 or n_late > 10:
        print("WEAK CHARACTER: Some tokens show phase preference")
        verdict = "WEAK"
    else:
        print("NO CHARACTER: Tokens distribute evenly across phases")
        verdict = "NONE"

    if n_ordinal > 30:
        print(f"  {n_ordinal} tokens concentrated in specific ordinals")
        print("  --> Paragraphs have POSITIONAL VOCABULARY")
    else:
        print(f"  Only {n_ordinal} tokens show ordinal concentration")
        print("  --> Vocabulary is POSITION-NEUTRAL")

    # Save results
    output = {
        'early_enriched_count': n_early,
        'late_enriched_count': n_late,
        'ordinal_specific_count': n_ordinal,
        'verdict': verdict,
        'early_enriched_tokens': [(t[0], t[1]) for t in early_enriched[:20]],
        'late_enriched_tokens': [(t[0], t[1]) for t in late_enriched[:20]]
    }

    with open(results_dir / 'paragraph_character_probe.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to paragraph_character_probe.json")

if __name__ == '__main__':
    main()
