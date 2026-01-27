#!/usr/bin/env node
/**
 * apply-learning.js
 *
 * Applies a learning to test backup/rollback system
 * Works with workspace .claude/skills/ directory
 */

import { readFileSync, existsSync, writeFileSync, copyFileSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Workspace root is 3 levels up from .claude/skills/reflect/
const workspaceRoot = join(__dirname, '..', '..', '..');
const skillsDir = join(workspaceRoot, '.claude', 'skills');

const testLearnings = JSON.parse(readFileSync(join(__dirname, 'test-learnings.json'), 'utf-8'));

const scenario = process.argv[2];

if (!scenario || !['1', '2', '3'].includes(scenario)) {
  console.log('Usage: node apply-learning.js <1|2|3>');
  console.log('  1 = HIGH Confidence → work-command-center');
  console.log('  2 = MEDIUM Confidence → work-command-center');
  console.log('  3 = LOW Confidence → reflect');
  process.exit(1);
}

let change, skillName;

switch (scenario) {
  case '1':
    skillName = 'work-command-center';
    change = testLearnings.scenario_1_high_confidence;
    console.log('Applying SCENARIO 1: HIGH Confidence (Critical Correction)');
    break;
  case '2':
    skillName = 'work-command-center';
    change = testLearnings.scenario_2_medium_confidence;
    console.log('Applying SCENARIO 2: MEDIUM Confidence (Best Practice)');
    break;
  case '3':
    skillName = 'reflect';
    change = testLearnings.scenario_3_low_confidence;
    console.log('Applying SCENARIO 3: LOW Confidence (Consideration)');
    break;
}

console.log(`Target: ${skillName}/SKILL.md`);
console.log('');
console.log('Pre-flight checks:');

const skillPath = join(skillsDir, skillName, 'SKILL.md');
const backupDir = join(skillsDir, skillName, '.backups');

if (!existsSync(skillPath)) {
  console.log(`✗ Skill file not found: ${skillPath}`);
  process.exit(1);
}
console.log(`  ✓ Skill file exists: ${skillPath}`);

if (existsSync(backupDir)) {
  console.log(`  ✓ Backup directory exists: ${backupDir}`);
} else {
  console.log(`  ℹ Backup directory will be created: ${backupDir}`);
}

console.log('');
console.log('Creating backup...');

// Create backup
if (!existsSync(backupDir)) {
  mkdirSync(backupDir, { recursive: true });
}

const timestamp = new Date()
  .toISOString()
  .replace(/[-:T]/g, '')
  .slice(0, 14); // YYYYMMDDHHmmss

const backupPath = join(backupDir, `SKILL_${timestamp}.md`);
copyFileSync(skillPath, backupPath);
console.log(`  ✓ Backup created: ${backupPath}`);

console.log('');
console.log('Applying learning...');

// Read and parse existing skill
const content = readFileSync(skillPath, 'utf-8');
const parts = content.split('---');

if (parts.length < 3) {
  console.log('✗ Invalid SKILL.md format (missing YAML frontmatter)');
  process.exit(1);
}

const frontmatter = parts[1];
const body = parts.slice(2).join('---').trim();

// Apply update based on confidence level
let updatedBody = body;
const proposedUpdates = change.proposed_updates || {};

if (proposedUpdates.low_confidence) {
  for (const signal of proposedUpdates.low_confidence) {
    const suggestion = signal.suggestion || signal.description || 'Consideration';
    const consideration = `- Consider: ${suggestion}\n`;

    // Find "Future Enhancements" section and add to it
    if (body.includes('## Future Enhancements')) {
      const beforeSection = updatedBody.split('## Future Enhancements')[0];
      const afterHeader = updatedBody.split('## Future Enhancements')[1];

      // Find next section
      const nextSectionMatch = afterHeader.match(/\n## /);

      if (nextSectionMatch) {
        const nextSectionIndex = afterHeader.indexOf(nextSectionMatch[0]);
        const sectionContent = afterHeader.substring(0, nextSectionIndex);
        const rest = afterHeader.substring(nextSectionIndex);
        updatedBody = `${beforeSection}## Future Enhancements${sectionContent}\n${consideration}${rest}`;
      } else {
        updatedBody = `${beforeSection}## Future Enhancements${afterHeader}\n${consideration}`;
      }

      console.log(`  ✓ Added consideration to "Future Enhancements" section`);
    }
  }
} else if (proposedUpdates.medium_confidence) {
  for (const signal of proposedUpdates.medium_confidence) {
    const practice = signal.practice || signal.description || 'Best practice';
    const bestPractice = `- ${practice}\n`;

    if (body.includes('## Best Practices')) {
      // Add to existing section
      const beforeSection = updatedBody.split('## Best Practices')[0];
      const afterHeader = updatedBody.split('## Best Practices')[1];
      const nextSectionMatch = afterHeader.match(/\n## /);

      if (nextSectionMatch) {
        const nextSectionIndex = afterHeader.indexOf(nextSectionMatch[0]);
        const sectionContent = afterHeader.substring(0, nextSectionIndex);
        const rest = afterHeader.substring(nextSectionIndex);
        updatedBody = `${beforeSection}## Best Practices${sectionContent}\n${bestPractice}${rest}`;
      } else {
        updatedBody = `${beforeSection}## Best Practices${afterHeader}\n${bestPractice}`;
      }
    } else {
      // Create new section before "Last Updated"
      updatedBody = `${updatedBody}\n\n## Best Practices\n\n${bestPractice}`;
    }

    console.log(`  ✓ Added best practice`);
  }
} else if (proposedUpdates.high_confidence) {
  for (const signal of proposedUpdates.high_confidence) {
    const description = signal.description || 'Correction';
    const oldApproach = signal.old_approach || 'Previous approach';
    const newApproach = signal.new_approach || 'New approach';

    const correction =
      `\n**${description}**\n\n` +
      `- ✗ Don't: ${oldApproach}\n` +
      `- ✓ Do: ${newApproach}\n` +
      `  *(Learned: ${new Date().toISOString().split('T')[0]})*\n`;

    if (body.includes('## Critical Corrections')) {
      // Add to existing section
      const beforeSection = updatedBody.split('## Critical Corrections')[0];
      const afterHeader = updatedBody.split('## Critical Corrections')[1];
      const nextSectionMatch = afterHeader.match(/\n## /);

      if (nextSectionMatch) {
        const nextSectionIndex = afterHeader.indexOf(nextSectionMatch[0]);
        const sectionContent = afterHeader.substring(0, nextSectionIndex);
        const rest = afterHeader.substring(nextSectionIndex);
        updatedBody = `${beforeSection}## Critical Corrections${sectionContent}\n${correction}${rest}`;
      } else {
        updatedBody = `${beforeSection}## Critical Corrections${afterHeader}\n${correction}`;
      }
    } else {
      // Insert at beginning
      updatedBody = `## Critical Corrections\n${correction}\n---\n\n${updatedBody}`;
    }

    console.log(`  ✓ Added critical correction`);
  }
}

// Reconstruct file
const updatedContent = `---\n${frontmatter}---\n\n${updatedBody}`;

// Write updated file
writeFileSync(skillPath, updatedContent, 'utf-8');

console.log('');
console.log('╔════════════════════════════════════════════════════════════════╗');
console.log('║ Learning Applied Successfully                                  ║');
console.log('╚════════════════════════════════════════════════════════════════╝');
console.log('');
console.log('Verification steps:');
console.log(`  1. View backup: type "${backupPath}"`);
console.log(`  2. View changes: type "${skillPath}"`);
console.log(`  3. Test rollback: copy "${backupPath}" "${skillPath}"`);
console.log('  4. Commit: git add .claude/skills/' + skillName + '/SKILL.md');
console.log('           git commit -m "Learn: [description]"');
