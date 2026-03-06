# C1488: Headless Compound Population Structure

**Tier:** 2
**Scope:** B, MIDDLE, headless, compound, population, census, grammar
**Phase:** HEADLESS_COMPOUND_SUBGRAMMAR (Phase 536)
**Date:** 2026-03-06

## Statement

Headless compounds (MIDDLEs whose initial atom is NOT a HEAD atom {a,e,o,k,t}) constitute 20.5% of compound tokens (3,312/16,153) and 36.8% of compound types (469/1,273). They are primarily MODIFIER-initial (77.5% of tokens): i=918 (27.7%), d=805 (24.3%), c=612 (18.5%). TERMINAL-initial compounds account for 19.3%: l=428, r=122, y=71, h=16, m=1. OTHER-initial (q,g,x) account for 3.2%. Mean length 2.64 atoms (vs headed 2.75). Headless compounds are NOT a residual category -- they form a structured population with consistent grammatical properties.

## Evidence

- **Total:** 3,312 tokens, 469 types (20.5% of 16,153 compound tokens)
- **MOD-initial:** 2,568 tokens (77.5%) -- i(918), d(805), c(612), p(157), f(44), s(32)
- **TERM-initial:** 638 tokens (19.3%) -- l(428), r(122), y(71), h(16), m(1)
- **OTHER-initial:** 106 tokens (3.2%) -- q(104), g(1), x(1)
- **Length:** mean 2.64 (std 0.854) vs headed 2.75 (std 0.874), KS p<0.001
- **Modal length:** 2 atoms (52.3% of headless vs 46.4% of headed)

## Cross-references

- C1393: Compound MIDDLE composition grammar (HEAD+MOD*+TERM)
- C1394: Instruction encoding architecture (18 atoms in 4 slot roles)
- C1397: Headless compound functional grammar (this refines and supersedes)
- C1475: HEAD atom categorical domain differentiation (defines what headless LACKS)
