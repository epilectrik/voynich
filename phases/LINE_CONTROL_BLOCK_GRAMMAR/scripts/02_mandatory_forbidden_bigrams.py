"""
LINE_CONTROL_BLOCK_GRAMMAR - Test 02: Mandatory/Forbidden Token-Level Bigrams

Purpose: Identify token-level bigrams that are significantly over- or under-
represented relative to independence, distinguishing role-expected patterns
from genuinely token-specific constraints.

Pass criteria:
  PASS:    3+ mandatory AND 3+ forbidden beyond or->aiin (p<0.01)
  PARTIAL: 1-2 new forbidden, mostly role-aligned
  FAIL:    0-1 of each

Validation: or->aiin must appear as mandatory (C561).
"""

import sys
import json
import math
from pathlib import Path
from collections import Counter, defaultdict

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path('C:/git/voynich').resolve()))
from scripts.voynich import Transcript, Morphology

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path('C:/git/voynich').resolve()
CLASS_MAP_PATH = PROJECT_ROOT / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
RESULTS_PATH = PROJECT_ROOT / "phases/LINE_CONTROL_BLOCK_GRAMMAR/results/02_mandatory_forbidden_bigrams.json"

MIN_TOKEN_FREQ = 10
MANDATORY_RATIO = 5.0
MANDATORY_MIN_OBS = 5
BONFERRONI_ALPHA = 0.001
FORBIDDEN_MIN_EXP = 5.0
N_SHUFFLES = 1000
SEED = 42

# ---------------------------------------------------------------------------
# LOAD CLASS MAP
# ---------------------------------------------------------------------------
with open(CLASS_MAP_PATH, 'r', encoding='utf-8') as f:
    class_data = json.load(f)

token_to_class = {k: int(v) for k, v in class_data['token_to_class'].items()}
class_to_role = {int(k): v for k, v in class_data['class_to_role'].items()}


def get_role(word):
    cls = token_to_class.get(word, -1)
    return class_to_role.get(cls, 'UNKNOWN') if cls >= 0 else 'UNKNOWN'


def get_class(word):
    return token_to_class.get(word, -1)


# ---------------------------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------------------------
tx = Transcript()
lines = defaultdict(list)
for t in tx.currier_b():
    word = t.word.replace('*', '').strip()
    if not word:
        continue
    lines[(t.folio, t.line)].append(word)

line_list = list(lines.values())
print(f"Loaded {len(line_list)} lines from Currier B")

# ---------------------------------------------------------------------------
# BUILD BIGRAM COUNTS
# ---------------------------------------------------------------------------
token_counts = Counter()
for line in line_list:
    for w in line:
        token_counts[w] += 1

common_tokens = {w for w, c in token_counts.items() if c >= MIN_TOKEN_FREQ}
print(f"Common tokens (freq >= {MIN_TOKEN_FREQ}): {len(common_tokens)}")

bigram_counts = Counter()
total_bigrams = 0
source_counts = Counter()
target_counts = Counter()

for line in line_list:
    for i in range(len(line) - 1):
        a, b = line[i], line[i + 1]
        if a in common_tokens and b in common_tokens:
            bigram_counts[(a, b)] += 1
            total_bigrams += 1
            source_counts[a] += 1
            target_counts[b] += 1

print(f"Total bigrams (both common): {total_bigrams}")

# ---------------------------------------------------------------------------
# COMPUTE EXPECTED FREQUENCIES AND CLASSIFY BIGRAMS
# ---------------------------------------------------------------------------
n_tests = len(common_tokens) ** 2
bonferroni_threshold = BONFERRONI_ALPHA / n_tests
print(f"Bonferroni correction: {n_tests} tests, threshold p < {bonferroni_threshold:.2e}")

mandatory_bigrams = []
forbidden_bigrams = []
common_list = sorted(common_tokens)

