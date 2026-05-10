#!/usr/bin/env python3
"""
Phase 692: Voynich-thinker training corpus builder.

Walks the repo and produces a JSONL training corpus combining:
  1. Constraint system (2018 constraints with reasoning)
  2. Phase reports (research methodology + findings)
  3. Structural contracts (formal API specs)
  4. Workshop dictionaries (compound-level operational interpretations)
  5. INTERPRETATION_SUMMARY + MODEL_CONTEXT (interpretive synthesis)
  6. Memory notes (researcher insights)
  7. Methodology docs (epistemic framework)
  8. RAW VOYNICH CORPUS (4,435 H-track lines)
  9. Annotated transcript (tokens + structural metadata)
 10. Cold-read tables (13 folios with workshop interpretations)
 11. Atom decomposition lookup (with explicit structural-only tier)
 12. Top-level project docs (CLAUDE.md)

Each JSONL entry: {source, type, tier, content, metadata}.

Type categories (used to format prompts during fine-tuning):
  - constraint       : structured claim with evidence
  - phase_report     : research narrative
  - contract         : formal structural spec
  - lexicon_entry    : token to operational meaning
  - interpretation   : tier 3-4 synthesis
  - memory_note      : researcher's insight
  - methodology      : epistemic framework
  - raw_voynich      : actual Voynich text (no commentary)
  - annotated_voynich: Voynich text + structural metadata
  - cold_read        : Voynich line + workshop interpretation
  - atom_decomp      : structural decomposition (NOT semantic)
  - project_doc      : project-level documentation

Output: phases/PHASE_692_VOYNICH_THINKER/data/training_corpus.jsonl
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PHASE_DIR = Path(__file__).resolve().parents[1]
OUT_PATH = PHASE_DIR / 'data' / 'training_corpus.jsonl'
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)


def write_entry(f, source, type_, tier, content, metadata=None):
    """Write a single JSONL entry."""
    if not content or len(content.strip()) < 10:
        return False
    rec = {
        'source': source,
        'type': type_,
        'tier': tier,
        'content': content.strip(),
        'metadata': metadata or {},
    }
    f.write(json.dumps(rec, ensure_ascii=False) + '\n')
    return True


def safe_read(path, max_size=10_000_000):
    """Read a file, return None if too large or unreadable."""
    try:
        size = path.stat().st_size
        if size > max_size:
            return None
        return path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return None


def add_constraint_files(f):
    """Add constraint files from context/CLAIMS/."""
    n = 0
    claims_dir = PROJECT_ROOT / 'context' / 'CLAIMS'
    for p in sorted(claims_dir.glob('C*.md')):
        text = safe_read(p)
        if not text:
            continue
        # Determine tier from content
        tier = 2
        if 'Tier 0' in text or '**Tier:** 0' in text:
            tier = 0
        elif 'Tier 1' in text or '**Tier:** 1' in text:
            tier = 1
        elif 'Tier 3' in text or '**Tier:** 3' in text:
            tier = 3
        elif 'Tier 4' in text or '**Tier:** 4' in text:
            tier = 4
        cnum_match = re.match(r'C(\d+)', p.stem)
        c_num = cnum_match.group(0) if cnum_match else p.stem
        if write_entry(f, str(p.relative_to(PROJECT_ROOT)), 'constraint', tier, text,
                       {'constraint_id': c_num}):
            n += 1
    # Also include the master INDEX
    idx = claims_dir / 'INDEX.md'
    if idx.exists():
        text = safe_read(idx)
        if text and write_entry(f, 'context/CLAIMS/INDEX.md', 'constraint_index', 0, text):
            n += 1
    return n


def add_phase_reports(f):
    """Add phase INDEX.md files (the report-level summaries)."""
    n = 0
    phases_dir = PROJECT_ROOT / 'phases'
    for d in sorted(phases_dir.iterdir()):
        if not d.is_dir():
            continue
        idx = d / 'INDEX.md'
        if not idx.exists():
            continue
        text = safe_read(idx)
        if text and write_entry(f, str(idx.relative_to(PROJECT_ROOT)), 'phase_report', 2,
                               text, {'phase': d.name}):
            n += 1
    return n


def add_structural_contracts(f):
    """Add CASC, BCSC, HTSC, PSC, ACT contracts."""
    n = 0
    sc_dir = PROJECT_ROOT / 'context' / 'STRUCTURAL_CONTRACTS'
    if not sc_dir.exists():
        return 0
    for p in sc_dir.glob('*.yaml'):
        text = safe_read(p)
        if text and write_entry(f, str(p.relative_to(PROJECT_ROOT)), 'contract', 0,
                               text, {'contract_name': p.stem}):
            n += 1
    return n


def add_workshop_dictionaries(f):
    """Add b_dictionary, PT-013 from PENDING_TESTS, middle_dictionary, dark_pipeline."""
    n = 0
    files = [
        ('phases/B_OPERATIONAL_DICTIONARY/results/b_dictionary_top100_v3.md', 'lexicon_top100', 2),
        ('phases/B_OPERATIONAL_DICTIONARY/results/b_dictionary_seeds.md', 'lexicon_seeds', 2),
        ('phases/B_OPERATIONAL_DICTIONARY/results/b_dictionary_top100_v2.md', 'lexicon_top100_v2', 2),
        ('context/PENDING_TESTS.md', 'pending_tests', 3),
        ('context/DARK_PIPELINE_DICTIONARY.md', 'dark_pipeline', 3),
        ('context/GLOSSING.md', 'glossing_rules', 0),
    ]
    for rel, kind, tier in files:
        p = PROJECT_ROOT / rel
        text = safe_read(p)
        if text and write_entry(f, rel, 'lexicon_entry', tier, text, {'kind': kind}):
            n += 1
    # middle_dictionary.json — flatten to readable text per entry
    mdp = PROJECT_ROOT / 'data' / 'middle_dictionary.json'
    if mdp.exists():
        try:
            md = json.loads(mdp.read_text(encoding='utf-8'))
            # Take only entries with non-empty gloss or autogloss
            entries = []
            for k, v in md.items():
                if not isinstance(v, dict):
                    continue
                gloss = v.get('gloss')
                autogloss = v.get('autogloss')
                if not gloss and not autogloss:
                    continue
                line = f"MIDDLE: {k}"
                if gloss:
                    line += f" | Gloss: {gloss}"
                if autogloss:
                    line += f" | Atom-composition: {autogloss}"
                if v.get('autogloss_confidence'):
                    line += f" | Confidence: {v['autogloss_confidence']}"
                if v.get('regime'):
                    line += f" | Regime: {v['regime']}"
                if v.get('token_count'):
                    line += f" | n={v['token_count']}"
                entries.append(line)
            content = "Compound MIDDLE dictionary (1,345 entries from data/middle_dictionary.json):\n" + "\n".join(entries)
            if write_entry(f, 'data/middle_dictionary.json', 'lexicon_entry', 2, content,
                          {'kind': 'middle_dictionary', 'n_entries': len(entries)}):
                n += 1
        except Exception as e:
            print(f"  Failed to parse middle_dictionary: {e}")
    return n


def add_interpretation_files(f):
    """Add INTERPRETATION_SUMMARY and MODEL_CONTEXT."""
    n = 0
    files = [
        ('context/SPECULATIVE/INTERPRETATION_SUMMARY.md', 3),
        ('context/MODEL_CONTEXT.md', 0),
    ]
    for rel, tier in files:
        p = PROJECT_ROOT / rel
        text = safe_read(p)
        if text and write_entry(f, rel, 'interpretation', tier, text):
            n += 1
    return n


def add_memory_notes(f):
    """Add user's project memory notes."""
    n = 0
    memory_dir = Path('C:/Users/epilectrik/.claude/projects/C--git-voynich/memory')
    if not memory_dir.exists():
        return 0
    for p in sorted(memory_dir.glob('*.md')):
        text = safe_read(p)
        if text and write_entry(f, f'memory/{p.name}', 'memory_note', 3, text):
            n += 1
    return n


