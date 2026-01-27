#!/usr/bin/env node
/**
 * reflect-engine.js
 *
 * Extracts learning signals from conversation transcripts.
 * Identifies corrections, approvals, and patterns with confidence levels.
 *
 * Ported from Python claude-reflect-system to Node.js ESM for skill-builder standards.
 */

import { readFileSync, existsSync, readdirSync, statSync } from 'fs';
import { join, resolve } from 'path';
import { homedir } from 'os';

// Correction patterns (HIGH confidence)
const CORRECTION_PATTERNS = [
  /(?:no,?\s+don't\s+(?:do|use)\s+(.+?)[,.]?\s+(?:do|use)\s+(.+))/i,
  /(?:actually,?\s+(.+?)\s+(?:is|should be)\s+(.+))/i,
  /(?:instead\s+of\s+(.+?),?\s+(?:you\s+should|use|do)\s+(.+))/i,
  /(?:never\s+(?:do|use)\s+(.+))/i,
  /(?:always\s+(?:do|use|check for)\s+(.+))/i,
];

// Approval patterns (MEDIUM confidence)
const APPROVAL_PATTERNS = [
  /(?:(?:yes,?\s+)?(?:that's\s+)?(?:perfect|great|exactly|correct))/i,
  /(?:works?\s+(?:perfectly|great|well))/i,
  /(?:(?:good|nice)\s+(?:job|work))/i,
];

// Question patterns (LOW confidence)
const QUESTION_PATTERNS = [
  /(?:have\s+you\s+considered\s+(.+))/i,
  /(?:why\s+not\s+(?:try|use)\s+(.+))/i,
  /(?:what\s+about\s+(.+))/i,
];

/**
 * Main entry point - extracts signals from transcript
 * @param {string|null} transcriptPath - Path to transcript.jsonl file (optional)
 * @returns {Object} Signals grouped by skill name
 */
export function extractSignals(transcriptPath = null) {
  if (!transcriptPath) {
    transcriptPath = findLatestTranscript();
  }

  if (!transcriptPath || !existsSync(transcriptPath)) {
    console.warn(`Warning: Transcript not found: ${transcriptPath}`);
    return {};
  }

  const signals = [];
  const messages = loadTranscript(transcriptPath);
  const skillsUsed = findSkillInvocations(messages);

  messages.forEach((msg, i) => {
    if (msg.role !== 'user') return;

    const content = String(msg.content || '');
    const context = messages.slice(Math.max(0, i - 5), i + 1);

    // Check for corrections (HIGH confidence)
    for (const pattern of CORRECTION_PATTERNS) {
      const match = content.match(pattern);
      if (match) {
        signals.push({
          confidence: 'HIGH',
          type: 'correction',
          content,
          context,
          skills: skillsUsed.length > 0 ? skillsUsed : ['general'],
          match: match.slice(1), // Groups only (exclude full match)
          description: extractCorrectionDescription(content, match)
        });
      }
    }

    // Check for approvals (MEDIUM confidence)
    const prevMsg = i > 0 ? messages[i - 1] : null;
    if (prevMsg && prevMsg.role === 'assistant') {
      for (const pattern of APPROVAL_PATTERNS) {
        if (pattern.test(content)) {
          signals.push({
            confidence: 'MEDIUM',
            type: 'approval',
            content,
            context,
            skills: skillsUsed.length > 0 ? skillsUsed : ['general'],
            previous_approach: extractApproach(prevMsg),
            description: 'Approved approach'
          });
        }
      }
    }

    // Check for questions/suggestions (LOW confidence)
    for (const pattern of QUESTION_PATTERNS) {
      const match = content.match(pattern);
      if (match) {
        signals.push({
          confidence: 'LOW',
          type: 'question',
          content,
          context,
          skills: skillsUsed.length > 0 ? skillsUsed : ['general'],
          suggestion: match[1] || content,
          description: `Consider: ${match[1] || content}`
        });
      }
    }
  });

  return groupBySkill(signals);
}

/**
 * Find most recent transcript file
 * @returns {string|null} Path to transcript or null if not found
 */
function findLatestTranscript() {
  try {
    // Check environment variable first
    if (process.env.TRANSCRIPT_PATH) {
      return process.env.TRANSCRIPT_PATH;
    }

    // Search SESSION_DIR for latest transcript.jsonl
    const sessionDir = process.env.SESSION_DIR || join(homedir(), '.claude', 'session-env');
    const sessionDirResolved = resolve(sessionDir);

    if (existsSync(sessionDirResolved)) {
      const transcripts = [];
      const dirs = readdirSync(sessionDirResolved);

      for (const dir of dirs) {
        const transcriptPath = join(sessionDirResolved, dir, 'transcript.jsonl');
        if (existsSync(transcriptPath)) {
          const stats = statSync(transcriptPath);
          transcripts.push({ path: transcriptPath, mtime: stats.mtimeMs });
        }
      }

      if (transcripts.length > 0) {
        // Return most recently modified
        transcripts.sort((a, b) => b.mtime - a.mtime);
        return transcripts[0].path;
      }
    }
  } catch (error) {
    console.error(`Error finding transcript: ${error.message}`);
  }

  return null;
}

/**
 * Load transcript from JSONL file
 * @param {string} path - Path to transcript.jsonl
 * @returns {Array<Object>} Array of message objects
 */
function loadTranscript(path) {
  const messages = [];

  try {
    const content = readFileSync(path, 'utf-8');
    const lines = content.split('\n');

    for (const line of lines) {
      if (line.trim()) {
        try {
          const msg = JSON.parse(line);
          messages.push(msg);
        } catch (parseError) {
          // Skip malformed JSON lines
          continue;
        }
      }
    }
  } catch (error) {
    console.error(`Error loading transcript: ${error.message}`);
  }

  return messages;
}

/**
 * Find skill invocations in messages
 * @param {Array<Object>} messages - Transcript messages
 * @returns {Array<string>} List of invoked skill names
 */
function findSkillInvocations(messages) {
  const skills = new Set();

  for (const msg of messages) {
    // Check tool_uses for Skill tool invocations
    if (msg.tool_uses) {
      for (const tool of msg.tool_uses) {
        if (tool.name === 'Skill' && tool.parameters?.skill) {
          skills.add(tool.parameters.skill);
        }
      }
    }

    // Check content for /skill-name patterns
    const content = String(msg.content || '');
    const matches = content.matchAll(/\/([a-z][a-z0-9-]*)/g);
    for (const match of matches) {
      skills.add(match[1]);
    }
  }

  return Array.from(skills);
}

/**
 * Extract approach from assistant message (first 500 chars)
 * @param {Object} message - Message object
 * @returns {string} Extracted approach text
 */
function extractApproach(message) {
  const content = String(message.content || '');
  return content.substring(0, 500);
}

/**
 * Create human-readable description from correction
 * @param {string} content - Full message content
 * @param {Array} match - Regex match result
 * @returns {string} Correction description
 */
function extractCorrectionDescription(content, match) {
  const groups = match.slice(1); // Exclude full match at index 0

  if (groups.length === 2) {
    return `Use '${groups[1]}' instead of '${groups[0]}'`;
  } else if (groups.length === 1) {
    return `Correction: ${groups[0]}`;
  }

  return 'User provided correction';
}

/**
 * Group signals by associated skill
 * @param {Array<Object>} signals - All extracted signals
 * @returns {Object} Signals grouped by skill name
 */
function groupBySkill(signals) {
  const grouped = {};

  for (const signal of signals) {
    for (const skill of (signal.skills || ['general'])) {
      if (!grouped[skill]) {
        grouped[skill] = [];
      }
      grouped[skill].push(signal);
    }
  }

  return grouped;
}

/**
 * CLI entry point
 */
if (import.meta.url === `file://${process.argv[1]}`) {
  const transcriptPath = process.argv[2] || null;
  const signals = extractSignals(transcriptPath);
  console.log(JSON.stringify(signals, null, 2));
}
