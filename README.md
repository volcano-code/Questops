# QuestOps

QuestOps is a Unity game-development Agent project focused on **verified quest authoring**.

## Target workflow

```text
Natural-language quest brief
  -> DeepSeek Harness project grounding / Skills / tools
  -> structured quest draft
  -> deterministic validation
  -> bounded repair
  -> human approval
  -> create-only apply
  -> Unity PlayMode outcome verification
  -> auditable evidence
```

## Canonical release case

The first release is intentionally narrow:

```text
Player level 5
-> talk to npc_blacksmith_01
-> collect item_iron_ore x3
-> return to the blacksmith
-> receive 100 gold exactly once
```

## Current repository status

This repository has been initialized for the recovery/development track.

Important evidence policy:

- software unit tests are not reported as Agent benchmark success;
- fixture/offline flows are not reported as real model calls;
- source test inventory is not reported as Unity execution;
- integration gates use PASS / FAIL / BLOCKED / NOT_RUN;
- no model-generated change is applied without explicit approval.

## Planned components

- Unity / C#: quest runtime, deterministic validator, Editor tooling, graybox PlayMode
- Python / FastAPI: orchestration, validation, evidence, browser API
- DeepSeek Harness: real sessions, typed project tools, Skills, policy boundaries
- React / TypeScript: small local workbench for request submission and run inspection

## Scope freeze

Until the canonical end-to-end case is green, this project does **not** add multi-agent orchestration, A2A, Agentic RL, long-term learning memory, or additional game systems.

