#!/usr/bin/env python3
"""
Phase 692 Step 2: Format the training corpus for LoRA fine-tuning.

Reads training_corpus.jsonl (5,936 entries) and produces two output formats:

  training_text.jsonl    - Plain text format: {"text": "..."} per sample
                           Works with any causal LM. Each entry becomes one or
                           more training samples (long entries get chunked).

  training_chat.jsonl    - ChatML conversational format: {"messages": [...]}
                           Q&A pairs derived from constraints + cold reads +
                           workshop dictionaries. Teaches conversational use.

Strategy:
  - Knowledge ingestion (text format): every entry with structural framing
  - Q&A synthesis (chat format): generate questions from entries that have
    obvious Q&A structure (constraints, dictionaries, cold reads)

Long-entry handling:
  - Target chunk size: ~6000 chars (~2000 tokens)
  - Split at paragraph/section boundaries
  - Add continuation markers so model knows it's part of a longer doc

The text format is the primary training signal. Chat is for conversational
fine-tuning at the end.
"""
import json
import re
import sys
from pathlib import Path

PHASE_DIR = Path(__file__).resolve().parents[1]
IN_PATH = PHASE_DIR / 'data' / 'training_corpus.jsonl'
OUT_TEXT = PHASE_DIR / 'data' / 'training_text.jsonl'
OUT_CHAT = PHASE_DIR / 'data' / 'training_chat.jsonl'

CHUNK_SIZE = 6000  # chars per training sample (~2000 tokens)
MIN_SAMPLE = 200   # below this, drop


SYSTEM_PROMPT = """You are an expert on the Voynich Manuscript research project. The project has registered 2018+ structural constraints across 691+ research phases. You reason in terms of constraints (cited as C####), tier-marked claims (Tier 0=frozen, 1=falsified, 2=established, 3=speculative, 4=exploratory), and operational/structural categories.

Critical distinctions you maintain:
- Atom decomposition (e.g., kee = heat.cool.cool) is STRUCTURAL ONLY, not semantic.
- Compound/operational reading (e.g., kee = "gentle stabilized heat", balneum mariae signature per C1455) is the meaningful interpretation.
- You always distinguish what is corroborated (Tier 2) from what is speculative (Tier 3-4).
- You cite specific constraints when making claims.
- You acknowledge what is falsified (Tier 1) and refuse to reproduce it."""


def chunk_text(text, chunk_size=CHUNK_SIZE):
    """Split long text into chunks at paragraph boundaries."""
    if len(text) <= chunk_size:
        return [text]
    # Try to split on double newline
    paragraphs = text.split('\n\n')
    chunks = []
    current = []
    current_len = 0
    for para in paragraphs:
        plen = len(para) + 2
        if current_len + plen > chunk_size and current:
            chunks.append('\n\n'.join(current))
            current = [para]
            current_len = plen
        else:
            current.append(para)
            current_len += plen
    if current:
        chunks.append('\n\n'.join(current))
    # Hard split any chunks still too long
    final = []
    for c in chunks:
        while len(c) > chunk_size * 1.5:
            split_at = c.rfind('\n', 0, chunk_size)
            if split_at < chunk_size // 2:
                split_at = chunk_size
            final.append(c[:split_at])
            c = c[split_at:]
        final.append(c)
    return final


def format_text_sample(entry, chunk_idx=None, n_chunks=None):
    """Format a single training sample with metadata header."""
    header_parts = [f"[Source: {entry['source']}]"]
    header_parts.append(f"[Type: {entry['type']}]")
    header_parts.append(f"[Tier: {entry['tier']}]")
    if entry.get('metadata'):
        meta_str = ', '.join(f"{k}={v}" for k, v in entry['metadata'].items()
                             if isinstance(v, (str, int, float)))
        if meta_str:
            header_parts.append(f"[Metadata: {meta_str}]")
    if chunk_idx is not None and n_chunks > 1:
        header_parts.append(f"[Chunk {chunk_idx+1}/{n_chunks}]")
    header = ' '.join(header_parts)
    return f"{header}\n\n{entry['content']}"


def synthesize_qa_constraint(entry):
    """For a constraint entry, generate a Q&A pair."""
    cid = entry.get('metadata', {}).get('constraint_id', '?')
    questions = [
        f"What does constraint {cid} establish?",
        f"Tell me about {cid}.",
        f"Explain {cid}.",
    ]
    # Use first question deterministically
    return questions[0], entry['content']


def synthesize_qa_phase(entry):
    """For a phase report, generate Q&A."""
    phase = entry.get('metadata', {}).get('phase', 'this phase')
    return f"What did {phase} investigate and find?", entry['content']


def synthesize_qa_cold_read(entry):
    """For a cold-read table, generate Q&A."""
    folio = entry.get('metadata', {}).get('folio', 'this folio')
    return f"What is the workshop reading of {folio}?", entry['content']


def synthesize_qa_lexicon(entry):
    """For a lexicon entry, generate Q&A."""
    kind = entry.get('metadata', {}).get('kind', 'lexicon')
    if kind == 'lexicon_top100':
        q = "What are the top operational interpretations of the most frequent Voynich tokens?"
    elif kind == 'pending_tests':
        q = "What pending test designations (PT-###) does the project use, and what do they mean?"
    elif kind == 'middle_dictionary':
        q = "What does the middle dictionary contain?"
    elif kind == 'dark_pipeline':
        q = "What is the dark pipeline dictionary?"
    elif kind == 'glossing_rules':
        q = "What are the glossing rules and atom decomposition system?"
    else:
        q = f"Explain the {kind} lexicon."
    return q, entry['content']


