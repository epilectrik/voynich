"""
Controlled recto/verso tests:
1. Section-stratified permutation (shuffle r/v pairings only within sections)
2. Adjacent-folio control (are adjacent different-leaf pairs equally similar?)
3. Without-qo cosine (does it survive removing the dominant channel?)
4. Broader baseline (shuffle against all 83 folios, not just r/v set)
"""
import sys, io, re, math, random, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, '.')
from scripts.voynich import Transcript, Morphology
from collections import Counter, defaultdict

tx = Transcript()
morph = Morphology()

# Load section info from atlas
try:
    with open('phases/ATOM_FOLIO_ATLAS/results/folio_atlas.json', encoding='utf-8') as f:
        atlas = json.load(f)
except:
    atlas = {}

def get_section(folio):
    if folio in atlas:
        return atlas[folio].get('section', '?')
    m = re.search(r'(\d+)', folio)
    if m:
        num = int(m.group(1))
        if 75 <= num <= 84: return 'B'
        if 103 <= num <= 116: return 'S'
    return 'H'

# Compute prefix distributions
folio_prefixes = defaultdict(Counter)
folio_order = []
seen = set()
for t in tx.currier_b():
    if '*' in t.word or not t.word.strip():
        continue
    if t.placement.startswith('L'):
        continue
    a = morph.atomize(t.word)
    pfx = a.prefix if a and a.prefix else 'bare'
    folio_prefixes[t.folio][pfx] += 1
    if t.folio not in seen:
        seen.add(t.folio)
        folio_order.append(t.folio)

all_prefixes = set()
for c in folio_prefixes.values():
    all_prefixes.update(c.keys())

def to_vector(counter, exclude=None):
    total = sum(v for k, v in counter.items() if k != exclude)
    if total == 0: return {}
    return {p: counter[p] / total for p in all_prefixes if p != exclude}

def cosine_sim(v1, v2):
    keys = set(v1.keys()) | set(v2.keys())
    dot = sum(v1.get(k, 0) * v2.get(k, 0) for k in keys)
    mag1 = math.sqrt(sum(v1.get(k, 0)**2 for k in keys))
    mag2 = math.sqrt(sum(v2.get(k, 0)**2 for k in keys))
    if mag1 == 0 or mag2 == 0: return 0
    return dot / (mag1 * mag2)

folio_vectors = {f: to_vector(c) for f, c in folio_prefixes.items()}
folio_vectors_noqo = {f: to_vector(c, exclude='qo') for f, c in folio_prefixes.items()}

# Find r/v pairs
pairs = []
folios_by_num = defaultdict(dict)
for f in folio_vectors:
    m = re.match(r'f(\d+)(r|v)$', f)
    if m:
        folios_by_num[int(m.group(1))][m.group(2)] = f

for num in sorted(folios_by_num.keys()):
    sides = folios_by_num[num]
    if 'r' in sides and 'v' in sides:
        rf, vf = sides['r'], sides['v']
        sec = get_section(rf)
        sim = cosine_sim(folio_vectors[rf], folio_vectors[vf])
        sim_noqo = cosine_sim(folio_vectors_noqo[rf], folio_vectors_noqo[vf])
        pairs.append((rf, vf, sim, sim_noqo, sec))

actual_mean = sum(s for _, _, s, _, _ in pairs) / len(pairs)
actual_mean_noqo = sum(s for _, _, _, s, _ in pairs) / len(pairs)

print(f"=== RECTO/VERSO CONTROLLED ANALYSIS ===\n")
print(f"Pairs: {len(pairs)}")
print(f"Actual mean cosine (with qo): {actual_mean:.4f}")
print(f"Actual mean cosine (WITHOUT qo): {actual_mean_noqo:.4f}")

# === TEST 1: Section-stratified permutation ===
print(f"\n=== TEST 1: SECTION-STRATIFIED PERMUTATION ===\n")

section_pairs = defaultdict(list)
for rf, vf, sim, sim_noqo, sec in pairs:
    section_pairs[sec].append((rf, vf, sim))

print("Sections:", {s: len(p) for s, p in section_pairs.items()})

n_perm = 10000
perm_means = []
for _ in range(n_perm):
    total_sim = 0
    count = 0
    for sec, sec_ps in section_pairs.items():
        if len(sec_ps) < 2:
            for _, _, s in sec_ps:
                total_sim += s
                count += 1
            continue
        r_folios = [rf for rf, vf, s in sec_ps]
        v_folios = [vf for rf, vf, s in sec_ps]
        random.shuffle(v_folios)
        for i in range(len(r_folios)):
            total_sim += cosine_sim(folio_vectors[r_folios[i]], folio_vectors[v_folios[i]])
            count += 1
    perm_means.append(total_sim / count)

