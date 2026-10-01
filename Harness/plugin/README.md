# QuestOps DeepSeek Harness plugin

This is the installable Cordis/Harness bundle used by RC1.

It registers two read-only model-callable tools:

- `questops_read_project_contract`
- `questops_read_authoring_skill`

The plugin also installs an agent-scoped `tools.restrict({ allow: ... })` mask so inherited tools from `sdk-minimal` — notably its danger-full-access persistent shell — are not part of the RC1 model tool surface. DeepSeek Harness documents `tools.restrict` as the scope-aligned mechanism for filtering inherited global tools.

There is deliberately no approval, write, shell, or apply capability in the RC1 model surface. Human approval and create-only apply remain host-side operations.

`Harness/install_smoke.py` proves the bundle can be installed and composed. `Harness/live_smoke.py` additionally inspects real `request/header` events and fails unless the visible model tool set is exactly the two read-only QuestOps tools.

A source file, plugin-install success, or mock test can never set `harnessLive=PASS`; a real credentialed model session is required.
