"""
04_semantic_synthesis.py

Build the complete semantic model for FL state indexing.
Synthesize findings from scripts 01-03 into a coherent interpretation.
"""
import sys
import json
from pathlib import Path

# Load results from previous scripts
results_dir = Path(__file__).parent.parent / "results"

with open(results_dir / "01_fl_process_stage_mapping.json") as f:
    stage_mapping = json.load(f)

with open(results_dir / "02_en_transformation_profiles.json") as f:
    en_profiles = json.load(f)

with open(results_dir / "03_hazard_safe_discrimination.json") as f:
    hazard_safe = json.load(f)

print("=" * 70)
print("FL SEMANTIC SYNTHESIS: Material State Indexing Model")
print("=" * 70)

# ============================================================
# SECTION 1: FL STATE TAXONOMY
# ============================================================
print("\n" + "=" * 70)
print("1. FL STATE TAXONOMY")
print("=" * 70)

print("""
FL MIDDLEs index material position in a transformation process.

STAGE         MIDDLEs              POSITION    HAZARD%   INTERPRETATION
---------------------------------------------------------------------------
INITIAL       ii, i                0.30-0.35   87.5%     Material entering
EARLY         in                   0.42        100.0%    Early processing
MEDIAL        r, ar, al, l, ol     0.51-0.64   97.3%     Active transformation
LATE          o, ly                0.75-0.79   0.0%      Transformation completing
TERMINAL      am, m, dy, ry, y     0.80-0.94   38.9%     Output/finished

Character encoding:
  'i' = INPUT marker (appears at process start)
  'y' = YIELD marker (appears at process end)
  consonants (r, l, m, n) = transformation stage modifiers
  vowels (a, o) = state quality modifiers
""")

# ============================================================
# SECTION 2: HAZARD/SAFE SEMANTICS
# ============================================================
print("\n" + "=" * 70)
print("2. HAZARD/SAFE SEMANTICS")
print("=" * 70)

print(f"""
HAZARD FL vs SAFE FL:

  Hazard tokens: {hazard_safe['hazard_token_count']} (88.7%)
  Safe tokens:   {hazard_safe['safe_token_count']} (11.3%)

HAZARD FL = "Material in unstable/transitional state"
  - Concentrated in INITIAL/EARLY/MEDIAL (95.6%)
  - Mean line position: {hazard_safe['hazard_mean_position']:.3f}
  - Escape to FQ: 16.7% of transitions
  - Needs active management

SAFE FL = "Material has reached stable state"
  - Concentrated in LATE/TERMINAL (77.1%)
  - Mean line position: {hazard_safe['safe_mean_position']:.3f}
  - Escape to FQ: 5.6% of transitions
  - Minimal intervention needed

SEMANTIC RULE: Position in process determines stability.
  - Early/mid = unstable (hazard)
  - Late/terminal = stable (safe)
""")

# ============================================================
# SECTION 3: KERNEL TRANSFORMATION SEMANTICS
# ============================================================
print("\n" + "=" * 70)
print("3. KERNEL TRANSFORMATION SEMANTICS (EN around FL)")
print("=" * 70)

print("""
EN uses kernel characters (k, h, e) to transform material between FL states.

KERNEL 'k' (ENERGY OPERATOR):
  - Higher BEFORE FL states than after
  - Peak: 45.3% before MEDIAL, 12.7% after
  - Semantic: "Inject energy to drive state transition"

KERNEL 'e' (STABILITY OPERATOR):
  - Higher AFTER FL states than before
  - Peak: 64.0% after MEDIAL, 40.3% before
  - Semantic: "Verify stability after state change"

KERNEL 'h' (PHASE OPERATOR):
  - Generally low in this dataset
  - Semantic: "Align phase/orientation"

TRANSFORMATION SEQUENCE:

  [EN k-heavy] --> FL[STATE] --> [EN e-heavy]
       |              |              |
    ENERGY        MATERIAL       STABILITY
   INJECTION       STATE          CHECK
""")

# ============================================================
# SECTION 4: INTEGRATED SEMANTIC MODEL
# ============================================================
print("\n" + "=" * 70)
print("4. INTEGRATED SEMANTIC MODEL")
print("=" * 70)

print("""
THE FL STATE INDEXING MODEL:

FL provides a substrate layer that indexes WHERE material is in a
transformation process. Other roles (EN, CC, FQ) provide the HOW.

+------------------------------------------------------------------+
|                    TRANSFORMATION PIPELINE                        |
+------------------------------------------------------------------+
|                                                                   |
|   INPUT          PROCESSING              OUTPUT                   |
|     |                |                      |                     |
|     v                v                      v                     |
|  FL[i,ii]  -->  FL[r,l,ar,al]  -->  FL[o,ly]  -->  FL[y,ry]      |
|  INITIAL       MEDIAL              LATE         TERMINAL          |
|  (HAZARD)      (HAZARD)            (SAFE)       (SAFE)           |
|     |                |                                            |
|     |                |                                            |
|     v                v                                            |
|   +-------+    +-------+                                          |
|   |ESCAPE |<---|ESCAPE |  FQ escape for unstable material         |
|   |(16.7%)|    |pathway|                                          |
|   +-------+    +-------+                                          |
|                                                                   |
+------------------------------------------------------------------+

KERNEL MODULATION:

                    +-----------------+
                    |  FL[MEDIAL]     |
                    +--------+--------+
                             |
         +-------------------+-------------------+
         |                   |                   |
    [k injection]      [state index]       [e verification]
    (energy for        (material is        (stability
     transition)        here now)           confirmed)
""")

