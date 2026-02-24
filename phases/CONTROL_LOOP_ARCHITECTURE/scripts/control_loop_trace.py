#!/usr/bin/env python3
"""
Gap 5: Integrated Control Loop Trace

Annotate complete paragraphs with control flow:
- Role, gloss, cycle phase, mode, position for every token
- 5 long paragraphs from different sections (B, H, S, C, T)
- Human-readable traces showing the extraction loop in action

Output: phases/CONTROL_LOOP_ARCHITECTURE/results/control_loop_traces.json
"""

import sys
import json
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology, BFolioDecoder

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / 'phases' / 'CONTROL_LOOP_ARCHITECTURE' / 'results'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

tx = Transcript()
morph = Morphology()
decoder = BFolioDecoder()

# Atom glosses
CHAR_GLOSS = {
    'k': 'heat', 'e': 'cool', 'h': 'watch', 'y': 'end',
    'i': 'iterate', 'n': 'halt', 'a': 'accept', 'm': 'final',
    'd': 'seal', 't': 'drive', 'c': 'adjust', 'p': 'pause',
    'f': 'flag', 's': 'separate', 'g': 'complete',
    'o': 'vessel', 'l': 'collect', 'r': 'flow',
}

SUFFIX_SCOPE = {
    'dy': 'BATCH_CLOSE', 'edy': 'BATCH_CLOSE', 'eey': 'BATCH_CLOSE',
    'ey': 'BATCH_CLOSE', 'hy': 'BATCH_CLOSE', 'ry': 'BATCH_CLOSE',
    'ly': 'BATCH_CLOSE', 'am': 'FINALIZE', 'om': 'FINALIZE',
    'ain': 'LOOP_CHECK', 'aiin': 'LOOP_CHECK',
    'iin': 'LOOP_CHECK', 'oiin': 'LOOP_CHECK',
    'in': 'ITERATE', 'an': 'ITERATE', 's': 'SEPARATE',
}

def gloss_token(tok):
    """Produce a rich gloss for a BTokenAnalysis."""
    m = tok.morph
    parts = []

    # Prefix gloss
    if m.prefix:
        prefix_atoms = [CHAR_GLOSS.get(c, c) for c in m.prefix]
        parts.append(f"[{'+'.join(prefix_atoms)}]")

    # MIDDLE gloss
    if m.middle:
        mid_atoms = [CHAR_GLOSS.get(c, c) for c in m.middle]
        parts.append('+'.join(mid_atoms))

    # Suffix scope
    if m.suffix:
        scope = SUFFIX_SCOPE.get(m.suffix, 'MOD')
        parts.append(f"({scope})")

    return ' '.join(parts)

def trace_line(line_a, line_idx, n_body):
    """Produce a trace dict for one line."""
    token_traces = []
    for tok in line_a.tokens:
        token_traces.append({
            'word': tok.word,
            'gloss': gloss_token(tok),
            'prefix_role': tok.prefix_role,
            'fl_stage': tok.fl_stage,
            'kernels': tok.kernels,
            'macro_state': tok.macro_state,
        })

    # Line-level annotations
    zone_label = line_a.paragraph_zone or 'BODY'
    mode_label = line_a.suffix_mode or '?'
    fl_prog = line_a.fl_progression

    pos_frac = line_idx / max(n_body - 1, 1) if n_body > 1 else 0.5
    if pos_frac < 0.33:
        pos_label = 'EARLY'
    elif pos_frac < 0.67:
        pos_label = 'MID'
    else:
        pos_label = 'LATE'

    return {
        'line_id': line_a.line_id,
        'tokens': token_traces,
        'token_count': line_a.token_count,
        'zone': zone_label,
        'suffix_mode': mode_label,
        'fl_progression': fl_prog,
        'position': pos_label,
        'flow_render': line_a.flow_render(),
        'structural': line_a.structural(),
        'interpretive': line_a.interpretive(),
    }

