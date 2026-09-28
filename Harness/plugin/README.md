# QuestOps DeepSeek Harness plugin

This is the real Cordis/Harness plugin source for project grounding.

It registers two model-callable read-only tools:

- `questops_read_project_contract`
- `questops_read_authoring_skill`

The plugin deliberately has **no apply/approval/write tool**. Approval and create-only apply stay outside model authority.

## Development smoke

Use a DeepSeek Harness checkout with dependencies installed. Copy
`cordis.patch.example.yml`, replace all paths with absolute paths, then load the
overlay with the Harness development command.

A source file or successful TypeScript parse is not enough to set
`harnessLive=PASS`. Promotion requires evidence from a real Harness session
showing the plugin loaded and the model actually called the QuestOps tools.

The plugin API follows the Harness Cordis tool pattern: `apply(ctx)`,
`inject=['tools']`, and `defineTool(...)`.
