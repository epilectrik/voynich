# PHASE_775 — Is Currier B's word-boundary rule the key of a context-keyed cipher? (rank decoding)

**Status:** DESIGN. The draft pre-registration (`PRE_REGISTRATION.md`) is written. The certification on disjoint
segments is next, then a lean-expert audit, lock and one run on B. **Nothing has been computed on B's token order.**

## Question (from the human's challenge: a new, text-only test)
B's strongest rule couples each word's beginning to the previous word's ending. If that rule is the key of a cipher
whose alphabet switches with the previous ending, replacing each word by its frequency rank among the words that
follow the same ending ("rank decoding") would undo the key and bring back the hidden text's word order.

## Design so far (controls only)
- **Prototype** (`prelock_proto775.py`): with the true key, rank decoding brings back the hidden word order of ciphers
  built from real plaintext (NT, verse and recipes clearly; pharmacy lists weakly).
- **Design calibration** (`prelock_calib775.py`): the **key gain** separates the controls.
  - The key gain is the order seen by ranking within the previous ending, minus the order seen with global ranks.
  - Every keyed cipher is positive (up to +0.023).
  - Every control without a keyed message is negative: 28 no-message runs, 6 twins and 2 plain codes.
- **Thresholds** (`prelock_thresholds775.py`): τ_K1 0.0033 and τ_K2 0.0041. NEG_K1 −0.0002 and NEG_K2 −0.0009. The
  scope is plaintexts with word-order index O ≥ 0.04.