mean_perm = sum(perm_means) / n_perm
std_perm = (sum((x - mean_perm)**2 for x in perm_means) / n_perm) ** 0.5
p_section = sum(1 for x in perm_means if x >= actual_mean) / n_perm

print(f"Actual mean cosine: {actual_mean:.4f}")
print(f"Within-section random: {mean_perm:.4f} (std={std_perm:.4f})")
print(f"p-value (section-stratified): {p_section:.4f}")
if p_section < 0.01:
    print("SURVIVES section control!")
elif p_section < 0.05:
    print("Marginally survives section control")
else:
    print("KILLED by section control -- effect is section-level, not leaf-level")

# === TEST 2: Adjacent-folio control ===
print(f"\n=== TEST 2: ADJACENT-FOLIO CONTROL ===\n")

# Compare r/v similarity to adjacent-different-leaf similarity
adj_sims = []
for i in range(len(folio_order) - 1):
    f1, f2 = folio_order[i], folio_order[i+1]
    # Skip if they're recto/verso of the same leaf
    m1 = re.match(r'f(\d+)', f1)
    m2 = re.match(r'f(\d+)', f2)
    if m1 and m2 and m1.group(1) == m2.group(1):
        continue
    sim = cosine_sim(folio_vectors[f1], folio_vectors[f2])
    adj_sims.append((f1, f2, sim))

mean_adj = sum(s for _, _, s in adj_sims) / len(adj_sims)
mean_rv = actual_mean

print(f"Recto/verso mean cosine: {mean_rv:.4f} (n={len(pairs)})")
print(f"Adjacent-different-leaf mean cosine: {mean_adj:.4f} (n={len(adj_sims)})")
print(f"R/V advantage: {mean_rv - mean_adj:+.4f}")

if mean_rv - mean_adj > 0.03:
    print("R/V pairs are MORE similar than adjacent different-leaf pairs.")
    print("The effect is leaf-specific, not just proximity.")
else:
    print("R/V pairs are NOT more similar than adjacent pairs.")
    print("The effect is just sequential proximity (C361).")

# === TEST 3: Without qo ===
print(f"\n=== TEST 3: WITHOUT QO ===\n")

n_perm2 = 10000
perm_noqo = []
for _ in range(n_perm2):
    total_sim = 0
    count = 0
    for sec, sec_ps in section_pairs.items():
        if len(sec_ps) < 2:
            for rf, vf, s in sec_ps:
                total_sim += cosine_sim(folio_vectors_noqo[rf], folio_vectors_noqo[vf])
                count += 1
            continue
        r_folios = [rf for rf, vf, s in sec_ps]
        v_folios = [vf for rf, vf, s in sec_ps]
        random.shuffle(v_folios)
        for i in range(len(r_folios)):
            total_sim += cosine_sim(folio_vectors_noqo[r_folios[i]], folio_vectors_noqo[v_folios[i]])
            count += 1
    perm_noqo.append(total_sim / count)

mean_perm_noqo = sum(perm_noqo) / n_perm2
p_noqo = sum(1 for x in perm_noqo if x >= actual_mean_noqo) / n_perm2

print(f"Without-qo actual mean cosine: {actual_mean_noqo:.4f}")
print(f"Without-qo section-stratified random: {mean_perm_noqo:.4f}")
print(f"Without-qo p-value: {p_noqo:.4f}")
if p_noqo < 0.01:
    print("SURVIVES even without qo -- multi-channel effect confirmed")
else:
    print("Effect is primarily driven by qo (thermal) channel")

# === TEST 4: Broader baseline ===
print(f"\n=== TEST 4: BROADER BASELINE (all 83 folios) ===\n")

all_folios_list = list(folio_vectors.keys())
n_perm3 = 10000
perm_broad = []
r_folios_all = [rf for rf, vf, s, sn, sec in pairs]
for _ in range(n_perm3):
    random_vs = random.sample(all_folios_list, len(r_folios_all))
    sims = [cosine_sim(folio_vectors[r_folios_all[i]], folio_vectors[random_vs[i]]) for i in range(len(r_folios_all))]
    perm_broad.append(sum(sims) / len(sims))

mean_broad = sum(perm_broad) / n_perm3
p_broad = sum(1 for x in perm_broad if x >= actual_mean) / n_perm3

print(f"Actual mean cosine: {actual_mean:.4f}")
print(f"Random-from-all-83 mean: {mean_broad:.4f}")
print(f"p-value (broad baseline): {p_broad:.4f}")