def add_methodology_docs(f):
    """Add SYSTEM/ methodology files + key meta docs."""
    n = 0
    sys_dir = PROJECT_ROOT / 'context' / 'SYSTEM'
    if sys_dir.exists():
        for p in sys_dir.glob('*.md'):
            text = safe_read(p)
            if text and write_entry(f, str(p.relative_to(PROJECT_ROOT)), 'methodology', 0, text):
                n += 1
    # CLAUDE_INDEX
    idx = PROJECT_ROOT / 'context' / 'CLAUDE_INDEX.md'
    text = safe_read(idx)
    if text and write_entry(f, 'context/CLAUDE_INDEX.md', 'methodology', 0, text):
        n += 1
    # Top-level CLAUDE.md
    top = PROJECT_ROOT / 'CLAUDE.md'
    text = safe_read(top)
    if text and write_entry(f, 'CLAUDE.md', 'project_doc', 0, text):
        n += 1
    return n


def add_voynich_transcript(f):
    """Add the H-track transcript in three framings."""
    sys.path.insert(0, str(PROJECT_ROOT))
    from scripts.voynich import Transcript

    tx = Transcript()
    by_folio_line = defaultdict(lambda: defaultdict(list))
    for tok in tx.all(h_only=True):
        if not tok.word or tok.is_uncertain:
            continue
        by_folio_line[tok.folio][str(tok.line)].append(tok)

    # 1. Raw corpus per folio
    n = 0
    for folio in sorted(by_folio_line.keys()):
        lines_data = by_folio_line[folio]
        try:
            sorted_lines = sorted(lines_data.keys(), key=lambda x: int(x))
        except ValueError:
            sorted_lines = sorted(lines_data.keys())
        body = []
        for L in sorted_lines:
            tokens = [t.word for t in lines_data[L]]
            body.append(f"L{L}: {' '.join(tokens)}")
        sec = lines_data[sorted_lines[0]][0].language if sorted_lines else '?'
        content = f"Folio {folio} (language={sec}):\n" + "\n".join(body)
        if write_entry(f, f'voynich/{folio}', 'raw_voynich', 0, content,
                      {'folio': folio, 'n_lines': len(sorted_lines)}):
            n += 1

    # 2. Annotated per-line (small chunks, with structural metadata)
    for folio in sorted(by_folio_line.keys()):
        lines_data = by_folio_line[folio]
        try:
            sorted_lines = sorted(lines_data.keys(), key=lambda x: int(x))
        except ValueError:
            sorted_lines = sorted(lines_data.keys())
        for L in sorted_lines:
            tokens_objs = lines_data[L]
            tokens = [t.word for t in tokens_objs]
            placement_codes = list(set(t.placement for t in tokens_objs if t.placement))
            line_initial = any(t.line_initial for t in tokens_objs)
            line_final = any(t.line_final for t in tokens_objs)
            par_initial = any(t.par_initial for t in tokens_objs)
            par_final = any(t.par_final for t in tokens_objs)
            section = tokens_objs[0].language
            content = (
                f"Folio {folio}, Line {L} (section {section}):\n"
                f"  Tokens: {' '.join(tokens)}\n"
                f"  N tokens: {len(tokens)}\n"
                f"  Placement codes: {placement_codes}\n"
                f"  Position flags: line_initial={line_initial}, line_final={line_final}, "
                f"par_initial={par_initial}, par_final={par_final}"
            )
            if write_entry(f, f'voynich_annotated/{folio}/L{L}', 'annotated_voynich', 0, content,
                          {'folio': folio, 'line': L, 'section': section}):
                n += 1
    return n


