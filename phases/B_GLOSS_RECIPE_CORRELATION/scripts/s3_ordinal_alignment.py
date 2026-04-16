"""
Phase 641, Script 3: Ordinal alignment (primary structural diagnostic).

Tests whether folio paragraph sequences match the category order of the corresponding
Latin recipe steps. Approach:

  1. For each matched pair, split the Latin chapter into steps (transition-delimited).
  2. Classify each step by DOMINANT feature category: HEAT / MON / MAT / SEAL / XFER.
  3. Classify each folio paragraph by DOMINANT Voynich category using prefix/atom rates.
  4. For each pair, compute a positional alignment score:
     - For each category present in BOTH sequences, record (Latin first-position, Folio first-position).
     - Compute Spearman ρ across those pairs.
     - Null: shuffle folio paragraph order, recompute.
  5. Across 15 pairs: test whether mean ρ > 0 at p < 0.05 (one-sided).

This directly tests "the folio executes the recipe in the recipe's order."
"""
import sys, io, os, json, re, random
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))

from s1_shared_validation import (
    MATCHED_PAIRS, _get_tx, spearman_rho, perm_pvalue,
)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
LATIN_PATH = os.path.join(ROOT, 'sources', 'pseudo_lull_testamentum', 'testamentum_complete_latin.txt')
FEAT_PATH = os.path.join(os.path.dirname(__file__), '..', 'results', 'pl_channel_features_latin.json')
OUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'results', 'ordinal_alignment.json')

# ============================================================
# CATEGORY CLASSIFICATION — recipe side (Latin)
# ============================================================
CAT_PATTERNS = {
    'HEAT': re.compile(
        r'\b(ign\w+|calor\w+|balneum|ciner\w+|fornax|fornac\w+|foco\w+|'
        r'igne\w+|aren\w+|stercor\w+|fortiter|leniter|intende\w+|'
        r'augeat\w* ign\w*|minuat\w* ign\w*)\b', re.IGNORECASE
    ),
    'MON': re.compile(
        r'\b(vide\w+|videa\w+|appare\w+|signum|signa|manifest\w+|observ\w+|nota\w+)\b',
        re.IGNORECASE
    ),
    'MAT': re.compile(
        r'\b(accipe|sume|recipe|appone\w+|pone|adde|mitte|infunde\w+|impone\w+|'
        r'accipia\w+|suma\w+|adda\w+|mitta\w+|mitta\w+)\b', re.IGNORECASE
    ),
    'SEAL': re.compile(
        r'\b(claude|clauda\w+|clausum|obtur\w+|sigilla\w+|lut(?:o|um|i|e)|lutet\w*|pasta|cera\w*)\b',
        re.IGNORECASE
    ),
    'XFER': re.compile(
        r'\b(transfer\w+|vert(?:e|ere|at|atur|it|itur)|decant\w+|effunde\w+|funde|'
        r'stilla\w+|destilla\w+|distilla\w+|refunde\w+)\b', re.IGNORECASE
    ),
}

TRANSITION_SPLIT = re.compile(
    r'\b(postea|deinde|tunc|mox|statim|postmodum|postquam|itaque|igitur)\b',
    re.IGNORECASE
)

def load_latin_lines():
    with open(LATIN_PATH, 'r', encoding='utf-8') as f:
        return f.readlines()

