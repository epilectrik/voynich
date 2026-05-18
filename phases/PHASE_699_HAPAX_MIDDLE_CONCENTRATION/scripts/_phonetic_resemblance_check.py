"""Quick sanity check: how many MIDDLEs phonetically resemble alchemical apparatus names?

If many MIDDLEs accidentally resemble apparatus words, the 'alod = aludel'
identification has high false-positive prior.
"""
import sys, io
from collections import defaultdict, Counter
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = Path("C:/git/voynich")
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology

morph = Morphology()

# Common alchemical apparatus/material terms (medieval Latin/vernacular forms)
APPARATUS = [
    ("aludel", "ash-phase sublimation vessel"),
    ("alembic", "distillation head"),
    ("cucurbit", "distillation body"),
    ("matrass", "long-necked flask"),
    ("retort", "curved distillation vessel"),
    ("pelican", "circulatory vessel"),
    ("crucible", "calcination vessel"),
    ("athanor", "self-feeding furnace"),
    ("balneum", "water bath"),
    ("cendres", "ashes"),
    ("ignis", "fire"),
    ("aqua", "water"),
    ("oleum", "oil"),
    ("aurum", "gold"),
    ("argentum", "silver"),
    ("mercurius", "mercury"),
    ("sulfur", "sulfur"),
]

def collect_middles():
    tx = Transcript()
    middles = Counter()
    for t in tx.currier_b():
        if not t.word or t.is_uncertain: continue
        if not (t.placement and t.placement.startswith("P")): continue
        try:
            m = morph.extract(t.word.lower())
            if m.middle:
                middles[m.middle] += 1
        except Exception:
            pass
    return middles


def common_prefix_chars(a, b, max_check=5):
    """Count shared starting characters (cheap phonetic-resemblance score)."""
    for i in range(min(len(a), len(b), max_check)):
        if a[i] != b[i]:
            return i
    return min(len(a), len(b), max_check)


def main():
    middles = collect_middles()
    print(f"Currier B MIDDLE inventory: {len(middles)} unique")

    print(f"\n=== PHONETIC RESEMBLANCE CHECK ===")
    print(f"For each apparatus name, find MIDDLEs sharing 3+ starting characters:\n")

    for name, gloss in APPARATUS:
        # Compare against all MIDDLEs
        hits = []
        for m in middles:
            shared = common_prefix_chars(m, name)
            if shared >= 3:
                hits.append((m, shared, middles[m]))
        hits.sort(key=lambda x: (-x[1], -x[2]))
        n_hits = len(hits)
        if hits:
            sample = hits[:5]
            print(f"  {name} ({gloss}): {n_hits} candidate MIDDLEs")
            for m, shared, freq in sample:
                hapax = " [HAPAX]" if freq == 1 else ""
                print(f"    {m}: {shared} shared chars, freq={freq}{hapax}")
        else:
            print(f"  {name} ({gloss}): 0 candidate MIDDLEs")

    # Specific: how unique is alod ≈ aludel as a resemblance?
    print(f"\n=== ALOD-CLASS RESEMBLANCE ===")
    alod_class = []
    for m in middles:
        if m.startswith("al"):
            alod_class.append((m, middles[m]))
    alod_class.sort(key=lambda x: -x[1])
    print(f"  MIDDLEs starting with 'al': {len(alod_class)}")
    for m, freq in alod_class[:15]:
        hapax = " [HAPAX]" if freq == 1 else ""
        print(f"    {m}: freq={freq}{hapax}")


if __name__ == "__main__":
    main()