def add_cold_read_tables(f):
    """Add Phase 668 cold-read tables (13 folios)."""
    n = 0
    cr_dir = PROJECT_ROOT / 'phases' / 'PHASE_668_F76R_COLD_READ' / 'results' / 'data'
    if not cr_dir.exists():
        return 0
    for p in sorted(cr_dir.glob('f*_workshop_tables.md')):
        text = safe_read(p)
        if text and write_entry(f, str(p.relative_to(PROJECT_ROOT)), 'cold_read', 3, text,
                               {'folio': p.stem.split('_')[0]}):
            n += 1
    for p in sorted(cr_dir.glob('f*_cold_read.txt')):
        text = safe_read(p)
        if text and write_entry(f, str(p.relative_to(PROJECT_ROOT)), 'cold_read', 3, text,
                               {'folio': p.stem.split('_')[0]}):
            n += 1
    # Also include the f75r full decode
    f75r_full = PROJECT_ROOT / 'phases' / 'RECIPE_FOLIO_CORRESPONDENCE' / 'results' / 'f75r_full_decode.txt'
    text = safe_read(f75r_full)
    if text and write_entry(f, str(f75r_full.relative_to(PROJECT_ROOT)), 'cold_read', 3, text,
                           {'folio': 'f75r'}):
        n += 1
    return n


