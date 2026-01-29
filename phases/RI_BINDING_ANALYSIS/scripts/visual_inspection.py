"""
Visual inspection: display a full A folio and a compatible B folio
with RI/PP/INFRA classification marked up for direct observation.
"""

import sys
import json
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology, RecordAnalyzer

tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()

# Load class map for B
class_token_map_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_token_map_path, 'r') as f:
    ctm = json.load(f)
token_to_class = {tok: int(cls) for tok, cls in ctm['token_to_class'].items()}

# Pick a medium-sized A folio
folios = analyzer.get_folios()
folio_sizes = {}
for fol in folios:
    folio_sizes[fol] = len(analyzer.analyze_folio(fol))

# Pick one near the median size with decent RI content
target_size = sorted(folio_sizes.values())[len(folio_sizes)//2]
candidates = [f for f, s in folio_sizes.items() if abs(s - target_size) <= 2]

# Pick the first candidate
a_folio = candidates[0]
print(f"Selected A folio: {a_folio} ({folio_sizes[a_folio]} lines)")
print()

# ============================================================
# Display A folio
# ============================================================
print("=" * 80)
print(f"CURRIER A FOLIO: {a_folio}")
print("=" * 80)
print()
print("Legend: [RI] = Registry-Internal, [PP] = Pipeline-Participating,")
print("        [IN] = Infrastructure, [??] = Unknown")
print()

records = analyzer.analyze_folio(a_folio)

# Collect PP middles for this folio
folio_pp_middles = set()
folio_ri_middles = set()
folio_pp_prefixes = set()
folio_pp_suffixes = set()

for rec in records:
    for t in rec.tokens:
        if t.is_pp and t.middle:
            folio_pp_middles.add(t.middle)
            m = morph.extract(t.word)
            if m.prefix:
                folio_pp_prefixes.add(m.prefix)
            if m.suffix:
                folio_pp_suffixes.add(m.suffix)
        if t.is_ri and t.middle:
            folio_ri_middles.add(t.middle)

for i, rec in enumerate(records):
    line_type = "RI-BEARING" if rec.ri_count > 0 else "PP-PURE"
    print(f"Line {i+1:2d} [{line_type:>10}] ({rec.ri_count}RI {rec.pp_count}PP {rec.infra_count}IN)")

    tokens_display = []
    for t in rec.tokens:
        tag = "RI" if t.is_ri else ("PP" if t.is_pp else ("IN" if t.is_infra else "??"))
        m = morph.extract(t.word)
        parts = []
        if m.articulator:
            parts.append(f"art={m.articulator}")
        if m.prefix:
            parts.append(f"pre={m.prefix}")
        parts.append(f"mid={m.middle}")
        if m.suffix:
            parts.append(f"suf={m.suffix}")
        morph_str = " ".join(parts)
        tokens_display.append(f"  {t.word:16s} [{tag}] {morph_str}")

    for td in tokens_display:
        print(td)
    print()

print(f"FOLIO PP POOL: {len(folio_pp_middles)} PP MIDDLEs, {len(folio_ri_middles)} RI MIDDLEs")
print(f"PP MIDDLEs: {sorted(folio_pp_middles)[:20]}{'...' if len(folio_pp_middles) > 20 else ''}")
print(f"RI MIDDLEs: {sorted(folio_ri_middles)}")
print()

# ============================================================
# Find a compatible B folio
# ============================================================

# Build B token inventory
b_tokens = {}
for token in tx.currier_b():
    w = token.word
    if w in b_tokens:
        continue
    m = morph.extract(w)
    if m.middle:
        b_tokens[w] = (m.prefix, m.middle, m.suffix)

b_middles_set = set(mid for _, mid, _ in b_tokens.values())
b_prefixes_set = set(pref for pref, _, _ in b_tokens.values() if pref)
b_suffixes_set = set(suf for _, _, suf in b_tokens.values() if suf)
b_token_class = {tok: token_to_class[tok] for tok in b_tokens if tok in token_to_class}

# Filter B tokens using this A folio's PP pool
shared_mids = folio_pp_middles & b_middles_set
shared_prefs = folio_pp_prefixes & b_prefixes_set
shared_sufs = folio_pp_suffixes & b_suffixes_set

legal_b_tokens = set()
for tok, (pref, mid, suf) in b_tokens.items():
    if mid in shared_mids:
        if (pref is None or pref in shared_prefs):
            if (suf is None or suf in shared_sufs):
                legal_b_tokens.add(tok)

legal_classes = set(b_token_class[t] for t in legal_b_tokens if t in b_token_class)
print(f"Legal B tokens from this A folio: {len(legal_b_tokens)}")
print(f"Legal B classes: {len(legal_classes)}/49")
print()

# Pick a B folio with high compatibility
b_fol_tokens = defaultdict(list)
for token in tx.currier_b():
    b_fol_tokens[token.folio].append(token.word)

best_b = None
best_score = 0
for bfol, btoks in b_fol_tokens.items():
    legal_count = sum(1 for t in btoks if t in legal_b_tokens)
    score = legal_count / len(btoks) if btoks else 0
    if score > best_score:
        best_score = score
        best_b = bfol

print(f"Best compatible B folio: {best_b} (compatibility: {best_score:.3f})")
print()

# ============================================================
# Display B folio
# ============================================================
print("=" * 80)
print(f"CURRIER B FOLIO: {best_b}")
print("=" * 80)
print()
print("Legend: [LEGAL] = legal under this A folio's PP filter")
print("        [ILLEGAL] = filtered out (MIDDLE/PREFIX/SUFFIX mismatch)")
print()

# Get B folio lines
b_lines = defaultdict(list)
for token in tx.currier_b():
    if token.folio == best_b:
        b_lines[token.line].append(token.word)

for line_num in sorted(b_lines.keys()):
    tokens = b_lines[line_num]
    legal_count = sum(1 for t in tokens if t in legal_b_tokens)
    illegal_count = len(tokens) - legal_count
    print(f"Line {line_num:2s} ({legal_count}/{len(tokens)} legal)")

    for tok in tokens:
        m = morph.extract(tok)
        is_legal = tok in legal_b_tokens
        cls = token_to_class.get(tok, '?')

        parts = []
        if m.prefix:
            parts.append(f"pre={m.prefix}")
        parts.append(f"mid={m.middle}")
        if m.suffix:
            parts.append(f"suf={m.suffix}")
        morph_str = " ".join(parts)

        tag = "LEGAL" if is_legal else "ILLEGAL"

        # Why illegal?
        reason = ""
        if not is_legal and m.middle:
            if m.middle not in shared_mids:
                reason = "(MIDDLE not in A PP pool)"
            elif m.prefix and m.prefix not in shared_prefs:
                reason = "(PREFIX not in A PP pool)"
            elif m.suffix and m.suffix not in shared_sufs:
                reason = "(SUFFIX not in A PP pool)"

        print(f"  {tok:16s} [{tag:>7}] cls={str(cls):>3} {morph_str} {reason}")
    print()

# Summary stats
total_b_tok = sum(len(toks) for toks in b_lines.values())
total_legal = sum(1 for toks in b_lines.values() for t in toks if t in legal_b_tokens)
print(f"B folio summary: {total_legal}/{total_b_tok} tokens legal ({100*total_legal/total_b_tok:.1f}%)")
print(f"Empty lines: {sum(1 for toks in b_lines.values() if not any(t in legal_b_tokens for t in toks))}/{len(b_lines)}")
