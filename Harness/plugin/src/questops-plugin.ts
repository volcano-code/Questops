import { readFile } from 'node:fs/promises'
import type { Context } from '@deepseek-ai/cordis'
import Schema from '@deepseek-ai/schemastery'
import { defineTool } from '@deepseek-ai/dsh-tools'

export const name = 'questops-project-tools'
export const inject = ['tools']

export interface Config {
  contractPath: string
  skillPath: string
}

export const Config: Schema<Config> = Schema.object({
  contractPath: Schema.string().required(),
  skillPath: Schema.string().required(),
})

async function readUtf8(path: string): Promise<string> {
  if (!path) throw new Error('path is required')
  return readFile(path, 'utf8')
}

export function apply(ctx: Context, config: Config) {
  ctx.tools.register(defineTool({
    name: 'questops_read_project_contract',
    description: 'Read the grounded QuestOps canonical quest contract before drafting.',
    parameters: {},
    output: {
      schema: { type: 'string' },
      render: (_args, value) => [{ type: 'text', text: value }],
    },
    async execute() {
      return readUtf8(config.contractPath)
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
      return readUtf8(config.skillPath)
    },
  }))
}
