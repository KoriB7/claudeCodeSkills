---
name: skill-builder
version: 1.0.0
description: Guides the creation of new Claude Code skills with consistent formatting, structure, and organization. Use when creating or refactoring skills to ensure uniformity across your skill library.
category: guide
allowed-tools: Read, Write, Glob, Bash
---

# Skill Builder

A meta-skill for creating well-structured, consistent Claude Code skills.

## Quick Start

When the user wants to create a new skill:

1. **Gather Requirements** - Ask about:
   - Skill name (kebab-case)
   - Purpose/description (action-verb first)
   - Category: `tool` (converts/calculates), `guide` (reviews/instructs), or `integration` (syncs/connects)
   - Complexity tier (determines folder structure)

2. **Generate Structure** - Create appropriate files based on tier

3. **Populate Template** - Fill in the skill.md with standardized sections

---

## Skill Categories

| Category | Purpose | Examples |
|----------|---------|----------|
| **tool** | Converts, calculates, transforms data | xlsx-to-csv, energize-denver-audit |
| **guide** | Reviews code, provides instructions | axon-review, github-sync |
| **integration** | Connects external services | github-sync |

---

## Complexity Tiers

### Tier 1: Simple (Single-file utility)
```
skill-name/
├── skill.md          # Main definition with embedded logic
└── README.md         # User documentation (optional)
```
**Use when**: Skill is purely instructional or uses only Claude's built-in capabilities.

### Tier 2: Standard (Tool with implementation)
```
skill-name/
├── skill.md          # Main definition
├── README.md         # User documentation
└── scripts/
    └── main.py       # Implementation script
```
**Use when**: Skill requires a script for automation.

### Tier 3: Complex (Full-featured tool)
```
skill-name/
├── skill.md          # Main definition
├── README.md         # User documentation
├── scripts/
│   └── main.py       # Implementation script
├── data/
│   └── *.csv         # Reference data files
├── templates/
│   └── output.txt    # Output templates
└── examples/
    └── example.md    # Usage examples
```
**Use when**: Skill needs reference data, templates, or extensive examples.

---

## Standard Metadata Format

All skills MUST include this YAML frontmatter:

```yaml
---
name: skill-name-in-kebab-case
version: 1.0.0
description: [Action verb] [what it does]. [When to use it].
category: tool|guide|integration
allowed-tools: Tool1, Tool2, Tool3
---
```

### Field Guidelines

| Field | Required | Format | Example |
|-------|----------|--------|---------|
| `name` | Yes | kebab-case | `energize-denver-audit` |
| `version` | Yes | semver | `1.0.0` |
| `description` | Yes | Action verb first, <250 chars | `Converts Excel files to CSV format...` |
| `category` | Yes | One of: tool, guide, integration | `tool` |
| `allowed-tools` | Yes | Comma-separated tool names | `Read, Write, Bash` |

### Description Pattern
Start with action verb matching the category:
- **tool**: "Converts...", "Calculates...", "Transforms...", "Generates..."
- **guide**: "Reviews...", "Guides...", "Instructs...", "Validates..."
- **integration**: "Syncs...", "Connects...", "Integrates...", "Pushes..."

---

## Standard Section Order

All skill.md files should follow this section order:

```markdown
# Skill Name

[One-paragraph overview]

## Quick Start
[Minimal steps to use the skill]

## How It Works
[Process explanation, numbered steps]

## Usage
[Detailed usage instructions with examples]

## Output Format
[Expected output structure/format]

## Options / Configuration
[Available parameters, flags, customization]

## Troubleshooting
[Common issues and solutions]

## References
[Data sources, related skills, documentation links]
```

**Notes:**
- Omit sections that don't apply (e.g., no "References" for simple utilities)
- Add category-specific sections as needed (e.g., "Best Practices" for guides)

---

## Code Example Standards

Use consistent formatting for examples:

### Good/Bad Pattern
```markdown
**✅ GOOD**: Brief explanation of why this is correct
\`\`\`language
code example here
\`\`\`

**❌ BAD**: Brief explanation of what's wrong
\`\`\`language
anti-pattern here
\`\`\`
```

