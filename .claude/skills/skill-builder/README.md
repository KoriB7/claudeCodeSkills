# Skill Builder

A meta-skill for creating well-structured, consistent Claude Code skills.

## Purpose

This skill ensures all skills in your library follow the same:
- Metadata format (YAML frontmatter)
- Section organization
- File structure conventions
- Documentation standards

## Usage

When you want to create a new skill, just tell Claude:

```
Create a new skill for [purpose]
```

Or invoke directly:

```
/skill-builder
```

Claude will guide you through:
1. Naming and categorizing the skill
2. Determining the appropriate complexity tier
3. Generating the folder structure
4. Populating templates with your content
5. Validating the final result

## What It Standardizes

### Metadata
All skills get consistent YAML frontmatter:
```yaml
---
name: skill-name
version: 1.0.0
description: Action-verb description...
category: tool|guide|integration
allowed-tools: Read, Write, Bash
---
```

### Section Order
1. Quick Start
2. How It Works
3. Usage
4. Output Format
5. Options/Configuration
6. Troubleshooting
7. References

### File Structure
Three tiers based on complexity:
- **Tier 1**: Just skill.md (simple utilities)
- **Tier 2**: skill.md + README + scripts/ (tools with automation)
- **Tier 3**: Full structure with data/, templates/, examples/

## Templates Included

- Tool skill template (converts/calculates)
- Guide skill template (reviews/instructs)
- Integration skill template (syncs/connects)
- README template
- Python script header template

## Version History

- **1.0.0**: Initial release
