"""Compare C section vs Z section - what makes them different?"""
from apps.azc_folio_animator.core.folio_loader import FolioLoader
from collections import Counter

loader = FolioLoader()
loader.load()

# Section assignments
c_folios = ['f57v', 'f67v2', 'f68v3', 'f69r', 'f69v', 'f70r1', 'f70r2']
z_folios = ['f70v1', 'f70v2', 'f71r', 'f71v', 'f72r1', 'f72r2', 'f72r3', 'f72v1', 'f72v2', 'f72v3', 'f73r', 'f73v']
a_folios = ['f67r1', 'f67r2', 'f67v1', 'f68r1', 'f68r2', 'f68r3', 'f68v1', 'f68v2']

def get_section_vocab(folio_ids):
    """Get combined vocabulary for a section."""
    all_tokens = []
    vocab = set()
    for fid in folio_ids:
        folio = loader.get_folio(fid.lstrip('f'))
        if folio:
            for t in folio.tokens:
                all_tokens.append(t.text)
                vocab.add(t.text)
    return vocab, Counter(all_tokens)

c_vocab, c_freq = get_section_vocab(c_folios)
z_vocab, z_freq = get_section_vocab(z_folios)
a_vocab, a_freq = get_section_vocab(a_folios)

print("=== Section Sizes ===")
print(f"C section: {len(c_folios)} folios, {len(c_vocab)} types, {sum(c_freq.values())} tokens")
print(f"Z section: {len(z_folios)} folios, {len(z_vocab)} types, {sum(z_freq.values())} tokens")
print(f"A section: {len(a_folios)} folios, {len(a_vocab)} types, {sum(a_freq.values())} tokens")

print("\n=== Vocabulary Overlap ===")
cz_shared = c_vocab & z_vocab
ca_shared = c_vocab & a_vocab
za_shared = z_vocab & a_vocab
all_shared = c_vocab & z_vocab & a_vocab

print(f"C & Z shared: {len(cz_shared)} types")
print(f"C & A shared: {len(ca_shared)} types")
print(f"Z & A shared: {len(za_shared)} types")
print(f"All three shared: {len(all_shared)} types")

print("\n=== Unique to Each Section ===")
c_only = c_vocab - z_vocab - a_vocab
z_only = z_vocab - c_vocab - a_vocab
a_only = a_vocab - c_vocab - z_vocab

print(f"C only: {len(c_only)} types")
print(f"Z only: {len(z_only)} types")
print(f"A only: {len(a_only)} types")

print("\n=== Top 15 Tokens in Each Section ===")
print("\nC section:")
for t, c in c_freq.most_common(15):
    in_z = "Z" if t in z_vocab else "-"
    in_a = "A" if t in a_vocab else "-"
    print(f"  {t:12} {c:4}  [{in_z}{in_a}]")

print("\nZ section:")
for t, c in z_freq.most_common(15):
    in_c = "C" if t in c_vocab else "-"
    in_a = "A" if t in a_vocab else "-"
    print(f"  {t:12} {c:4}  [{in_c}{in_a}]")

print("\n=== Distinctive Tokens (high in one, absent in other) ===")
print("\nHigh in C, absent in Z:")
c_not_z = [(t, c) for t, c in c_freq.most_common(50) if t not in z_vocab]
for t, c in c_not_z[:10]:
    print(f"  {t:12} {c:4}")

print("\nHigh in Z, absent in C:")
z_not_c = [(t, c) for t, c in z_freq.most_common(50) if t not in c_vocab]
for t, c in z_not_c[:10]:
    print(f"  {t:12} {c:4}")

# Get Currier A vocabulary for comparison
test_folios = ['1r', '1v', '2r', '3r', '4r', '5r', '10r', '15r', '20r']
currier_a_vocab = set()
currier_a_freq = Counter()
for fid in test_folios:
    folio = loader.get_folio(fid)
    if folio:
        for t in folio.tokens:
            currier_a_vocab.add(t.text)
            currier_a_freq[t.text] += 1

print("\n=== Currier A Compatibility ===")
c_currier_overlap = c_vocab & currier_a_vocab
z_currier_overlap = z_vocab & currier_a_vocab

print(f"C overlaps with Currier A: {len(c_currier_overlap)} types")
print(f"Z overlaps with Currier A: {len(z_currier_overlap)} types")

# By token occurrence
c_currier_tokens = sum(currier_a_freq[t] for t in c_currier_overlap)
z_currier_tokens = sum(currier_a_freq[t] for t in z_currier_overlap)
total_currier = sum(currier_a_freq.values())

print(f"C covers {c_currier_tokens}/{total_currier} ({100*c_currier_tokens/total_currier:.1f}%) of Currier A tokens")
print(f"Z covers {z_currier_tokens}/{total_currier} ({100*z_currier_tokens/total_currier:.1f}%) of Currier A tokens")
