#!/usr/bin/env python
"""
Test 10 falsifiable predictions from character-level glyph theory.
Tests against H-track transcript (37,957 tokens).
"""
import sys
sys.path.insert(0, r'C:\git\voynich')
from scripts.voynich import Transcript
from collections import Counter, defaultdict

tx = Transcript()

# Collect all valid tokens
all_tokens = []
for tok in tx.all(h_only=True):
    if tok.word.strip() and '*' not in tok.word:
        all_tokens.append(tok)

# Build line-level structure
lines = defaultdict(list)
for tok in all_tokens:
    lines[(tok.folio, tok.line)].append(tok)

all_words = [tok.word for tok in all_tokens]

print("=" * 70)
print("PREDICTION TEST: 10 Falsifiable Claims from Glyph Dictionary v1.0")
print("=" * 70)
print(f"Total lines: {len(lines)}")
print(f"Total tokens: {len(all_tokens)}")
print()

# =====================================================================
# PREDICTION 1: Herbal folios (f1r-f6v) lines start with ch/sh/k/t/p/f
# =====================================================================
print("-" * 70)
print("PREDICTION 1: Herbal lines (f1r-f6v) start with ch/sh/k/t/p/f")
print("-" * 70)

herbal_folios = {'f1r', 'f1v', 'f2r', 'f2v', 'f3r', 'f3v',
                 'f4r', 'f4v', 'f5r', 'f5v', 'f6r', 'f6v'}
pred1_pass = 0
pred1_fail = 0
pred1_fail_examples = []

valid_starts = ('ch', 'sh', 'k', 't', 'p', 'f')

for (folio, line), toks in sorted(lines.items()):
    if folio in herbal_folios and toks:
        first = toks[0].word
        if first.startswith(valid_starts):
            pred1_pass += 1
        else:
            pred1_fail += 1
            if len(pred1_fail_examples) < 10:
                pred1_fail_examples.append(f"  {folio}.{line}: '{first}'")

total1 = pred1_pass + pred1_fail
if total1 > 0:
    print(f"Lines starting with ch/sh/k/t/p/f: {pred1_pass}/{total1} ({100*pred1_pass/total1:.1f}%)")
    print(f"Lines starting with OTHER: {pred1_fail}/{total1} ({100*pred1_fail/total1:.1f}%)")
    if pred1_fail_examples:
        print(f"Counter-examples (first 10):")
        for ex in pred1_fail_examples:
            print(ex)
    # What do failures start with?
    fail_starts = Counter()
    for (folio, line), toks in sorted(lines.items()):
        if folio in herbal_folios and toks:
            first = toks[0].word
            if not first.startswith(valid_starts):
                fail_starts[first[:3]] += 1
    if fail_starts:
        print(f"Failure initial chars: {fail_starts.most_common(15)}")
print()

# =====================================================================
# PREDICTION 2: r never opens a line
# =====================================================================
print("-" * 70)
print("PREDICTION 2: r never opens a line (expected: 0)")
print("-" * 70)

r_opens = 0
r_open_examples = []

for tok in all_tokens:
    if tok.line_initial and tok.word.startswith('r'):
        r_opens += 1
        if len(r_open_examples) < 15:
            r_open_examples.append(f"  {tok.folio}.{tok.line}: '{tok.word}'")

total_lines = sum(1 for tok in all_tokens if tok.line_initial)
print(f"Lines opening with r-token: {r_opens}/{total_lines}")
if r_open_examples:
    print(f"Counter-examples:")
    for ex in r_open_examples:
        print(ex)
print()

# =====================================================================
# PREDICTION 3: d never closes a line
# =====================================================================
print("-" * 70)
print("PREDICTION 3: d never closes a line (last token ends in d)")
print("-" * 70)

d_closes = 0
d_close_examples = []

for tok in all_tokens:
    if tok.line_final and tok.word.endswith('d'):
        d_closes += 1
        if len(d_close_examples) < 15:
            d_close_examples.append(f"  {tok.folio}.{tok.line}: '{tok.word}'")

total_line_finals = sum(1 for tok in all_tokens if tok.line_final)
print(f"Lines ending with d-final token: {d_closes}/{total_line_finals} ({100*d_closes/total_line_finals:.1f}%)")
if d_close_examples:
    print(f"Examples (first 15):")
    for ex in d_close_examples:
        print(ex)
print()

# =====================================================================
# PREDICTION 4: q never appears alone or as sole operation
# =====================================================================
print("-" * 70)
print("PREDICTION 4: q never appears alone (expected: 0)")
print("-" * 70)

q_alone = []
for tok in all_tokens:
    if tok.word == 'q':
        q_alone.append(f"  {tok.folio}.{tok.line}")

