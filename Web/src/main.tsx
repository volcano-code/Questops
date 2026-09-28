import React from "react";
import { createRoot } from "react-dom/client";
import "./style.css";

const gates = ["Backend", "Web", "Harness Live", "Unity EditMode", "Unity PlayMode", "Full E2E"];

function App() {
  return (
    <main>
      <p className="eyebrow">QUESTOPS / VERIFIED GAME DEV AGENT</p>
      <h1>Canonical release candidate</h1>
      <p>Level 5 → blacksmith → 3 iron ore → 100 gold → exactly once.</p>
      <section>
        <h2>Release gates</h2>
        <div className="grid">
          {gates.map((gate) => <article key={gate}><strong>{gate}</strong><span>NOT_RUN</span></article>)}
        </div>
      </section>
      <section>
        <h2>Evidence policy</h2>
        <p>Fixture ≠ live model. Test inventory ≠ Unity execution. Apply requires human approval.</p>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")!).render(<React.StrictMode><App /></React.StrictMode>);
