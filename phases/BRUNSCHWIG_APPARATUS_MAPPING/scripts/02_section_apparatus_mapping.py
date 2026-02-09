"""Test 02: Section-to-apparatus formal mapping.
Test 03: Positional prefix-operation assignment.

Combine section enrichment, positional data, and MIDDLE selectivity
to map sections to Brunschwig apparatus types and prefixes to operations.
"""
import sys
from pathlib import Path
from collections import Counter, defaultdict
import json
sys.path.insert(0, str(Path(r'C:\git\voynich')))
from scripts.voynich import Transcript, Morphology
from scipy.stats import spearmanr

morph = Morphology()

# Collect all B tokens
all_tokens = []
for tok in Transcript().currier_b():
    w = tok.word
    if not w.strip() or '*' in w:
        continue
    m = morph.extract(w)
    all_tokens.append({
        'word': w, 'morph': m, 'folio': tok.folio, 'line': tok.line,
        'section': tok.section, 'line_initial': tok.line_initial,
        'line_final': tok.line_final, 'par_initial': tok.par_initial,
    })

# Build structures
lines = defaultdict(list)
folio_tokens = defaultdict(list)
for tok in all_tokens:
    lines[(tok['folio'], tok['line'])].append(tok)
    folio_tokens[tok['folio']].append(tok)

sections = sorted(set(t['section'] for t in all_tokens))
target_pfx = ['qo','ch','sh','ok','ot','da','ol','lk','sa','te','ke','pch','lch','tch']

# =============================================
# TEST 02: SECTION-APPARATUS MAPPING
# =============================================
print("=" * 80)
print("TEST 02: SECTION-TO-APPARATUS MAPPING")
print("=" * 80)

# Brunschwig apparatus monitoring requirements
print("""
BRUNSCHWIG APPARATUS MONITORING REQUIREMENTS:

  Balneum Marie (Degree 1):
    Required: REPLENISH water, MONITOR_TEMP (finger test), COOL overnight
    Not needed: REGULATE_FIRE, MONITOR_DRIPS (no fire to regulate)
    Character: Gentle, continuous water management, few check operations

  Standard Alembic (Degree 2):
    Required: SEAL, REGULATE_FIRE, MONITOR_DRIPS, COOL
    Optional: REPLENISH (if using sand/ash bed)
    Character: Moderate fire control, drip timing, sealing critical

  Direct Fire (Degree 3):
    Required: SEAL (critical), REGULATE_FIRE (critical), MONITOR_DRIPS
    Not needed: REPLENISH
    Character: Intense, fire management dominant, high risk

  Precision (any degree, REGIME_4):
    Required: All monitoring + exact timing
    Character: Tight control, high checkpoint density
""")

# Per-section prefix profiles as fingerprints
print("\nSECTION PREFIX FINGERPRINTS:")
print("-" * 70)

sec_pfx_rates = defaultdict(dict)
for sec in sections:
    sec_tokens = [t for t in all_tokens if t['section'] == sec and t['morph'].prefix]
    total = len(sec_tokens)
    if total < 100:
        continue
    pfx_counts = Counter(t['morph'].prefix for t in sec_tokens)
    for pfx in target_pfx:
        sec_pfx_rates[sec][pfx] = pfx_counts.get(pfx, 0) / total * 100

    print(f"\n  {sec} (n={total}):")
    # Key ratios that discriminate apparatus
    qo_rate = sec_pfx_rates[sec].get('qo', 0)
    ch_rate = sec_pfx_rates[sec].get('ch', 0)
    sh_rate = sec_pfx_rates[sec].get('sh', 0)
    lk_rate = sec_pfx_rates[sec].get('lk', 0)
    ol_rate = sec_pfx_rates[sec].get('ol', 0)
    ok_rate = sec_pfx_rates[sec].get('ok', 0)
    da_rate = sec_pfx_rates[sec].get('da', 0)

    ch_sh = ch_rate / sh_rate if sh_rate > 0 else 0
    lk_ol = lk_rate / ol_rate if ol_rate > 0 else 0
    ok_ot = ok_rate / sec_pfx_rates[sec].get('ot', 0.001)

    print(f"    qo={qo_rate:.1f}% ch={ch_rate:.1f}% sh={sh_rate:.1f}% lk={lk_rate:.1f}% ol={ol_rate:.1f}%")
    print(f"    ch/sh={ch_sh:.2f}  lk/ol={lk_ol:.2f}  ok/ot={ok_ot:.2f}  da={da_rate:.1f}%")