def trace_paragraph(para, folio, section):
    """Produce a complete trace for one paragraph."""
    body_lines = [l for l in para.lines if not l.is_header]
    n_body = len(body_lines)

    line_traces = []
    # Header first (if present)
    for l in para.lines:
        if l.is_header:
            line_traces.append(trace_line(l, -1, n_body))
            break

    # Body lines
    for i, l in enumerate(body_lines):
        line_traces.append(trace_line(l, i, n_body))

    # Mode sequence summary
    mode_seq = [l.suffix_mode for l in body_lines if l.suffix_mode]
    alternations = sum(1 for i in range(1, len(mode_seq)) if mode_seq[i] != mode_seq[i-1])
    total_trans = max(len(mode_seq) - 1, 1)
    interleave = alternations / total_trans if total_trans > 0 else 0

    return {
        'folio': folio,
        'section': section,
        'paragraph_id': para.paragraph_id,
        'line_count': para.line_count,
        'token_count': para.token_count,
        'kernel_balance': para.kernel_balance,
        'structural': para.structural(),
        'interpretive': para.interpretive(),
        'mode_sequence': mode_seq,
        'interleave_rate': round(interleave, 2),
        'tail_signature': para.tail_product_signature,
        'lines': line_traces,
    }

# ============================================================
# SELECT TARGET PARAGRAPHS
# ============================================================
print("Selecting 5 long paragraphs from different sections...")

# Find folios by section, pick ones with long paragraphs
section_folios = defaultdict(list)
for t in tx.currier_b():
    if t.section and t.folio not in section_folios.get(t.section, []):
        section_folios[t.section].append(t.folio)

# Candidate folios per section (pick first few to test)
target_folios = {
    'B': 'f75r',   # Known rich paragraph (P9 from earlier trace)
    'H': 'f34r',
    'S': 'f103r',
    'C': 'f86v6',
    'T': 'f113r',
}

# For each target, find the longest paragraph
traces = []
for section, folio in target_folios.items():
    print(f"\n  {section}: {folio}")
    try:
        paragraphs = decoder.analyze_folio_paragraphs(folio)
    except Exception as e:
        print(f"    Error: {e}")
        # Try fallback folio
        fallback = section_folios.get(section, [''])[0]
        if fallback:
            print(f"    Trying fallback: {fallback}")
            try:
                paragraphs = decoder.analyze_folio_paragraphs(fallback)
                folio = fallback
            except:
                continue
        else:
            continue

    if not paragraphs:
        print(f"    No paragraphs found")
        continue

    # Pick longest paragraph
    longest = max(paragraphs, key=lambda p: p.token_count)
    print(f"    {longest.paragraph_id}: {longest.line_count}L / {longest.token_count}T / {longest.kernel_balance}")

    trace = trace_paragraph(longest, folio, section)
    traces.append(trace)

# ============================================================
# PRINT TRACES
# ============================================================
for trace in traces:
    print(f"\n{'='*80}")
    print(f"  {trace['folio']} {trace['paragraph_id']} ({trace['section']})")
    print(f"  {trace['structural']}")
    print(f"  {trace['interpretive']}")
    print(f"  Modes: {''.join(trace['mode_sequence'])} (interleave={trace['interleave_rate']:.0%})")
    if trace['tail_signature']:
        print(f"  Tail: {trace['tail_signature']}")
    print(f"{'='*80}")

    for line in trace['lines']:
        mode = line['suffix_mode']
        zone = line['zone']
        fl = line['fl_progression']
        print(f"\n  L{line['line_id']:4s} [{zone:5s}] Mode={mode} FL={fl:7s} {line['position']}")
        print(f"    {line['flow_render']}")
        # Token-level detail
        for tok in line['tokens']:
            fl_tag = f" FL:{tok['fl_stage']}" if tok['fl_stage'] else ""
            kern = f" kern:{','.join(tok['kernels'])}" if tok['kernels'] else ""
            role = f" {tok['prefix_role']}" if tok['prefix_role'] else ""
            print(f"      {tok['word']:14s} -> {tok['gloss']:40s}{role}{fl_tag}{kern}")

# ============================================================
# COMPILE RESULTS
# ============================================================
results = {
    'trace_count': len(traces),
    'sections_covered': [t['section'] for t in traces],
    'traces': traces,
}

output_path = OUTPUT_DIR / 'control_loop_traces.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults written to: {output_path}")
