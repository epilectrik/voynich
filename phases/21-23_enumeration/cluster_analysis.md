# Process Cluster Analysis
*Focus on clusters, not individual matches*

---

## Cluster Characteristics

### HIGH Cluster (6 members)

**Domain composition:**
- Biological Systems: 3 (50%)
- Chemical Process: 2 (33%)
- Industrial Systems: 1 (17%)

**Similarity statistics:**
- Mean: 0.888
- Std: 0.030
- Range: [0.858, 0.952]

**Members:**
- Reflux Distillation (0.952)
- Blood Glucose Regulation (0.886)
- Distillation Column (Industrial) (0.885)
- Temperature Regulation (Mammalian) (0.878)
- Biological Homeostasis (0.871)
- Steam Boiler Pressure Control (0.858)

### MEDIUM Cluster (2 members)

**Domain composition:**
- Energy Systems: 1 (50%)
- Mechanical Systems: 1 (50%)

**Similarity statistics:**
- Mean: 0.791
- Std: 0.000
- Range: [0.791, 0.791]

**Members:**
- Nuclear Reactor Control (0.791)
- Hydraulic Servo System (0.791)

### LOW Cluster (11 members)

**Domain composition:**
- Chemical Process: 4 (36%)
- Control Theory: 1 (9%)
- Automotive: 1 (9%)
- Aerospace: 1 (9%)
- Metallurgy: 1 (9%)
- Building Systems: 1 (9%)
- Environmental: 1 (9%)
- Biological Process: 1 (9%)

**Similarity statistics:**
- Mean: 0.693
- Std: 0.029
- Range: [0.653, 0.749]

**Members:**
- PID Controller (Generic) (0.749)
- Exothermic Reactor Control (0.735)
- Cruise Control (Vehicle) (0.712)
- Aircraft Autopilot (0.700)
- Fractional Crystallization (0.696)
- Metallurgical Annealing (0.692)
- HVAC Climate Control (0.680)
- Wastewater Treatment (Aerobic) (0.671)
- Fermentation (Bioreactor) (0.670)
- Batch Reactor Control (0.661)
- Solvent Extraction (0.653)

### DISTANT Cluster (11 members)

**Domain composition:**
- Pre-modern Craft: 5 (45%)
- Food Process: 3 (27%)
- Chemical Process: 1 (9%)
- Building Systems: 1 (9%)
- Industrial Process: 1 (9%)

**Similarity statistics:**
- Mean: 0.558
- Std: 0.047
- Range: [0.497, 0.634]

**Members:**
- Medieval Alchemy (Calcination) (0.634)
- Crystallization (Industrial) (0.618)
- Thermostat (Simple) (0.604)
- Medieval Glass Furnace (0.592)
- Beer Brewing (Fermentation) (0.567)
- Paper Pulp Digester (0.565)
- Dyeing Vat (Pre-modern) (0.530)
- Blacksmith Forge Welding (0.513)
- Cheese Making (0.511)
- Pottery Kiln Firing (0.504)
- Retort Canning (0.497)

## Cross-Cluster Patterns

### HIGH vs MEDIUM Differentiators

Processes in HIGH cluster share these properties with Voynich:
- Higher categorical match (control topology, operator model)
- Closer forbidden transition counts
- Similar kernel structure presence

### Domain Exclusions

Domains with NO high-similarity matches:
- Food Process
- Building Systems
- Industrial Process
- Pre-modern Craft

