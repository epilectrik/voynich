"""
Channel-Slot Grammar Analysis
==============================
Tests whether the three-slot composition grammar (HEAD/MODIFIER/TERMINAL)
behaves differently across PREFIX channels.

Core question: Does each PREFIX channel emphasize different slots within
compound MIDDLEs, or is the grammar universal?

Analyses:
1. Per-channel atom position profiles
2. Per-channel head-match rate (category prediction)
3. Per-channel k/t role distribution
4. Per-channel modifier effect
5. Cross-channel consistency test (cosine similarity)

References: C1209 (MIDDLE slot syntax), C1210 (slot grammar), C1218/C1219
(PREFIX base-modifier grammar), C1190 (MIDDLE behavioral atomicity),
C1305 (MIDDLE determines category), C1379 (two-level parallel composition)
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from scripts.voynich import Transcript, Morphology
from collections import Counter, defaultdict
import numpy as np
from itertools import combinations
import json

# ============================================================
# CONFIGURATION
# ============================================================

ATOMS = set('abcdefghiklmnoprstxy')

# Slot classification from C1209
SLOT_CLASS = {
    'a': 'HEAD',    'e': 'HEAD',    'o': 'HEAD',    'q': 'HEAD',
    'c': 'MODIFIER', 'i': 'MODIFIER', 'p': 'MODIFIER', 'd': 'MODIFIER',
    'f': 'MODIFIER', 's': 'MODIFIER',
    'n': 'TERMINAL', 'y': 'TERMINAL', 'm': 'TERMINAL', 'r': 'TERMINAL',
    'h': 'TERMINAL', 'l': 'TERMINAL',
    'k': 'FREE',   't': 'FREE',
}

# Category assignment from atom deep dives
ATOM_CAT = {
    'k': 'THERMAL', 'e': 'THERMAL', 'h': 'THERMAL',
    'y': 'THERMAL', 'n': 'THERMAL', 'm': 'THERMAL',
    'a': 'FLOW', 'i': 'FLOW', 't': 'FLOW', 'r': 'FLOW',
    'o': 'STAGING', 'l': 'STAGING', 's': 'STAGING',
    'c': 'MONITORING', 'd': 'MARKING', 'p': 'MARKING', 'f': 'MARKING',
}

MIN_CHANNEL_COMPOUNDS = 50  # Minimum compound tokens per PREFIX channel

# ============================================================
# DATA LOADING
# ============================================================

def load_data():
    """Load Currier B tokens, extract PREFIX and compound MIDDLEs."""
    tx = Transcript()
    morph = Morphology()

    records = []
    for token in tx.currier_b():
        word = token.word
        if not word or not word.strip():
            continue
        if '*' in word:
            continue

        m = morph.extract(word)
        if not m or not m.middle:
            continue

        # Decompose MIDDLE into atoms
        atoms = [ch for ch in m.middle if ch in ATOMS]
        if len(atoms) < 2:
            continue  # Only compound MIDDLEs

        prefix = m.prefix if m.prefix else 'BARE'

        records.append({
            'word': word,
            'prefix': prefix,
            'middle': m.middle,
            'atoms': atoms,
            'suffix': m.suffix,
            'folio': token.folio,
        })

    return records

def cosine_similarity(v1, v2):
    """Compute cosine similarity between two vectors."""
    v1 = np.array(v1, dtype=float)
    v2 = np.array(v2, dtype=float)
    dot = np.dot(v1, v2)
    n1 = np.linalg.norm(v1)
    n2 = np.linalg.norm(v2)
    if n1 == 0 or n2 == 0:
        return 0.0
    return dot / (n1 * n2)

# ============================================================
# ANALYSIS 1: Per-Channel Atom Position Profiles
# ============================================================

def analysis_1(records):
    """For each PREFIX channel, compute mean normalized position of each atom."""
    print("\n" + "=" * 80)
    print("ANALYSIS 1: Per-Channel Atom Position Profiles")
    print("=" * 80)
    print("\nFor each atom, its mean normalized position (0=first, 1=last) within")
    print("compound MIDDLEs, broken down by PREFIX channel.\n")

    # Global atom positions
    global_positions = defaultdict(list)  # atom -> [positions]

    # Per-channel atom positions
    channel_positions = defaultdict(lambda: defaultdict(list))  # prefix -> atom -> [positions]
    channel_counts = Counter()

    for rec in records:
        atoms = rec['atoms']
        n = len(atoms)
        prefix = rec['prefix']
        channel_counts[prefix] += 1

        for i, atom in enumerate(atoms):
            pos = i / (n - 1) if n > 1 else 0.5
            global_positions[atom].append(pos)
            channel_positions[prefix][atom].append(pos)

    # Filter channels by minimum count
    valid_channels = sorted([ch for ch, cnt in channel_counts.items()
                            if cnt >= MIN_CHANNEL_COMPOUNDS])

    print(f"Valid channels (>={MIN_CHANNEL_COMPOUNDS} compound tokens): {len(valid_channels)}")
    print(f"Channel counts:")
    for ch in valid_channels:
        print(f"  {ch:6s}: {channel_counts[ch]:5d} compound tokens")

    # Compute global means
    global_means = {}
    for atom in sorted(ATOMS):
        if global_positions[atom]:
            global_means[atom] = np.mean(global_positions[atom])

    # Print table: atom x channel
    print(f"\n{'Atom':>5s} {'Slot':>10s} {'Global':>7s}", end='')
    for ch in valid_channels:
        print(f" {ch:>7s}", end='')
    print(f"  {'Range':>6s}")
    print("-" * (30 + 8 * len(valid_channels)))

    atom_channel_data = {}  # For later use

    for atom in sorted(global_means.keys(), key=lambda a: global_means[a]):
        slot = SLOT_CLASS.get(atom, '?')
        gm = global_means[atom]
        print(f"  {atom:>3s} {slot:>10s} {gm:7.3f}", end='')

        channel_vals = []
        for ch in valid_channels:
            if channel_positions[ch][atom]:
                val = np.mean(channel_positions[ch][atom])
                n_obs = len(channel_positions[ch][atom])
                channel_vals.append(val)
                if n_obs < 5:
                    print(f" {val:6.3f}*", end='')
                else:
                    print(f" {val:7.3f}", end='')
            else:
                print(f"     -- ", end='')
                channel_vals.append(None)

        # Range across channels
        real_vals = [v for v in channel_vals if v is not None]
        if len(real_vals) >= 2:
            rng = max(real_vals) - min(real_vals)
            print(f"  {rng:6.3f}")
        else:
            print(f"     --")

        atom_channel_data[atom] = {ch: v for ch, v in zip(valid_channels, channel_vals)}

    print("\n* = fewer than 5 observations")

    # Identify atoms with largest cross-channel variation
    print("\n--- Atoms with LARGEST cross-channel position variation ---")
    variations = []
    for atom, ch_data in atom_channel_data.items():
        vals = [v for v in ch_data.values() if v is not None]
        if len(vals) >= 3:
            variations.append((atom, max(vals) - min(vals), np.std(vals)))

    variations.sort(key=lambda x: -x[1])
    for atom, rng, std in variations[:8]:
        slot = SLOT_CLASS.get(atom, '?')
        print(f"  {atom} ({slot:10s}): range={rng:.3f}, std={std:.3f}")

    # Check: do HEAD atoms always stay first?
    print("\n--- HEAD atoms (a,e,o) position by channel ---")
    for atom in ['a', 'e', 'o']:
        if atom in atom_channel_data:
            vals = {ch: v for ch, v in atom_channel_data[atom].items() if v is not None}
            always_first = all(v < 0.4 for v in vals.values())
            print(f"  {atom}: {'ALWAYS HEAD (<0.4)' if always_first else 'VARIES'} "
                  f"range [{min(vals.values()):.3f} - {max(vals.values()):.3f}]")

    # Check: do TERMINAL atoms always stay last?
    print("\n--- TERMINAL atoms (y,n,m,h,l,r) position by channel ---")
    for atom in ['y', 'n', 'm', 'h', 'l', 'r']:
        if atom in atom_channel_data:
            vals = {ch: v for ch, v in atom_channel_data[atom].items() if v is not None}
            always_last = all(v > 0.6 for v in vals.values())
            print(f"  {atom}: {'ALWAYS TERMINAL (>0.6)' if always_last else 'VARIES'} "
                  f"range [{min(vals.values()):.3f} - {max(vals.values()):.3f}]")

    return valid_channels, channel_positions, global_means, atom_channel_data

# ============================================================
# ANALYSIS 2: Per-Channel Head-Match Rate
# ============================================================

def analysis_2(records, valid_channels):
    """For each channel, what % of compounds match HEAD atom's vs TERMINAL atom's category?"""
    print("\n" + "=" * 80)
    print("ANALYSIS 2: Per-Channel Category Match Rate (HEAD vs TERMINAL)")
    print("=" * 80)
    print("\nFor each compound MIDDLE under each PREFIX channel:")
    print("  - Does the compound's dominant category match the FIRST atom's category?")
    print("  - Does it match the LAST atom's category?")
    print("  - Higher head-match = head-initial grammar; higher terminal-match = terminal-driven.\n")

    # We need a way to assign category to compound MIDDLEs
    # Use atom vote: count atoms by category, majority wins

    channel_head_match = defaultdict(list)  # prefix -> [0/1]
    channel_term_match = defaultdict(list)
    channel_modifier_match = defaultdict(list)

    for rec in records:
        prefix = rec['prefix']
        if prefix not in valid_channels:
            continue

        atoms = rec['atoms']
        if len(atoms) < 2:
            continue

        # Compound category by atom vote
        cat_votes = Counter()
        for a in atoms:
            if a in ATOM_CAT:
                cat_votes[ATOM_CAT[a]] += 1

        if not cat_votes:
            continue
        compound_cat = cat_votes.most_common(1)[0][0]

        # HEAD atom category (first atom)
        first_atom = atoms[0]
        first_cat = ATOM_CAT.get(first_atom)

        # TERMINAL atom category (last atom)
        last_atom = atoms[-1]
        last_cat = ATOM_CAT.get(last_atom)

        # MODIFIER atoms (middle positions, if any)
        if len(atoms) >= 3:
            mid_atoms = atoms[1:-1]
            mid_cats = Counter(ATOM_CAT.get(a) for a in mid_atoms if a in ATOM_CAT)
            if mid_cats:
                mid_cat = mid_cats.most_common(1)[0][0]
                channel_modifier_match[prefix].append(1 if mid_cat == compound_cat else 0)

        if first_cat:
            channel_head_match[prefix].append(1 if first_cat == compound_cat else 0)
        if last_cat:
            channel_term_match[prefix].append(1 if last_cat == compound_cat else 0)

    # Print results
    print(f"{'Channel':>8s} {'N':>6s} {'Head%':>7s} {'Term%':>7s} {'Mod%':>7s} "
          f"{'H-T':>6s} {'Dominant':>10s}")
    print("-" * 65)

    global_head = []
    global_term = []

    head_rates = {}
    term_rates = {}

    for ch in valid_channels:
        n = len(channel_head_match[ch])
        head_rate = np.mean(channel_head_match[ch]) * 100 if channel_head_match[ch] else 0
        term_rate = np.mean(channel_term_match[ch]) * 100 if channel_term_match[ch] else 0
        mod_rate = np.mean(channel_modifier_match[ch]) * 100 if channel_modifier_match[ch] else 0
        diff = head_rate - term_rate
        dominant = "HEAD" if diff > 5 else ("TERMINAL" if diff < -5 else "BALANCED")

        print(f"{ch:>8s} {n:>6d} {head_rate:>6.1f}% {term_rate:>6.1f}% {mod_rate:>6.1f}% "
              f"{diff:>+5.1f}% {dominant:>10s}")

        global_head.extend(channel_head_match[ch])
        global_term.extend(channel_term_match[ch])
        head_rates[ch] = head_rate
        term_rates[ch] = term_rate

    print("-" * 65)
    gh = np.mean(global_head) * 100 if global_head else 0
    gt = np.mean(global_term) * 100 if global_term else 0
    print(f"{'GLOBAL':>8s} {len(global_head):>6d} {gh:>6.1f}% {gt:>6.1f}% "
          f"       {gh-gt:>+5.1f}%")

    # Identify channels that diverge from global pattern
    print("\n--- Channels diverging from global head-match rate ---")
    for ch in valid_channels:
        hr = head_rates.get(ch, 0)
        deviation = hr - gh
        if abs(deviation) > 5:
            print(f"  {ch}: head-match {hr:.1f}% (global {gh:.1f}%, delta {deviation:+.1f}%)")

    return head_rates, term_rates

# ============================================================
# ANALYSIS 3: Per-Channel k/t Role Distribution
# ============================================================

def analysis_3(records, valid_channels):
    """For k and t atoms, compute positional distribution (FIRST/MIDDLE/LAST) per channel."""
    print("\n" + "=" * 80)
    print("ANALYSIS 3: Per-Channel k/t FREE Atom Role Distribution")
    print("=" * 80)
    print("\nk and t are FREE atoms that change role by position.")
    print("k-first = actor (heating), k-last = target (being heated)")
    print("t-first = actor (transferring), t-last = target (being transferred)\n")

    for target_atom in ['k', 't']:
        print(f"\n--- {target_atom}-atom positional distribution ---")

        channel_positions = defaultdict(lambda: Counter())  # prefix -> {FIRST, MIDDLE, LAST}

        for rec in records:
            prefix = rec['prefix']
            if prefix not in valid_channels:
                continue

            atoms = rec['atoms']
            n = len(atoms)

            for i, atom in enumerate(atoms):
                if atom != target_atom:
                    continue
                if i == 0:
                    pos = 'FIRST'
                elif i == n - 1:
                    pos = 'LAST'
                else:
                    pos = 'MIDDLE'
                channel_positions[prefix][pos] += 1

        print(f"{'Channel':>8s} {'N':>5s} {'FIRST%':>8s} {'MID%':>8s} {'LAST%':>8s} "
              f"{'F:L ratio':>10s}")
        print("-" * 55)

        global_counts = Counter()

        for ch in valid_channels:
            counts = channel_positions[ch]
            total = sum(counts.values())
            if total < 5:
                continue

            first_pct = counts['FIRST'] / total * 100
            mid_pct = counts['MIDDLE'] / total * 100
            last_pct = counts['LAST'] / total * 100
            fl_ratio = (counts['FIRST'] / counts['LAST']) if counts['LAST'] > 0 else float('inf')

            print(f"{ch:>8s} {total:>5d} {first_pct:>7.1f}% {mid_pct:>7.1f}% {last_pct:>7.1f}% "
                  f"{fl_ratio:>10.2f}")

            global_counts += counts

        total = sum(global_counts.values())
        if total > 0:
            print("-" * 55)
            first_pct = global_counts['FIRST'] / total * 100
            mid_pct = global_counts['MIDDLE'] / total * 100
            last_pct = global_counts['LAST'] / total * 100
            fl_ratio = (global_counts['FIRST'] / global_counts['LAST']) if global_counts['LAST'] > 0 else float('inf')
            print(f"{'GLOBAL':>8s} {total:>5d} {first_pct:>7.1f}% {mid_pct:>7.1f}% {last_pct:>7.1f}% "
                  f"{fl_ratio:>10.2f}")

# ============================================================
# ANALYSIS 4: Per-Channel Modifier Effect
# ============================================================

def analysis_4(records, valid_channels):
    """For modifier atoms (c, s, p, d, f, i), compute frequency by channel."""
    print("\n" + "=" * 80)
    print("ANALYSIS 4: Per-Channel Modifier Frequency")
    print("=" * 80)
    print("\nModifier atoms (c,s,p,d,f,i) shape compound behavior.")
    print("Question: do channels prefer different modifiers?\n")

    modifiers = ['c', 's', 'p', 'd', 'f', 'i']

    # Count modifier occurrences per channel
    channel_mod_counts = defaultdict(Counter)  # prefix -> {modifier: count}
    channel_totals = Counter()  # prefix -> total atoms

    for rec in records:
        prefix = rec['prefix']
        if prefix not in valid_channels:
            continue

        atoms = rec['atoms']
        channel_totals[prefix] += len(atoms)
        for atom in atoms:
            if atom in modifiers:
                channel_mod_counts[prefix][atom] += 1

    # Global rates
    global_mod_counts = Counter()
    global_total = 0
    for ch in valid_channels:
        global_mod_counts += channel_mod_counts[ch]
        global_total += channel_totals[ch]

    global_rates = {m: global_mod_counts[m] / global_total * 100 for m in modifiers}

    # Print table
    print(f"{'Channel':>8s} {'N_atoms':>8s}", end='')
    for m in modifiers:
        print(f" {m:>7s}", end='')
    print(f"  {'Total%':>7s}")
    print("-" * (20 + 8 * len(modifiers) + 10))

    channel_profiles = {}

    for ch in valid_channels:
        total = channel_totals[ch]
        if total < 20:
            continue

        print(f"{ch:>8s} {total:>8d}", end='')
        profile = []
        total_mod = 0
        for m in modifiers:
            rate = channel_mod_counts[ch][m] / total * 100
            enrichment = rate / global_rates[m] if global_rates[m] > 0 else 0
            # Mark enriched (>1.5x) or depleted (<0.5x)
            marker = ''
            if enrichment > 1.5:
                marker = '+'
            elif enrichment < 0.5 and channel_mod_counts[ch][m] > 0:
                marker = '-'
            elif channel_mod_counts[ch][m] == 0:
                marker = '0'
            print(f" {rate:>5.1f}%{marker:1s}", end='')
            profile.append(rate)
            total_mod += rate
        print(f"  {total_mod:>6.1f}%")
        channel_profiles[ch] = profile

    print("-" * (20 + 8 * len(modifiers) + 10))
    print(f"{'GLOBAL':>8s} {global_total:>8d}", end='')
    total_mod = 0
    for m in modifiers:
        print(f" {global_rates[m]:>6.1f}%", end='')
        total_mod += global_rates[m]
    print(f"  {total_mod:>6.1f}%")

    print("\n  + = >1.5x enriched vs global   - = <0.5x depleted   0 = absent")

    # Find most channel-variable modifiers
    print("\n--- Modifier variability across channels ---")
    for m_idx, m in enumerate(modifiers):
        rates = [channel_profiles[ch][m_idx] for ch in channel_profiles if len(channel_profiles[ch]) > m_idx]
        if len(rates) >= 3:
            cv = np.std(rates) / np.mean(rates) if np.mean(rates) > 0 else 0
            print(f"  {m}: mean={np.mean(rates):.2f}%, std={np.std(rates):.2f}%, "
                  f"CV={cv:.2f}, range=[{min(rates):.1f}%-{max(rates):.1f}%]")

    return channel_profiles

# ============================================================
# ANALYSIS 5: Cross-Channel Consistency Test
# ============================================================

def analysis_5(records, valid_channels, global_means):
    """Compute positional profile similarity across channels for each atom."""
    print("\n" + "=" * 80)
    print("ANALYSIS 5: Cross-Channel Consistency Test (Cosine Similarity)")
    print("=" * 80)
    print("\nFor each atom, compute its positional distribution (% FIRST, % MIDDLE, % LAST)")
    print("separately for each PREFIX channel, then measure pairwise cosine similarity.")
    print("High cosine (>0.8) = universal grammar. Low cosine = channel-specific behavior.\n")

    # Build 3-bin positional profiles per atom per channel
    # Bins: FIRST (pos < 0.25), MIDDLE (0.25 <= pos <= 0.75), LAST (pos > 0.75)
    channel_atom_bins = defaultdict(lambda: defaultdict(lambda: [0, 0, 0]))

    for rec in records:
        prefix = rec['prefix']
        if prefix not in valid_channels:
            continue

        atoms = rec['atoms']
        n = len(atoms)

        for i, atom in enumerate(atoms):
            pos = i / (n - 1) if n > 1 else 0.5
            if pos < 0.25:
                bin_idx = 0  # FIRST
            elif pos > 0.75:
                bin_idx = 2  # LAST
            else:
                bin_idx = 1  # MIDDLE
            channel_atom_bins[prefix][atom][bin_idx] += 1

    # For each atom, compute pairwise cosine between channels
    all_atoms = sorted(set(a for ch in valid_channels
                          for a in channel_atom_bins[ch].keys()))

    print(f"{'Atom':>5s} {'Slot':>10s} {'MeanCos':>8s} {'MinCos':>8s} {'MaxCos':>8s} "
          f"{'N_pairs':>8s} {'Verdict':>12s}")
    print("-" * 70)

    atom_consistency = {}

    for atom in all_atoms:
        # Collect profiles from channels with enough data
        profiles = {}
        for ch in valid_channels:
            bins = channel_atom_bins[ch][atom]
            total = sum(bins)
            if total >= 10:  # Need enough observations
                profiles[ch] = [b / total for b in bins]

        if len(profiles) < 3:
            continue

        # Pairwise cosine similarity
        channels_list = sorted(profiles.keys())
        cosines = []
        for i in range(len(channels_list)):
            for j in range(i + 1, len(channels_list)):
                cs = cosine_similarity(profiles[channels_list[i]],
                                      profiles[channels_list[j]])
                cosines.append((channels_list[i], channels_list[j], cs))

        cos_vals = [c[2] for c in cosines]
        mean_cos = np.mean(cos_vals)
        min_cos = min(cos_vals)
        max_cos = max(cos_vals)

        slot = SLOT_CLASS.get(atom, '?')
        verdict = "UNIVERSAL" if min_cos > 0.8 else ("MIXED" if mean_cos > 0.7 else "CHANNEL-SPEC")

        print(f"  {atom:>3s} {slot:>10s} {mean_cos:>8.3f} {min_cos:>8.3f} {max_cos:>8.3f} "
              f"{len(cosines):>8d} {verdict:>12s}")

        atom_consistency[atom] = {
            'mean_cos': mean_cos,
            'min_cos': min_cos,
            'max_cos': max_cos,
            'profiles': profiles,
            'cosines': cosines,
            'verdict': verdict,
        }

    # Show the WORST cosine pairs for channel-specific atoms
    print("\n--- Atoms with CHANNEL-SPECIFIC behavior (mean cosine < 0.8) ---")
    channel_spec_atoms = [(a, d) for a, d in atom_consistency.items()
                          if d['mean_cos'] < 0.8]
    channel_spec_atoms.sort(key=lambda x: x[1]['mean_cos'])

    for atom, data in channel_spec_atoms:
        slot = SLOT_CLASS.get(atom, '?')
        print(f"\n  {atom} ({slot}): mean cosine = {data['mean_cos']:.3f}")

        # Show the profile for each channel
        print(f"    {'Channel':>8s} {'FIRST%':>8s} {'MID%':>8s} {'LAST%':>8s}")
        for ch in sorted(data['profiles'].keys()):
            p = data['profiles'][ch]
            print(f"    {ch:>8s} {p[0]*100:>7.1f}% {p[1]*100:>7.1f}% {p[2]*100:>7.1f}%")

        # Show worst pairs
        worst = sorted(data['cosines'], key=lambda x: x[2])[:3]
        print(f"    Worst pairs: ", end='')
        for c1, c2, cs in worst:
            print(f"{c1}-{c2}={cs:.3f} ", end='')
        print()

    # Summary matrix: channel x channel similarity (averaged over all atoms)
    print("\n--- Channel-to-Channel Overall Similarity Matrix ---")
    print("  (Mean cosine across all atoms with sufficient data)\n")

    # Build pairwise channel similarity
    channel_pair_cosines = defaultdict(list)
    for atom, data in atom_consistency.items():
        for c1, c2, cs in data['cosines']:
            key = tuple(sorted([c1, c2]))
            channel_pair_cosines[key].append(cs)

    # Print matrix
    print(f"{'':>8s}", end='')
    for ch in valid_channels:
        print(f" {ch:>7s}", end='')
    print()

    channel_similarity_matrix = {}
    for ch1 in valid_channels:
        print(f"{ch1:>8s}", end='')
        for ch2 in valid_channels:
            if ch1 == ch2:
                print(f"   1.000", end='')
                continue
            key = tuple(sorted([ch1, ch2]))
            if key in channel_pair_cosines:
                mean_cs = np.mean(channel_pair_cosines[key])
                channel_similarity_matrix[key] = mean_cs
                if mean_cs < 0.7:
                    print(f"  {mean_cs:.3f}*", end='')
                else:
                    print(f"  {mean_cs:.3f} ", end='')
            else:
                print(f"      -- ", end='')
        print()

    print("\n  * = low similarity (<0.7)")

    return atom_consistency

# ============================================================
# ANALYSIS 6: Slot Dominance by Channel (BONUS)
# ============================================================

def analysis_6(records, valid_channels):
    """Which slot class (HEAD/MODIFIER/TERMINAL/FREE) dominates in each channel?"""
    print("\n" + "=" * 80)
    print("ANALYSIS 6 (BONUS): Slot Class Distribution by Channel")
    print("=" * 80)
    print("\nWhat fraction of atoms in each channel are HEAD/MODIFIER/TERMINAL/FREE?\n")

    slots = ['HEAD', 'MODIFIER', 'TERMINAL', 'FREE']
    channel_slot_counts = defaultdict(Counter)

    for rec in records:
        prefix = rec['prefix']
        if prefix not in valid_channels:
            continue

        for atom in rec['atoms']:
            slot = SLOT_CLASS.get(atom, 'OTHER')
            channel_slot_counts[prefix][slot] += 1

    # Global
    global_counts = Counter()
    for ch in valid_channels:
        global_counts += channel_slot_counts[ch]
    global_total = sum(global_counts.values())
    global_rates = {s: global_counts[s] / global_total * 100 for s in slots}

    print(f"{'Channel':>8s} {'N':>6s}", end='')
    for s in slots:
        print(f" {s:>10s}", end='')
    print(f"  {'H:T ratio':>10s}")
    print("-" * (20 + 11 * len(slots) + 12))

    for ch in valid_channels:
        total = sum(channel_slot_counts[ch].values())
        if total < 20:
            continue

        print(f"{ch:>8s} {total:>6d}", end='')
        rates = {}
        for s in slots:
            rate = channel_slot_counts[ch][s] / total * 100
            rates[s] = rate
            enrichment = rate / global_rates[s] if global_rates[s] > 0 else 0
            marker = '+' if enrichment > 1.3 else ('-' if enrichment < 0.7 else ' ')
            print(f" {rate:>8.1f}%{marker}", end='')

        ht_ratio = rates['HEAD'] / rates['TERMINAL'] if rates['TERMINAL'] > 0 else float('inf')
        print(f"  {ht_ratio:>10.2f}")

    print("-" * (20 + 11 * len(slots) + 12))
    print(f"{'GLOBAL':>8s} {global_total:>6d}", end='')
    for s in slots:
        print(f" {global_rates[s]:>9.1f}%", end='')
    ht_ratio = global_rates['HEAD'] / global_rates['TERMINAL'] if global_rates['TERMINAL'] > 0 else 0
    print(f"  {ht_ratio:>10.2f}")

    print("\n  + = >1.3x enriched vs global   - = <0.7x depleted")

# ============================================================
# ANALYSIS 7: Per-Channel Atom Pair Preferences (BONUS)
# ============================================================

def analysis_7(records, valid_channels):
    """Which atom PAIRS are characteristic of each channel?"""
    print("\n" + "=" * 80)
    print("ANALYSIS 7 (BONUS): Channel-Characteristic Atom Pairs")
    print("=" * 80)
    print("\nFor each channel, find atom bigrams that are significantly enriched/depleted")
    print("compared to global rates. Shows channel-specific construction preferences.\n")

    # Count atom bigrams per channel
    channel_bigrams = defaultdict(Counter)
    global_bigrams = Counter()
    channel_total_bigrams = Counter()
    global_total_bigrams = 0

    for rec in records:
        prefix = rec['prefix']
        if prefix not in valid_channels:
            continue

        atoms = rec['atoms']
        for i in range(len(atoms) - 1):
            bigram = atoms[i] + atoms[i+1]
            channel_bigrams[prefix][bigram] += 1
            global_bigrams[bigram] += 1
            channel_total_bigrams[prefix] += 1
            global_total_bigrams += 1

    # For each channel, find top enriched bigrams
    for ch in valid_channels:
        total_ch = channel_total_bigrams[ch]
        if total_ch < 30:
            continue

        enrichments = []
        for bigram, count in channel_bigrams[ch].items():
            if count < 3:
                continue
            expected_rate = global_bigrams[bigram] / global_total_bigrams
            observed_rate = count / total_ch
            if expected_rate > 0:
                enrichment = observed_rate / expected_rate
                enrichments.append((bigram, count, enrichment, observed_rate * 100))

        if not enrichments:
            continue

        enrichments.sort(key=lambda x: -x[2])

        top_enriched = [e for e in enrichments if e[2] > 1.5][:5]
        top_depleted = sorted([e for e in enrichments if e[2] < 0.5], key=lambda x: x[2])[:3]

        if top_enriched or top_depleted:
            print(f"\n  {ch} (N={total_ch} bigrams):")
            if top_enriched:
                print(f"    Enriched: ", end='')
                for bg, cnt, enr, rate in top_enriched:
                    print(f"{bg}({enr:.1f}x, n={cnt}) ", end='')
                print()
            if top_depleted:
                print(f"    Depleted: ", end='')
                for bg, cnt, enr, rate in top_depleted:
                    print(f"{bg}({enr:.2f}x, n={cnt}) ", end='')
                print()

# ============================================================
# SUMMARY
# ============================================================

def print_summary(atom_consistency, head_rates, term_rates, valid_channels):
    """Print final verdict."""
    print("\n" + "=" * 80)
    print("FINAL SUMMARY: UNIVERSAL vs CHANNEL-SPECIFIC GRAMMAR")
    print("=" * 80)

    # Count verdicts
    verdicts = Counter(d['verdict'] for d in atom_consistency.values())
    total_atoms = sum(verdicts.values())

    print(f"\n  Atom consistency verdicts (N={total_atoms} atoms tested):")
    for v in ['UNIVERSAL', 'MIXED', 'CHANNEL-SPEC']:
        count = verdicts.get(v, 0)
        pct = count / total_atoms * 100 if total_atoms > 0 else 0
        print(f"    {v:>15s}: {count:3d} ({pct:5.1f}%)")

    # Overall verdict
    universal_frac = verdicts.get('UNIVERSAL', 0) / total_atoms if total_atoms > 0 else 0
    channel_spec_frac = verdicts.get('CHANNEL-SPEC', 0) / total_atoms if total_atoms > 0 else 0

    print(f"\n  Head-match rate variation across channels:")
    hr_vals = [v for v in head_rates.values() if v > 0]
    if hr_vals:
        print(f"    Range: [{min(hr_vals):.1f}% - {max(hr_vals):.1f}%]")
        print(f"    CV: {np.std(hr_vals)/np.mean(hr_vals):.3f}")

    tr_vals = [v for v in term_rates.values() if v > 0]
    if tr_vals:
        print(f"\n  Terminal-match rate variation across channels:")
        print(f"    Range: [{min(tr_vals):.1f}% - {max(tr_vals):.1f}%]")
        print(f"    CV: {np.std(tr_vals)/np.mean(tr_vals):.3f}")

    # List channel-specific atoms
    cs_atoms = [(a, d) for a, d in atom_consistency.items() if d['verdict'] == 'CHANNEL-SPEC']
    mixed_atoms = [(a, d) for a, d in atom_consistency.items() if d['verdict'] == 'MIXED']

    print(f"\n  ====================================")
    if universal_frac > 0.7:
        print(f"  VERDICT: PREDOMINANTLY UNIVERSAL")
        print(f"  ====================================")
        print(f"  The three-slot composition grammar is broadly consistent across")
        print(f"  PREFIX channels. {universal_frac*100:.0f}% of atoms show universal positional")
        print(f"  behavior (cosine > 0.8 across all channel pairs).")
    elif channel_spec_frac > 0.3:
        print(f"  VERDICT: CHANNEL-SPECIFIC")
        print(f"  ====================================")
        print(f"  The composition grammar shows significant channel-dependent variation.")
        print(f"  {channel_spec_frac*100:.0f}% of atoms have channel-specific positional behavior.")
    else:
        print(f"  VERDICT: MIXED / PARTIALLY CHANNEL-SPECIFIC")
        print(f"  ====================================")
        print(f"  The base grammar is universal but some atoms shift behavior by channel.")

    if cs_atoms:
        print(f"\n  Channel-specific atoms:")
        for a, d in sorted(cs_atoms, key=lambda x: x[1]['mean_cos']):
            slot = SLOT_CLASS.get(a, '?')
            cat = ATOM_CAT.get(a, '?')
            print(f"    {a} ({slot:10s}, {cat:10s}): mean cosine = {d['mean_cos']:.3f}")

    if mixed_atoms:
        print(f"\n  Mixed-consistency atoms:")
        for a, d in sorted(mixed_atoms, key=lambda x: x[1]['mean_cos']):
            slot = SLOT_CLASS.get(a, '?')
            cat = ATOM_CAT.get(a, '?')
            print(f"    {a} ({slot:10s}, {cat:10s}): mean cosine = {d['mean_cos']:.3f}")

    # Specific channel divergences
    print(f"\n  Key channel divergences:")

    # Find the most divergent channel pair overall
    all_pair_means = {}
    for atom_data in atom_consistency.values():
        for c1, c2, cs in atom_data['cosines']:
            key = tuple(sorted([c1, c2]))
            if key not in all_pair_means:
                all_pair_means[key] = []
            all_pair_means[key].append(cs)

    pair_summary = [(k, np.mean(v)) for k, v in all_pair_means.items()]
    pair_summary.sort(key=lambda x: x[1])

    print(f"\n    Most SIMILAR channel pairs:")
    for (c1, c2), mean_cs in pair_summary[-5:]:
        print(f"      {c1}-{c2}: mean cosine = {mean_cs:.3f}")

    print(f"\n    Most DIVERGENT channel pairs:")
    for (c1, c2), mean_cs in pair_summary[:5]:
        print(f"      {c1}-{c2}: mean cosine = {mean_cs:.3f}")

# ============================================================
# MAIN
# ============================================================

def main():
    print("Channel-Slot Grammar Analysis")
    print("=" * 80)
    print("Testing whether compound MIDDLE composition grammar varies by PREFIX channel\n")

    # Load data
    print("Loading data...")
    records = load_data()
    print(f"Loaded {len(records)} compound MIDDLE tokens from Currier B")

    # Count unique MIDDLEs
    unique_middles = set(r['middle'] for r in records)
    print(f"Unique compound MIDDLEs: {len(unique_middles)}")

    # Atom length distribution
    lengths = Counter(len(r['atoms']) for r in records)
    print(f"Atom count distribution: {dict(sorted(lengths.items()))}")

    # PREFIX distribution (all)
    pfx_counts = Counter(r['prefix'] for r in records)
    print(f"\nPREFIX distribution (top 15):")
    for pfx, cnt in pfx_counts.most_common(15):
        print(f"  {pfx:8s}: {cnt:5d}")

    # Run analyses
    valid_channels, channel_positions, global_means, atom_channel_data = analysis_1(records)
    head_rates, term_rates = analysis_2(records, valid_channels)
    analysis_3(records, valid_channels)
    analysis_4(records, valid_channels)
    atom_consistency = analysis_5(records, valid_channels, global_means)
    analysis_6(records, valid_channels)
    analysis_7(records, valid_channels)

    # Final summary
    print_summary(atom_consistency, head_rates, term_rates, valid_channels)

if __name__ == '__main__':
    main()
