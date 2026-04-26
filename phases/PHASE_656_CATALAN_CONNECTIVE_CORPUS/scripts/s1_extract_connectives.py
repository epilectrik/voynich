"""
Phase 656 Stage A — SISMEL Catalan Connective Extractor

Extracts every conditional/temporal/repetition connective from the SISMEL
Catalan subrecipe corpus, per the locked pre-registration in
PRE_REGISTRATION.md (commit 9986d5a).

This script implements the frozen specification. No regex revisions are
permitted without a documented bug fix and commit-hash diff.

Output:
  results/CONNECTIVE_CORPUS.json           (Practica + Mercuriorum, parts II/III)
  results/CONNECTIVE_CORPUS_THEORICA.json  (Theorica negative control, part I)
  results/CONNECTIVE_INVENTORY.md          (frequency table + examples)
"""

import io
import json
import random
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ---------------------------------------------------------------------------
# Locked configuration (per PRE_REGISTRATION.md section 4)
# ---------------------------------------------------------------------------

# Each entry: (category, regex, weak_si flag injection)
# Order matters for compound forms — `en tro tant que` BEFORE `tro que`.
CONNECTIVE_PATTERNS = [
    # BOUNDED_DURATION (compound forms first to avoid being eaten by simpler ones)
    ('BOUNDED_DURATION', r'\ben tro a tant que\b'),
    ('BOUNDED_DURATION', r'\ben tro tant que\b'),
    ('BOUNDED_DURATION', r'\ben tro que\b'),
    ('BOUNDED_DURATION', r'\bfins que\b'),
    ('BOUNDED_DURATION', r'\btro que\b'),

    # CONDITIONAL_HYPOTHETICAL
    ('CONDITIONAL_HYPOTHETICAL', r'\bsi donchs\b'),
    ('CONDITIONAL_HYPOTHETICAL', r'\bsi donques\b'),

    # CAUSAL
    ('CAUSAL', r'\bper ço que\b'),
    ('CAUSAL', r'\bper ço\b'),
    ('CAUSAL', r'\bper co\b'),

    # CONSEQUENT
    ('CONSEQUENT', r'\blavors\b'),
    ('CONSEQUENT', r'\badonques\b'),
    ('CONSEQUENT', r'\bdonchs\b'),
    ('CONSEQUENT', r'\bdonques\b'),

    # TEMPORAL_AFTER (compound first)
    ('TEMPORAL_AFTER', r'\be apr[éeèê]s\b'),
    ('TEMPORAL_AFTER', r'\bapr[éeèê]s\b'),
    ('TEMPORAL_AFTER', r'\bpuys\b'),
    ('TEMPORAL_AFTER', r'\bpuis\b'),

    # CONDITIONAL_TEMPORAL
    ('CONDITIONAL_TEMPORAL', r'\bquant\b'),
    ('CONDITIONAL_TEMPORAL', r'\bquan\b'),

    # REPETITION (compound first)
    ('REPETITION', r'\baltres vegades\b'),
    ('REPETITION', r'\baltra vegada\b'),
    ('REPETITION', r'\btotes vegades\b'),
    ('REPETITION', r'\btots vegades\b'),
    ('REPETITION', r'\bnovament\b'),
    ('REPETITION', r'\bvegades\b'),
    ('REPETITION', r'\bvegada\b'),

    # MANNER
    ('MANNER', r'\bsegons que\b'),

    # Standalone si (last; weak_si=True)
    ('CONDITIONAL_HYPOTHETICAL_WEAK', r'\bsi(?=\s+\w)\b'),
]

# Pre-cleaning regexes
RE_FOLIO_MARKER = re.compile(r'f\.\s*\d+[rv][a-z]?', flags=re.IGNORECASE)
RE_OCR_PLACEHOLDER = re.compile(r'\*+')
RE_APOS_NORM = re.compile(r"[’‘ʼ]")  # smart apostrophes -> straight