def synthesize_qa_voynich(entry):
    """For raw Voynich, frame as 'show me the text of folio X'."""
    folio = entry.get('metadata', {}).get('folio', 'this folio')
    return f"Show me the H-track text of folio {folio}.", entry['content']


def synthesize_qa_recipe_match(entry):
    """For a recipe-match file."""
    kind = entry.get('metadata', {}).get('kind', 'recipe match')
    return f"What confirmed Voynich-Pseudo Lull recipe matches does the project have? ({kind})", entry['content']


def synthesize_qa_methodology(entry):
    """For methodology docs."""
    src = entry['source'].split('/')[-1]
    return f"What does {src} establish about project methodology?", entry['content']


def synthesize_qa_interpretation(entry):
    """For interpretation files."""
    return "What is the project's interpretive synthesis of Voynich?", entry['content']


def synthesize_qa_memory(entry):
    """For memory notes."""
    src = entry['source'].split('/')[-1]
    return f"What does the memory note '{src}' record?", entry['content']


def synthesize_qa_atom_decomp(entry):
    """For the atom decomposition table — emphasize the warning."""
    q = "Show me the atom decomposition table for Voynich tokens. Be sure to note that atom decomposition is structural only, NOT semantic."
    return q, entry['content']


# Type → Q&A synthesizer
QA_SYNTHESIZERS = {
    'constraint': synthesize_qa_constraint,
    'phase_report': synthesize_qa_phase,
    'cold_read': synthesize_qa_cold_read,
    'lexicon_entry': synthesize_qa_lexicon,
    'raw_voynich': synthesize_qa_voynich,
    'recipe_match': synthesize_qa_recipe_match,
    'methodology': synthesize_qa_methodology,
    'interpretation': synthesize_qa_interpretation,
    'memory_note': synthesize_qa_memory,
    'atom_decomp': synthesize_qa_atom_decomp,
}


def main():
    n_text = 0
    n_chat = 0
    text_chars = 0
    chat_chars = 0

    with open(IN_PATH, encoding='utf-8') as fin, \
         open(OUT_TEXT, 'w', encoding='utf-8') as fout_text, \
         open(OUT_CHAT, 'w', encoding='utf-8') as fout_chat:

        for line in fin:
            entry = json.loads(line)

            # === TEXT FORMAT ===
            content = entry['content']
            chunks = chunk_text(content, CHUNK_SIZE)
            for ci, chunk in enumerate(chunks):
                if len(chunk) < MIN_SAMPLE:
                    continue
                # Build chunk-aware entry
                e2 = dict(entry)
                e2['content'] = chunk
                sample_text = format_text_sample(e2, ci, len(chunks))
                fout_text.write(json.dumps({'text': sample_text}, ensure_ascii=False) + '\n')
                n_text += 1
                text_chars += len(sample_text)

            # === CHAT FORMAT (Q&A) ===
            etype = entry['type']
            if etype in QA_SYNTHESIZERS:
                qa_question, qa_answer = QA_SYNTHESIZERS[etype](entry)
                # Chunk the answer if needed
                ans_chunks = chunk_text(qa_answer, CHUNK_SIZE - 200)
                for ci, ans_chunk in enumerate(ans_chunks):
                    if len(ans_chunk) < MIN_SAMPLE:
                        continue
                    if len(ans_chunks) > 1:
                        q = f"{qa_question} (part {ci+1}/{len(ans_chunks)})"
                    else:
                        q = qa_question
                    chat_sample = {
                        'messages': [
                            {'role': 'system', 'content': SYSTEM_PROMPT},
                            {'role': 'user', 'content': q},
                            {'role': 'assistant', 'content': ans_chunk},
                        ]
                    }
                    fout_chat.write(json.dumps(chat_sample, ensure_ascii=False) + '\n')
                    n_chat += 1
                    chat_chars += len(json.dumps(chat_sample, ensure_ascii=False))

    # Reporting
    print(f"=== Output files ===")
    print(f"  {OUT_TEXT}")
    print(f"    {n_text:,} samples, {text_chars:,} chars total ({text_chars/1024/1024:.1f} MB)")
    print(f"    avg sample size: {text_chars/n_text:.0f} chars")
    print(f"  {OUT_CHAT}")
    print(f"    {n_chat:,} samples, {chat_chars:,} chars total ({chat_chars/1024/1024:.1f} MB)")
    print(f"    avg sample size: {chat_chars/n_chat:.0f} chars" if n_chat else "")

    # Show a sample of each
    print("\n=== Sample TEXT entry ===")
    with open(OUT_TEXT, encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i == 5:
                r = json.loads(line)
                print(r['text'][:800])
                break
    print("\n=== Sample CHAT entry ===")
    with open(OUT_CHAT, encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i == 5:
                r = json.loads(line)
                print(json.dumps(r, indent=2, ensure_ascii=False)[:1200])
                break


if __name__ == '__main__':
    main()
