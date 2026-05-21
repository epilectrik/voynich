"""PHASE_723 v1: Distillation-discriminative matcher.

Phase 1-2: Validate that hand-tuned distillation-vs-metalwork features actually
discriminate Latin corpora correctly before attempting Voynich-side mapping.

Pre-registered:
- Codicillus + Rupescissa (distillation class) should show distillation_score > metalwork_score
- Theophilus (metalwork class) should show metalwork_score > distillation_score
- Theophilus vs Codicillus difference in discrimination_score should be substantial (>0.010) and significant (p<0.01)

If this passes, the features work as discriminators and we can proceed to apply
them to Voynich (Phase 4). If fails, text-level discrimination is not tractable
with this approach.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median, stdev

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path("C:/git/voynich")
OUT_PATH = ROOT / 'phases' / 'PHASE_723_DISTILLATION_DISCRIMINATIVE_MATCHER' / 'results' / 'distillation_matcher_v1.json'


# ---- Feature definitions ----

# Distillation-class markers (Latin)
DISTILLATION_MARKERS = {
    # Apparatus
    'alembic', 'alembico', 'alembicum', 'alembica', 'alembiqu',
    'cucurbita', 'cucurbitae', 'cucurbitam',
    'capitellum', 'capitelli', 'capitello',
    'distillatorium', 'distillatorii', 'distillatorio',
    'serpentinum', 'serpentini',
    'recipiens', 'recipienti', 'recipientem',
    'aludel', 'aludella',
    # Phase-transition operations
    'distill', 'sublim', 'evaporat', 'condens', 'vaporat', 'transmut',
    'exhal', 'ascendit', 'ascendere', 'descendit', 'descendere',
    # Reversibility markers
    'revert', 'restaur', 'regenera', 'redit', 'reduc', 'iter',
    'repet', 'pelican',
    # Circulation markers
    'circul', 'rotatio', 'refluxu', 'redux',
    # State markers (vapor/quintessence)
    'vapor', 'quintessen', 'spiritus', 'aer',
}

# Metalwork-class markers (Latin)
METALWORK_MARKERS = {
    # Apparatus (avoid ambiguous: fornax, crucibulum used in both)
    'incus', 'incudis', 'incude', 'incudem',
    'malleus', 'mallei', 'malleo', 'malleum',
    'tenax', 'tenaci',
    # Irreversible-transformation operations
    'fundere', 'fundit', 'fundimus', 'fundo', 'fund',
    'conflat', 'conflar',
    'cudo', 'cudere', 'cudis', 'cudit', 'cudimus',
    'trahere', 'trahit', 'trahimus',
    'polire', 'polit', 'limare',
    'fabric', 'fabri',
    'forg',
    # Metallic materials (most are alchemically referenced too — be careful)
    # Including a subset that's mainly metalwork-context
    'ferrum', 'ferri', 'ferreum',
    'ferramentum',
    'electrum',
    # Solid-state markers
    'durus', 'indurat', 'rigid', 'tempera',
}

# Ambiguous markers EXCLUDED to prevent masking
EXCLUDED_AMBIGUOUS = {
    'fornax', 'forni', 'fornace', 'fornacem',  # furnace - both domains
    'crucibulum', 'crucibuli', 'crucibulo',  # crucible - both
    'ignis', 'ignem', 'igni',  # fire - both
    'aqua', 'aquae', 'aquam',  # water - both
    'terra', 'terrae', 'terram',  # earth - both
    'aurum', 'auri', 'aureum',  # gold - common in alchemy
    'argentum', 'argenti',  # silver - common in alchemy
    'plumbum', 'plumbi',  # lead - common in alchemy
    'stannum', 'stanni',  # tin
    'cuprum', 'cupri',  # copper
}


def has_marker(word, marker_set):
    """Check if word matches any marker (allows prefix matching for stems)."""
    w = word.lower()
    if w in marker_set:
        return True
    # For stem-style markers (ending without explicit conjugation), check prefix
    for m in marker_set:
        # Only treat as stem if marker has 4-9 chars (avoid 'a' matching anything)
        if 4 <= len(m) <= 10 and w.startswith(m):
            return True
    return False


def score_paragraph(words):
    """Return (distillation_score, metalwork_score, n_dist, n_metal)."""
    n = len(words)
    if n == 0:
        return 0, 0, 0, 0
    n_dist = sum(1 for w in words if has_marker(w, DISTILLATION_MARKERS))
    n_metal = sum(1 for w in words if has_marker(w, METALWORK_MARKERS))
    return n_dist / n, n_metal / n, n_dist, n_metal


def load_paragraphs(filepath, min_len=15, max_len=80, skip_lines=0):
    if not Path(filepath).exists():
        return []
    text = Path(filepath).read_text(encoding='utf-8', errors='replace')
    lines = text.split('\n')
    if skip_lines > 0:
        lines = lines[skip_lines:]
    paragraphs = []
    current = []
    for line in lines:
        if not line.strip():
            if current:
                words = re.findall(r"\b[a-zA-Z]+\b", " ".join(current))
                if min_len <= len(words) <= max_len:
                    paragraphs.append([w.lower() for w in words])
                current = []
        else:
            current.append(line.strip())
    if current:
        words = re.findall(r"\b[a-zA-Z]+\b", " ".join(current))
        if min_len <= len(words) <= max_len:
            paragraphs.append([w.lower() for w in words])
    return paragraphs


def analyze_corpus(label, paragraphs, expected_class):
    """Compute discrimination statistics for a corpus."""
    if not paragraphs:
        return {'label': label, 'error': 'no paragraphs'}

    distillation_scores = []
    metalwork_scores = []
    discrimination_scores = []
    total_dist_hits = 0
    total_metal_hits = 0
    total_words = 0

    for p in paragraphs:
        dist, metal, n_d, n_m = score_paragraph(p)
        distillation_scores.append(dist)
        metalwork_scores.append(metal)
        discrimination_scores.append(dist - metal)
        total_dist_hits += n_d
        total_metal_hits += n_m
        total_words += len(p)

    return {
        'label': label,
        'expected_class': expected_class,
        'n_paragraphs': len(paragraphs),
        'total_words': total_words,
        'total_distillation_hits': total_dist_hits,
        'total_metalwork_hits': total_metal_hits,
        'distillation_score_mean': mean(distillation_scores),
        'distillation_score_median': median(distillation_scores),
        'distillation_score_stdev': stdev(distillation_scores) if len(distillation_scores) > 1 else 0,
        'metalwork_score_mean': mean(metalwork_scores),
        'metalwork_score_median': median(metalwork_scores),
        'discrimination_score_mean': mean(discrimination_scores),
        'discrimination_score_median': median(discrimination_scores),
        'discrimination_score_stdev': stdev(discrimination_scores) if len(discrimination_scores) > 1 else 0,
        'discrimination_scores': discrimination_scores,
    }


def mann_whitney_u(sample_a, sample_b):
    """Two-sided Mann-Whitney U test (asymptotic)."""
    import math
    n_a, n_b = len(sample_a), len(sample_b)
    combined = [(v, 'a') for v in sample_a] + [(v, 'b') for v in sample_b]
    combined.sort(key=lambda x: x[0])
    # Compute ranks (handle ties via average)
    ranks = [0.0] * len(combined)
    i = 0
    while i < len(combined):
        j = i
        while j < len(combined) and combined[j][0] == combined[i][0]:
            j += 1
        avg_rank = (i + j + 1) / 2  # +1 because 1-indexed
        for k in range(i, j):
            ranks[k] = avg_rank
        i = j
    r_a = sum(ranks[idx] for idx in range(len(combined)) if combined[idx][1] == 'a')
    u_a = r_a - n_a * (n_a + 1) / 2
    u_b = n_a * n_b - u_a
    u = min(u_a, u_b)
    # Asymptotic z
    mu = n_a * n_b / 2
    sigma = math.sqrt(n_a * n_b * (n_a + n_b + 1) / 12)
    if sigma == 0:
        return u, 1.0
    z = (u - mu) / sigma
    # Two-sided p
    from math import erf, sqrt
    p = 2 * (1 - 0.5 * (1 + erf(abs(z) / sqrt(2))))
    return u, p


def main():
    print("=" * 90)
    print("PHASE_723 DISTILLATION-DISCRIMINATIVE MATCHER v1")
    print("=" * 90)

    # Load corpora
    print("\n[Loading corpora at 15-80 word paragraph filter]")
    cod = load_paragraphs(ROOT / 'sources' / 'codicillus' / 'codicillus_complete_latin.txt')
    print(f"  Codicillus: {len(cod)} paragraphs")
    rup = load_paragraphs(ROOT / 'sources' / 'rupescissa' / 'rupescissa_latin_1561.txt', skip_lines=200)
    print(f"  Rupescissa: {len(rup)} paragraphs")

    theo_text = (ROOT / 'sources' / 'theophilus' / 'theophilus_hendrie_1847.txt').read_text(
        encoding='utf-8', errors='replace'
    )
    theo_lines = theo_text.split('\n')
    theo_body = []
    theo_body.extend(theo_lines[2242:4283])
    theo_body.extend(theo_lines[7213:9147])
    theo_body.extend(theo_lines[10537:11337])
    theo_paras = []
    current = []
    for line in theo_body:
        if not line.strip():
            if current:
                words = re.findall(r"\b[a-zA-Z]+\b", " ".join(current))
                if 15 <= len(words) <= 80:
                    theo_paras.append([w.lower() for w in words])
                current = []
        else:
            current.append(line.strip())
    if current:
        words = re.findall(r"\b[a-zA-Z]+\b", " ".join(current))
        if 15 <= len(words) <= 80:
            theo_paras.append([w.lower() for w in words])
    print(f"  Theophilus body: {len(theo_paras)} paragraphs")

    # Analyze each corpus
    print("\n[Computing distillation/metalwork scores]")
    cod_r = analyze_corpus('Codicillus', cod, 'distillation')
    rup_r = analyze_corpus('Rupescissa', rup, 'distillation')
    theo_r = analyze_corpus('Theophilus body', theo_paras, 'metalwork')

    # Summary table
    print("\n" + "=" * 90)
    print("CORPUS SIGNATURE TABLE (per-paragraph score means)")
    print("=" * 90)
    print(f"\n{'Corpus':<25}{'class':<14}{'n_paras':>10}{'dist_score':>14}"
          f"{'metal_score':>14}{'discrim_score':>16}")
    print("-" * 95)
    for r in [cod_r, rup_r, theo_r]:
        if 'error' in r:
            print(f"{r['label']:<25} ERROR")
            continue
        print(f"{r['label']:<25}{r['expected_class']:<14}{r['n_paragraphs']:>10}"
              f"{r['distillation_score_mean']:>+14.5f}"
              f"{r['metalwork_score_mean']:>+14.5f}"
              f"{r['discrimination_score_mean']:>+16.5f}")

    print("\nTotal marker hits (raw counts):")
    for r in [cod_r, rup_r, theo_r]:
        if 'error' in r:
            continue
        print(f"  {r['label']:<25} dist_hits={r['total_distillation_hits']:>5}  "
              f"metal_hits={r['total_metalwork_hits']:>5}  total_words={r['total_words']}")

    # Pre-registered criteria
    print("\n" + "=" * 90)
    print("PRE-REGISTERED CRITERIA CHECK")
    print("=" * 90)

    # C1: Codicillus discrimination_score > +0.005
    cod_disc = cod_r['discrimination_score_mean']
    c1_pass = cod_disc > +0.005
    print(f"\n  C1: Codicillus discrimination_score > +0.005? "
          f"({cod_disc:+.5f}) → {'PASS' if c1_pass else 'FAIL'}")

    # C2: Rupescissa discrimination_score > +0.005
    rup_disc = rup_r['discrimination_score_mean']
    c2_pass = rup_disc > +0.005
    print(f"  C2: Rupescissa discrimination_score > +0.005? "
          f"({rup_disc:+.5f}) → {'PASS' if c2_pass else 'FAIL'}")

    # C3: Theophilus discrimination_score < -0.005
    theo_disc = theo_r['discrimination_score_mean']
    c3_pass = theo_disc < -0.005
    print(f"  C3: Theophilus discrimination_score < -0.005? "
          f"({theo_disc:+.5f}) → {'PASS' if c3_pass else 'FAIL'}")

    # C4: Theophilus vs Codicillus difference > 0.010
    diff = abs(cod_disc - theo_disc)
    c4_pass = diff > 0.010
    print(f"  C4: |Codicillus - Theophilus| > 0.010? "
          f"({diff:.5f}) → {'PASS' if c4_pass else 'FAIL'}")

    # C5: Mann-Whitney test for Codicillus vs Theophilus
    u, p_val = mann_whitney_u(cod_r['discrimination_scores'], theo_r['discrimination_scores'])
    c5_pass = p_val < 0.01
    print(f"  C5: Mann-Whitney p < 0.01 (Codicillus vs Theophilus)? "
          f"(U={u:.1f}, p={p_val:.5f}) → {'PASS' if c5_pass else 'FAIL'}")

    n_pass = sum([c1_pass, c2_pass, c3_pass, c4_pass, c5_pass])
    print(f"\n  PASS COUNT: {n_pass}/5")

    if n_pass >= 4:
        verdict = "DISTILLATION-DISCRIMINATIVE FEATURES VALIDATED — proceed to Phase 3-4"
    elif n_pass >= 2:
        verdict = "PARTIAL — some discrimination but features need refinement"
    else:
        verdict = "FEATURE DESIGN FAILED — text-level distillation discrimination not tractable"

    print(f"\n  VERDICT: {verdict}")

    # Top distillation-scored chapters per corpus (qualitative check)
    print("\n" + "=" * 90)
    print("QUALITATIVE CHECK: Top-5 most distillation-dense paragraphs per corpus")
    print("=" * 90)
    for r, paras in [(cod_r, cod), (rup_r, rup), (theo_r, theo_paras)]:
        scores = list(zip(r['discrimination_scores'], range(len(paras))))
        scores.sort(key=lambda x: -x[0])
        print(f"\n  {r['label']}:")
        for s, idx in scores[:3]:
            snippet = ' '.join(paras[idx][:15])
            print(f"    score={s:+.4f}: {snippet}...")

    # Save
    out = {
        'method': 'PHASE_723 v1 distillation-discriminative matcher',
        'feature_lists': {
            'distillation_markers': sorted(DISTILLATION_MARKERS),
            'metalwork_markers': sorted(METALWORK_MARKERS),
            'excluded_ambiguous': sorted(EXCLUDED_AMBIGUOUS),
        },
        'results': {
            'codicillus': {k: v for k, v in cod_r.items() if k != 'discrimination_scores'},
            'rupescissa': {k: v for k, v in rup_r.items() if k != 'discrimination_scores'},
            'theophilus_body': {k: v for k, v in theo_r.items() if k != 'discrimination_scores'},
        },
        'criteria': {
            'c1_codicillus_pos': {'observed': cod_disc, 'pass': c1_pass},
            'c2_rupescissa_pos': {'observed': rup_disc, 'pass': c2_pass},
            'c3_theophilus_neg': {'observed': theo_disc, 'pass': c3_pass},
            'c4_separation': {'observed': diff, 'pass': c4_pass},
            'c5_mannwhitney': {'u': u, 'p': p_val, 'pass': c5_pass},
            'n_pass': n_pass,
        },
        'verdict': verdict,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str), encoding='utf-8')
    print(f"\nWritten: {OUT_PATH.relative_to(ROOT)}")


if __name__ == '__main__':
    main()
