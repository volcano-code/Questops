# Recovery status

This branch is the GitHub-side recovery bootstrap.

## What is real now

- GitHub repository exists and has a real `main` branch.
- `dev/recovery` is a real development branch.
- The release-gate manifest and checker are committed on this branch.

## What is not claimed yet

The historical QuestOps Recovery ZIP/file tree has **not** been reconstructed in
this repository by the GitHub connector. The chat artifact and the GitHub
connector do not currently expose a direct binary/file-tree bridge.

Accordingly, these remain NOT_RUN until the full source tree is present and
executed in the appropriate environment:

- React dependency install/typecheck/Vitest/Vite build/browser smoke
- DeepSeek Harness SDK/plugin/model live smoke
- Unity compile/EditMode
- canonical Unity PlayMode
- full Harness -> validation -> approval -> apply -> outcome E2E

## Canonical acceptance case

1. player level = 5;
2. interact with `npc_blacksmith_01`;
3. collect `item_iron_ore` x3;
4. return to the blacksmith;
5. receive 100 gold;
6. quest becomes completed;
7. repeated interaction must not grant a second reward.

The project must preserve human approval before any model-generated draft is
applied.