# Compute section-level monitoring intensity indicators
print(f"\n\nSECTION MONITORING INTENSITY:")
print("-" * 70)

for sec in sections:
    sec_toks = [t for t in all_tokens if t['section'] == sec]
    if len(sec_toks) < 100:
        continue

    prefixed = [t for t in sec_toks if t['morph'].prefix]
    total_pfx = len(prefixed)

    # Fire-monitoring intensity: lk concentration
    lk_count = sum(1 for t in prefixed if t['morph'].prefix == 'lk')
    fire_monitor = lk_count / total_pfx * 100 if total_pfx > 0 else 0

    # Test/check intensity: ch concentration
    ch_count = sum(1 for t in prefixed if t['morph'].prefix == 'ch')
    test_intensity = ch_count / total_pfx * 100 if total_pfx > 0 else 0

    # Observation intensity: sh concentration
    sh_count = sum(1 for t in prefixed if t['morph'].prefix == 'sh')
    observe_intensity = sh_count / total_pfx * 100 if total_pfx > 0 else 0

    # Continuation intensity: ol (sustained process)
    ol_count = sum(1 for t in prefixed if t['morph'].prefix == 'ol')
    continue_intensity = ol_count / total_pfx * 100 if total_pfx > 0 else 0

    # Setup intensity: da
    da_count = sum(1 for t in prefixed if t['morph'].prefix == 'da')
    setup_intensity = da_count / total_pfx * 100 if total_pfx > 0 else 0

    # Execution intensity: qo
    qo_count = sum(1 for t in prefixed if t['morph'].prefix == 'qo')
    exec_intensity = qo_count / total_pfx * 100 if total_pfx > 0 else 0

    print(f"\n  {sec}:")
    print(f"    fire-monitor(lk): {fire_monitor:>5.1f}%  {'***' if fire_monitor > 3 else '*' if fire_monitor > 1.5 else ''}")
    print(f"    test(ch):         {test_intensity:>5.1f}%")
    print(f"    observe(sh):      {observe_intensity:>5.1f}%")
    print(f"    continue(ol):     {continue_intensity:>5.1f}%  {'***' if continue_intensity > 6 else '*' if continue_intensity > 4 else ''}")
    print(f"    setup(da):        {setup_intensity:>5.1f}%  {'***' if setup_intensity > 7 else '*' if setup_intensity > 5 else ''}")
    print(f"    execute(qo):      {exec_intensity:>5.1f}%  {'***' if exec_intensity > 25 else '*' if exec_intensity > 20 else ''}")

# =============================================
# SECTION-APPARATUS ASSIGNMENT
# =============================================
print(f"\n\n{'='*70}")
print("SECTION-APPARATUS ASSIGNMENT (evidence synthesis)")
print(f"{'='*70}")

assignments = {
    'S': {
        'apparatus': 'Fire methods (Degree 2-3)',
        'evidence': [
            'lk (fire-monitoring) 3.4% = highest of any section (1.78x)',
            'ol (continuation) 3.2% = lowest, below B (6.7%)',
            'qo (execution) 20.6% = standard',
            'ch/sh ratio 2.00 = balanced testing and observation',
        ],
        'brunschwig_match': 'Standard alembic + direct fire: drip monitoring, fire regulation, sealing',
    },
    'B': {
        'apparatus': 'Balneum mariae (Degree 1)',
        'evidence': [
            'ol (continuation) 6.7% = highest of any section (1.47x)',
            'lk (fire-monitoring) 0.8% = very low (0.36x)',
            'qo (execution) 27.5% = highest of any section (1.30x)',
            'sh (observation) 14.8% = elevated',
            'ch/sh ratio 0.96 = observation-dominant (not test-dominant)',
        ],
        'brunschwig_match': 'Balneum mariae: sustained water management, continuous monitoring, less fire regulation',
    },
    'H': {
        'apparatus': 'Gentle/precision (Degree 1, REGIME_4)',
        'evidence': [
            'lk (fire-monitoring) 0.3% = near-zero (0.13x)',
            'ok (gate) 10.4% = highest of any section (1.36x)',
            'da (setup) 8.6% = highest (1.53x)',
            'qo (execution) 11.9% = LOWEST of any section (0.56x)',
            'ch/sh ratio 1.85 = test-dominant (precision)',
        ],
        'brunschwig_match': 'Gentle balneum mariae with precision: tight control, high gating, low fire, exact timing per C494',
    },
    'C': {
        'apparatus': 'Mixed/transitional',
        'evidence': [
            'ot (post-process) 11.1% = highest (1.48x)',
            'tch (preparation) 2.1% = highest (2.33x)',
            'te (preparation) 2.9% = highest (1.91x)',
            'lch (completion) 0.4% = very low (0.27x)',
            'ok (gate) 3.1% = lowest (0.41x)',
        ],
        'brunschwig_match': 'Heavy prep + post-process: may encode rectification-heavy protocols',
    },
    'T': {
        'apparatus': 'Setup-dominant',
        'evidence': [
            'da (setup) 11.4% = highest (2.02x)',
            'sh (observation) 17.2% = highest (1.42x)',
            'ol (continuation) 2.6% = lowest (0.56x)',
            'Small sample (n=662)',
        ],
        'brunschwig_match': 'High setup overhead, general setup instructions?',
    },
}

