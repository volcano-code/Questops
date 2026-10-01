import React, { FormEvent, useState } from "react";
import { createRoot } from "react-dom/client";
import { createRun, RunMode, RunResult } from "./api";
import "./style.css";

const gates = ["Backend", "Web", "Harness Live", "Unity EditMode", "Unity PlayMode", "Full E2E"];

function App() {
  const [intent, setIntent] = useState("Create the canonical blacksmith iron-ore quest.");
  const [mode, setMode] = useState<RunMode>("fixture");
  const [consent, setConsent] = useState(false);
  const [result, setResult] = useState<RunResult | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true); setError(""); setResult(null);
    try { setResult(await createRun(intent, mode, consent)); }
    catch (e) { setError(e instanceof Error ? e.message : "Run failed"); }
    finally { setBusy(false); }
  }

  return (
    <main>
      <p className="eyebrow">QUESTOPS / VERIFIED GAME DEV AGENT</p>
      <h1>Canonical release candidate</h1>
      <p>Level 5 → blacksmith → 3 iron ore → 100 gold → exactly once.</p>

      <section className="panel">
        <h2>Create a run</h2>
        <form onSubmit={submit}>
          <label>Quest request<textarea value={intent} onChange={e => setIntent(e.target.value)} /></label>
          <div className="row">
            <label>Mode
              <select value={mode} onChange={e => { setMode(e.target.value as RunMode); setConsent(false); }}>
                <option value="fixture">Fixture / no model</option>
                <option value="live">Live DeepSeek Harness</option>
              </select>
            </label>
            {mode === "live" && <label className="consent">
              <input type="checkbox" checked={consent} onChange={e => setConsent(e.target.checked)} />
              I explicitly allow a real model call.
            </label>}
          </div>
          <button disabled={busy || !intent.trim() || (mode === "live" && !consent)}>
            {busy ? "Running…" : "Create run"}
          </button>
        </form>
        {error && <pre className="error">{error}</pre>}
        {result && <div className="result">
          <strong>{result.mode === "live" ? "LIVE MODEL" : "FIXTURE — NOT A MODEL CALL"}</strong>
          <span>Run {result.runId}</span>
          <pre>{JSON.stringify(result.draft, null, 2)}</pre>
        </div>}
      </section>

      <section>
        <h2>Release gates</h2>
        <div className="grid">{gates.map(gate => <article key={gate}><strong>{gate}</strong><span>SEE CI EVIDENCE</span></article>)}</div>
      </section>
      <section><h2>Evidence policy</h2><p>Fixture ≠ live model. Source inventory ≠ Unity execution. Browser has no approval/apply endpoint.</p></section>
    </main>
  );
}

createRoot(document.getElementById("root")!).render(<React.StrictMode><App /></React.StrictMode>);
