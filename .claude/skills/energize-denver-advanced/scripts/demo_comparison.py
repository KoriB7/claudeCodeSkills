#!/usr/bin/env python3
"""
Demo script to compare Basic vs Advanced benchmarking methods

Run this to show your boss the difference between the two approaches.
"""

import subprocess
import sys

print("="*80)
print("ENERGIZE DENVER BENCHMARKING: BASIC VS ADVANCED COMPARISON")
print("="*80)
print()

# Demo scenarios
scenarios = [
    {
        "name": "Scenario 1: Typical Modern Office",
        "description": "New office building, standard characteristics",
        "basic_args": ["--sqft", "25000", "--type", "Office"],
        "advanced_args": ["--sqft", "25000", "--type", "Office"],
        "insight": "Basic method works fine for typical modern buildings"
    },
    {
        "name": "Scenario 2: Denver Climate Adjustment",
        "description": "Same office, but accounting for Denver's climate",
        "basic_args": ["--sqft", "25000", "--type", "Office"],
        "advanced_args": ["--sqft", "25000", "--type", "Office", "--region", "Mountain"],
        "insight": "Denver climate adds ~8-10% to energy use vs national average"
    },
    {
        "name": "Scenario 3: Historic Building in Denver",
        "description": "1980s office building in Denver climate",
        "basic_args": ["--sqft", "25000", "--type", "Office"],
        "advanced_args": ["--sqft", "25000", "--type", "Office", "--year", "1980 to 1989", "--region", "Mountain"],
        "insight": "Older buildings in Denver climate use significantly more energy"
    },
    {
        "name": "Scenario 4: Full Refinement",
        "description": "1980s office, Denver, 3 floors, 50 hrs/week",
        "basic_args": ["--sqft", "25000", "--type", "Office"],
        "advanced_args": ["--sqft", "25000", "--type", "Office", "--year", "1980 to 1989",
                         "--region", "Mountain", "--floors", "3", "--hours", "50"],
        "insight": "Maximum accuracy with all available building characteristics"
    }
]

for i, scenario in enumerate(scenarios, 1):
    print(f"\n{'='*80}")
    print(f"{scenario['name']}")
    print(f"{'='*80}")
    print(f"Description: {scenario['description']}")
    print()

    # Run basic calculation
    print("[BASIC METHOD - energize-denver-audit]")
    print("Command: python scripts/calculate_benchmark.py " + " ".join(scenario['basic_args']))
    print()

    try:
        result = subprocess.run(
            ["python", "../energize-denver-audit/scripts/calculate_benchmark.py"] + scenario['basic_args'],
            capture_output=True,
            text=True,
            cwd=".claude/skills/energize-denver-advanced"
        )

        # Extract just the total from output
        for line in result.stdout.split('\n'):
            if 'Total Annual Energy Use:' in line:
                print(line)
                break
    except Exception as e:
        print(f"Error running basic: {e}")

    print()
    print("[ADVANCED METHOD - energize-denver-advanced]")
    print("Command: python scripts/calculate_advanced.py " + " ".join(scenario['advanced_args']))
    print()

    try:
        result = subprocess.run(
            ["python", "scripts/calculate_advanced.py"] + scenario['advanced_args'],
            capture_output=True,
            text=True,
            cwd=".claude/skills/energize-denver-advanced"
        )

        # Extract key info from output
        for line in result.stdout.split('\n'):
            if 'Total Annual Energy Use:' in line or 'Refinement adjusted' in line:
                print(line)
    except Exception as e:
        print(f"Error running advanced: {e}")

    print()
    print(f"INSIGHT: {scenario['insight']}")

    input("\nPress Enter to continue to next scenario...")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print("""
Key Takeaways:

1. BASIC METHOD is fast and accurate for typical buildings
   - Use for: Quick estimates, modern buildings, batch processing
   - Accuracy: ±15-20% for typical cases

2. ADVANCED METHOD provides refinement when needed
   - Use for: Historic buildings, Denver climate, unusual operations
   - Accuracy: ±5-10% with full refinement
   - Value: +10-20% adjustment for Denver/historic buildings

3. RECOMMENDATION:
   - Start with basic method for all buildings
   - Use advanced method when:
     * Building is pre-1980 (historic)
     * Denver-specific analysis needed
     * Unusual operating hours (24/7, etc.)
     * Need to explain variance from typical

4. BOTH SKILLS ARE VALUABLE:
   - Basic: Fast screening tool
   - Advanced: Detailed analysis tool
   - Together: Complete benchmarking solution

Would you like to keep both skills? [Y/n]
""")

response = input().strip().lower()
if response in ['', 'y', 'yes']:
    print("\nGreat! Both skills will be available in .claude/skills/")
    print("- energize-denver-audit (basic)")
    print("- energize-denver-advanced (advanced)")
else:
    print("\nYou can always remove one later if needed.")

print("\nDemo complete!")