# next_verb_candidate heuristic (descriptive metadata only, NOT load-bearing)
RE_VERB_CANDIDATE = re.compile(r'\b(\w{3,}?(?:ar|er|ir|re))\b')

CONTEXT_WINDOW = 60  # chars on each side
NEXT_VERB_WINDOW = 30  # search window after connective end

# Sentence terminators (per pre-registration section 5)
SENTENCE_TERMINATORS = re.compile(r'[.!?;]')


def normalize_text(raw):
    """Apply locked pre-cleaning per PRE_REGISTRATION section 3."""
    if not raw:
        return ''
    text = unicodedata.normalize('NFC', raw)
    text = RE_FOLIO_MARKER.sub('', text)
    text = RE_OCR_PLACEHOLDER.sub('', text)
    text = RE_APOS_NORM.sub("'", text)
    return text


def compute_phase_ordinal(text, char_offset):
    """Sentence index = count of sentence-terminators before the offset."""
    return len(SENTENCE_TERMINATORS.findall(text[:char_offset]))


def find_next_verb(text_lower, start):
    """Heuristic next-verb candidate within NEXT_VERB_WINDOW chars after start."""
    window = text_lower[start:start + NEXT_VERB_WINDOW]
    m = RE_VERB_CANDIDATE.search(window)
    return m.group(1) if m else None


def extract_connectives_from_text(raw_text, subrecipe_meta):
    """
    Return list of instance records for one subrecipe's catalan field.

    Uses a non-overlap masking strategy: as each pattern matches, the matched
    span is masked out so a later (less specific) pattern cannot re-match it.
    """
    text = normalize_text(raw_text)
    text_lower = text.lower()

    # Boolean mask of consumed positions
    consumed = bytearray(len(text_lower))

    instances = []

    for category, pattern in CONNECTIVE_PATTERNS:
        for m in re.finditer(pattern, text_lower):
            start, end = m.span()
            # If any char in span already consumed, skip
            if any(consumed[i] for i in range(start, end)):
                continue
            # Mark consumed
            for i in range(start, end):
                consumed[i] = 1

            weak_si = (category == 'CONDITIONAL_HYPOTHETICAL_WEAK')
            cat_out = 'CONDITIONAL_HYPOTHETICAL' if weak_si else category

            ctx_left_start = max(0, start - CONTEXT_WINDOW)
            ctx_right_end = min(len(text), end + CONTEXT_WINDOW)
            context_left = text[ctx_left_start:start]
            context_right = text[end:ctx_right_end]

            surface_form = text[start:end]
            phase_ordinal = compute_phase_ordinal(text, start)
            next_verb = find_next_verb(text_lower, end)

            instances.append({
                'subrecipe_id': subrecipe_meta['id'],
                'part': subrecipe_meta['part'],
                'chapter_num': subrecipe_meta['chapter_num'],
                'sub_idx': subrecipe_meta['sub_idx'],
                'label_canonical': subrecipe_meta.get('label_canonical', ''),
                'char_offset': start,
                'phase_ordinal': phase_ordinal,
                'surface_form': surface_form,
                'category': cat_out,
                'weak_si': weak_si,
                'context_left': context_left,
                'context_right': context_right,
                'next_verb_candidate': next_verb,
            })

    instances.sort(key=lambda r: r['char_offset'])
    return instances


def build_corpus(subrecipes, allow_parts):
    """Return (instances, per-subrecipe-meta-list)."""
    all_instances = []
    sr_meta = []
    for s in subrecipes:
        if s.get('part') not in allow_parts:
            continue
        meta = {
            'id': s.get('id'),
            'part': s.get('part'),
            'chapter_num': s.get('chapter_num'),
            'sub_idx': s.get('sub_idx'),
            'label_canonical': s.get('label_canonical', ''),
        }
        cat_text = s.get('catalan') or ''
        if not cat_text.strip():
            sr_meta.append({**meta, 'catalan_chars': 0, 'instance_count': 0})
            continue
        instances = extract_connectives_from_text(cat_text, meta)
        all_instances.extend(instances)
        sr_meta.append({
            **meta,
            'catalan_chars': len(cat_text),
            'instance_count': len(instances),
        })
    return all_instances, sr_meta


