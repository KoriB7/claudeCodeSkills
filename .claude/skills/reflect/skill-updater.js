#!/usr/bin/env node
/**
 * skill-updater.js
 *
 * Safely updates skill files with learnings from reflect-engine.js
 * Handles backups, YAML frontmatter, confidence-based updates, validation, and rollback.
 *
 * Ported from Python claude-reflect-system to Node.js ESM for skill-builder standards.
 */

import { readFileSync, writeFileSync, copyFileSync, existsSync, mkdirSync, readdirSync, statSync, unlinkSync } from 'fs';
import { join, dirname } from 'path';
import { homedir } from 'os';

/**
 * Main update function - safely applies learning to a skill
 * @param {Object} change - Change object with skill_name and proposed_updates
 * @returns {boolean} True if successful, false otherwise
 */
export async function updateSkill(change) {
  const skillName = change.skill_name;
  const skillPath = join(homedir(), '.claude', 'skills', skillName, 'SKILL.md');

  if (!existsSync(skillPath)) {
    console.log(`✗ Skill not found: ${skillPath}`);
    return false;
  }

  // 1. Create backup
  const backupPath = createBackup(skillPath);
  if (!backupPath) {
    console.log(`✗ Failed to create backup for ${skillName}`);
    return false;
  }

  try {
    // 2. Parse existing skill
    const content = readFileSync(skillPath, 'utf-8');
    const { frontmatter, body } = parseSkillFile(content);

    // 3. Apply updates based on confidence
    let updatedBody = body;
    const proposedUpdates = change.proposed_updates || {};

    for (const signal of (proposedUpdates.high_confidence || [])) {
      updatedBody = applyHighConfidenceUpdate(updatedBody, signal);
    }

    for (const signal of (proposedUpdates.medium_confidence || [])) {
      updatedBody = applyMediumConfidenceUpdate(updatedBody, signal);
    }

    for (const signal of (proposedUpdates.low_confidence || [])) {
      updatedBody = applyLowConfidenceUpdate(updatedBody, signal);
    }

    // 4. Reconstruct file
    const updatedContent = reconstructSkillFile(frontmatter, updatedBody);

    // 5. Validate YAML
    validateSkillYaml(updatedContent);

    // 6. Write atomically
    writeFileSync(skillPath, updatedContent, 'utf-8');

    console.log(`✓ Updated ${skillName}`);
    console.log(`  Backup saved: ${backupPath}`);
    return true;

  } catch (error) {
    // Rollback on error
    copyFileSync(backupPath, skillPath);
    console.log(`✗ Error updating ${skillName}: ${error.message}`);
    console.log(`  Rolled back to backup: ${backupPath}`);
    return false;
  }
}

/**
 * Create timestamped backup of skill file
 * @param {string} skillPath - Path to SKILL.md
 * @returns {string|null} Backup path or null on failure
 */
function createBackup(skillPath) {
  try {
    // Format: SKILL_20260112093045.md
    const timestamp = new Date()
      .toISOString()
      .replace(/[-:T]/g, '')
      .slice(0, 14); // YYYYMMDDHHmmss

    const backupDir = join(dirname(skillPath), '.backups');

    if (!existsSync(backupDir)) {
      mkdirSync(backupDir, { recursive: true });
    }

    const backupPath = join(backupDir, `SKILL_${timestamp}.md`);
    copyFileSync(skillPath, backupPath);

    // Cleanup old backups (>30 days)
    cleanupOldBackups(backupDir, 30);

    return backupPath;
  } catch (error) {
    console.error(`Error creating backup: ${error.message}`);
    return null;
  }
}

/**
 * Remove backups older than specified days
 * @param {string} backupDir - Backup directory path
 * @param {number} days - Days threshold for deletion
 */
function cleanupOldBackups(backupDir, days = 30) {
  try {
    const cutoffTime = Date.now() - (days * 24 * 60 * 60 * 1000);
    const files = readdirSync(backupDir);

    for (const file of files) {
      if (file.startsWith('SKILL_') && file.endsWith('.md')) {
        const filePath = join(backupDir, file);
        const stats = statSync(filePath);

        if (stats.mtimeMs < cutoffTime) {
          unlinkSync(filePath);
        }
      }
    }
  } catch (error) {
    // Non-critical, don't fail on cleanup errors
  }
}

/**
 * Parse SKILL.md into frontmatter and body
 * @param {string} content - Full file content
 * @returns {Object} { frontmatter, body }
 */
function parseSkillFile(content) {
  const parts = content.split('---');

  if (parts.length < 3) {
    throw new Error('Invalid SKILL.md format: missing YAML frontmatter (needs --- delimiters)');
  }

  // Simple YAML parsing for our use case (name and description fields)
  const frontmatter = parseSimpleYaml(parts[1]);
  const body = parts.slice(2).join('---').trim();

  return { frontmatter, body };
}

