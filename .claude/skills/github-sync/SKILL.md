---
name: github-sync
description: Sync Claude Code skills to GitHub repository. Use when the user wants to save, commit, push, or backup skills to git/GitHub, or when they ask to sync their skills.
allowed-tools: Bash, Read, Glob
---

# GitHub Skills Sync

## Overview

This skill helps sync your Claude Code skills directory to a GitHub repository, ensuring your custom skills are version controlled and backed up.

## Instructions

When the user asks to sync skills to GitHub, follow this workflow:

### 1. Check Git Status

First, verify the current git state:

```bash
# Check if we're in a git repo
git status

# Check current branch
git branch --show-current

# Check remote configuration
git remote -v
```

### 2. If Not a Git Repo Yet

If `.git` doesn't exist, initialize:

**Ask the user:**
- "I notice this isn't a git repository yet. Would you like me to:"
  - "1. Initialize a new repo here"
  - "2. Connect to an existing GitHub repo"
  - "3. Cancel"

**If initializing new repo:**
```bash
git init
git add .claude/skills/
git commit -m "Initial commit: Add Claude Code skills"
```

Then ask for GitHub repo URL to add as remote.

**If connecting to existing:**
```bash
git remote add origin <user-provided-url>
git pull origin main --allow-unrelated-histories
```

### 3. Review Changes

Show what will be committed:

```bash
# Show status
git status

# Show diff of changed files
git diff .claude/skills/

# List all skill files
ls -R .claude/skills/
```

**Present to user:**
- List new skills
- List modified skills
- List deleted skills (if any)
- Ask for confirmation to proceed

### 4. Stage Skills

Stage all skills in the `.claude/skills/` directory:

```bash
git add .claude/skills/
```

### 5. Create Commit

**Ask user for commit message, or suggest:**
- "Update skills: [brief description of changes]"
- "Add new skill: [skill-name]"
- "Update [skill-name]: [what changed]"

**Default format if user doesn't specify:**
```
Update Claude Code skills

- Added: [list new skills]
- Modified: [list changed skills]
- Removed: [list deleted skills]

🤖 Synced with Claude Code
```

```bash
git commit -m "User's message or generated message"
```

### 6. Push to GitHub

```bash
# Push to remote (usually 'origin main' or 'origin master')
git push origin main
```

**If push fails:**
- Check if remote is configured: `git remote -v`
- Check if upstream is set: `git branch -vv`
- Try: `git push -u origin main` (sets upstream)
- If rejected, may need: `git pull origin main --rebase` then push again

### 7. Verify Success

```bash
# Confirm last commit
git log -1 --oneline

# Show remote status
git status
```

**Report to user:**
- ✅ "Successfully synced X skills to GitHub"
- 📊 "Commit: [commit hash] - [commit message]"
- 🔗 "Repository: [remote URL]"
- 📁 "Synced skills: [list skill names]"

## Common Scenarios

### Scenario A: First Time Setup

User has never used git before:

1. Check if git is installed: `git --version`
2. If not installed, provide instructions for their OS
3. Check git config: `git config user.name` and `git config user.email`
4. If not configured, guide them to set it up:
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```
5. Initialize repo and guide through GitHub repo creation
6. Add remote and push

### Scenario B: Regular Sync

User already has everything set up:

1. Check status
2. Show changes
3. Stage, commit, push
4. Confirm success

### Scenario C: Merge Conflicts

If pull/push fails due to conflicts:

1. Explain what happened
2. Show conflicting files
3. Guide through resolution:
   ```bash
   # Pull with rebase
   git pull origin main --rebase

   # If conflicts, help resolve them
   git status
   # Show conflicted files

   # After resolution
   git add .
   git rebase --continue
   git push origin main
   ```

### Scenario D: Selective Sync

User wants to sync only specific skills:

```bash
# Stage specific skill
git add .claude/skills/skill-name/

# Or multiple skills
git add .claude/skills/skill1/ .claude/skills/skill2/
```

## Error Handling

### Common Errors:

**"fatal: not a git repository"**
- Offer to initialize git repo

**"fatal: 'origin' does not appear to be a git repository"**
- Remote not configured, ask for GitHub URL

**"error: failed to push some refs"**
- Remote has changes, need to pull first
- Run: `git pull origin main --rebase`

**"Author identity unknown"**
- Git config not set
- Guide through setting user.name and user.email

**"Permission denied (publickey)"**
- SSH key not configured
- Suggest using HTTPS instead, or help set up SSH keys

**"rejected: non-fast-forward"**
- Remote has commits not in local
- Need to pull and merge/rebase first

## Best Practices

1. **Always review changes** before committing
2. **Write clear commit messages** describing what changed
3. **Pull before pushing** if working across multiple machines
4. **Use meaningful branch names** if working on experimental skills
5. **Don't commit sensitive data** (API keys, credentials, etc.)

## GitHub Repository Setup

If user needs to create a GitHub repo:

1. **Guide them to:**
   - Go to github.com
   - Click "New repository"
   - Name it (e.g., "claude-code-skills")
   - Choose public or private
   - Don't initialize with README (we already have files)
   - Copy the repository URL

2. **Then add remote:**
   ```bash
   git remote add origin https://github.com/username/repo-name.git
   git push -u origin main
   ```

## Advanced Options

### Create .gitignore

If needed, create `.gitignore` to exclude files:

```
# .gitignore for Claude Code skills
*.log
.DS_Store
Thumbs.db
temp/
*.tmp
```

### Add README

Suggest creating a README for the skills repo:

```markdown
# My Claude Code Skills

Custom skills for Claude Code CLI.

## Skills

- **skill-name**: Description of what it does

## Installation

Copy to your Claude Code skills directory:
- Personal: `~/.claude/skills/`
- Project: `.claude/skills/`

## Usage

These skills are automatically detected by Claude Code.
```

### Branching Strategy

If user wants to work on experimental skills:

```bash
# Create feature branch
git checkout -b feature/new-skill-name

# Work on skill...

# Commit changes
git add .claude/skills/new-skill-name/
git commit -m "Add new skill: skill-name"

# Push branch
git push -u origin feature/new-skill-name

# When ready, merge to main
git checkout main
git merge feature/new-skill-name
git push origin main
```

## Safety Checks

Before pushing, verify:

- [ ] No sensitive data in skill files (API keys, passwords, etc.)
- [ ] Skill files are in correct format (SKILL.md with frontmatter)
- [ ] All referenced files are included
- [ ] Commit message is clear and descriptive
- [ ] Remote URL is correct
- [ ] Branch is correct (main/master)

## Output Format

After successful sync, provide:

```
✅ Skills synced to GitHub successfully!

📊 Summary:
   - Repository: https://github.com/user/repo
   - Branch: main
   - Commit: abc1234 - "Your commit message"

📁 Synced Skills:
   - axon-review
   - github-sync
   - [other skills...]

🔗 View on GitHub: [link to commit]
```

## Troubleshooting

If anything goes wrong:

1. Show the error message
2. Explain what it means in simple terms
3. Provide step-by-step solution
4. Offer to run commands to fix it
5. Verify fix worked

## Quick Commands Reference

```bash
# Status
git status

# Add skills
git add .claude/skills/

# Commit
git commit -m "Your message"

# Push
git push origin main

# Pull
git pull origin main

# View history
git log --oneline -5

# View remote
git remote -v

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Discard local changes
git checkout -- .claude/skills/
```
