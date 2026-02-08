"""
Extract all instruction types from Brunschwig curated recipes.
Generates a master list of actions with counts and examples.
"""
import json
from collections import defaultdict

with open('data/brunschwig_curated_v2.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Collect all actions with their occurrences
actions = defaultdict(lambda: {'count': 0, 'examples': []})

for recipe in data['recipes']:
    recipe_id = recipe['id']
    recipe_name = recipe.get('name_english', '')
    steps = recipe.get('procedural_steps', []) or []

    for step in steps:
        action = step.get('action', '')
        if action:
            actions[action]['count'] += 1
            # Store first 3 examples
            if len(actions[action]['examples']) < 3:
                german = step.get('german_text', '')[:60]
                english = step.get('english_translation', '')[:60]
                actions[action]['examples'].append({
                    'recipe_id': recipe_id,
                    'recipe_name': recipe_name,
                    'german': german,
                    'english': english
                })

# Sort by count descending
sorted_actions = sorted(actions.items(), key=lambda x: -x[1]['count'])

# Generate markdown
md_lines = []
md_lines.append("# Brunschwig Instruction Taxonomy")
md_lines.append("")
md_lines.append("Master list of procedural actions extracted from 245 curated Brunschwig recipes.")
md_lines.append("")
md_lines.append(f"**Total unique actions:** {len(actions)}")
md_lines.append(f"**Total action instances:** {sum(a['count'] for a in actions.values())}")
md_lines.append("")
md_lines.append("---")
md_lines.append("")
md_lines.append("## Action Summary")
md_lines.append("")
md_lines.append("| Rank | Action | Count | % of Total |")
md_lines.append("|------|--------|-------|------------|")

total_instances = sum(a['count'] for a in actions.values())
for i, (action, data) in enumerate(sorted_actions, 1):
    pct = 100 * data['count'] / total_instances
    md_lines.append(f"| {i} | {action} | {data['count']} | {pct:.1f}% |")

md_lines.append("")
md_lines.append("---")
md_lines.append("")
md_lines.append("## Detailed Action Definitions")
md_lines.append("")

for action, data in sorted_actions:
    md_lines.append(f"### {action}")
    md_lines.append("")
    md_lines.append(f"**Occurrences:** {data['count']}")
    md_lines.append("")
    md_lines.append("**Examples:**")
    md_lines.append("")
    for ex in data['examples']:
        md_lines.append(f"- Recipe {ex['recipe_id']} ({ex['recipe_name']})")
        md_lines.append(f"  - German: *{ex['german']}...*")
        md_lines.append(f"  - English: {ex['english']}...")
        md_lines.append("")

md_lines.append("---")
md_lines.append("")
md_lines.append("## Action Categories")
md_lines.append("")
md_lines.append("### Physical Preparation (Pre-distillation)")
md_lines.append("")

# Categorize actions
prep_actions = ['GATHER', 'COLLECT', 'PLUCK', 'SELECT', 'OBTAIN']
mechanical_actions = ['CHOP', 'POUND', 'CRUSH', 'BREAK', 'BORE', 'STRIP', 'BUTCHER']
cleaning_actions = ['WASH', 'CLEAN', 'FILTER']
processing_actions = ['STEEP', 'MACERATE', 'MIX', 'DRY', 'KILL']
distillation_actions = ['DISTILL', 'REDISTILL', 'REFINE']

categories = [
    ("Collection/Gathering", prep_actions, "Acquiring raw materials"),
    ("Mechanical Processing", mechanical_actions, "Physical breakdown of materials"),
    ("Cleaning/Purification", cleaning_actions, "Removing impurities"),
    ("Pre-treatment", processing_actions, "Chemical/biological preparation"),
    ("Distillation", distillation_actions, "Heat-based extraction")
]

for cat_name, cat_actions, cat_desc in categories:
    md_lines.append(f"**{cat_name}** - {cat_desc}")
    md_lines.append("")
    found = [a for a in cat_actions if a in actions]
    if found:
        for a in found:
            md_lines.append(f"- {a}: {actions[a]['count']} occurrences")
    else:
        md_lines.append("- (none found)")
    md_lines.append("")

# Check for uncategorized
all_categorized = set(prep_actions + mechanical_actions + cleaning_actions + processing_actions + distillation_actions)
uncategorized = [a for a in actions.keys() if a not in all_categorized]
if uncategorized:
    md_lines.append("**Uncategorized:**")
    md_lines.append("")
    for a in uncategorized:
        md_lines.append(f"- {a}: {actions[a]['count']} occurrences")
    md_lines.append("")

md_lines.append("---")
md_lines.append("")
md_lines.append("## Process Flow Pattern")
md_lines.append("")
md_lines.append("Typical Brunschwig recipe follows this sequence:")
md_lines.append("")
md_lines.append("```")
md_lines.append("1. GATHER/COLLECT/OBTAIN  →  Acquire material")
md_lines.append("2. WASH/CLEAN             →  Remove dirt/impurities")
md_lines.append("3. CHOP/POUND/CRUSH       →  Mechanical breakdown")
md_lines.append("4. [STEEP/MACERATE]       →  Optional pre-treatment")
md_lines.append("5. DISTILL                →  Heat extraction")
md_lines.append("6. [REDISTILL/REFINE]     →  Optional purification")
md_lines.append("```")
md_lines.append("")

# Write output
output_path = 'context/DATA/BRUNSCHWIG_INSTRUCTION_TAXONOMY.md'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(md_lines))

print(f"Generated: {output_path}")
print(f"\nSummary:")
print(f"  Total unique actions: {len(actions)}")
print(f"  Total instances: {total_instances}")
print(f"\nTop 10 actions:")
for action, data in sorted_actions[:10]:
    print(f"  {action}: {data['count']}")
