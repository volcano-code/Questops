# Harness boundary

This directory separates deterministic CI fixtures from real DeepSeek Harness evidence.

- `MockHarnessAdapter` is for software tests only. It always reports `mode=mock` and `liveModel=false`.
- `HttpHarnessAdapter` talks to a QuestOps-owned gateway endpoint. It fails closed unless the upstream proves `mode=live`, `liveModel=true`, and a non-empty `traceId`.
- A future real DeepSeek Harness SDK/plugin process must implement that gateway contract. Until it is installed and a real model/tool session is recorded, the `harnessLive` release gate stays BLOCKED/NOT_RUN.

A passing mock test is never sufficient evidence for `harnessLive=PASS`.
