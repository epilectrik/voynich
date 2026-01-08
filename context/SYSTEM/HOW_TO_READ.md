# How to Read This Context System

**Purpose:** Navigation instructions for AI readers and human researchers.

---

## The Core Principle

> "Read the smallest file that answers your question. If insufficient, that file tells you where to expand next."

This system uses **progressive disclosure**. Never read all files at once.

---

## Reading Protocol

### Step 1: Start at CLAUDE_INDEX.md

This is the only file that should be read automatically. It contains:
- Project identity (3 sentences)
- Tier definitions (4-row table)
- Navigation table (where to find what)
- Stop conditions (what not to do)

**Token budget:** ~4,000 tokens

### Step 2: Follow Links as Needed

When you encounter something you need to know more about:
1. Check the navigation table in CLAUDE_INDEX.md
2. Read only the linked file
3. That file will have its own navigation pointers

**Don't read adjacent files "just in case."**

### Step 3: Stop When Sufficient

You have enough context when:
- You can answer the user's question
- You've found the relevant constraint
- You understand the tier and closure status

**Common mistake:** Reading all of ARCHITECTURE/ when you only needed one section.

---

## Directory Reading Order (If You Must Read Multiple)

If a task requires broad context, read in this order:

1. **CLAUDE_INDEX.md** (always first)
2. **CORE/** (Tier 0-1 facts) - only if checking fundamentals
3. **Relevant ARCHITECTURE/** file - only the system you're working with
4. **CLAIMS/INDEX.md** - only if looking up constraints
5. **Specific claim file** - only if you need full detail

**Never start with SPECULATIVE/**. It's optional context, not foundation.

---

## File Size Expectations

All files in this system are designed to stay under the 25k token READ limit:

| Category | Typical Size | Max Size |
|----------|--------------|----------|
| Index files | 2-4k tokens | 8k |
| Topic files | 4-8k tokens | 12k |
| Grouped registries | 8-12k tokens | 15k |
| Individual claims | 500-1k tokens | 2k |

If a file is approaching 15k tokens, it should be split.

---

## Cross-Reference Conventions

### Internal Links

Files link to each other using relative paths:
- `[CORE/frozen_conclusion.md](CORE/frozen_conclusion.md)` from index
- `[../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)` from subdirectory

### Constraint Citations

Format: `C###` or `Constraint ###`
- Find in `CLAIMS/INDEX.md` first
- Full details in individual file or grouped registry

### Phase Citations

Format: `Phase PHASE_NAME` or `phases/PHASE_NAME/`
- Find in `MAPS/phase_index.md`
- Full documentation in `phases/` directory

---

## What NOT to Do

1. **Don't read archive/** - that's raw memory, not curated knowledge
2. **Don't read all of phases/** - 118 directories, too much context
3. **Don't read SPECULATIVE/ first** - it's interpretation, not foundation
4. **Don't ignore STOP_CONDITIONS.md** - it prevents wasted effort

---

## Navigation Footer Convention

Every file ends with a navigation footer:

```
← [Previous.md](Previous.md) | [Next.md](Next.md) →
```

Or:

```
← [CLAIMS/INDEX.md](INDEX.md) | ↑ [CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
```

Follow these to maintain reading flow.

---

## Navigation

← [METHODOLOGY.md](METHODOLOGY.md) | [CHANGELOG.md](CHANGELOG.md) →
