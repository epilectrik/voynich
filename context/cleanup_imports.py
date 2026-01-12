#!/usr/bin/env python
"""Remove incorrectly imported constraints from registry files"""
import re
from pathlib import Path

CLAIMS_DIR = Path(__file__).parent / 'CLAIMS'

def cleanup_registry(registry_path):
    """Remove the 'Imported Constraints' section from a registry file"""
    if not registry_path.exists():
        return False

    content = registry_path.read_text(encoding='utf-8')

    # Find and remove the "Imported Constraints" section
    # Pattern: ---\n\n## Imported Constraints\n\n ... until next --- or ## Navigation
    pattern = r'\n---\n\n## Imported Constraints\n\n.*?(?=\n---\n\n## Navigation|\n## Navigation|$)'

    new_content, count = re.subn(pattern, '', content, flags=re.DOTALL)

    if count > 0:
        registry_path.write_text(new_content, encoding='utf-8')
        print(f"Cleaned {registry_path.name}")
        return True

    return False


def main():
    files_to_clean = [
        'organization.md',
        'operations.md',
        'currier_a.md',
        'azc_system.md',
        'morphology.md',
    ]

    for filename in files_to_clean:
        cleanup_registry(CLAIMS_DIR / filename)

    print("Cleanup complete!")


if __name__ == '__main__':
    main()