### Command Examples
```markdown
\`\`\`bash
# Description of what this command does
python scripts/main.py --flag value
\`\`\`
```

### Output Examples
```markdown
**Example Output:**
\`\`\`
| Column 1 | Column 2 |
|----------|----------|
| Value    | Value    |
\`\`\`
```

---

## Workflow: Creating a New Skill

### Step 1: Gather Information
Ask the user:
1. "What should this skill be called?" (suggest kebab-case)
2. "What does it do?" (help them form action-verb description)
3. "Is this a tool (converts/calculates), guide (reviews/instructs), or integration (connects)?"
4. "Does it need scripts, data files, or templates?" (determines tier)

### Step 2: Create Directory Structure
Based on tier, create the appropriate folders:

```bash
# Tier 1
mkdir -p .claude/skills/{skill-name}

# Tier 2
mkdir -p .claude/skills/{skill-name}/scripts

# Tier 3
mkdir -p .claude/skills/{skill-name}/{scripts,data,templates,examples}
```

### Step 3: Generate skill.md
Use the template below, customized for the category.

### Step 4: Generate README.md (Tier 2+)
Create user-facing documentation.

### Step 5: Generate Scripts (if needed)
Create implementation files with proper headers and documentation.

### Step 6: Validate
Check that:
- [ ] Metadata is complete and valid
- [ ] All required sections are present
- [ ] Examples are provided
- [ ] Troubleshooting section exists
- [ ] File naming is consistent (lowercase skill.md)

---

## Templates

### Template: Tool Skill (skill.md)

```markdown
---
name: {skill-name}
version: 1.0.0
description: {Action verb} {what}. {When to use}.
category: tool
allowed-tools: Read, Write, Bash
---

# {Skill Name}

{One paragraph describing what this tool does and its primary use case.}

## Quick Start

1. Provide {required input}
2. Run the skill: `/{skill-name}`
3. Review the output

## How It Works

1. **Step 1**: {Description}
2. **Step 2**: {Description}
3. **Step 3**: {Description}

## Usage

### Basic Usage
{Minimal example}

### With Options
{Example with parameters}

## Output Format

{Description of output structure}

**Example:**
\`\`\`
{sample output}
\`\`\`

## Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--option1` | string | none | {description} |

## Troubleshooting

### Issue: {Common problem}
**Solution**: {How to fix}

### Issue: {Another problem}
**Solution**: {How to fix}

## References

- {Link or reference 1}
- {Link or reference 2}
```

### Template: Guide Skill (skill.md)

```markdown
---
name: {skill-name}
version: 1.0.0
description: {Reviews/Guides/Validates} {what}. {When to use}.
category: guide
allowed-tools: Read, Grep, Glob
---

# {Skill Name}

{One paragraph describing what this guide covers and when to use it.}

## Quick Start

When reviewing/guiding {subject}:
1. {First thing to check/do}
2. {Second thing}
3. {Third thing}

## Checklist

### {Category 1}
- [ ] {Check item 1}
- [ ] {Check item 2}
- [ ] {Check item 3}

### {Category 2}
- [ ] {Check item 1}
- [ ] {Check item 2}

## Best Practices

### {Practice Area 1}

**✅ GOOD**: {Why this is correct}
\`\`\`
{good example}
\`\`\`

**❌ BAD**: {Why this is wrong}
\`\`\`
{bad example}
\`\`\`

### {Practice Area 2}
{Continue pattern...}

## Common Pitfalls

1. **{Pitfall 1}**: {Description and how to avoid}
2. **{Pitfall 2}**: {Description and how to avoid}

## Output Format

When providing feedback, use this format:

\`\`\`
## {Subject} Review

### Summary
{Overall assessment}

### Issues Found
- ✅ {What's good}
- ⚠️ {Warning/suggestion}
- ❌ {Problem that needs fixing}

### Recommendations
{Actionable next steps}
\`\`\`

## References

- {Related guide or documentation}
```

### Template: Integration Skill (skill.md)

