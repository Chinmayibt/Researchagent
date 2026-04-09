import React from "react";

type Props = {
  error: string;
};

/** Shown only when a run error is present. */
export default function CommandActions({ error }: Props) {
  if (!error) return null;

  return (
    <section className="card command-card command-card--secondary" role="alert" aria-label="Run error">
      <p className="error" role="alert">
        {error}
      </p>
    </section>
  );
}
