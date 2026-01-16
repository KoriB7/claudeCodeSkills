---
name: github-sync
version: 1.0.0
description: Syncs Claude Code skills to a GitHub repository. Use when the user wants to save, commit, push, or backup skills to git/GitHub, or when they ask to sync their skills.
category: integration
allowed-tools: Bash, Read, Glob
---

# GitHub Skills Sync

Syncs your Claude Code skills directory to a GitHub repository for version control and backup.

## Quick Start

When user asks to sync skills:
1. Check git status
2. Review changes
3. Stage skill files
4. Create commit with message
5. Push to GitHub
6. Verify success

## How It Works

1. **Check Git Status** - Verify repo state and branch
2. **Review Changes** - Show new, modified, deleted skills
3. **Stage Skills** - Add `.claude/skills/` to staging
4. **Create Commit** - Use descriptive message
5. **Push to Remote** - Send to GitHub
6. **Verify Success** - Confirm and report

## Usage

### Standard Sync Workflow

```bash
# 1. Check status
git status
git branch --show-current
git remote -v

# 2. Review changes
git diff .claude/skills/

# 3. Stage skills
git add .claude/skills/

# 4. Commit
git commit -m "Update Claude Code skills"

# 5. Push
git push origin main

# 6. Verify
git log -1 --oneline
```

### First Time Setup

If not a git repo yet, ask user preference:
1. Initialize new repo
2. Connect to existing GitHub repo
3. Cancel

**Initialize new:**
```bash
git init
git add .claude/skills/
git commit -m "Initial commit: Add Claude Code skills"
```

**Connect to existing:**
```bash
git remote add origin <user-provided-url>
git pull origin main --allow-unrelated-histories
```

### Selective Sync

For specific skills only:
```bash
git add .claude/skills/skill-name/
git add .claude/skills/skill1/ .claude/skills/skill2/
```

## Output Format

**Success:**
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

**Commit Message Format:**
```
Update Claude Code skills

- Added: [list new skills]
- Modified: [list changed skills]
- Removed: [list deleted skills]

🤖 Synced with Claude Code
```

## Options

### Git Configuration (if needed)
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Branch Operations
```bash
# Create feature branch
git checkout -b feature/new-skill-name

# Merge to main when ready
git checkout main
git merge feature/new-skill-name
git push origin main
```

## Troubleshooting

**"fatal: not a git repository"**
- Solution: Offer to initialize git repo

**"fatal: 'origin' does not appear to be a git repository"**
- Solution: Remote not configured, ask for GitHub URL

**"error: failed to push some refs"**
- Solution: Remote has changes, run `git pull origin main --rebase`

**"Author identity unknown"**
- Solution: Set git config user.name and user.email

**"Permission denied (publickey)"**
- Solution: Use HTTPS instead of SSH, or set up SSH keys

**"rejected: non-fast-forward"**
- Solution: Pull and merge/rebase first

## Best Practices

1. **Always review changes** before committing
2. **Write clear commit messages** describing what changed
3. **Pull before pushing** if working across multiple machines
4. **Use meaningful branch names** for experimental skills
5. **Don't commit sensitive data** (API keys, credentials)

## Safety Checks

Before pushing, verify:
- [ ] No sensitive data in skill files
- [ ] Skill files are in correct format (skill.md with frontmatter)
- [ ] All referenced files are included
- [ ] Commit message is clear
- [ ] Remote URL is correct
- [ ] Branch is correct (main/master)

## Common Scenarios

### Scenario A: First Time Setup
1. Check if git installed: `git --version`
2. Check git config
3. Initialize repo
4. Guide through GitHub repo creation
5. Add remote and push

### Scenario B: Regular Sync
1. Check status
2. Show changes
3. Stage, commit, push
4. Confirm success

### Scenario C: Merge Conflicts
1. Explain what happened
2. Show conflicting files
3. Guide through resolution
4. Complete rebase and push

## Quick Commands Reference

```bash
git status                    # Status
git add .claude/skills/       # Add skills
git commit -m "message"       # Commit
git push origin main          # Push
git pull origin main          # Pull
git log --oneline -5          # View history
git remote -v                 # View remote
git reset --soft HEAD~1       # Undo last commit (keep changes)
git checkout -- .claude/skills/  # Discard local changes
```

## References

- GitHub documentation: https://docs.github.com/
- Git reference: https://git-scm.com/docs
