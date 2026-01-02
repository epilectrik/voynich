# Speculative Process Family Alignment
> **FRAMING**: This is explicitly speculative. The grammar is locked. These are pattern-matches, not claims.

## Available Constraints (Facts Respected)
- Closed-loop, self-circulating geometry required (G1 open flow = 93.5% failure)
- Continuous operation, not batch-finite
- Phase transitions avoided (CLASS_C = 19.8% failure, all PHASE_COLLAPSE)
- Expert-operated (no definitions, no remedial instruction)
- Enumerated safe programs (not continuous tuning)
- Stability and containment prioritized over speed/yield
- Waiting/damping explicitly encoded (LINK operator)
- Compatible with: porous solids, non-swelling solids, homogeneous fluids
- Incompatible with: emulsions, phase-unstable materials

## Process Family Alignment Matrix

### CONTINUOUS_EXTRACTION
**Description**: Gradual removal of mobile fractions through circulation

**Alignment Strength**: STRONG

**What it fits**:
- LINK encodes waiting for mobility-limited transport
- High kernel contact = active driving of flow
- Low hazard density = avoidance of concentration spikes
- Explains program diversity: different substrates need different extraction rates

**What it fails to explain**:
- Why some programs have very high intervention frequencies
- The specific meaning of recovery operations

---

### CIRCULATION_CONDITIONING
**Description**: Continuous circulation to maintain material in target state

**Alignment Strength**: STRONG

**What it fits**:
- LINK-heavy programs = extended waiting for equilibration
- STATE-C convergence = target state maintenance
- Low LINK programs = faster refresh cycles
- Explains 100% convergence: all programs reach stable maintenance

**What it fails to explain**:
- Why 6 extended runs are structurally necessary
- The specific distinction between recovery operations

---

### REDISTRIBUTION_PROCESS
**Description**: Progressive movement of components between regions

**Alignment Strength**: MODERATE

**What it fits**:
- Cycle regularity = periodic refresh of concentration gradients
- Hazard topology = preventing runaway concentration
- Near-miss counts = operating near concentration limits
- Explains compact vs extended: different redistribution depths

**What it fails to explain**:
- Why material CLASS_C fails specifically
- The role of reset-present programs

---

### BREAKDOWN_DIGESTION
**Description**: Gradual transformation of material through circulation

**Alignment Strength**: WEAK

**What it fits**:
- Long programs = extended processing time
- Recovery ops = handling intermediate states
- Kernel contact = driving transformation
- Explains LINK: allowing time for slow transformations

**What it fails to explain**:
- Perfect reversibility of hazard boundaries (all bidirectional)
- Why CLASS_C (phase-unstable) fails but swelling materials work

---

### SEPARATION_BY_MOBILITY
**Description**: Differential movement of fractions based on transport properties

**Alignment Strength**: MODERATE

**What it fits**:
- Template diversity = different mobility profiles
- LINK = waiting for slower fractions to equilibrate
- Geometry selectivity = needs defined flow paths
- Explains CLASS_D compatibility: rapid diffusion enables separation

**What it fails to explain**:
- Why no endpoint signals exist in the grammar
- The specific role of near-miss operations

---

### MAINTENANCE_HOLDING
**Description**: Keeping material in stable operating regime indefinitely

**Alignment Strength**: MODERATE

**What it fits**:
- Ultra-conservative programs = pure maintenance
- LINK-heavy = minimal intervention needed
- Low intervention frequency = stable holding
- 100% STATE-C convergence = all programs can maintain

**What it fails to explain**:
- High hazard density in some programs
- Extended run programs (12.6% envelope gap)

---

## Alignment Summary
| Process Family | Alignment | Key Support | Key Gap |
|----------------|-----------|-------------|----------|
| CONTINUOUS_EXTRACTION | STRONG | LINK encodes waiting for mobility-limited transpor... | Why some programs have very high interve... |
| CIRCULATION_CONDITIONING | STRONG | LINK-heavy programs = extended waiting for equilib... | Why 6 extended runs are structurally nec... |
| REDISTRIBUTION_PROCESS | MODERATE | Cycle regularity = periodic refresh of concentrati... | Why material CLASS_C fails specifically |
| BREAKDOWN_DIGESTION | WEAK | Long programs = extended processing time | Perfect reversibility of hazard boundari... |
| SEPARATION_BY_MOBILITY | MODERATE | Template diversity = different mobility profiles | Why no endpoint signals exist in the gra... |
| MAINTENANCE_HOLDING | MODERATE | Ultra-conservative programs = pure maintenance | High hazard density in some programs |

## Most Consistent Interpretations
Based on constraint satisfaction, the following process families show strongest alignment:

**STRONG**: CONTINUOUS_EXTRACTION, CIRCULATION_CONDITIONING
**MODERATE**: REDISTRIBUTION_PROCESS, SEPARATION_BY_MOBILITY, MAINTENANCE_HOLDING
**WEAK**: BREAKDOWN_DIGESTION

## Common Thread Analysis
All STRONG-aligned process families share:
1. **Circulation as primary mechanism** - Material moves in loops, not straight paths
2. **Time-dependent outcomes** - Longer circulation = greater effect
3. **No discrete endpoint** - Operation continues until externally terminated
4. **Stability priority** - Avoiding runaways more important than speed
5. **Damping as control** - LINK maps to physical waiting/settling time

## What Would Distinguish Between STRONG Candidates
| Discriminator | CONTINUOUS_EXTRACTION | CIRCULATION_CONDITIONING |
|---------------|----------------------|-------------------------|
| Irreversibility | YES (removal) | NO (maintenance) |
| Cumulative change | YES | NO |
| Extended runs needed | To extract more | To maintain longer |
| Reset meaning | Start fresh extraction | Return to initial state |

**SPECULATIVE CONCLUSION**: The grammar is *equally consistent* with extraction-type and conditioning-type processes. Internal analysis cannot distinguish between them.