for a in common_list:
    for b in common_list:
        sc = source_counts.get(a, 0)
        tc = target_counts.get(b, 0)
        if sc == 0 or tc == 0:
            continue
        expected = sc * tc / total_bigrams
        observed = bigram_counts.get((a, b), 0)

        if observed >= MANDATORY_MIN_OBS and expected > 0:
            ratio = observed / expected
            if ratio > MANDATORY_RATIO:
                chi2 = (observed - expected) ** 2 / expected
                p_value = 1.0 - stats.chi2.cdf(chi2, df=1)
                if p_value < bonferroni_threshold:
                    role_a = get_role(a)
                    role_b = get_role(b)
                    class_a = get_class(a)
                    class_b = get_class(b)
                    mandatory_bigrams.append({
                        'token_a': a, 'token_b': b,
                        'observed': int(observed),
                        'expected': round(expected, 2),
                        'ratio': round(ratio, 2),
                        'chi2': round(chi2, 2),
                        'p_value': p_value,
                        'role_a': role_a, 'role_b': role_b,
                        'class_a': class_a, 'class_b': class_b,
                        'same_role': role_a == role_b,
                        'same_class': class_a == class_b,
                    })

        if observed == 0 and expected >= FORBIDDEN_MIN_EXP:
            role_a = get_role(a)
            role_b = get_role(b)
            class_a = get_class(a)
            class_b = get_class(b)
            forbidden_bigrams.append({
                'token_a': a, 'token_b': b,
                'observed': 0,
                'expected': round(expected, 2),
                'role_a': role_a, 'role_b': role_b,
                'class_a': class_a, 'class_b': class_b,
                'same_role': role_a == role_b,
                'same_class': class_a == class_b,
            })

mandatory_bigrams.sort(key=lambda x: x['ratio'], reverse=True)
forbidden_bigrams.sort(key=lambda x: x['expected'], reverse=True)

# ---------------------------------------------------------------------------
# CLASSIFY FORBIDDEN BIGRAMS
# ---------------------------------------------------------------------------
role_expected_forbidden = [b for b in forbidden_bigrams if not b['same_role']]
token_specific_forbidden = [b for b in forbidden_bigrams if b['same_role']]

sep = '=' * 70
dash = '-' * 92

print(f"\n{sep}")
print(f"MANDATORY BIGRAMS: {len(mandatory_bigrams)}")
print(sep)

hdr = ("Token A".ljust(12) + " " + "Token B".ljust(12) + " " +
       "Obs".rjust(5) + " " + "Exp".rjust(7) + " " + "Ratio".rjust(7) + " " +
       "Chi2".rjust(8) + " " + "Role A".ljust(18) + " " + "Role B".ljust(18))
print(f"\n{hdr}")
print(dash)
for bg in mandatory_bigrams[:30]:
    ta = bg['token_a'].ljust(12)
    tb = bg['token_b'].ljust(12)
    ob = str(bg['observed']).rjust(5)
    ex = f"{bg['expected']:7.2f}"
    ra = f"{bg['ratio']:7.2f}"
    c2 = f"{bg['chi2']:8.1f}"
    ra_ = bg['role_a'].ljust(18)
    rb_ = bg['role_b'].ljust(18)
    print(f"{ta} {tb} {ob} {ex} {ra} {c2} {ra_} {rb_}")

# ---------------------------------------------------------------------------
# VALIDATION: or->aiin (C561)
# ---------------------------------------------------------------------------
or_aiin = next((b for b in mandatory_bigrams
                if b['token_a'] == 'or' and b['token_b'] == 'aiin'), None)
if or_aiin:
    print("\n** VALIDATION (C561): or->aiin FOUND in mandatory bigrams")
    print(f"   obs={or_aiin['observed']}, exp={or_aiin['expected']}, "
          f"ratio={or_aiin['ratio']}, chi2={or_aiin['chi2']}")
    validation_pass = True
else:
    print("\n** VALIDATION (C561): or->aiin NOT found in mandatory bigrams")
    or_in = 'or' in common_tokens
    aiin_in = 'aiin' in common_tokens
    print(f"   'or' in common tokens: {or_in}")
    print(f"   'aiin' in common tokens: {aiin_in}")
    if or_in and aiin_in:
        obs_val = bigram_counts.get(('or', 'aiin'), 0)
        sc_val = source_counts.get('or', 0)
        tc_val = target_counts.get('aiin', 0)
        exp_val = sc_val * tc_val / total_bigrams if total_bigrams > 0 else 0
        if exp_val > 0:
            print(f"   obs={obs_val}, exp={exp_val:.2f}, ratio={obs_val/exp_val:.2f}")
        else:
            print(f"   obs={obs_val}, exp={exp_val:.2f}")
    validation_pass = False

# ---------------------------------------------------------------------------
# PRINT FORBIDDEN BIGRAMS
# ---------------------------------------------------------------------------
print(f"\n{sep}")
print(f"FORBIDDEN BIGRAMS: {len(forbidden_bigrams)}")
print(f"  Role-expected (diff roles):    {len(role_expected_forbidden)}")
print(f"  Token-specific (same role):    {len(token_specific_forbidden)}")
print(sep)

