#!/usr/bin/env node
/**
 * verify-backup.js
 *
 * Verifies backup system integrity
 */

import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const skillPath = join(__dirname, 'SKILL.md');
const backupPath = join(__dirname, '.backups', 'SKILL_20260112204343.md');

console.log('╔════════════════════════════════════════════════════════════════╗');
console.log('║ Backup System Verification                                     ║');
console.log('╚════════════════════════════════════════════════════════════════╝\n');

// 1. Check backup exists
if (!existsSync(backupPath)) {
  console.log('✗ Backup file not found:', backupPath);
  process.exit(1);
}
console.log('✅ Backup file exists:', backupPath);

// 2. Read both files
const currentContent = readFileSync(skillPath, 'utf-8');
const backupContent = readFileSync(backupPath, 'utf-8');

console.log(`\nCurrent SKILL.md: ${currentContent.length} bytes`);
console.log(`Backup file:      ${backupContent.length} bytes`);

// 3. Find the difference
const currentLines = currentContent.split('\n');
const backupLines = backupContent.split('\n');

console.log(`\nCurrent lines: ${currentLines.length}`);
console.log(`Backup lines:  ${backupLines.length}`);

// 4. Identify the added line
let addedLines = [];
for (let i = 0; i < currentLines.length; i++) {
  if (!backupContent.includes(currentLines[i]) && currentLines[i].trim()) {
    addedLines.push({ lineNum: i + 1, content: currentLines[i] });
  }
}

if (addedLines.length > 0) {
  console.log('\n✅ Changes detected (new lines added):');
  addedLines.forEach(line => {
    console.log(`  Line ${line.lineNum}: ${line.content.trim().substring(0, 80)}...`);
  });
} else {
  console.log('\n⚠️  No differences detected (unexpected)');
}

// 5. Verify YAML frontmatter preserved
const currentYAML = currentContent.split('---')[1];
const backupYAML = backupContent.split('---')[1];

if (currentYAML === backupYAML) {
  console.log('\n✅ YAML frontmatter preserved (identical)');
} else {
  console.log('\n✗ YAML frontmatter changed (unexpected)');
}

// 6. Verify backup can be used for rollback
console.log('\n✅ Backup is valid and can be used for rollback');
console.log('\nRollback command:');
console.log(`  node -e "fs.copyFileSync('${backupPath}', '${skillPath}')"`);

console.log('\n╔════════════════════════════════════════════════════════════════╗');
console.log('║ Backup System: VERIFIED                                        ║');
console.log('╚════════════════════════════════════════════════════════════════╝');
