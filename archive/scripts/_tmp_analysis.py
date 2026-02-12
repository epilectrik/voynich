import json
from collections import defaultdict

d = json.load(open('C:/git/voynich/data/middle_dictionary.json'))
middles = d['middles']

# Group by character length
by_len = defaultdict(list)
for name, entry in middles.items():
    by_len[len(name)].append((name, entry))

total_tokens_all = sum(e['token_count'] for _, e in middles.items())
print(f'Total unique middles: {len(middles)}')
print(f'Total token count (sum of all): {total_tokens_all}')
print()

print('=' * 70)
print('GROUP SUMMARY BY CHARACTER LENGTH')
print('=' * 70)
for length in sorted(by_len.keys()):
    entries = by_len[length]
    total_tokens = sum(e['token_count'] for _, e in entries)
    pct = (total_tokens / total_tokens_all) * 100
    print(f'  {length}-char: {len(entries):4d} unique middles, {total_tokens:6d} total tokens ({pct:.1f}%)')

print()
# 5+ combined
entries_5plus = []
for length in sorted(by_len.keys()):
    if length >= 5:
        entries_5plus.extend(by_len[length])
total_5plus = sum(e['token_count'] for _, e in entries_5plus)
pct_5plus = (total_5plus / total_tokens_all) * 100
print(f'  5+-char combined: {len(entries_5plus):4d} unique middles, {total_5plus:6d} total tokens ({pct_5plus:.1f}%)')

# Distribution summary
tokens_1 = sum(e['token_count'] for _, e in by_len.get(1, []))
tokens_2 = sum(e['token_count'] for _, e in by_len.get(2, []))
tokens_3 = sum(e['token_count'] for _, e in by_len.get(3, []))
tokens_4 = sum(e['token_count'] for _, e in by_len.get(4, []))
print()
print('=' * 70)
print('DISTRIBUTION ANALYSIS')
print('=' * 70)
print(f'  1-char: {tokens_1:6d} tokens = {tokens_1/total_tokens_all*100:.1f}%')
print(f'  2-char: {tokens_2:6d} tokens = {tokens_2/total_tokens_all*100:.1f}%')
print(f'  3-char: {tokens_3:6d} tokens = {tokens_3/total_tokens_all*100:.1f}%')
print(f'  4-char: {tokens_4:6d} tokens = {tokens_4/total_tokens_all*100:.1f}%')
print(f'  5+char: {total_5plus:6d} tokens = {pct_5plus:.1f}%')

print()
print('=' * 70)
print('SECTION 1: ALL 1-CHAR MIDDLES (full entries)')
print('=' * 70)
one_chars = sorted(by_len.get(1, []), key=lambda x: -x[1]['token_count'])
for name, entry in one_chars:
    kernel = entry.get('kernel', 'null')
    regime = entry.get('regime', 'null')
    gloss = entry.get('gloss', 'null')
    count = entry.get('token_count', 0)
    folio_count = entry.get('folio_count', 'N/A')
    prefix_comp = entry.get('prefix_composites', None)
    prefix_excl = entry.get('prefix_exclusive', None)
    fl_stage = entry.get('fl_stage', None)
    print(f'  "{name}": count={count}, folio_count={folio_count}, kernel={kernel}, regime={regime}, gloss="{gloss}"')
    if prefix_comp:
        print(f'         prefix_composites: {list(prefix_comp.keys())}')
    if prefix_excl is not None:
        print(f'         prefix_exclusive: {prefix_excl}')
    if fl_stage is not None:
        print(f'         fl_stage: {fl_stage}')
    # Show all fields
    extra_keys = set(entry.keys()) - {'kernel', 'regime', 'gloss', 'token_count', 'folio_count', 'example_tokens', 'notes', 'prefix_composites'}
    if extra_keys:
        for k in sorted(extra_keys):
            print(f'         {k}: {entry[k]}')

print()
print('=' * 70)
print('SECTION 2: ALL 2-CHAR MIDDLES (full entries)')
print('=' * 70)
two_chars = sorted(by_len.get(2, []), key=lambda x: -x[1]['token_count'])
for name, entry in two_chars:
    kernel = entry.get('kernel', 'null')
    regime = entry.get('regime', 'null')
    gloss = entry.get('gloss', 'null')
    count = entry.get('token_count', 0)
    folio_count = entry.get('folio_count', 'N/A')
    prefix_comp = entry.get('prefix_composites', None)
    prefix_excl = entry.get('prefix_exclusive', None)
    print(f'  "{name}": count={count}, folio_count={folio_count}, kernel={kernel}, regime={regime}, gloss="{gloss}"')
    if prefix_comp:
        print(f'         prefix_composites: {list(prefix_comp.keys())}')
    if prefix_excl is not None:
        print(f'         prefix_exclusive: {prefix_excl}')
    extra_keys = set(entry.keys()) - {'kernel', 'regime', 'gloss', 'token_count', 'folio_count', 'example_tokens', 'notes', 'prefix_composites'}
    if extra_keys:
        for k in sorted(extra_keys):
            print(f'         {k}: {entry[k]}')

print()
print('=' * 70)
print('SECTION 3: 1-CHAR MIDDLES GROUPED BY KERNEL')
print('=' * 70)
kernel_groups = defaultdict(list)
for name, entry in one_chars:
    k = entry.get('kernel') or 'null'
    kernel_groups[k].append((name, entry))

for kernel in ['K', 'H', 'E', 'KE', 'HE', 'null']:
    if kernel in kernel_groups:
        items = kernel_groups[kernel]
        total = sum(e['token_count'] for _, e in items)
        names = [n for n, _ in items]
        print(f'  kernel={kernel}: {len(items)} middles, {total} tokens')
        for n, e in items:
            print(f'    "{n}": count={e["token_count"]}, gloss="{e.get("gloss")}", regime={e.get("regime")}')

print()
print('=' * 70)
print('SECTION 4: PREFIX EXCLUSIVITY CHECK')
print('=' * 70)
print('Checking all fields in 1-char and 2-char middles for prefix-related keys...')
all_keys_1 = set()
all_keys_2 = set()
for name, entry in by_len.get(1, []):
    all_keys_1.update(entry.keys())
for name, entry in by_len.get(2, []):
    all_keys_2.update(entry.keys())
print(f'  All fields in 1-char entries: {sorted(all_keys_1)}')
print(f'  All fields in 2-char entries: {sorted(all_keys_2)}')

# Check for prefix_composites in 1-char
has_prefix_comp_1 = [(n, list(e['prefix_composites'].keys())) for n, e in by_len.get(1, []) if e.get('prefix_composites')]
has_prefix_comp_2 = [(n, list(e['prefix_composites'].keys())) for n, e in by_len.get(2, []) if e.get('prefix_composites')]
print()
print(f'  1-char middles with prefix_composites: {len(has_prefix_comp_1)}')
for n, keys in has_prefix_comp_1:
    print(f'    "{n}" -> prefixes: {keys}')
print(f'  2-char middles with prefix_composites: {len(has_prefix_comp_2)}')
for n, keys in has_prefix_comp_2:
    print(f'    "{n}" -> prefixes: {keys}')

# Check for auto_composed
auto_1 = [(n, e.get('auto_composed')) for n, e in by_len.get(1, []) if e.get('auto_composed')]
auto_2 = [(n, e.get('auto_composed')) for n, e in by_len.get(2, []) if e.get('auto_composed')]
print()
print(f'  1-char middles with auto_composed=True: {len(auto_1)}')
print(f'  2-char middles with auto_composed=True: {len(auto_2)}')
for n, v in auto_2:
    print(f'    "{n}": auto_composed={v}')