/**
 * Simple YAML parser for frontmatter (name and description only)
 * @param {string} yamlText - YAML content
 * @returns {Object} Parsed object
 */
function parseSimpleYaml(yamlText) {
  const lines = yamlText.trim().split('\n');
  const result = {};

  for (const line of lines) {
    const match = line.match(/^([a-z_]+):\s*(.+)$/i);
    if (match) {
      const key = match[1].trim();
      let value = match[2].trim();

      // Remove quotes if present
      if ((value.startsWith('"') && value.endsWith('"')) ||
          (value.startsWith("'") && value.endsWith("'"))) {
        value = value.slice(1, -1);
      }

      result[key] = value;
    }
  }

  return result;
}

/**
 * Apply HIGH confidence update (Critical Corrections)
 * @param {string} body - Markdown body
 * @param {Object} signal - Signal object
 * @returns {string} Updated body
 */
function applyHighConfidenceUpdate(body, signal) {
  const description = signal.description || 'Correction';
  const oldApproach = signal.old_approach || signal.match?.[0] || 'Previous approach';
  const newApproach = signal.new_approach || signal.match?.[1] || 'New approach';

  const correction =
    `\n**${description}**\n\n` +
    `- ✗ Don't: ${oldApproach}\n` +
    `- ✓ Do: ${newApproach}\n` +
    `  *(Learned: ${new Date().toISOString().split('T')[0]})*\n`;

  if (body.includes('## Critical Corrections')) {
    return insertIntoSection(body, '## Critical Corrections', correction);
  } else {
    // Insert at beginning
    return `## Critical Corrections\n${correction}\n---\n\n${body}`;
  }
}

/**
 * Apply MEDIUM confidence update (Best Practices)
 * @param {string} body - Markdown body
 * @param {Object} signal - Signal object
 * @returns {string} Updated body
 */
function applyMediumConfidenceUpdate(body, signal) {
  const description = signal.description || signal.pattern || 'Approved approach';
  const practice = signal.previous_approach ?
    `${description}: ${signal.previous_approach.substring(0, 100)}...` :
    description;

  const bestPractice = `- ${practice}\n`;

  if (body.includes('## Best Practices')) {
    return insertIntoSection(body, '## Best Practices', bestPractice);
  } else {
    // Append near end (before "Saving Next Steps" if exists)
    if (body.includes('## Saving Next Steps')) {
      const parts = body.split('## Saving Next Steps');
      return `${parts[0]}\n## Best Practices\n\n${bestPractice}\n## Saving Next Steps${parts[1]}`;
    } else {
      return `${body}\n\n## Best Practices\n\n${bestPractice}`;
    }
  }
}

/**
 * Apply LOW confidence update (Considerations)
 * @param {string} body - Markdown body
 * @param {Object} signal - Signal object
 * @returns {string} Updated body
 */
function applyLowConfidenceUpdate(body, signal) {
  const suggestion = signal.suggestion || signal.description || 'Consideration';
  const consideration = `- Consider: ${suggestion}\n`;

  if (body.includes('## Considerations')) {
    return insertIntoSection(body, '## Considerations', consideration);
  } else {
    // Append near end (before "Best Practices" if exists)
    if (body.includes('## Best Practices')) {
      const parts = body.split('## Best Practices');
      return `${parts[0]}\n## Considerations\n\n${consideration}\n## Best Practices${parts[1]}`;
    } else if (body.includes('## Saving Next Steps')) {
      const parts = body.split('## Saving Next Steps');
      return `${parts[0]}\n## Considerations\n\n${consideration}\n## Saving Next Steps${parts[1]}`;
    } else {
      return `${body}\n\n## Considerations\n\n${consideration}`;
    }
  }
}

/**
 * Insert content into existing section
 * @param {string} body - Markdown body
 * @param {string} sectionHeader - Section header (e.g., "## Best Practices")
 * @param {string} content - Content to insert
 * @returns {string} Updated body
 */
