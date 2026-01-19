"""
T7: Puff Data Quality Audit
Analyze coverage and quality of Puff extraction data
"""

import json
from pathlib import Path
from collections import Counter

RESULTS_DIR = Path(__file__).parent.parent.parent / "results"

def audit_puff_data():
    """Audit Puff data quality and coverage."""

    # Load reference data (clean)
    with open(RESULTS_DIR / "puff_83_chapters.json", 'r', encoding='utf-8') as f:
        reference = json.load(f)

    # Load extracted semantics (noisy)
    with open(RESULTS_DIR / "puff_chapter_semantics.json", 'r', encoding='utf-8') as f:
        semantics = json.load(f)

    print("=" * 60)
    print("T7: PUFF DATA QUALITY AUDIT")
    print("=" * 60)

    # Reference data analysis
    chapters = reference['chapters']
    print(f"\n[REFERENCE DATA: puff_83_chapters.json]")
    print(f"  Total chapters: {len(chapters)}")

    # Count flags
    dangerous = [c for c in chapters if c.get('dangerous')]
    aromatic = [c for c in chapters if c.get('aromatic')]
    external = [c for c in chapters if c.get('external_source')]

    print(f"  Dangerous materials: {len(dangerous)}")
    for d in dangerous:
        print(f"    - Ch.{d['chapter']}: {d['german']} ({d['latin']})")

    print(f"  Aromatic materials: {len(aromatic)}")
    print(f"  External sources (Ch.83-84): {len(external)}")

    # Category distribution
    categories = Counter(c['category'] for c in chapters)
    print(f"\n  Category distribution:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"    {cat}: {count}")

    # Semantics data analysis
    extracted = semantics['chapters']
    stats = semantics.get('extraction_stats', {})

    print(f"\n[EXTRACTED SEMANTICS: puff_chapter_semantics.json]")
    print(f"  Chapters extracted: {len(extracted)}")
    print(f"  Coverage: {len(extracted)}/{len(chapters)} = {100*len(extracted)/len(chapters):.1f}%")

    # Application method quality
    app_dist = stats.get('application_distribution', {})
    print(f"\n  Application method distribution:")
    for method, count in app_dist.items():
        print(f"    {method}: {count}")

    unknown_rate = app_dist.get('unknown', 0) / len(extracted) if extracted else 0
    print(f"  Unknown rate: {100*unknown_rate:.1f}%")

    # Humoral quality
    temp_dist = stats.get('temperature_distribution', {})
    print(f"\n  Humoral temperature distribution:")
    for temp, count in temp_dist.items():
        print(f"    {temp}: {count}")

    neutral_rate = temp_dist.get('neutral', 0) / len(extracted) if extracted else 0
    print(f"  Neutral (uninformative) rate: {100*neutral_rate:.1f}%")

    # Data quality assessment
    print("\n" + "=" * 60)
    print("DATA QUALITY ASSESSMENT")
    print("=" * 60)

    print("""
[CLEAN DATA - Usable for all tests]
  - puff_83_chapters.json: 84/84 chapters (100%)
  - Category flags: Complete
  - Dangerous flags: 5 chapters marked
  - Aromatic flags: 16 chapters marked

[NOISY DATA - Limited usability]
  - puff_chapter_semantics.json: 47/84 chapters (56%)
  - Application method: 58% unknown
  - Humoral profile: 91% neutral (uninformative)
  - Chapter alignment: Not preserved (OCR indices != chapter numbers)

[TEST VIABILITY]
  T4 (Category -> PREFIX): VIABLE - uses clean reference data
  T8 (Complexity -> Cluster): VIABLE - can use chapter position as complexity proxy
  T9 (Danger -> HT): VIABLE - uses clean dangerous flags
  T5 (Humoral -> REGIME): LIMITED - 91% neutral, low signal
  T3 (Organ -> Zone): SKIP - high risk + noisy data
""")

    # Generate audit report
    audit_report = {
        "audit_date": "2026-01-19",
        "reference_data": {
            "file": "puff_83_chapters.json",
            "total_chapters": len(chapters),
            "coverage": "100%",
            "dangerous_chapters": [c['chapter'] for c in dangerous],
            "aromatic_count": len(aromatic),
            "external_source_count": len(external),
            "category_distribution": dict(categories)
        },
        "extracted_semantics": {
            "file": "puff_chapter_semantics.json",
            "chapters_extracted": len(extracted),
            "coverage_pct": round(100 * len(extracted) / len(chapters), 1),
            "application_unknown_pct": round(100 * unknown_rate, 1),
            "humoral_neutral_pct": round(100 * neutral_rate, 1),
            "alignment_preserved": False
        },
        "test_viability": {
            "T4_category_prefix": "VIABLE",
            "T8_complexity_cluster": "VIABLE",
            "T9_danger_ht": "VIABLE",
            "T5_humoral_regime": "LIMITED",
            "T3_organ_zone": "SKIP"
        },
        "recommendation": "Proceed with T4, T8, T9 using clean reference data"
    }

    with open(RESULTS_DIR / "puff_data_audit.json", 'w', encoding='utf-8') as f:
        json.dump(audit_report, f, indent=2)

    print(f"\nAudit saved to: results/puff_data_audit.json")

    return audit_report

if __name__ == "__main__":
    audit_puff_data()
