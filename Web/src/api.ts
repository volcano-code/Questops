export type RunMode = "fixture" | "live";

export type RunResult = {
  runId: string;
  mode: RunMode;
  liveModel: boolean;
  draft: Record<string, unknown>;
  evidence: Record<string, unknown>;
};

export function buildRunBody(intent: string, mode: RunMode, allowModelCall: boolean) {
  return { intent: intent.trim(), mode, allow_model_call: mode === "live" && allowModelCall };
}

export async function createRun(intent: string, mode: RunMode, allowModelCall: boolean): Promise<RunResult> {
  const response = await fetch("/api/runs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(buildRunBody(intent, mode, allowModelCall)),
  });
  if (!response.ok) throw new Error("Request failed with status " + response.status);
  return response.json() as Promise<RunResult>;
}