def add_atom_decompositions(f):
    """Add atom-decomp lookup with explicit 'structural only' marker."""
    sys.path.insert(0, str(PROJECT_ROOT))
    from scripts.voynich import Transcript, Morphology

    tx = Transcript()
    morph = Morphology()
    seen_tokens = set()
    for tok in tx.all(h_only=True):
        if not tok.word or tok.is_uncertain:
            continue
        seen_tokens.add(tok.word)

    entries = []
    for tok in sorted(seen_tokens):
        try:
            a = morph.atomize(tok)
        except Exception:
            continue
        if not a or not a.atoms:
            continue
        entries.append(f"{tok}: prefix={a.prefix or 'none'}, atoms={a.atoms}, gloss={a.gloss}")
        if len(entries) >= 8021:
            break

    content = (
        "ATOM DECOMPOSITION TABLE (STRUCTURAL ONLY — NOT SEMANTIC).\n"
        "WARNING: atom decomposition is structurally accurate but semantically misleading.\n"
        "Example: kee atom-decomposes to 'heat.cool.cool' BUT operationally means 'gentle stabilized heat' (per C1455 balneum mariae signature).\n"
        "Compound semantics are PRIMARY; atom decomposition is reading positional slots, not meaning.\n"
        "Use this table only for structural analysis, NEVER for semantic translation.\n\n"
    )
    content += "\n".join(entries)
    if write_entry(f, 'atom_decomposition_table', 'atom_decomp', 0, content,
                  {'n_tokens': len(entries)}):
        return 1
    return 0


def add_recipe_match_files(f):
    """Add Phase 668 recipe-folio matching outputs and Phase 641 catalan findings."""
    n = 0
    files = [
        ('phases/RECIPE_FOLIO_CORRESPONDENCE/results/full_spectrum_results.txt', 'recipe_match_summary'),
        ('phases/RECIPE_FOLIO_CORRESPONDENCE/results/f75r_full_decode.txt', 'f75r_decode'),
        ('phases/RECIPE_FOLIO_CORRESPONDENCE/results/dark_pipeline_inventory.txt', 'dark_pipeline'),
        ('phases/PHASE_641_SISMEL_RERUN/results/catalan_atom_decode_findings.md', 'catalan_atoms'),
        ('phases/PHASE_641_SISMEL_RERUN/results/catalan_crib_findings.md', 'catalan_cribs'),
        ('phases/PHASE_641_SISMEL_RERUN/results/catalan_vs_latin_detail.md', 'catalan_vs_latin'),
        ('phases/PHASE_641_SISMEL_RERUN/results/sismel_latin_lexicon_v2.md', 'sismel_lexicon'),
        ('phases/PHASE_641_SISMEL_RERUN/results/sismel_latin_category_candidates.md', 'sismel_categories'),
    ]
    for rel, kind in files:
        p = PROJECT_ROOT / rel
        text = safe_read(p)
        if text and write_entry(f, rel, 'recipe_match', 3, text, {'kind': kind}):
            n += 1
    # recipe_matching.json — convert to readable text
    rmp = PROJECT_ROOT / 'phases/RECIPE_FOLIO_CORRESPONDENCE/results/recipe_matching.json'
    if rmp.exists():
        try:
            data = json.loads(rmp.read_text(encoding='utf-8'))
            table = data.get('T1_distillation_matching', {}).get('match_table', [])
            lines = ["Confirmed Voynich-PL distillation matches (Phase 668):\n"]
            for m in table:
                conf = '[CONFIRMED]' if m.get('confident') else '[CANDIDATE]'
                lines.append(f"  {conf} {m['folio']} <-> Ch{m['chapter_number']} (family={m.get('family','?')}, distance={m['distance']:.3f}, ratio={m['ratio']:.2f})")
            content = '\n'.join(lines)
            if write_entry(f, 'phases/RECIPE_FOLIO_CORRESPONDENCE/results/recipe_matching.json',
                          'recipe_match', 2, content, {'kind': 'match_table'}):
                n += 1
        except Exception as e:
            print(f"  Failed to parse recipe_matching.json: {e}")
    return n


