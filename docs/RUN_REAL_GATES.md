# Run the real gates

The repository CI can prove Python/Web software behavior and a real Harness SDK/plugin installation. Two gates require credentials or installed proprietary tooling.

## Harness live

Prerequisites: Python 3.10+, Node 22 + pnpm (only for plugin installation), the published `deepseek-harness-sdk`, and a valid `DEEPSEEK_API_KEY`.

Run:

    python Harness/install_smoke.py --workspace .
    DEEPSEEK_API_KEY=... python Harness/live_smoke.py --workspace .

The live smoke fails unless the model calls both QuestOps read-only tools. It stores session/tool evidence hashes rather than promoting mock output.

For GitHub Actions, configure the repository secret `DEEPSEEK_API_KEY`. Without it, CI reports `harnessLive=BLOCKED`.

## Unity EditMode + PlayMode

On Windows, run:

    py -3 tools/run_unity_tests.py --unity "C:\\Program Files\\Unity\\Hub\\Editor\\6000.3.23f1\\Editor\\Unity.exe" --project .

The runner invokes Unity Test Framework in batch mode for both `QuestOps.Tests.EditMode` and `QuestOps.Tests.PlayMode`, requires result XML with at least one test, and rejects process or test failures.

Outputs are written under `artifacts/unity/`. Source presence alone is not execution evidence.