for sec, info in assignments.items():
    print(f"\n  SECTION {sec}: {info['apparatus']}")
    for e in info['evidence']:
        print(f"    - {e}")
    print(f"    Brunschwig: {info['brunschwig_match']}")

# =============================================
# TEST 03: PREFIX-OPERATION ASSIGNMENT
# =============================================
print(f"\n\n{'='*80}")
print("TEST 03: PREFIX-OPERATION ASSIGNMENT")
print(f"{'='*80}")

# Brunschwig operation frequencies (from BRSC v2.0 audit)
bru_ops = {
    # Preparation (pch/tch already mapped by F-BRU-012)
    'GATHER': 162, 'CHOP': 92, 'STRIP': 32, 'POUND': 14, 'CRUSH': 9,
    # Pre-treatment
    'DRY': 73, 'MIX': 19, 'MACERATE': 12, 'FERMENT': 4,
    # Distillation
    'DISTILL': 227,
    # Mid-process
    'SEAL': 16, 'MONITOR_DRIPS': 18, 'MONITOR_TEMP': 3, 'REGULATE_FIRE': 5, 'COOL': 5, 'REPLENISH': 8,
    # Post-process
    'RECTIFY': 28, 'FILTER': 19, 'POUR': 20, 'STRAIN': 4, 'SETTLE': 3, 'MELT': 7,
    # Storage
    'STORE': 36, 'SEAL_VESSEL': 15, 'RENEW': 4,
}

# Voynich prefix frequencies
pfx_freq = Counter()
for tok in all_tokens:
    if tok['morph'].prefix:
        pfx_freq[tok['morph'].prefix] += 1

# Evidence matrix: each prefix mapped using combined evidence
print("""
EVIDENCE TRIANGULATION:

For each prefix, we combine:
  1. POSITIONAL evidence (C931) — where in the line
  2. SECTION evidence (C930 + Test 02) — which sections
  3. MIDDLE selectivity (Test 01) — what objects it operates on
  4. FREQUENCY (rank) — how common
  5. CO-OCCURRENCE — what other prefixes appear with it

LEGEND:
  [P] = Positional evidence
  [S] = Section evidence
  [M] = Middle selectivity evidence
  [F] = Frequency evidence
  [C] = Co-occurrence evidence
""")