function insertIntoSection(body, sectionHeader, content) {
  const parts = body.split(sectionHeader);
  if (parts.length < 2) return body; // Section not found

  const before = parts[0];
  const afterHeader = parts[1];

  // Find next section (starts with ##)
  const nextSectionMatch = afterHeader.match(/\n## /);

  if (nextSectionMatch) {
    const nextSectionIndex = afterHeader.indexOf(nextSectionMatch[0]);
    const sectionContent = afterHeader.substring(0, nextSectionIndex);
    const rest = afterHeader.substring(nextSectionIndex);
    return `${before}${sectionHeader}${sectionContent}\n${content}${rest}`;
  } else {
    // No next section, append to end of current section
    return `${before}${sectionHeader}${afterHeader}\n${content}`;
  }
}

/**
 * Reconstruct SKILL.md with YAML frontmatter and body
 * @param {Object} frontmatter - Frontmatter object
 * @param {string} body - Markdown body
 * @returns {string} Complete file content
 */
function reconstructSkillFile(frontmatter, body) {
  // Simple YAML serialization
  const yamlLines = [];
  for (const [key, value] of Object.entries(frontmatter)) {
    // Quote values with special characters
    const needsQuotes = /[:#\[\]{}]/.test(value);
    const formattedValue = needsQuotes ? `"${value.replace(/"/g, '\\"')}"` : value;
    yamlLines.push(`${key}: ${formattedValue}`);
  }

  const yamlStr = yamlLines.join('\n');
  return `---\n${yamlStr}\n---\n\n${body}`;
}

/**
 * Validate SKILL.md YAML frontmatter
 * @param {string} content - Full file content
 * @throws {Error} If validation fails
 */
function validateSkillYaml(content) {
  try {
    const parts = content.split('---');

    if (parts.length < 3) {
      throw new Error('Missing YAML frontmatter delimiters');
    }

    const frontmatter = parseSimpleYaml(parts[1]);

    if (!frontmatter.name) {
      throw new Error("Missing required 'name' field in frontmatter");
    }

    if (!frontmatter.description) {
      throw new Error("Missing required 'description' field in frontmatter");
    }

  } catch (error) {
    throw new Error(`Invalid YAML after update: ${error.message}`);
  }
}

/**
 * Generate diff preview
 * @param {string} originalPath - Path to original SKILL.md
 * @param {Object} change - Change object
 * @returns {string} Diff preview text
 */
export function generateDiffPreview(originalPath, change) {
  try {
    const original = readFileSync(originalPath, 'utf-8');
    const { frontmatter, body } = parseSkillFile(original);

    let updatedBody = body;
    const proposedUpdates = change.proposed_updates || {};

    for (const signal of (proposedUpdates.high_confidence || [])) {
      updatedBody = applyHighConfidenceUpdate(updatedBody, signal);
    }

    for (const signal of (proposedUpdates.medium_confidence || [])) {
      updatedBody = applyMediumConfidenceUpdate(updatedBody, signal);
    }

    for (const signal of (proposedUpdates.low_confidence || [])) {
      updatedBody = applyLowConfidenceUpdate(updatedBody, signal);
    }

    const updated = reconstructSkillFile(frontmatter, updatedBody);

    // Simple diff (show new sections)
    const diff = [];
    diff.push('=== Proposed Changes ===\n');

    if (proposedUpdates.high_confidence?.length > 0) {
      diff.push('\n[HIGH CONFIDENCE - Critical Corrections]');
      for (const signal of proposedUpdates.high_confidence) {
        diff.push(`  ${signal.description || 'Correction'}`);
      }
    }

    if (proposedUpdates.medium_confidence?.length > 0) {
      diff.push('\n[MEDIUM CONFIDENCE - Best Practices]');
      for (const signal of proposedUpdates.medium_confidence) {
        diff.push(`  ${signal.description || signal.pattern || 'Approved'}`);
      }
    }

    if (proposedUpdates.low_confidence?.length > 0) {
      diff.push('\n[LOW CONFIDENCE - Considerations]');
      for (const signal of proposedUpdates.low_confidence) {
        diff.push(`  ${signal.suggestion || signal.description || 'Suggestion'}`);
      }
    }

    diff.push('\n=== End of Changes ===\n');

    return diff.join('\n');
  } catch (error) {
    return `Error generating diff: ${error.message}`;
  }
}

/**
 * CLI entry point
 */
if (import.meta.url === `file://${process.argv[1]}`) {
  const args = process.argv.slice(2);
  const command = args[0];

  if (command === 'propose' && args.length >= 2) {
    // Show diff preview
    const skillName = args[1];
    const skillPath = join(homedir(), '.claude', 'skills', skillName, 'SKILL.md');

    // Example test change
    const testChange = {
      skill_name: skillName,
      proposed_updates: {
        high_confidence: [{
          description: 'Test correction (DEMO)',
          old_approach: 'Old way',
          new_approach: 'New way'
        }]
      }
    };

    console.log(generateDiffPreview(skillPath, testChange));

  } else if (command === 'apply' && args.length >= 2) {
    // Apply update
    const skillName = args[1];
    const testChange = {
      skill_name: skillName,
      proposed_updates: {
        high_confidence: [{
          description: 'Test correction',
          old_approach: 'Old way',
          new_approach: 'New way'
        }]
      }
    };

    await updateSkill(testChange);

  } else {
    console.log('Usage:');
    console.log('  node skill-updater.js propose <skill-name>   # Show diff preview');
    console.log('  node skill-updater.js apply <skill-name>     # Apply test update');
  }
}