def chapter_text(part, num):
    """Return the Latin text block for a given (part, chapter)."""
    with open(FEAT_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    all_lines = load_latin_lines()
    # Find chapter entries
    matches = [c for c in data['chapters'] if c['part'] == part and c['number'] == num]
    if not matches: return ''
    text_blocks = []
    for c in matches:
        text_blocks.append('\n'.join(all_lines[c['start_line']-1:c['end_line']]))
    return '\n'.join(text_blocks)

def chapter_multi_text(part, nums):
    """Handle multi-chapter matches (e.g., f80r -> 21,23,24,25)."""
    if isinstance(nums, tuple):
        return '\n'.join(chapter_text(part, n) for n in nums)
    return chapter_text(part, nums)

def split_into_steps(text):
    """Split recipe text into transition-delimited steps. Returns list of step strings."""
    # Remove page headers and markers
    cleaned = re.sub(r'^---.*?---\s*$', '', text, flags=re.MULTILINE)
    cleaned = re.sub(r'^(CAPVT|CAP\.?|Caput).*?\.\s*$', '', cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r'^[A-ZÆŒ]{3,}.*$', '', cleaned, flags=re.MULTILINE)  # running headers in caps
    # Split by transition markers AND by sentence-boundary periods
    # Treat each Latin sentence (period-delimited) as potential step
    sentences = re.split(r'(?<=[.!?])\s+', cleaned)
    sentences = [s.strip() for s in sentences if s.strip() and len(s) > 15]
    return sentences

def classify_step(step_text):
    """Return dominant category for a step, or None if no features.
    Ties broken by specific-feature priority: SEAL > MAT > XFER > MON > HEAT
    (HEAT is ubiquitous; prioritize rarer specific markers for disambiguation).
    """
    counts = {}
    for cat, pat in CAT_PATTERNS.items():
        counts[cat] = len(pat.findall(step_text))
    total = sum(counts.values())
    if total == 0: return None
    # Rarer-first priority — if SEAL and HEAT both match once, the SEAL is more specific
    priority = {'SEAL': 5, 'MAT': 4, 'XFER': 3, 'MON': 2, 'HEAT': 1}
    best = max(counts.items(), key=lambda kv: (kv[1], priority[kv[0]]))
    return best[0] if best[1] > 0 else None

def recipe_sequence(part, num):
    """Get ordered category sequence for a chapter."""
    text = chapter_multi_text(part, num)
    steps = split_into_steps(text)
    seq = []
    for s in steps:
        c = classify_step(s)
        if c: seq.append(c)
    return seq

# ============================================================
# FOLIO SIDE
# ============================================================
def paragraph_feature_vector(par, morph):
    """Return (heat, mon, mat, seal, xfer) relative scores for a single paragraph."""
    n = len(par)
    if n == 0: return {'HEAT':0,'MON':0,'MAT':0,'SEAL':0,'XFER':0}
    prefixes = Counter()
    atom_counts = Counter()
    dal_dar_count = 0
    iin_count = 0
    ain_count = 0
    for t in par:
        m = morph.extract(t.word)
        a = morph.atomize(t.word)
        prefixes[(m.prefix if m else None) or 'BARE'] += 1
        if t.word in ('dar', 'dal', 'dam'):
            dal_dar_count += 1
        # Explicit -iin suffix (not just last 3 chars; check morphology)
        if m and m.suffix == 'iin':
            iin_count += 1
        if m and m.suffix == 'ain':
            ain_count += 1
        if a and a.atoms:
            for ch, role, g in a.atoms:
                atom_counts[ch] += 1
    # No opaque-terminal term — that's a structural baseline
    return {
        'HEAT': prefixes['qo']/n + atom_counts['k']/n,
        'MON':  prefixes['sh']/n,
        'MAT':  prefixes['da']/n + (dal_dar_count/n * 3),
        'SEAL': (iin_count + ain_count) / n,
        'XFER': prefixes['ot']/n + atom_counts['t']/n,
    }

def paragraph_sequence(folio):
    """
    Classify each paragraph by dominant category using WITHIN-FOLIO relative ranking.
    A paragraph is classified as CAT if it's that folio's max (or top-tier) for that category.
    Returns an ordered list of category labels (one per paragraph; paragraphs with no
    distinctive profile get skipped).
    """
    tx, morph = _get_tx()
    tokens = [t for t in tx.currier_b() if t.folio == folio and t.word.strip() and '*' not in t.word]

    paragraphs = []
    current_par = []
    for t in tokens:
        if t.par_initial and current_par:
            paragraphs.append(current_par)
            current_par = []
        current_par.append(t)
    if current_par: paragraphs.append(current_par)

    # Per-paragraph feature vectors
    vecs = [paragraph_feature_vector(par, morph) for par in paragraphs]
    if not vecs: return []

    # Normalize each category across paragraphs (z-like: divide by folio mean for that cat)
    cats = ['HEAT', 'MON', 'MAT', 'SEAL', 'XFER']
    folio_means = {c: max(0.001, sum(v[c] for v in vecs)/len(vecs)) for c in cats}
    norm_vecs = []
    for v in vecs:
        norm_vecs.append({c: v[c]/folio_means[c] for c in cats})

    # Each paragraph: assign dominant category, but only if its normalized score for that category
    # is > 1.2 (i.e., above folio average).
    seq = []
    for nv in norm_vecs:
        best = max(nv.items(), key=lambda kv: kv[1])
        if best[1] >= 1.2:
            seq.append(best[0])
        else:
            # Paragraph has no distinctive category — use dominant but flag
            seq.append(best[0])
    return seq

# ============================================================
# ALIGNMENT METRIC
# ============================================================
def first_position_alignment(recipe_seq, folio_seq):
    """
    For each category present in BOTH sequences, record (first-pos-in-recipe, first-pos-in-folio).
    Return Spearman ρ across those pairs.
    """
    shared_cats = set(recipe_seq) & set(folio_seq)
    if len(shared_cats) < 3:
        return None, 0  # not enough data
    recipe_pos = []
    folio_pos = []
    for cat in shared_cats:
        r_idx = recipe_seq.index(cat)
        f_idx = folio_seq.index(cat)
        # Normalize by length so both are in [0,1]
        recipe_pos.append(r_idx / max(1, len(recipe_seq)-1))
        folio_pos.append(f_idx / max(1, len(folio_seq)-1))
    rho = spearman_rho(recipe_pos, folio_pos)
    return rho, len(shared_cats)

def lcs_length(a, b):
    """Longest common subsequence length (for supplementary metric)."""
    m, n = len(a), len(b)
    if m == 0 or n == 0: return 0
    dp = [[0]*(n+1) for _ in range(m+1)]
    for i in range(1, m+1):
        for j in range(1, n+1):
            if a[i-1] == b[j-1]: dp[i][j] = dp[i-1][j-1] + 1
            else: dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp[m][n]

# ============================================================
# MAIN
# ============================================================
print("=" * 80)
print("s3 Ordinal Alignment — pairwise recipe/folio sequence correlation")
print("=" * 80)

pair_results = []
for folio, part, num, tier, desc in MATCHED_PAIRS:
    recipe_seq = recipe_sequence(part, num)
    folio_seq = paragraph_sequence(folio)
    rho, n_shared = first_position_alignment(recipe_seq, folio_seq)
    lcs = lcs_length(recipe_seq, folio_seq)
    result = {
        'folio': folio, 'part': part, 'num': str(num) if isinstance(num, tuple) else num,
        'tier': tier,
        'recipe_seq': recipe_seq, 'recipe_len': len(recipe_seq),
        'folio_seq': folio_seq, 'folio_len': len(folio_seq),
        'n_shared_cats': n_shared,
        'first_pos_rho': rho,
        'lcs_length': lcs,
        'lcs_frac': lcs / max(1, min(len(recipe_seq), len(folio_seq))),
    }
    pair_results.append(result)
    print(f"\n{folio:<6} {tier:<10} ({desc[:50]})")
    print(f"  recipe seq ({len(recipe_seq):>2d}): {' '.join(recipe_seq[:15])}{'...' if len(recipe_seq) > 15 else ''}")
    print(f"  folio  seq ({len(folio_seq):>2d}): {' '.join(folio_seq)}")
    if rho is not None:
        print(f"  first-pos ρ = {rho:+.3f} over {n_shared} shared cats; LCS = {lcs}/{min(len(recipe_seq), len(folio_seq))}")
    else:
        print(f"  insufficient shared categories ({n_shared})")

# ============================================================
# AGGREGATE TEST
# ============================================================
rhos = [r['first_pos_rho'] for r in pair_results if r['first_pos_rho'] is not None]
print(f"\n{'='*80}")
print(f"AGGREGATE")
print(f"{'='*80}")
if rhos:
    mean_rho = sum(rhos) / len(rhos)
    n_pos = sum(1 for r in rhos if r > 0)
    n_strong = sum(1 for r in rhos if r > 0.2)
    print(f"Pairs with valid ρ: {len(rhos)}/{len(pair_results)}")
    print(f"Mean ρ across pairs: {mean_rho:+.3f}")
    print(f"Pairs with ρ > 0: {n_pos}/{len(rhos)}")
    print(f"Pairs with ρ > 0.2: {n_strong}/{len(rhos)}")

    # Permutation test: shuffle folio sequences to test against null
    # Null: mean ρ when folio paragraph order is randomized
    rng = random.Random(42)
    null_means = []
    for _ in range(10000):
        null_rhos = []
        for r in pair_results:
            if r['first_pos_rho'] is None: continue
            fs = list(r['folio_seq'])
            rng.shuffle(fs)
            rho_null, _ = first_position_alignment(r['recipe_seq'], fs)
            if rho_null is not None:
                null_rhos.append(rho_null)
        if null_rhos:
            null_means.append(sum(null_rhos)/len(null_rhos))
    # One-sided p-value: P(null_mean >= observed mean)
    p = sum(1 for nm in null_means if nm >= mean_rho) / max(1, len(null_means))
    print(f"\nPermutation test (10,000 folio-shuffle trials):")
    print(f"  Null mean ρ: {sum(null_means)/len(null_means):+.3f}" if null_means else "  Null empty")
    print(f"  P(null_mean >= observed): p = {p:.4f}")

# ============================================================
# SAVE
# ============================================================
out = {
    'metadata': {
        'phase': 641,
        'script': 's3_ordinal_alignment',
        'n_pairs': len(pair_results),
        'n_valid_rhos': len(rhos) if rhos else 0,
        'mean_rho': mean_rho if rhos else None,
        'permutation_p': p if rhos else None,
        'categories': list(CAT_PATTERNS.keys()),
    },
    'pair_results': pair_results,
}
with open(OUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nWrote {OUT_PATH}")