mappings = [
    {
        'prefix': 'pch',
        'freq': pfx_freq.get('pch', 0),
        'operation': 'GATHER/COLLECT',
        'brunschwig_freq': 162,
        'confidence': 'HIGH',
        'evidence': [
            '[P] 48.2% line-initial, 25.5x par-initial (procedure opener)',
            '[S] Even across sections (universal operation)',
            '[M] Selects ed, d, od, eod (material-class MIDDLEs)',
            '[F] Rank 12 prefix / Rank 1 prep operation',
            '[C] Already confirmed by F-BRU-012',
        ],
    },
    {
        'prefix': 'tch',
        'freq': pfx_freq.get('tch', 0),
        'operation': 'CHOP/CUT',
        'brunschwig_freq': 92,
        'confidence': 'HIGH',
        'evidence': [
            '[P] 52.9% line-initial, 10.7x par-initial (procedure opener)',
            '[S] Enriched in C (2.33x) and H (1.82x) sections',
            '[M] Selects eod, dy, od, ed (material/process MIDDLEs)',
            '[F] Rank 14 prefix / Rank 2 prep operation',
            '[C] Already confirmed by F-BRU-012',
        ],
    },
    {
        'prefix': 'sa',
        'freq': pfx_freq.get('sa', 0),
        'operation': 'DRY/MACERATE (pre-treatment)',
        'brunschwig_freq': 73 + 12,
        'confidence': 'MEDIUM',
        'evidence': [
            '[P] 43.8% line-initial (3.89x init/final) = early-phase operation',
            '[S] Slightly B-enriched (1.28x), H-depleted (0.76x)',
            '[M] Selects iin (10.6x), i (11.2x), in (13.6x), r (6.9x) = CONTINUATION MIDDLEs',
            '[M] Jaccard 0.67 with da (shared MIDDLE profile = same functional family)',
            '[M] Jaccard 0.00 with ch/sh/ok/ot/ke/lch/tch (completely different objects)',
            '[F] Rank 9 prefix (n=329) / DRY is rank 1 pre-treatment (n=73)',
        ],
    },
    {
        'prefix': 'te',
        'freq': pfx_freq.get('te', 0),
        'operation': 'STRIP/WASH (preparation)',
        'brunschwig_freq': 32 + 4,
        'confidence': 'MEDIUM',
        'evidence': [
            '[P] 19.7% line-initial (3.35x init/final) = early-phase',
            '[S] Enriched in C (1.91x) and H (1.40x)',
            '[M] Selects dy (10.4x), o, d, ey = observation/material MIDDLEs',
            '[M] Similar MIDDLE profile to ke (Jaccard 0.67)',
            '[F] Rank 10 prefix (n=289) / STRIP is rank 4 prep (n=32)',
        ],
    },
    {
        'prefix': 'qo',
        'freq': pfx_freq.get('qo', 0),
        'operation': 'DISTILL/EXECUTE (core execution)',
        'brunschwig_freq': 227,
        'confidence': 'HIGH',
        'evidence': [
            '[P] init/final 1.19x = uniform distribution (always present)',
            '[S] B-enriched (1.30x) = high execution density in balneum',
            '[M] Selects t (4.2x), ke (4.0x), k (implied) = CORE KERNEL operators exclusively',
            '[M] Jaccard 0.00 with ok/ot/sa (completely non-overlapping)',
            '[F] Rank 1 prefix (n=4069) / DISTILL is most frequent operation',
        ],
    },
    {
        'prefix': 'sh',
        'freq': pfx_freq.get('sh', 0),
        'operation': 'MONITOR (continuous observation)',
        'brunschwig_freq': 18 + 3,
        'confidence': 'HIGH',
        'evidence': [
            '[P] 3.14x init/final = front-loaded in lines (monitoring starts early)',
            '[S] B-enriched (1.22x), T-enriched (1.42x)',
            '[M] Selects eck, eek, ect, ek, ey = OBSERVATION MIDDLEs',
            '[M] Jaccard 0.82 with ch (shared monitoring family)',
            '[C] C929: sh precedes heat adjustment (18.3%), continuous process monitoring',
            '[F] Rank 3 prefix (n=2329) — very common because monitoring is continuous',
        ],
    },
    {
        'prefix': 'ch',
        'freq': pfx_freq.get('ch', 0),
        'operation': 'TEST (discrete state testing)',
        'brunschwig_freq': 0,
        'confidence': 'HIGH',
        'evidence': [
            '[P] init/final 0.54x = mid-to-late (testing after execution)',
            '[S] Slightly H-enriched (1.16x) = precision sections',
            '[M] Selects ck (3.6x), ckh (3.5x), ct (3.6x) = CONTROL MIDDLEs',
            '[C] C929: ch precedes close (1.53x), input (1.98x), iterate (2.01x)',
            '[C] C929: ch = discrete testing (finger test, taste test, clarity check)',
            '[F] Rank 2 prefix (n=3492) — very common because testing is frequent',
        ],
        'note': 'Not a single Brunschwig operation — ch is the universal test/check verb',
    },
    {
        'prefix': 'lk',
        'freq': pfx_freq.get('lk', 0),
        'operation': 'MONITOR_DRIPS / REGULATE_FIRE (fire-method monitoring)',
        'brunschwig_freq': 18 + 5,
        'confidence': 'HIGH',
        'evidence': [
            '[P] init/final 0.17x = mid-to-late (during distillation)',
            '[S] 81.7% in section S (1.78x) = fire-method specific (C930)',
            '[M] Selects aiin (4.7x), ain (4.5x), ch (4.2x), ech (9.3x) = checkpoint MIDDLEs',
            '[M] Completely avoids k, t, ke (0/2068, 0/562, 0/421) = not thermal execution',
            '[M] Jaccard 0.18 with ch/sh (structurally distinct from general monitoring)',
            '[F] Rank 8 prefix (n=438) / MONITOR_DRIPS+REGULATE = 23 in Brunschwig',
        ],
    },
    {
        'prefix': 'ok',
        'freq': pfx_freq.get('ok', 0),
        'operation': 'SEAL/GATE (sealing + process gating)',
        'brunschwig_freq': 16 + 15,
        'confidence': 'MEDIUM',
        'evidence': [
            '[P] init/final 0.50x = mid-execution (applied during process)',
            '[S] H-enriched (1.36x), C-depleted (0.41x)',
            '[M] Selects ain (5.3x), aiin (4.6x), al (4.3x), ar (3.5x) = CHECKPOINT/CLOSE MIDDLEs',
            '[M] Jaccard 0.82 with ot (shared functional family)',
            '[M] Avoids k, t, ke (all zero) = not thermal execution',
            '[F] Rank 4 prefix (n=1476) / SEAL+SEAL_VESSEL = 31',
        ],
    },
    {
        'prefix': 'ot',
        'freq': pfx_freq.get('ot', 0),
        'operation': 'RECTIFY/FILTER/POUR (post-process)',
        'brunschwig_freq': 28 + 19 + 20,
        'confidence': 'MEDIUM',
        'evidence': [
            '[P] init/final 0.36x = LATE position (post-distillation)',
            '[S] C-enriched (1.48x), B-depleted (0.67x)',
            '[M] Selects al (4.6x), am (4.3x), ar (4.0x), ain (3.6x) = CLOSE/FINALIZE MIDDLEs',
            '[M] Jaccard 0.82 with ok (sister pair, similar objects)',
            '[M] Avoids k, t, iin, ke (all zero)',
            '[F] Rank 5 prefix (n=1448) / RECTIFY+FILTER+POUR = 67',
        ],
    },
    {
        'prefix': 'da',
        'freq': pfx_freq.get('da', 0),
        'operation': 'SETUP/MIX/REPLENISH (setup + maintenance)',
        'brunschwig_freq': 19 + 8,
        'confidence': 'MEDIUM',
        'evidence': [
            '[P] init/final 1.15x = BIMODAL (both setup and teardown)',
            '[S] H-enriched (1.53x), T-enriched (2.02x) = preparation-heavy sections',
            '[M] Selects iin (10.4x), r (6.9x), i (8.2x), in (7.9x), m (11.1x) = CONTINUATION MIDDLEs',
            '[M] Jaccard 0.67 with sa (shared continuation objects)',
            '[M] Jaccard 0.00 with ch/sh/ok/ot (completely different domain)',
            '[F] Rank 6 prefix (n=1083) / MIX+REPLENISH = 27',
        ],
    },
    {
        'prefix': 'ol',
        'freq': pfx_freq.get('ol', 0),
        'operation': 'STORE/CONTINUE (sustained operations, storage)',
        'brunschwig_freq': 36 + 4,
        'confidence': 'MEDIUM',
        'evidence': [
            '[P] init/final 0.40x = FINAL position (end-of-procedure)',
            '[S] B-enriched (1.47x) = water-bath operations (sustained)',
            '[M] Selects sh (10.3x), kee (7.1x), ch (5.7x), k (dominant) = KERNEL operators',
            '[M] Top MIDDLE is k in ALL sections (k=108 in B, k=57 in S)',
            '[M] Avoids edy, ey, iin, ed, eo (all zero) = no observation targets',
            '[C] Anti-correlated with lk across folios (rho=-0.147, not significant but negative)',
            '[F] Rank 7 prefix (n=875) / STORE = 36',
        ],
    },
    {
        'prefix': 'ke',
        'freq': pfx_freq.get('ke', 0),
        'operation': 'COOL/SETTLE (thermal equilibration)',
        'brunschwig_freq': 5 + 3,
        'confidence': 'LOW-MEDIUM',
        'evidence': [
            '[P] init/final 0.29x = LATE position',
            '[S] H-enriched (1.37x), C-depleted (0.45x)',
            '[M] Selects dy (7.3x), o (5.0x), eo (2.6x) = observation/state MIDDLEs',
            '[M] Similar MIDDLE profile to te (Jaccard 0.67)',
            '[M] Avoids k, l, t, iin, r (all zero)',
            '[F] Rank 11 prefix (n=259) / COOL+SETTLE = 8',
        ],
    },
    {
        'prefix': 'lch',
        'freq': pfx_freq.get('lch', 0),
        'operation': 'POUR/STRAIN (liquid transfer)',
        'brunschwig_freq': 20 + 4,
        'confidence': 'LOW-MEDIUM',
        'evidence': [
            '[P] init/final 0.40x = FINAL position',
            '[S] B-enriched (1.30x), H-depleted (0.24x), C-depleted (0.27x)',
            '[M] Selects edy (4.1x), ey (3.6x) = OBSERVATION MIDDLEs',
            '[M] Avoids k, t, iin, aiin, ke (all zero) = no kernel or checkpoint targets',
            '[C] Co-occurs with lk (1.39x enriched on same lines)',
            '[F] Rank 13 prefix (n=315) / POUR+STRAIN = 24',
        ],
    },
]