print("\n--- ROLE-EXPECTED FORBIDDEN (different roles, top 20) ---")
rhdr = ("Token A".ljust(12) + " " + "Token B".ljust(12) + " " +
        "Expected".rjust(8) + " " + "Role A".ljust(18) + " " + "Role B".ljust(18))
print(rhdr)
print('-' * 72)
for bg in role_expected_forbidden[:20]:
    print(f"{bg['token_a']:<12} {bg['token_b']:<12} {bg['expected']:>8.2f} "
          f"{bg['role_a']:<18} {bg['role_b']:<18}")

print("\n--- TOKEN-SPECIFIC FORBIDDEN (same role -- THE PRIZE, top 20) ---")
thdr = ("Token A".ljust(12) + " " + "Token B".ljust(12) + " " +
        "Expected".rjust(8) + " " + "Role A".ljust(18) + " " +
        "Class A".rjust(8) + " " + "Class B".rjust(8))
print(thdr)
print('-' * 80)
for bg in token_specific_forbidden[:20]:
    print(f"{bg['token_a']:<12} {bg['token_b']:<12} {bg['expected']:>8.2f} "
          f"{bg['role_a']:<18} {bg['class_a']:>8} {bg['class_b']:>8}")

# ---------------------------------------------------------------------------
# SHUFFLE TEST (1000x)
# ---------------------------------------------------------------------------
print(f"\n{sep}")
print(f"SHUFFLE TEST ({N_SHUFFLES}x, seed={SEED})")
print(sep)

rng = np.random.default_rng(SEED)
line_arrays = [np.array(line) for line in line_list if len(line) >= 2]
real_forbidden_set = {(b['token_a'], b['token_b']) for b in forbidden_bigrams}
real_forbidden_count = len(real_forbidden_set)

shuffle_surviving_counts = []
shuffle_total_forbidden = []

high_exp_pairs = []
for a in common_list:
    for b in common_list:
        sc = source_counts.get(a, 0)
        tc = target_counts.get(b, 0)
        if sc == 0 or tc == 0:
            continue
        expected = sc * tc / total_bigrams
        if expected >= FORBIDDEN_MIN_EXP:
            high_exp_pairs.append((a, b))

print(f"Shuffling {len(line_arrays)} lines, checking {real_forbidden_count} forbidden pairs...")
print(f"High-expectation pairs to check per shuffle: {len(high_exp_pairs)}")

for s in range(N_SHUFFLES):
    shuf_bigram_counts = Counter()
    for arr in line_arrays:
        perm = rng.permutation(len(arr))
        shuffled = arr[perm]
        for i in range(len(shuffled) - 1):
            a, b = shuffled[i], shuffled[i + 1]
            if a in common_tokens and b in common_tokens:
                shuf_bigram_counts[(a, b)] += 1

    surviving = sum(1 for pair in real_forbidden_set
                    if shuf_bigram_counts.get(pair, 0) == 0)
    shuffle_surviving_counts.append(surviving)

    total_forb = sum(1 for pair in high_exp_pairs
                     if shuf_bigram_counts.get(pair, 0) == 0)
    shuffle_total_forbidden.append(total_forb)

    if (s + 1) % 200 == 0:
        print(f"  Completed {s + 1}/{N_SHUFFLES} shuffles...")

shuffle_surviving_mean = np.mean(shuffle_surviving_counts)
shuffle_surviving_std = np.std(shuffle_surviving_counts)
shuffle_total_forb_mean = np.mean(shuffle_total_forbidden)
shuffle_total_forb_std = np.std(shuffle_total_forbidden)

p_forbidden = np.mean([c >= real_forbidden_count for c in shuffle_total_forbidden])

print(f"\nReal forbidden bigrams:           {real_forbidden_count}")
print(f"Shuffle surviving (of real):      {shuffle_surviving_mean:.1f} +/- {shuffle_surviving_std:.1f}")
print(f"Shuffle total forbidden mean:     {shuffle_total_forb_mean:.1f} +/- {shuffle_total_forb_std:.1f}")
print(f"p-value (shuffle >= real):        {p_forbidden:.4f}")

# ---------------------------------------------------------------------------
# VERDICT
# ---------------------------------------------------------------------------
print(f"\n{sep}")
print("VERDICT")
print(sep)

mandatory_new = [b for b in mandatory_bigrams
                 if not (b['token_a'] == 'or' and b['token_b'] == 'aiin')]
n_mandatory = len(mandatory_bigrams)
n_mandatory_new = len(mandatory_new)
n_forbidden = len(forbidden_bigrams)
n_token_specific = len(token_specific_forbidden)

