import { readFile } from 'node:fs/promises'
import { join, relative, resolve } from 'node:path'
import { defineTool } from '@deepseek-ai/dsh-tools'

export const name = 'questops-project-tools'
export const inject = ['tools']

const ALLOWED_TOOLS = [
  'questops_read_project_contract',
  'questops_read_authoring_skill',
]

function projectRoot() {
  const raw = process.env.QUESTOPS_PROJECT_ROOT
  if (!raw) throw new Error('QUESTOPS_PROJECT_ROOT is required')
  return resolve(raw)
}

async function readProjectFile(relativePath) {
  const root = projectRoot()
  const target = resolve(root, relativePath)
  const rel = relative(root, target)
  if (rel.startsWith('..') || rel === '..') throw new Error('path escaped project root')
  return readFile(target, 'utf8')
}

export function apply(ctx) {
  ctx.tools.register(defineTool({
    name: 'questops_read_project_contract',
    description: 'Read the grounded QuestOps canonical quest contract before drafting.',
    parameters: {},
    output: {
      schema: { type: 'string' },
      render: (_args, value) => [{ type: 'text', text: value }],
    },
    async execute() {
      return readProjectFile(join('Schemas', 'canonical-quest.json'))
    },
  }))

  ctx.tools.register(defineTool({
    name: 'questops_read_authoring_skill',
    description: 'Read the QuestOps quest-authoring rules and capability boundary.',
    parameters: {},
    output: {
      schema: { type: 'string' },
      render: (_args, value) => [{ type: 'text', text: value }],
    },
    async execute() {
      return readProjectFile(join('Skills', 'quest-authoring', 'SKILL.md'))
    },
  }))

  // sdk-minimal ships a danger-full-access persistent shell. RC1 does not need it.
  // Restrict inherited/global tools at each agent scope so only the two read-only
  // QuestOps grounding capabilities remain visible and executable.
  ctx.on('agent/created', ({ agent }) => {
    agent.ctx.effect(() => agent.ctx.tools.restrict({ allow: ALLOWED_TOOLS }))
  })
}