for m in mappings:
    pfx = m['prefix']
    print(f"\n  {pfx:<6} -> {m['operation']}")
    print(f"         Voynich freq: {m['freq']:>5}  Brunschwig freq: {m['brunschwig_freq']:>4}  Confidence: {m['confidence']}")
    for e in m['evidence']:
        print(f"         {e}")
    if 'note' in m:
        print(f"         NOTE: {m['note']}")

# =============================================
# FREQUENCY RANK COMPARISON
# =============================================
print(f"\n\n{'='*70}")
print("FREQUENCY RANK COMPARISON: Brunschwig vs Voynich")
print(f"{'='*70}")

# Map operations to phase groups, match with prefix assignments
phase_map = {
    'PREPARATION': {'bru': 162+92+32+14+9, 'pfx': ['pch','tch','te'], 'pfx_freq': 0},
    'PRE-TREATMENT': {'bru': 73+19+12+4, 'pfx': ['sa'], 'pfx_freq': 0},
    'DISTILLATION': {'bru': 227, 'pfx': ['qo'], 'pfx_freq': 0},
    'MONITORING': {'bru': 18+3+5, 'pfx': ['sh','lk','ch'], 'pfx_freq': 0},
    'POST-PROCESS': {'bru': 28+19+20+4+3+7, 'pfx': ['ot','ke'], 'pfx_freq': 0},
    'COMPLETION': {'bru': 36+15+4+8+5+16, 'pfx': ['ol','ok','da','lch'], 'pfx_freq': 0},
}