print(f"Standalone 'q' tokens: {len(q_alone)}")
if q_alone:
    for ex in q_alone[:10]:
        print(ex)

# Also: q without following o
q_with_o = 0
q_without_o = 0
q_other_examples = Counter()
for word in all_words:
    if 'q' in word:
        if 'qo' in word:
            q_with_o += 1
        else:
            q_without_o += 1
            q_other_examples[word] += 1

print(f"q-tokens with 'qo': {q_with_o}")
print(f"q-tokens WITHOUT 'qo': {q_without_o}")
if q_other_examples:
    print(f"q without qo (top 10): {q_other_examples.most_common(10)}")
print()

# =====================================================================
# PREDICTION 5: sh always has o or l in same word
# =====================================================================
print("-" * 70)
print("PREDICTION 5: sh-tokens always contain o or l")
print("-" * 70)

sh_with_ol = 0
sh_without_ol = 0
sh_without_examples = Counter()

for word in all_words:
    if 'sh' in word:
        if 'o' in word or 'l' in word:
            sh_with_ol += 1
        else:
            sh_without_ol += 1
            sh_without_examples[word] += 1

total_sh = sh_with_ol + sh_without_ol
if total_sh > 0:
    print(f"sh-tokens with o or l: {sh_with_ol}/{total_sh} ({100*sh_with_ol/total_sh:.1f}%)")
    print(f"sh-tokens WITHOUT o or l: {sh_without_ol}/{total_sh} ({100*sh_without_ol/total_sh:.1f}%)")
    if sh_without_examples:
        print(f"Counter-examples (top 15): {sh_without_examples.most_common(15)}")
print()

# =====================================================================
# PREDICTION 6: kydain/kydainy clusters at line starts / folio starts
# =====================================================================
print("-" * 70)
print("PREDICTION 6: kydain* appears at line starts / first lines")
print("-" * 70)

kydain_total = 0
kydain_line_start = 0
kydain_par_start = 0
kydain_positions = []

for tok in all_tokens:
    if 'ydain' in tok.word or tok.word.startswith('kydain'):
        kydain_total += 1
        kydain_positions.append(f"  {tok.folio}.{tok.line}: '{tok.word}' (line_initial={tok.line_initial}, par_initial={tok.par_initial})")
        if tok.line_initial:
            kydain_line_start += 1
        if tok.par_initial:
            kydain_par_start += 1

print(f"Total kydain-like tokens: {kydain_total}")
if kydain_total > 0:
    print(f"  Line-initial: {kydain_line_start}/{kydain_total} ({100*kydain_line_start/kydain_total:.1f}%)")
    print(f"  Paragraph-initial: {kydain_par_start}/{kydain_total} ({100*kydain_par_start/kydain_total:.1f}%)")
    for p in kydain_positions[:15]:
        print(p)
else:
    # Broader search
    print("  No exact 'kydain' found. Searching similar patterns...")
    similar = Counter()
    for word in all_words:
        if 'dain' in word or 'daiin' in word:
            similar[word] += 1
    print(f"  Tokens with 'dain' or 'daiin': {similar.most_common(15)}")

    # Check 'daiin' position
    daiin_total = 0
    daiin_line_start = 0
    for tok in all_tokens:
        if tok.word == 'daiin' or tok.word == 'dain':
            daiin_total += 1
            if tok.line_initial:
                daiin_line_start += 1
    if daiin_total:
        print(f"  'daiin'/'dain' line-initial: {daiin_line_start}/{daiin_total} ({100*daiin_line_start/daiin_total:.1f}%)")
print()

# =====================================================================
# PREDICTION 7: m and p don't coexist in same word or line
# =====================================================================
print("-" * 70)
print("PREDICTION 7: m and p don't coexist in same word or line")
print("-" * 70)

# Same word
mp_same_word = Counter()
for word in all_words:
    if 'm' in word and 'p' in word:
        mp_same_word[word] += 1

print(f"Tokens containing both m and p: {sum(mp_same_word.values())} unique types: {len(mp_same_word)}")
if mp_same_word:
    print(f"  Top 15: {mp_same_word.most_common(15)}")

# Same line
mp_same_line = 0
mp_line_examples = []
for (folio, line), toks in sorted(lines.items()):
    words = [t.word for t in toks]
    has_m = any('m' in w for w in words)
    has_p = any('p' in w for w in words)
    if has_m and has_p:
        mp_same_line += 1
        if len(mp_line_examples) < 5:
            mp_line_examples.append(f"  {folio}.{line}: {' '.join(words[:8])}...")

print(f"Lines with both m-token and p-token: {mp_same_line}/{len(lines)} ({100*mp_same_line/len(lines):.1f}%)")
if mp_line_examples:
    for ex in mp_line_examples:
        print(ex)