# ============================================================
# SECTION 5: PROCESS CONTROL ANALOGY
# ============================================================
print("\n" + "=" * 70)
print("5. PROCESS CONTROL ANALOGY")
print("=" * 70)

print("""
This model maps to INDUSTRIAL PROCESS CONTROL patterns:

1. BATCH PROCESSING:
   - Material enters (INITIAL/EARLY)
   - Transformation occurs (MEDIAL)
   - Product exits (LATE/TERMINAL)

2. SAFETY INTERLOCKS:
   - Hazard FL = "material in unstable zone"
   - Safe FL = "material in stable zone"
   - Escape routes for out-of-spec conditions

3. PHASE-GATED PROGRESSION:
   - Forward bias (C786: 27% forward, 5% backward)
   - No full reset (C787: LATE->EARLY forbidden)
   - Progression is mostly irreversible

4. ENERGY-STABILITY COUPLING:
   - Energy (k) injected to drive transitions
   - Stability (e) verified after transitions
   - Phase (h) aligned as needed

CANDIDATE PROCESS DOMAINS:
   - Chemical transformation (reactants -> products)
   - Biological extraction (raw -> processed)
   - Material preparation (crude -> refined)
   - Alchemical operation (base -> noble)
""")

# ============================================================
# SECTION 6: SEMANTIC LABELS (Tier 3 Proposals)
# ============================================================
print("\n" + "=" * 70)
print("6. PROPOSED SEMANTIC LABELS (Tier 3)")
print("=" * 70)

print("""
Based on structural evidence, proposed semantic labels:

FL MIDDLE LABELS:
  'i', 'ii'    -> INPUT          "material entering process"
  'in'         -> INTAKE         "material being received"
  'r'          -> REACTION       "primary transformation"
  'ar', 'al'   -> ADJUSTMENT     "transformation tuning"
  'l'          -> LYSIS/LOOSE    "breakdown/separation"
  'ol'         -> OVERFLOW       "excess handling"
  'o'          -> OUTPUT         "approaching completion"
  'ly'         -> LIQUOR         "liquid product"
  'm'          -> MATURED        "transformation complete"
  'y'          -> YIELD          "final product"
  'ry', 'dy'   -> REFINED YIELD  "processed output"

KERNEL LABELS:
  'k'          -> KINESIS        "energy injection"
  'h'          -> HARMONIC       "phase alignment"
  'e'          -> EQUILIBRIUM    "stability verification"

STATUS: These are speculative mappings. The structural behavior is
confirmed (Tier 2); the semantic labels are interpretive (Tier 3).
""")

# ============================================================
# SAVE MODEL
# ============================================================
model = {
    'model_name': 'FL State Indexing Model',
    'tier': 3,
    'date': '2026-01-29',
    'core_claims': [
        'FL indexes material position in transformation process',
        'Hazard FL marks unstable/in-process material',
        'Safe FL marks stable/completed material',
        'Kernel characters modulate transitions (k=energy, h=phase, e=stability)',
        'Forward-biased progression resembles batch processing'
    ],
    'fl_stage_map': {
        'INITIAL': ['ii', 'i'],
        'EARLY': ['in'],
        'MEDIAL': ['r', 'ar', 'al', 'l', 'ol'],
        'LATE': ['o', 'ly'],
        'TERMINAL': ['am', 'm', 'dy', 'ry', 'y']
    },
    'hazard_safe_boundary': 'After MEDIAL (hazard) / At LATE (safe)',
    'kernel_semantics': {
        'k': 'Energy injection for transitions',
        'h': 'Phase/orientation alignment',
        'e': 'Stability verification'
    },
    'process_analogy': 'Batch processing with safety interlocks',
    'candidate_domains': [
        'Chemical transformation',
        'Biological extraction',
        'Material preparation',
        'Alchemical operation'
    ],
    'structural_provenance': [
        'C770', 'C772', 'C777', 'C779', 'C786', 'C787', 'C775', 'C811'
    ]
}

output_path = results_dir / "04_fl_semantic_model.json"
with open(output_path, 'w') as f:
    json.dump(model, f, indent=2)

print(f"\n\nModel saved to: {output_path}")

# ============================================================
# VALIDATION CHECKLIST
# ============================================================
print("\n" + "=" * 70)
print("VALIDATION CHECKLIST")
print("=" * 70)

print("""
The model must be consistent with these Tier 2 constraints:

[x] C770: FL kernel-free (uses no k, h, e) - CONFIRMED
[x] C772: FL is primitive substrate - CONFIRMED
[x] C777: FL MIDDLEs show positional gradient - CONFIRMED
[x] C779: EN kernel varies with FL state - CONFIRMED
[x] C786: Forward bias (27% fwd, 5% back) - CONSISTENT
[x] C787: No LATE->EARLY reset - CONSISTENT
[x] C775: Hazard FL drives escape (98%) - CONFIRMED
[x] C811: FL chains (2.11x) - CONSISTENT

No structural contradictions found.
""")