for phase, info in phase_map.items():
    info['pfx_freq'] = sum(pfx_freq.get(p, 0) for p in info['pfx'])

print(f"\n{'Phase':<16} {'Bru_freq':>8} {'Bru%':>8} {'Voy_freq':>8} {'Voy%':>8} {'ratio':>8}")
bru_total = sum(v['bru'] for v in phase_map.values())
voy_total = sum(v['pfx_freq'] for v in phase_map.values())

bru_pcts = []
voy_pcts = []
for phase, info in phase_map.items():
    bru_pct = info['bru'] / bru_total * 100
    voy_pct = info['pfx_freq'] / voy_total * 100 if voy_total > 0 else 0
    ratio = voy_pct / bru_pct if bru_pct > 0 else 0
    print(f"  {phase:<16} {info['bru']:>6} {bru_pct:>7.1f}% {info['pfx_freq']:>7} {voy_pct:>7.1f}% {ratio:>7.2f}x")
    bru_pcts.append(bru_pct)
    voy_pcts.append(voy_pct)

rho, p = spearmanr(bru_pcts, voy_pcts)
print(f"\n  Phase-level Spearman rho: {rho:+.3f}  p={p:.4f}")

# Save results
out = {
    'assignments': {sec: {'apparatus': info['apparatus'], 'evidence': info['evidence']} for sec, info in assignments.items()},
    'prefix_operations': {m['prefix']: {'operation': m['operation'], 'confidence': m['confidence'], 'freq': m['freq'], 'bru_freq': m['brunschwig_freq']} for m in mappings},
    'phase_comparison': {phase: {'bru_freq': info['bru'], 'voy_freq': info['pfx_freq'], 'prefixes': info['pfx']} for phase, info in phase_map.items()},
    'phase_spearman_rho': round(rho, 3),
    'phase_spearman_p': round(p, 4),
}

out_path = Path(r'C:\git\voynich\phases\BRUNSCHWIG_APPARATUS_MAPPING\results\02_apparatus_mapping.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=2)
print(f"\nResults saved to {out_path}")
