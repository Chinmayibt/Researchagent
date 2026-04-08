import React from "react";

export default function Settings() {
  return (
    <main className="workspace">
      <section className="card">
        <h2>Settings</h2>
        <p className="muted">API keys and runtime limits are configured on the backend via environment variables.</p>
        <ul>
          <li>`OPENROUTER_API_KEY`, `GROQ_API_KEY`</li>
          <li>`DEFAULT_MAX_PAPERS`, `DEFAULT_MAX_ITERATIONS`</li>
          <li>`OPENALEX_EMAIL`, `CROSSREF_MAILTO`</li>
        </ul>
      </section>
    </main>
  );
}
