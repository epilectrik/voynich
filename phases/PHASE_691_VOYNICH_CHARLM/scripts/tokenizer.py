#!/usr/bin/env python3
"""
Char-level tokenizer for Voynich char-LM.

Vocab:
  [PAD] = 0
  [MASK] = 1
  [CLS] = 2  (sequence start)
  [SEP] = 3  (sequence end)
  [SPACE] = 4  (token separator)
  [CURR_A] = 5  (only used in with-tag variant)
  [CURR_B] = 6
  [CURR_AZC] = 7
  <chars> = 8...

Two encoding modes:
  - 'with_tag': prepends [CURR_X] before the line content
  - 'without_tag': pure line content only (PRIMARY for probing)
"""
import json
from pathlib import Path

PHASE_DIR = Path(__file__).resolve().parent.parent

SPECIAL_TOKENS = ['[PAD]', '[MASK]', '[CLS]', '[SEP]', '[SPACE]', '[CURR_A]', '[CURR_B]', '[CURR_AZC]']
PAD_ID = 0
MASK_ID = 1
CLS_ID = 2
SEP_ID = 3
SPACE_ID = 4
SECTION_TAG_IDS = {'A': 5, 'B': 6, 'AZC': 7}


class CharTokenizer:
    def __init__(self, char_inventory):
        chars = sorted(char_inventory)
        self.id_to_token = list(SPECIAL_TOKENS) + chars
        self.token_to_id = {t: i for i, t in enumerate(self.id_to_token)}
        self.vocab_size = len(self.id_to_token)
        self.chars = chars

    def encode_line(self, tokens, section, with_tag=False, max_len=256):
        """tokens: list of str (token strings). section: 'A'/'B'/'AZC'."""
        ids = [CLS_ID]
        if with_tag:
            ids.append(SECTION_TAG_IDS[section])
        for ti, tok in enumerate(tokens):
            if ti > 0:
                ids.append(SPACE_ID)
            for ch in tok:
                if ch in self.token_to_id:
                    ids.append(self.token_to_id[ch])
                # silently drop unknown chars (shouldn't happen on H-track)
        ids.append(SEP_ID)
        if len(ids) > max_len:
            ids = ids[:max_len - 1] + [SEP_ID]
        return ids

    def decode(self, ids):
        out = []
        for i in ids:
            tok = self.id_to_token[i] if 0 <= i < self.vocab_size else '?'
            if tok == '[SPACE]':
                out.append(' ')
            elif tok in ('[PAD]', '[MASK]', '[CLS]', '[SEP]'):
                continue
            elif tok.startswith('[CURR_'):
                continue
            else:
                out.append(tok)
        return ''.join(out)

    def is_content_id(self, idx):
        """True for actual character IDs (excludes special tokens and section tags)."""
        return idx >= 8

    def save(self, path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({
                'vocab': self.id_to_token,
                'chars': self.chars,
            }, f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path):
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        return cls.__new__(cls).__init_from_data__(data['vocab'], data['chars'])

    def __init_from_data__(self, vocab, chars):
        self.id_to_token = vocab
        self.token_to_id = {t: i for i, t in enumerate(vocab)}
        self.vocab_size = len(vocab)
        self.chars = chars
        return self


def build_tokenizer():
    """Build tokenizer from char_inventory.json produced by build_corpus.py."""
    char_inv_path = PHASE_DIR / 'data' / 'char_inventory.json'
    with open(char_inv_path, encoding='utf-8') as f:
        chars = json.load(f)
    return CharTokenizer(chars)


if __name__ == '__main__':
    tok = build_tokenizer()
    out = PHASE_DIR / 'data' / 'tokenizer.json'
    tok.save(out)
    print(f"Vocab size: {tok.vocab_size}")
    print(f"Specials: {SPECIAL_TOKENS}")
    print(f"Chars: {tok.chars}")
    # Test
    sample = ['fachys', 'ykal', 'ar', 'ataiin']
    ids_with = tok.encode_line(sample, 'A', with_tag=True)
    ids_without = tok.encode_line(sample, 'A', with_tag=False)
    print(f"\nSample: {sample}")
    print(f"  with_tag    ({len(ids_with)} ids): {ids_with}")
    print(f"  without_tag ({len(ids_without)} ids): {ids_without}")
    print(f"  decoded: {tok.decode(ids_without)!r}")
    print(f"\nSaved tokenizer to {out}")