def category_part_table(instances):
    """category x part frequency table."""
    counts = Counter()
    for r in instances:
        counts[(r['category'], r['part'])] += 1
    return counts


def write_inventory_md(out_path, procedural, theorica, sr_meta_proc, sr_meta_theo):
    """Write CONNECTIVE_INVENTORY.md."""
    cats = sorted({r['category'] for r in procedural} | {r['category'] for r in theorica})
    parts = ['II', 'III', 'I']

    proc_counts = category_part_table(procedural)
    theo_counts = category_part_table(theorica)

    lines = []
    lines.append('# Phase 656 — Connective Inventory')
    lines.append('')
    lines.append('Per pre-registration, this is data prep — no claim of significance.')
    lines.append('')
    lines.append(f'**Procedural corpus** (Practica II + Mercuriorum III):')
    lines.append(f'- Total subrecipes scanned: {len(sr_meta_proc)}')
    lines.append(f'  - Subrecipes with >=1 instance: '
                 f'{sum(1 for s in sr_meta_proc if s["instance_count"] > 0)}')
    lines.append(f'- Total connective instances: {len(procedural)}')
    lines.append('')
    lines.append(f'**Theorica negative control** (part I):')
    lines.append(f'- Total subrecipes scanned: {len(sr_meta_theo)}')
    lines.append(f'- Total connective instances: {len(theorica)}')
    lines.append('')

    # Frequency table
    lines.append('## Frequency by category x part')
    lines.append('')
    lines.append('| Category | Practica (II) | Mercuriorum (III) | Theorica (I, control) |')
    lines.append('|---|---:|---:|---:|')
    for c in cats:
        lines.append(
            f'| {c} '
            f'| {proc_counts.get((c, "II"), 0)} '
            f'| {proc_counts.get((c, "III"), 0)} '
            f'| {theo_counts.get((c, "I"), 0)} |'
        )
    lines.append('')

    # Random examples per category for spot-checking
    lines.append('## Spot-check examples (3 random per category, procedural corpus)')
    lines.append('')
    lines.append('Use these to verify the regex categorization is correct.')
    lines.append('')
    rng = random.Random(20260426)
    by_cat = defaultdict(list)
    for r in procedural:
        by_cat[r['category']].append(r)
    for c in cats:
        bucket = by_cat.get(c, [])
        if not bucket:
            continue
        lines.append(f'### {c}  (N={len(bucket)})')
        sample = rng.sample(bucket, k=min(3, len(bucket)))
        for r in sample:
            ctx = r['context_left'] + '【' + r['surface_form'] + '】' + r['context_right']
            ctx = re.sub(r'\s+', ' ', ctx).strip()
            lines.append(f'- `{r["subrecipe_id"]}` ord={r["phase_ordinal"]}: ...{ctx}...')
        lines.append('')

    # Subrecipe coverage
    lines.append('## Coverage (procedural)')
    lines.append('')
    nonzero = [s for s in sr_meta_proc if s['instance_count'] > 0]
    if sr_meta_proc:
        avg_inst = sum(s['instance_count'] for s in sr_meta_proc) / len(sr_meta_proc)
        avg_density = sum(
            s['instance_count'] / (s['catalan_chars'] / 1000)
            for s in nonzero if s['catalan_chars'] >= 100
        ) / max(1, sum(1 for s in nonzero if s['catalan_chars'] >= 100))
    else:
        avg_inst = 0
        avg_density = 0
    lines.append(f'- Avg instances per subrecipe: {avg_inst:.1f}')
    lines.append(f'- Avg connective density (instances per 1000 chars, '
                 f'subrecipes >= 100 chars): {avg_density:.1f}')
    lines.append('')

    # Categories present in >= 50% of subrecipes (corpus-quality bar from pre-reg)
    cat_present_per_sr = defaultdict(set)
    for r in procedural:
        cat_present_per_sr[r['subrecipe_id']].add(r['category'])
    n_sr = len(sr_meta_proc)
    coverage_50 = []
    for c in cats:
        n_with = sum(1 for sid, s in cat_present_per_sr.items() if c in s)
        pct = 100.0 * n_with / n_sr if n_sr else 0
        if pct >= 50:
            coverage_50.append((c, n_with, pct))
    lines.append('### Categories present in >=50% of subrecipes')
    lines.append('')
    for c, n, pct in coverage_50:
        lines.append(f'- {c}: {n}/{n_sr} ({pct:.1f}%)')
    lines.append('')

    # Pre-registered quality bar check
    lines.append('## Pre-registered corpus-quality bar (PRE_REGISTRATION section 8)')
    lines.append('')
    bar_total = len(procedural) >= 800
    bar_cov = len(coverage_50) >= 3
    bar_theo = len(theorica) >= 100
    lines.append(f'- Total instances >= 800: {len(procedural)} '
                 f'-> {"PASS" if bar_total else "FAIL"}')
    lines.append(f'- >=3 categories present in >=50% of subrecipes: {len(coverage_50)} '
                 f'-> {"PASS" if bar_cov else "FAIL"}')
    lines.append(f'- Theorica control >= 100: {len(theorica)} '
                 f'-> {"PASS" if bar_theo else "FAIL"}')
    lines.append('- Manual 20-record spot-check: see "Spot-check examples" above; '
                 'humans verify >=18/20 correct categorization.')
    lines.append('')

    out_path.write_text('\n'.join(lines), encoding='utf-8')
    print(f'wrote {out_path}')


