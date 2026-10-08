/**
 * Docs must not contradict featureFlags.ts (AGENTS.md: docs state intent, code holds values).
 *
 * Flags a doc line when it asserts a flag value — `showX: true`, `showX=false`,
 * "`showX` defaults/stays **`false`**" — that differs from the code. Instruction lines
 * ("set … false to hide", "temporarily", "revert") and struck-through history (`~~`) are skipped.
 */

import { readdirSync, readFileSync } from 'node:fs'
import { join, relative, resolve } from 'node:path'
import { describe, expect, it } from 'vitest'
import { featureFlags } from '../featureFlags'

const REPO_ROOT = resolve(__dirname, '../../../..')
const DOC_DIRS = ['docs/planning', 'docs/architecture', 'docs/features', 'docs/guides', 'docs/setup']
const FLAGS = Object.keys(featureFlags) as (keyof typeof featureFlags)[]
const FLAG_NAMES = FLAGS.join('|')

// `showX: true` / `showX = false` / `showX=true` (backticks optional)
const DIRECT = new RegExp(`\\b(${FLAG_NAMES})\`?\\s*(?::|=)\\s*\`?(true|false)\\b`, 'g')
// "`showX` / `showY` stay **`false`**", "`showX` defaults **`true`**"
const PROSE = new RegExp(
  `((?:\`?(?:${FLAG_NAMES})\`?[\\s/,and]*)+)(?:defaults?(?: to)?|stays?|remains?|is|are)\\s+\\**\`?(true|false)\\b`,
  'g',
)
const INSTRUCTION = /\b(set|setting|temporarily|revert|flip|to hide|kill switch)\b/i

function docFiles(): string[] {
  const files = [join(REPO_ROOT, 'README.md')]
  for (const dir of DOC_DIRS) {
    const abs = join(REPO_ROOT, dir)
    let entries: string[] = []
    try {
      entries = readdirSync(abs)
    } catch {
      continue
    }
    files.push(...entries.filter((f) => f.endsWith('.md')).map((f) => join(abs, f)))
  }
  return files
}

export function findContradictions(text: string, source: string): string[] {
  const out: string[] = []
  text.split('\n').forEach((line, i) => {
    if (line.includes('~~') || INSTRUCTION.test(line)) return
    const report = (flag: string, claimed: string) => {
      const actual = String(featureFlags[flag as keyof typeof featureFlags])
      if (claimed !== actual) {
        out.push(`${source}:${i + 1}: says ${flag}=${claimed}, featureFlags.ts has ${actual}`)
      }
    }
    for (const m of line.matchAll(DIRECT)) report(m[1], m[2])
    for (const m of line.matchAll(PROSE)) {
      for (const flag of m[1].match(new RegExp(FLAG_NAMES, 'g')) ?? []) report(flag, m[2])
    }
  })
  return out
}

describe('docs ↔ featureFlags drift', () => {
  it('detects direct and prose assertions, ignores instructions', () => {
    const flag = 'showLightingTab'
    const wrong = String(!featureFlags[flag])
    expect(findContradictions(`- \`${flag}: ${wrong}\` in nav`, 'x.md')).toHaveLength(1)
    expect(findContradictions(`\`${flag}\` stays **\`${wrong}\`**`, 'x.md')).toHaveLength(1)
    expect(findContradictions(`To hide it, set \`${flag}: ${wrong}\``, 'x.md')).toEqual([])
    expect(findContradictions(`~~\`${flag}: ${wrong}\`~~`, 'x.md')).toEqual([])
  })

  it('no doc asserts a flag value that contradicts featureFlags.ts', () => {
    const problems = docFiles().flatMap((file) =>
      findContradictions(readFileSync(file, 'utf8'), relative(REPO_ROOT, file)),
    )
    expect(problems).toEqual([])
  })
})
