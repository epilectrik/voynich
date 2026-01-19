"""Create regime_folio_mapping.json from OPS2 cluster assignments."""
import json
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Load the OPS2 cluster assignments
ops2_path = PROJECT_ROOT / "phases" / "OPS2_control_strategy_clustering" / "ops2_folio_cluster_assignments.json"
ops2_data = json.loads(ops2_path.read_text())

# Build REGIME -> folios mapping
regime_folios = defaultdict(list)
for folio, info in ops2_data['assignments'].items():
    regime = info['cluster_id']
    regime_folios[regime].append(folio)

# Sort folios within each regime
for regime in regime_folios:
    regime_folios[regime].sort()

# Save the mapping
output_path = PROJECT_ROOT / "results" / "regime_folio_mapping.json"
output_path.write_text(json.dumps(dict(regime_folios), indent=2))

# Print summary
print("Created regime_folio_mapping.json:")
for regime in sorted(regime_folios.keys()):
    print(f"  {regime}: {len(regime_folios[regime])} folios")
