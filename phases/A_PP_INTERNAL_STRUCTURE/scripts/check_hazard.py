import yaml
with open('context/STRUCTURAL_CONTRACTS/currierB.bcsc.yaml') as f:
    bcsc = yaml.safe_load(f)

print("All instruction class IDs:")
ids = [cls['id'] for cls in bcsc.get('instruction_classes', [])]
print(ids)

print("\nLooking for hazard in class names:")
for cls in bcsc.get('instruction_classes', []):
    name = cls.get('name', '')
    if 'hazard' in name.lower() or 'haz' in name.lower():
        print('Class', cls['id'], ':', name)
        print('  Members:', cls.get('members', []))