print()

# =====================================================================
# PREDICTION 8: f followed by ch/m/g in same or next line
# =====================================================================
print("-" * 70)
print("PREDICTION 8: f-tokens -> ch/m/g in same or next line")
print("-" * 70)

sorted_keys = sorted(lines.keys())
key_to_idx = {k: i for i, k in enumerate(sorted_keys)}

f_lines = 0
f_followed = 0

for idx, key in enumerate(sorted_keys):
    toks = lines[key]
    words = [t.word for t in toks]
    has_f = any(w.startswith('f') for w in words)
    if not has_f:
        continue
    f_lines += 1

    # Check same line
    same = any('ch' in w or w.endswith('m') or w.endswith('g') or w.startswith('g') for w in words)

    # Check next line (same folio)
    next_match = False
    if idx + 1 < len(sorted_keys):
        nk = sorted_keys[idx + 1]
        if nk[0] == key[0]:  # Same folio
            nwords = [t.word for t in lines[nk]]
            next_match = any('ch' in w or w.endswith('m') or w.endswith('g') or w.startswith('g') for w in nwords)

    if same or next_match:
        f_followed += 1

# Baseline
baseline = sum(1 for toks in lines.values()
               if any('ch' in t.word or t.word.endswith('m') or t.word.endswith('g') or t.word.startswith('g') for t in toks))

print(f"Lines with f-tokens: {f_lines}")
if f_lines > 0:
    print(f"  Followed by ch/m/g: {f_followed}/{f_lines} ({100*f_followed/f_lines:.1f}%)")
    print(f"  Baseline (any line has ch/m/g): {baseline}/{len(lines)} ({100*baseline/len(lines):.1f}%)")
print()

# =====================================================================
# PREDICTION 9: ar appears as fixed unit
# =====================================================================
print("-" * 70)
print("PREDICTION 9: 'ar' appears as fixed unit")
print("-" * 70)

ar_count = sum(1 for w in all_words if 'ar' in w)
a_total = sum(1 for w in all_words if 'a' in w)

print(f"Tokens containing 'ar': {ar_count}")
print(f"Tokens containing 'a' (any): {a_total}")
if a_total > 0:
    print(f"  ar/a ratio: {100*ar_count/a_total:.1f}% of a-tokens contain ar")

# a + next char frequency
a_bigrams = Counter()
for w in all_words:
    for i, ch in enumerate(w):
        if ch == 'a' and i + 1 < len(w):
            a_bigrams[f"a{w[i+1]}"] += 1

print(f"\n'a'+next character frequency (top 10):")
for bigram, count in a_bigrams.most_common(10):
    print(f"  {bigram}: {count}")
print()

# =====================================================================
# PREDICTION 10: Currier B has more sh/y/o, less ch than A
# =====================================================================
print("-" * 70)
print("PREDICTION 10: Currier B has more sh/y/o, less ch than A")
print("-" * 70)

a_words = [tok.word for tok in tx.currier_a()]
b_words = [tok.word for tok in tx.currier_b()]

a_total_chars = sum(len(w) for w in a_words)
b_total_chars = sum(len(w) for w in b_words)

# Character frequencies
a_chars = Counter()
b_chars = Counter()
for w in a_words:
    for ch in w:
        a_chars[ch] += 1
for w in b_words:
    for ch in w:
        b_chars[ch] += 1

print(f"Currier A: {len(a_words)} tokens, {a_total_chars} characters")
print(f"Currier B: {len(b_words)} tokens, {b_total_chars} characters")
print()

# Single chars
for char in ['o', 'y']:
    a_pct = 100 * a_chars[char] / a_total_chars if a_total_chars else 0
    b_pct = 100 * b_chars[char] / b_total_chars if b_total_chars else 0
    diff = "MORE in B" if b_pct > a_pct else "LESS in B"
    print(f"  '{char}': A={a_pct:.2f}%, B={b_pct:.2f}% -> {diff} (predicted: MORE in B)")

# Digraphs
for digraph in ['sh', 'ch']:
    a_count = sum(w.count(digraph) for w in a_words)
    b_count = sum(w.count(digraph) for w in b_words)
    a_rate = 100 * a_count / len(a_words) if a_words else 0
    b_rate = 100 * b_count / len(b_words) if b_words else 0
    diff = "MORE in B" if b_rate > a_rate else "LESS in B"
    expected = "MORE in B" if digraph == 'sh' else "LESS in B"
    print(f"  '{digraph}': A={a_rate:.2f}%, B={b_rate:.2f}% per token -> {diff} (predicted: {expected})")
print()

# =====================================================================
# VERDICT SUMMARY
# =====================================================================
print("=" * 70)
print("VERDICT SUMMARY")
print("=" * 70)
