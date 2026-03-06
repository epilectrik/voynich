# C1527: Headless Functional Core Shared — 69 Types Cover 88-89% of Tokens

**Tier:** 2
**Scope:** GLOBAL, cross-system, headless, MIDDLE, overlap, shared, functional-core, type-exclusive, C1499, C1488
**Phase:** HEADLESS_CROSS_SYSTEM (Phase 542)

## Claim

Despite high type-level exclusivity (A=63.3%, B=68.0%, AZC=39.4% of headless MIDDLE types are system-exclusive), 69 headless MIDDLE types shared across all three systems account for 88.0% (A), 89.0% (B), and 88.1% (AZC) of all headless tokens. The headless vocabulary follows the same SHARED_SUBSTRATE_GRADED_SLOTS architecture as the overall atom ontology (C1499): a small shared functional core does the work while system-exclusive types provide low-frequency specialization. Pairwise Jaccard overlaps are modest (0.158-0.183), confirming that headless type diversity is system-specific even though token mass converges on the shared core. The dark pipeline in B carries 37.6% headless (1.47x bridge's 25.6%), but this B-specific dark headless enrichment does not hold in A or AZC (A: dark 0.90x bridge; AZC: dark 0.73x bridge), showing that headless-dark affinity is a B execution grammar phenomenon.

## Evidence

- Unique headless MIDDLE types: A=395, B=484, AZC=160
- Triple-shared types: 69
- Triple-shared token coverage: A=3832/4353=88.0%, B=5584/6277=89.0%, AZC=792/899=88.1%
- System-exclusive types: A=250 (63.3%), B=329 (68.0%), AZC=63 (39.4%)
- Pairwise Jaccard: A&B=0.183, A&AZC=0.164, B&AZC=0.158
- B pipeline headless rates: bridge=25.6%, dark=37.6% (1.47x, chi2=114.5, p=1.0e-26)
- A pipeline headless rates: bridge=38.6%, dark=34.8% (0.90x)
- AZC pipeline headless rates: bridge=29.4%, dark=21.6% (0.73x)

## Relationship to Prior Constraints

- **Extends C1499**: Shared substrate (Jaccard 0.895+). Headless follows the same architecture: shared core, graded deployment, system-specific tail vocabulary
- **Extends C1488**: Headless as coherent domain. The coherence extends cross-system at the token level (88-89% convergence on 69 types)
- **Connects C1139**: Bridge-dark complete disjointness (0/300 overlap). B-specific dark headless enrichment (1.47x) is consistent with dark pipeline's identification function (C1505) — identification vocabulary is headless infrastructure
- **Connects C1500**: Bridge enriched in e/k/t HEADs (executable backbone). Bridge's lower headless rate (25.6% in B) follows mechanistically: bridge = executable = headed

## Source

`phases/HEADLESS_CROSS_SYSTEM/results/headless_cross_system.json` (T6, T10)
