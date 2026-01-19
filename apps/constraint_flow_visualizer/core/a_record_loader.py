"""
Currier A Record Loader.

Loads full Currier A records (entire lines) from the corpus.
Per C233, C473, C481 - the record (line) is the structural unit
that interacts with AZC, not individual tokens.

A single token carries part of a constraint signature.
A record carries a complete constraint bundle.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ARecord:
    """
    A complete Currier A record (entire line).

    Per C484:
    - 1-token entries are typically labels (filtered by placement='L')
    - 2+ token entries are registry entries (constraint bundles)

    After placement filtering, nearly all records have 2+ tokens.
    Any remaining 1-token entries are legitimate paragraph text.
    """
    folio: str
    line_number: str
    section: str
    tokens: List[str]

    @property
    def display_name(self) -> str:
        """Display name for the record."""
        return f"{self.folio}.{self.line_number}"

    @property
    def token_count(self) -> int:
        """Number of tokens in the record."""
        return len(self.tokens)

    @property
    def is_registry_entry(self) -> bool:
        """
        Registry entries have 2+ tokens (C484).
        1-token entries are control operators.
        """
        return self.token_count >= 2

    @property
    def is_short_entry(self) -> bool:
        """Short entries have exactly 1 token (rare after label filtering)."""
        return self.token_count == 1

    @property
    def tokens_display(self) -> str:
        """Display string of all tokens."""
        return " ".join(self.tokens)


@dataclass
class ARecordStore:
    """Store of all Currier A records."""
    records_by_folio: Dict[str, List[ARecord]] = field(default_factory=dict)
    all_records: List[ARecord] = field(default_factory=list)

    @property
    def folios(self) -> List[str]:
        """Get sorted list of A folios."""
        return sorted(self.records_by_folio.keys())

    @property
    def total_records(self) -> int:
        """Total number of records."""
        return len(self.all_records)

    @property
    def registry_entries(self) -> List[ARecord]:
        """Records with 2+ tokens (actual registry entries)."""
        return [r for r in self.all_records if r.is_registry_entry]

    @property
    def short_entries(self) -> List[ARecord]:
        """Records with 1 token (rare after label filtering)."""
        return [r for r in self.all_records if r.is_short_entry]

    def get_records_for_folio(self, folio: str) -> List[ARecord]:
        """Get all records for a specific folio."""
        return self.records_by_folio.get(folio, [])


# =============================================================================
# LOADER
# =============================================================================

# Singleton store
_store: Optional[ARecordStore] = None


def _find_transcript_file() -> Optional[Path]:
    """Find the interlinear transcript file."""
    # Try several potential locations
    candidates = [
        Path(__file__).parent.parent.parent.parent / "data" / "transcriptions" / "interlinear_full_words.txt",
        Path("C:/git/voynich/data/transcriptions/interlinear_full_words.txt"),
        Path("data/transcriptions/interlinear_full_words.txt"),
    ]

    for path in candidates:
        if path.exists():
            return path

    return None


def load_a_records() -> ARecordStore:
    """
    Load all Currier A records from the corpus.

    Reads interlinear_full_words.txt, filters to:
    - transcriber='H' (PRIMARY track - mandatory per TRANSCRIPT_ARCHITECTURE.md)
    - language='A' (Currier A only)
    - placement starts with 'P' (paragraph text, excludes Labels)

    Labels (placement='L') are single tokens on page margins - NOT registry entries.

    Groups tokens by (folio, line_number) to reconstruct full records.

    Returns:
        ARecordStore with all A records grouped by folio
    """
    global _store

    if _store is not None:
        return _store

    transcript_path = _find_transcript_file()

    if transcript_path is None:
        # Return empty store if file not found
        print("WARNING: Transcript file not found. Using empty A record store.")
        _store = ARecordStore()
        return _store

    # Parse the interlinear file
    # Columns: word, ..., folio(2), section(3), ..., language(6), ..., line_number(11), transcriber(12)
    records_by_key: Dict[str, ARecord] = {}
    token_order: Dict[str, List[tuple]] = defaultdict(list)  # key -> [(position, token)]

    with open(transcript_path, 'r', encoding='utf-8') as f:
        # Skip header
        header = f.readline()

        for line_num, line in enumerate(f, start=2):
            parts = line.strip().split('\t')
            if len(parts) < 13:
                continue

            # Extract fields (strip quotes)
            def clean(s):
                return s.strip('"').strip()

            word = clean(parts[0])
            folio = clean(parts[2])
            section = clean(parts[3])
            language = clean(parts[6])
            placement = clean(parts[10])
            line_number = clean(parts[11])
            transcriber = clean(parts[12])

            # Filter: PRIMARY transcriber only (H)
            if transcriber != 'H':
                continue

            # Filter: Currier A only
            if language != 'A':
                continue

            # Filter: TEXT only (placement starts with 'P')
            # Excludes Labels (L) which are single tokens on page margins
            if not placement.startswith('P'):
                continue

            # Skip empty tokens
            if not word:
                continue

            # Build record key
            key = f"{folio}_{line_number}"

            # Track token order (use line_num in file as proxy for position)
            token_order[key].append((line_num, word))

            # Create record if new
            if key not in records_by_key:
                records_by_key[key] = ARecord(
                    folio=folio,
                    line_number=line_number,
                    section=section,
                    tokens=[]
                )

    # Build final records with tokens in order
    all_records = []
    records_by_folio = defaultdict(list)

    for key, record in records_by_key.items():
        # Sort tokens by their position in file
        sorted_tokens = sorted(token_order[key], key=lambda x: x[0])
        record.tokens = [t[1] for t in sorted_tokens]

        all_records.append(record)
        records_by_folio[record.folio].append(record)

    # Sort records within each folio by line number
    for folio in records_by_folio:
        records_by_folio[folio].sort(
            key=lambda r: (int(r.line_number) if r.line_number.isdigit() else 0, r.line_number)
        )

    _store = ARecordStore(
        records_by_folio=dict(records_by_folio),
        all_records=all_records
    )

    return _store


def get_a_record_store() -> ARecordStore:
    """Get the A record store (loads if needed)."""
    return load_a_records()


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_a_folios() -> List[str]:
    """Get sorted list of all Currier A folios."""
    return get_a_record_store().folios


def get_records_for_folio(folio: str) -> List[ARecord]:
    """Get all records for a specific folio."""
    return get_a_record_store().get_records_for_folio(folio)


def get_registry_entries() -> List[ARecord]:
    """Get all registry entries (2+ token records)."""
    return get_a_record_store().registry_entries


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("Loading Currier A records...")
    store = load_a_records()

    print(f"\nSummary:")
    print(f"  Total records: {store.total_records}")
    print(f"  Registry entries (2+ tokens): {len(store.registry_entries)}")
    print(f"  Control operators (1 token): {len(store.control_operators)}")
    print(f"  Unique folios: {len(store.folios)}")

    print(f"\nFirst 5 folios: {store.folios[:5]}")

    # Show example records
    if store.folios:
        first_folio = store.folios[0]
        records = store.get_records_for_folio(first_folio)
        print(f"\nRecords in {first_folio} ({len(records)} total):")
        for r in records[:5]:
            type_str = "REGISTRY" if r.is_registry_entry else "CONTROL_OP"
            print(f"  {r.display_name}: [{type_str}] {r.tokens_display}")