def main():
    repo_root = Path(__file__).resolve().parents[3]
    src = repo_root / 'phases' / 'SISMEL_RECIPE_CORPUS' / 'results' / 'sismel_subrecipes.json'
    out_dir = repo_root / 'phases' / 'PHASE_656_CATALAN_CONNECTIVE_CORPUS' / 'results'
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f'reading {src}')
    data = json.loads(src.read_text(encoding='utf-8'))
    subrecipes = data['subrecipes']
    print(f'  {len(subrecipes)} subrecipes loaded')

    procedural, sr_meta_proc = build_corpus(subrecipes, allow_parts={'II', 'III'})
    theorica, sr_meta_theo = build_corpus(subrecipes, allow_parts={'I'})

    print(f'procedural instances: {len(procedural)}')
    print(f'theorica instances:   {len(theorica)}')

    proc_path = out_dir / 'CONNECTIVE_CORPUS.json'
    proc_path.write_text(json.dumps({
        'phase': 656,
        'stage': 'A',
        'pre_registration_commit': '9986d5a',
        'parts_included': ['II', 'III'],
        'instance_count': len(procedural),
        'subrecipe_count': len(sr_meta_proc),
        'subrecipes': sr_meta_proc,
        'instances': procedural,
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'wrote {proc_path}')

    theo_path = out_dir / 'CONNECTIVE_CORPUS_THEORICA.json'
    theo_path.write_text(json.dumps({
        'phase': 656,
        'stage': 'A',
        'pre_registration_commit': '9986d5a',
        'parts_included': ['I'],
        'note': 'Negative-control corpus (theoretical chapters per C1748/C1932)',
        'instance_count': len(theorica),
        'subrecipe_count': len(sr_meta_theo),
        'subrecipes': sr_meta_theo,
        'instances': theorica,
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'wrote {theo_path}')

    inv_path = out_dir / 'CONNECTIVE_INVENTORY.md'
    write_inventory_md(inv_path, procedural, theorica, sr_meta_proc, sr_meta_theo)


if __name__ == '__main__':
    main()