def add_constraint_table_text(f):
    """Add CONSTRAINT_TABLE.txt as a single big entry."""
    p = PROJECT_ROOT / 'context' / 'CONSTRAINT_TABLE.txt'
    text = safe_read(p, max_size=20_000_000)
    if text and write_entry(f, 'context/CONSTRAINT_TABLE.txt', 'constraint_table', 0, text):
        return 1
    return 0


def main():
    print(f"Building Voynich-thinker training corpus → {OUT_PATH}")
    counts = {}
    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        print("\n[1/12] Constraint files (context/CLAIMS/C*.md)...")
        counts['constraints'] = add_constraint_files(f)
        print(f"  Added {counts['constraints']} entries")

        print("\n[2/12] Constraint table...")
        counts['constraint_table'] = add_constraint_table_text(f)
        print(f"  Added {counts['constraint_table']} entries")

        print("\n[3/12] Phase reports (phases/*/INDEX.md)...")
        counts['phase_reports'] = add_phase_reports(f)
        print(f"  Added {counts['phase_reports']} entries")

        print("\n[4/12] Structural contracts (CASC, BCSC, etc.)...")
        counts['contracts'] = add_structural_contracts(f)
        print(f"  Added {counts['contracts']} entries")

        print("\n[5/12] Workshop dictionaries (b_dictionary, PT-013, etc.)...")
        counts['lexicons'] = add_workshop_dictionaries(f)
        print(f"  Added {counts['lexicons']} entries")

        print("\n[6/12] Interpretation files (SUMMARY, MODEL_CONTEXT)...")
        counts['interpretations'] = add_interpretation_files(f)
        print(f"  Added {counts['interpretations']} entries")

        print("\n[7/12] Memory notes (.claude/projects/.../memory/)...")
        counts['memory'] = add_memory_notes(f)
        print(f"  Added {counts['memory']} entries")

        print("\n[8/12] Methodology docs (SYSTEM/)...")
        counts['methodology'] = add_methodology_docs(f)
        print(f"  Added {counts['methodology']} entries")

        print("\n[9/12] Voynich transcript (raw + annotated)...")
        counts['transcript'] = add_voynich_transcript(f)
        print(f"  Added {counts['transcript']} entries")

        print("\n[10/13] Cold-read tables (Phase 668)...")
        counts['cold_reads'] = add_cold_read_tables(f)
        print(f"  Added {counts['cold_reads']} entries")

        print("\n[11/13] Recipe match files (Phase 668 + 641)...")
        counts['recipe_matches'] = add_recipe_match_files(f)
        print(f"  Added {counts['recipe_matches']} entries")

        print("\n[12/13] Atom decomposition lookup (with structural-only marker)...")
        counts['atom_decomp'] = add_atom_decompositions(f)
        print(f"  Added {counts['atom_decomp']} entries")

    # Summary
    total = sum(counts.values())
    out_size = OUT_PATH.stat().st_size
    print(f"\n=== SUMMARY ===")
    for k, v in counts.items():
        print(f"  {k:25s}: {v:>5d} entries")
    print(f"  {'TOTAL':25s}: {total:>5d} entries")
    print(f"  File size: {out_size/1024/1024:.2f} MB ({out_size:,} bytes)")
    print(f"  Saved: {OUT_PATH}")


if __name__ == '__main__':
    main()