```markdown
---
name: {skill-name}
version: 1.0.0
description: {Syncs/Connects/Integrates} {what with what}. {When to use}.
category: integration
allowed-tools: Bash, Read, Write
---

# {Skill Name}

{One paragraph describing what this integration does and why it's useful.}

## Quick Start

1. Ensure {prerequisites}
2. Run `/{skill-name}`
3. {Expected outcome}

## Prerequisites

- {Requirement 1} (e.g., API key configured)
- {Requirement 2} (e.g., git repository initialized)

## How It Works

1. **{Phase 1}**: {Description}
2. **{Phase 2}**: {Description}
3. **{Phase 3}**: {Description}

## Usage

### Standard Sync
\`\`\`bash
/{skill-name}
\`\`\`

### With Options
\`\`\`bash
/{skill-name} --option value
\`\`\`

## Configuration

| Setting | Required | Description |
|---------|----------|-------------|
| `{setting1}` | Yes | {what it does} |
| `{setting2}` | No | {what it does} |

## Troubleshooting

### Issue: {Authentication/connection problem}
**Solution**: {Steps to resolve}

### Issue: {Sync conflict}
**Solution**: {Steps to resolve}

## References

- {External service documentation}
- {Related skills}
```

### Template: README.md

```markdown
# {Skill Name}

{Brief description - can be same as skill.md description}

## Installation

This skill is part of the Claude Code skills library. No additional installation required.

## Usage

\`\`\`
/{skill-name}
\`\`\`

{Or describe how Claude invokes this skill}

## Examples

### Example 1: {Use case}
{Input and expected output}

### Example 2: {Another use case}
{Input and expected output}

## Files

| File | Purpose |
|------|---------|
| `skill.md` | Main skill definition |
| `scripts/main.py` | {What the script does} |
| `data/*.csv` | {What data is included} |

## Contributing

To modify this skill, edit the files in `.claude/skills/{skill-name}/`.

## Version History

- **1.0.0**: Initial release
```

### Template: Python Script Header

```python
#!/usr/bin/env python3
"""
{Skill Name} - {Brief description}

This script is part of the {skill-name} Claude Code skill.
Location: .claude/skills/{skill-name}/scripts/main.py

Usage:
    python main.py [options]

Options:
    --option1    {description}
    --option2    {description}
"""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="{Description}")
    parser.add_argument("--option1", help="{help text}")
    args = parser.parse_args()

    # Implementation here
    pass


if __name__ == "__main__":
    main()
```

---

## Validation Checklist

Before finalizing a new skill, verify:

### Metadata
- [ ] `name` is kebab-case and matches folder name
- [ ] `version` follows semver (start with 1.0.0)
- [ ] `description` starts with action verb and is <250 characters
- [ ] `category` is one of: tool, guide, integration
- [ ] `allowed-tools` lists all tools the skill needs

### Structure
- [ ] Main file is named `skill.md` (lowercase)
- [ ] Folder structure matches complexity tier
- [ ] README.md exists for Tier 2+ skills
- [ ] Scripts have proper headers and documentation

### Content
- [ ] Quick Start section exists and is actionable
- [ ] How It Works explains the process
- [ ] Examples are concrete and realistic
- [ ] Output Format shows expected results
- [ ] Troubleshooting covers common issues

### Style
- [ ] Code examples use ✅/❌ pattern where appropriate
- [ ] Commands are in proper code blocks
- [ ] Tables are used for options/configuration
- [ ] Consistent heading hierarchy (# > ## > ###)

---

## Example: Creating a New Skill

**User**: "I want to create a skill that converts JSON to YAML"

**Response**:

1. **Gather info**:
   - Name: `json-to-yaml`
   - Description: "Converts JSON files to YAML format. Use when you need to transform configuration files or data between formats."
   - Category: `tool`
   - Tier: 2 (needs a conversion script)

2. **Create structure**:
```bash
mkdir -p .claude/skills/json-to-yaml/scripts
```

3. **Generate files**:
   - `skill.md` with tool template
   - `README.md` with usage docs
   - `scripts/convert.py` with conversion logic

4. **Validate** using checklist above

---

## Related Skills

- None currently (this is a meta-skill)

## Version History

- **1.0.0**: Initial release with templates for tool, guide, and integration skills
