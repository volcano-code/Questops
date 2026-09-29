# Run the real gates

QuestOps deliberately separates software checks from real external execution.

## Harness live

Prerequisites: Python 3.10+, Node 22 + pnpm for plugin installation, the published `deepseek-harness-sdk`, and a valid `DEEPSEEK_API_KEY`.

Run:

    python Harness/install_smoke.py --workspace .
    DEEPSEEK_API_KEY=... python Harness/live_smoke.py --workspace . --model deepseek-flash

The live smoke requires both QuestOps grounding tools, parses the model's final response as a strict canonical quest, validates it, and writes both `artifacts/harness/draft.json` and hashed live evidence. Mock output cannot promote `harnessLive`.

## Unity live

The project is frozen to Unity `6000.3.23f1`. A runner must pass the exact-version preflight before tests execute.

On Windows:

    py -3 tools/unity_preflight.py --unity "C:\Program Files\Unity\Hub\Editor\6000.3.23f1\Editor\Unity.exe" --project .
    py -3 tools/run_unity_tests.py --unity "C:\Program Files\Unity\Hub\Editor\6000.3.23f1\Editor\Unity.exe" --project . --mode all --canonical-artifact Schemas/canonical-quest.json

The runner requires non-empty NUnit XML and zero failed tests. PlayMode reads the supplied artifact and proves the canonical exactly-once outcome.

GitHub also contains the manual `unity-live.yml` workflow. It only targets a self-hosted runner labeled `questops-unity` and `unity-6000.3.23f1`.

## Full RC1 E2E

The manual `rc1-e2e.yml` workflow is the release path. It requires:

- a self-hosted Unity 6000.3.23f1 runner;
- repository secret `DEEPSEEK_API_KEY`;
- a human workflow dispatch where the `approval` input is exactly `APPROVE`.

One workflow then performs:

    real Harness tool calls
    -> validated model draft + SHA256
    -> approval artifact bound to that SHA256 and GitHub actor
    -> create-only apply
    -> Unity EditMode + PlayMode consuming the applied bytes
    -> commit/content hash-chain verification
    -> fullE2E PASS fragment

No step is allowed to substitute mock Harness output, Unity source inventory, or a different commit/artifact for release evidence.