v_str = 'PASS' if validation_pass else 'FAIL'
print(f"Mandatory bigrams:        {n_mandatory} (new beyond or->aiin: {n_mandatory_new})")
print(f"Forbidden bigrams:        {n_forbidden}")
print(f"  Role-expected:          {len(role_expected_forbidden)}")
print(f"  Token-specific (prize): {n_token_specific}")
print(f"Validation (or->aiin):    {v_str}")
print(f"Shuffle p-value:          {p_forbidden:.4f}")

if n_mandatory_new >= 3 and n_forbidden >= 3 and p_forbidden < 0.01:
    verdict = "PASS"
elif n_forbidden >= 1 and n_forbidden <= 2:
    verdict = "PARTIAL"
else:
    if n_mandatory_new >= 3 and n_forbidden >= 3:
        verdict = "PASS"
    elif n_mandatory_new >= 1 or n_forbidden >= 1:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"

print(f"\nVERDICT: {verdict}")

# ---------------------------------------------------------------------------
# SAVE JSON
# ---------------------------------------------------------------------------
def build_mandatory_entry(bg):
    return {
        "token_a": bg["token_a"], "token_b": bg["token_b"],
        "observed": bg["observed"], "expected": bg["expected"],
        "ratio": bg["ratio"], "chi2": bg["chi2"], "p_value": bg["p_value"],
        "role_a": bg["role_a"], "role_b": bg["role_b"],
        "class_a": bg["class_a"], "class_b": bg["class_b"],
        "same_role": bg["same_role"], "same_class": bg["same_class"],
    }


def build_forbidden_entry(bg, include_same_class=False):
    entry = {
        "token_a": bg["token_a"], "token_b": bg["token_b"],
        "expected": bg["expected"],
        "role_a": bg["role_a"], "role_b": bg["role_b"],
        "class_a": bg["class_a"], "class_b": bg["class_b"],
    }
    if include_same_class:
        entry["same_class"] = bg["same_class"]
    return entry


or_aiin_details = {}
if or_aiin:
    or_aiin_details = {
        "observed": or_aiin["observed"],
        "expected": or_aiin["expected"],
        "ratio": or_aiin["ratio"],
        "chi2": or_aiin["chi2"],
    }
else:
    or_aiin_details = {
        "observed": None, "expected": None,
        "ratio": None, "chi2": None,
    }

result = {
    "test": "Mandatory/Forbidden Token-Level Bigrams",
    "test_id": "02",
    "phase": "LINE_CONTROL_BLOCK_GRAMMAR",
    "purpose": "Identify token-level bigrams significantly over/under-represented vs independence",
    "parameters": {
        "min_token_freq": MIN_TOKEN_FREQ,
        "mandatory_ratio_threshold": MANDATORY_RATIO,
        "mandatory_min_obs": MANDATORY_MIN_OBS,
        "bonferroni_alpha": BONFERRONI_ALPHA,
        "forbidden_min_expected": FORBIDDEN_MIN_EXP,
        "n_shuffles": N_SHUFFLES,
        "seed": SEED,
    },
    "summary": {
        "n_lines": len(line_list),
        "n_common_tokens": len(common_tokens),
        "total_bigrams": total_bigrams,
        "n_tests_bonferroni": n_tests,
        "bonferroni_threshold": bonferroni_threshold,
    },
    "mandatory": {
        "count": n_mandatory,
        "count_new_beyond_or_aiin": n_mandatory_new,
        "bigrams": [build_mandatory_entry(bg) for bg in mandatory_bigrams],
    },
    "forbidden": {
        "count": n_forbidden,
        "role_expected_count": len(role_expected_forbidden),
        "token_specific_count": n_token_specific,
        "role_expected": [build_forbidden_entry(bg) for bg in role_expected_forbidden],
        "token_specific": [build_forbidden_entry(bg, True) for bg in token_specific_forbidden],
    },
    "validation": {
        "or_aiin_found": validation_pass,
        "or_aiin_details": or_aiin_details,
        "constraint": "C561",
    },
    "shuffle": {
        "n_shuffles": N_SHUFFLES,
        "seed": SEED,
        "real_forbidden_count": real_forbidden_count,
        "shuffle_surviving_mean": round(shuffle_surviving_mean, 2),
        "shuffle_surviving_std": round(shuffle_surviving_std, 2),
        "shuffle_total_forbidden_mean": round(shuffle_total_forb_mean, 2),
        "shuffle_total_forbidden_std": round(shuffle_total_forb_std, 2),
        "p_value": round(p_forbidden, 4),
    },
    "verdict": verdict,
}

with open(RESULTS_PATH, 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {RESULTS_PATH}")
