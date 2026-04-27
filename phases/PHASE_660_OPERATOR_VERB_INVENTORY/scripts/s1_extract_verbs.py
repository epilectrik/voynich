"""
Phase 660 s1 — SISMEL Catalan Operator-Verb Extractor

Locked methodology per PRE_REGISTRATION.md (commit c790cf1).

18 categories, non-overlap matching (longer/more-specific patterns first).
No hypothesis tests in Stage A.

Outputs:
  results/VERB_CORPUS.json           (parts II + III)
  results/VERB_CORPUS_THEORICA.json  (part I, negative control)
  results/VERB_INVENTORY.md          (frequency table + spot-check examples)
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
# LOCKED CONFIGURATION (per PRE_REGISTRATION.md section 2)
# ---------------------------------------------------------------------------

# Order = matching priority (longer/more-specific first within category).
# Format: (category, regex_string)
VERB_PATTERNS = [
    # PHASE_FUSE compound forms first
    ('PHASE_FUSE',     r'\bliquef\w*'),
    ('PHASE_FUSE',     r'\bliquefer\w*'),
    ('PHASE_FUSE',     r'\bliquefiar\w*'),
    ('PHASE_FUSE',     r'\bfond\w*'),
    ('PHASE_FUSE',     r'\bfonr\w*'),
    ('PHASE_FUSE',     r'\bfus\w*'),
    ('PHASE_FUSE',     r'\bfos\b'),

    # PHASE_FIX
    ('PHASE_FIX',      r'\bcongel\w*'),
    ('PHASE_FIX',      r'\bcoagul\w*'),
    ('PHASE_FIX',      r'\bfix\w*'),
    ('PHASE_FIX',      r'\bfixar\w*'),

    # DISTILLATION (compound spelling first)
    ('DISTILLATION',   r'\bdestil[·\.]?l\w*'),
    ('DISTILLATION',   r'\bdistil[·\.]?l\w*'),
    ('DISTILLATION',   r'\bdestil\w*'),
    ('DISTILLATION',   r'\bdistil\w*'),

    # SUBLIMATION
    ('SUBLIMATION',    r'\bsublim\w*'),

    # DISSOLUTION
    ('DISSOLUTION',    r'\bdissol\w*'),
    ('DISSOLUTION',    r'\bdesli\w*'),
    ('DISSOLUTION',    r'\bdeslliur\w*'),

    # PUTREFACTION
    ('PUTREFACTION',   r'\bputref\w*'),
    ('PUTREFACTION',   r'\bputrif\w*'),
    ('PUTREFACTION',   r'\bpudr\w*'),
    ('PUTREFACTION',   r'\bmacer\w*'),
    ('PUTREFACTION',   r'\bdigest\w*'),
    ('PUTREFACTION',   r'\bdigeri\w*'),
    ('PUTREFACTION',   r'\bdigerir\w*'),

    # REFINEMENT
    ('REFINEMENT',     r'\brectif\w*'),
    ('REFINEMENT',     r'\bmundif\w*'),
    ('REFINEMENT',     r'\bpurif\w*'),
    ('REFINEMENT',     r'\bdepur\w*'),
    ('REFINEMENT',     r'\blimp\w*'),
    ('REFINEMENT',     r'\bnetej\w*'),
    ('REFINEMENT',     r'\bneteg\w*'),

    # MULTIPLICATION
    ('MULTIPLICATION', r'\bmultipl\w*'),
    ('MULTIPLICATION', r'\baugme\w*'),
    ('MULTIPLICATION', r'\bcrei[xs]\w*'),

    # IMBIBITION
    ('IMBIBITION',     r'\benbeu\w*'),
    ('IMBIBITION',     r'\benbev\w*'),
    ('IMBIBITION',     r'\bimbib\w*'),
    ('IMBIBITION',     r'\buntar\w*'),
    ('IMBIBITION',     r'\buntu\w*'),
    ('IMBIBITION',     r'\blav\w*'),
    ('IMBIBITION',     r'\bbanya\w*'),

    # SEPARATION
    ('SEPARATION',     r'\bsepar\w*'),
    ('SEPARATION',     r'\bfiltr\w*'),
    ('SEPARATION',     r'\bparteix\w*'),
    ('SEPARATION',     r'\bparti\w*'),

    # CONTAINMENT
    ('CONTAINMENT',    r'\btap\w*'),
    ('CONTAINMENT',    r'\bcobr\w*'),
    ('CONTAINMENT',    r'\bcubr\w*'),
    ('CONTAINMENT',    r'\bsegell\w*'),
    ('CONTAINMENT',    r'\bsoter\w*'),
    ('CONTAINMENT',    r'\benterr\w*'),

    # MIXTURE
    ('MIXTURE',        r'\bmescl\w*'),
    ('MIXTURE',        r'\bmesc\w*'),
    ('MIXTURE',        r'\bconjun\w*'),
    ('MIXTURE',        r'\bajunt\w*'),
    ('MIXTURE',        r'\bcompon\w*'),
    ('MIXTURE',        r'\bcomposi\w*'),
    ('MIXTURE',        r'\bcompóndr\w*'),

    # ADDITION
    ('ADDITION',       r'\bajust\w*'),

    # HEAT_APPLY
    ('HEAT_APPLY',     r'\bescalf\w*'),
    ('HEAT_APPLY',     r'\bcrem\w*'),
    ('HEAT_APPLY',     r'\bcalcin\w*'),
    ('HEAT_APPLY',     r'\bbull\w*'),
    ('HEAT_APPLY',     r'\bcuit\w*'),
    ('HEAT_APPLY',     r'\bcoga\w*'),
    ('HEAT_APPLY',     r'\bcoc\w*'),
    ('HEAT_APPLY',     r'\bcoú\b'),
    ('HEAT_APPLY',     r'\bcou\b'),
    # Bug fix 2026-04-26: decocció family was missed by \bcoc\w* due to de- prefix.
    # Pre-reg-compliant: regex bug fix within existing locked HEAT_APPLY category.
    ('HEAT_APPLY',     r'\bdecoct\w*'),
    ('HEAT_APPLY',     r'\bdecoir\w*'),
    ('HEAT_APPLY',     r'\bdecoent\w*'),
    ('HEAT_APPLY',     r'\bdecoid\w*'),
    ('HEAT_APPLY',     r'\bdecoc\w*'),

    # OBSERVATION
    ('OBSERVATION',    r'\bguard\w*'),
    ('OBSERVATION',    r'\bveur\w*'),
    ('OBSERVATION',    r'\bmira\w*'),
    ('OBSERVATION',    r'\bveg\w*'),
    ('OBSERVATION',    r'\bsent\w*'),

    # QUALITY_TEST
    ('QUALITY_TEST',   r'\bprov\w*'),
    ('QUALITY_TEST',   r'\bexamin\w*'),
    ('QUALITY_TEST',   r'\bgust\w*'),

    # MATERIAL_TAKE
    ('MATERIAL_TAKE',  r'\bpendr\w*'),
    ('MATERIAL_TAKE',  r'\bpren\w*'),

    # MATERIAL_PLACE (last; very common, polysemous)
    ('MATERIAL_PLACE', r'\bmetr\w*'),
    ('MATERIAL_PLACE', r'\bmet-\w*'),
    ('MATERIAL_PLACE', r'\bmit-\w*'),
    ('MATERIAL_PLACE', r'\bmet\w*'),
]

# Pre-cleaning regexes
RE_FOLIO_MARKER = re.compile(r'f\.\s*\d+[rv][a-z]?', flags=re.IGNORECASE)
RE_OCR_PLACEHOLDER = re.compile(r'\*+')
RE_APOS_NORM = re.compile(r"[’‘ʼ]")

CONTEXT_WINDOW = 60
SENTENCE_TERMINATORS = re.compile(r'[.!?;]')


def normalize_text(raw):
    if not raw:
        return ''
    text = unicodedata.normalize('NFC', raw)
    text = RE_FOLIO_MARKER.sub('', text)
    text = RE_OCR_PLACEHOLDER.sub('', text)
    text = RE_APOS_NORM.sub("'", text)
    return text


def compute_phase_ordinal(text, char_offset):
    return len(SENTENCE_TERMINATORS.findall(text[:char_offset]))


def extract_from_text(raw_text, subrecipe_meta):
    text = normalize_text(raw_text)
    text_lower = text.lower()
    consumed = bytearray(len(text_lower))

    instances = []
    for category, pattern in VERB_PATTERNS:
        for m in re.finditer(pattern, text_lower, flags=re.IGNORECASE):
            start, end = m.span()
            if any(consumed[i] for i in range(start, end)):
                continue
            for i in range(start, end):
                consumed[i] = 1
            ctx_left = text[max(0, start - CONTEXT_WINDOW):start]
            ctx_right = text[end:min(len(text), end + CONTEXT_WINDOW)]
            instances.append({
                'subrecipe_id': subrecipe_meta['id'],
                'part': subrecipe_meta['part'],
                'chapter_num': subrecipe_meta['chapter_num'],
                'sub_idx': subrecipe_meta['sub_idx'],
                'label_canonical': subrecipe_meta.get('label_canonical', ''),
                'char_offset': start,
                'phase_ordinal': compute_phase_ordinal(text, start),
                'surface_form': text[start:end],
                'category': category,
                'context_left': ctx_left,
                'context_right': ctx_right,
            })

    instances.sort(key=lambda r: r['char_offset'])
    return instances


def build_corpus(subrecipes, allow_parts):
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
        instances = extract_from_text(cat_text, meta)
        all_instances.extend(instances)
        sr_meta.append({
            **meta,
            'catalan_chars': len(cat_text),
            'instance_count': len(instances),
        })
    return all_instances, sr_meta


def write_inventory_md(out_path, procedural, theorica, sr_meta_proc, sr_meta_theo):
    cats = sorted({r['category'] for r in procedural} | {r['category'] for r in theorica})
    proc_counts = Counter((r['category'], r['part']) for r in procedural)
    theo_counts = Counter((r['category'], r['part']) for r in theorica)

    lines = []
    lines.append('# Phase 660 — Verb Inventory')
    lines.append('')
    lines.append('Per pre-registration, this is data prep — no claim of significance.')
    lines.append('')
    lines.append(f'**Procedural corpus** (Practica II + Mercuriorum III):')
    lines.append(f'- Total subrecipes scanned: {len(sr_meta_proc)}')
    lines.append(f'- Subrecipes with >=1 instance: '
                 f'{sum(1 for s in sr_meta_proc if s["instance_count"] > 0)}')
    lines.append(f'- Total verb instances: {len(procedural)}')
    lines.append('')
    lines.append(f'**Theorica negative control** (part I):')
    lines.append(f'- Total subrecipes scanned: {len(sr_meta_theo)}')
    lines.append(f'- Total verb instances: {len(theorica)}')
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

    # Spot-check examples (3 random per category)
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

    # Coverage
    lines.append('## Coverage (procedural)')
    lines.append('')
    avg = sum(s['instance_count'] for s in sr_meta_proc) / max(1, len(sr_meta_proc))
    lines.append(f'- Avg instances per subrecipe: {avg:.1f}')
    lines.append('')

    # Categories present in >= 50%
    cat_present = defaultdict(set)
    for r in procedural:
        cat_present[r['category']].add(r['subrecipe_id'])
    n_sr = len(sr_meta_proc)
    coverage_50 = []
    for c in cats:
        n_with = len(cat_present.get(c, set()))
        pct = 100.0 * n_with / n_sr if n_sr else 0
        if pct >= 50:
            coverage_50.append((c, n_with, pct))
    lines.append('### Categories present in >=50% of subrecipes')
    lines.append('')
    for c, n, pct in sorted(coverage_50, key=lambda x: -x[2]):
        lines.append(f'- {c}: {n}/{n_sr} ({pct:.1f}%)')
    lines.append('')

    # Quality bar check
    lines.append('## Pre-registered corpus-quality bar (PRE_REGISTRATION section 6)')
    lines.append('')
    bar_total = len(procedural) >= 2000
    bar_cov = len(coverage_50) >= 5
    bar_theo = len(theorica) >= 200
    lines.append(f'- Total instances >= 2000: {len(procedural)} -> '
                 f'{"PASS" if bar_total else "FAIL"}')
    lines.append(f'- >=5 categories present in >=50% of subrecipes: {len(coverage_50)} -> '
                 f'{"PASS" if bar_cov else "FAIL"}')
    lines.append(f'- Theorica control >= 200: {len(theorica)} -> '
                 f'{"PASS" if bar_theo else "FAIL"}')
    lines.append('- Manual 30-record spot-check: see "Spot-check examples" above; '
                 'humans verify >=27/30 correct categorization.')
    lines.append('')

    out_path.write_text('\n'.join(lines), encoding='utf-8')
    print(f'wrote {out_path}')


def main():
    repo_root = Path(__file__).resolve().parents[3]
    src = repo_root / 'phases' / 'SISMEL_RECIPE_CORPUS' / 'results' / 'sismel_subrecipes.json'
    out_dir = repo_root / 'phases' / 'PHASE_660_OPERATOR_VERB_INVENTORY' / 'results'
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f'reading {src}')
    data = json.loads(src.read_text(encoding='utf-8'))
    subrecipes = data['subrecipes']
    print(f'  {len(subrecipes)} subrecipes loaded')

    procedural, sr_meta_proc = build_corpus(subrecipes, allow_parts={'II', 'III'})
    theorica, sr_meta_theo = build_corpus(subrecipes, allow_parts={'I'})

    print(f'procedural instances: {len(procedural)}')
    print(f'theorica instances:   {len(theorica)}')

    proc_path = out_dir / 'VERB_CORPUS.json'
    proc_path.write_text(json.dumps({
        'phase': 660,
        'stage': 'A',
        'pre_registration_commit': 'c790cf1',
        'parts_included': ['II', 'III'],
        'instance_count': len(procedural),
        'subrecipe_count': len(sr_meta_proc),
        'subrecipes': sr_meta_proc,
        'instances': procedural,
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'wrote {proc_path}')

    theo_path = out_dir / 'VERB_CORPUS_THEORICA.json'
    theo_path.write_text(json.dumps({
        'phase': 660,
        'stage': 'A',
        'pre_registration_commit': 'c790cf1',
        'parts_included': ['I'],
        'note': 'Negative-control corpus (theoretical chapters per C1748/C1932)',
        'instance_count': len(theorica),
        'subrecipe_count': len(sr_meta_theo),
        'subrecipes': sr_meta_theo,
        'instances': theorica,
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'wrote {theo_path}')

    inv_path = out_dir / 'VERB_INVENTORY.md'
    write_inventory_md(inv_path, procedural, theorica, sr_meta_proc, sr_meta_theo)


if __name__ == '__main__':
    main()
