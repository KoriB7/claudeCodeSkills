#!/usr/bin/env node
/**
 * show-detailed-diffs.js
 *
 * Shows the actual markdown content that will be added for each learning
 */

import { readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const testLearnings = JSON.parse(readFileSync(join(__dirname, 'test-learnings.json'), 'utf-8'));

console.log('╔════════════════════════════════════════════════════════════════╗');
console.log('║ Detailed Markdown Diff Preview                                 ║');
console.log('╚════════════════════════════════════════════════════════════════╝\n');

// Scenario 1: HIGH Confidence
const s1 = testLearnings.scenario_1_high_confidence.proposed_updates.high_confidence[0];
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('SCENARIO 1: work-command-center/SKILL.md');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('Location: At the beginning (before existing content)');
console.log('');
console.log('Markdown to be added:');
console.log('```markdown');
console.log('## Critical Corrections');
console.log('');
console.log(`**${s1.description}**`);
console.log('');
console.log(`- ✗ Don't: ${s1.old_approach}`);
console.log(`- ✓ Do: ${s1.new_approach}`);
console.log(`  *(Learned: ${new Date().toISOString().split('T')[0]})*`);
console.log('');
console.log('---');
console.log('```');
console.log('');

// Scenario 2: MEDIUM Confidence
const s2 = testLearnings.scenario_2_medium_confidence.proposed_updates.medium_confidence[0];
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('SCENARIO 2: work-command-center/SKILL.md');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('Location: Before "Saving Next Steps" section or at end');
console.log('');
console.log('Markdown to be added:');
console.log('```markdown');
console.log('## Best Practices');
console.log('');
console.log(`- ${s2.practice}`);
console.log('```');
console.log('');

// Scenario 3: LOW Confidence
const s3 = testLearnings.scenario_3_low_confidence.proposed_updates.low_confidence[0];
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('SCENARIO 3: reflect/SKILL.md');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('Location: In existing "Future Enhancements" section');
console.log('');
console.log('Markdown to be added:');
console.log('```markdown');
console.log('## Considerations');
console.log('');
console.log(`- Consider: ${s3.suggestion}`);
console.log('```');
console.log('');

console.log('╔════════════════════════════════════════════════════════════════╗');
console.log('║ Ready to Apply                                                 ║');
console.log('╚════════════════════════════════════════════════════════════════╝');
console.log('');
console.log('Choose which scenario to apply to test backup/rollback:');
console.log('  1. HIGH Confidence (Critical Correction) → work-command-center');
console.log('  2. MEDIUM Confidence (Best Practice) → work-command-center');
console.log('  3. LOW Confidence (Consideration) → reflect');
console.log('');
console.log('All changes will:');
console.log('  ✓ Create timestamped backup before modification');
console.log('  ✓ Preserve existing SKILL.md formatting');
console.log('  ✓ Update skill content with learning');
console.log('  ✓ Be ready for Git commit');
