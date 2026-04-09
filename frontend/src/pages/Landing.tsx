import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  LayoutDashboard,
  MessageSquare,
  Map,
  Mic,
  FileText,
  Search,
  Share2,
  FileDown,
  CheckCircle2,
  Sparkles,
  Shield,
  Cpu,
  Zap,
} from "lucide-react";
import MotionReveal from "../components/MotionReveal";
import { useDocumentTitle } from "../hooks/useDocumentTitle";

export default function Landing() {
  useDocumentTitle("Mantis — Research workspace & agents");
  const [headerScrolled, setHeaderScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setHeaderScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <div className="landing">
      <a href="#landing-main" className="skip-link">
        Skip to main content
      </a>

      <header className={`landing-header${headerScrolled ? " landing-header--scrolled" : ""}`}>
        <div className="landing-header-inner">
          <Link to="/" className="landing-brand">
            <span className="landing-logo-mark">M</span>
            <span className="landing-logo-text">Mantis</span>
          </Link>
          <nav className="landing-header-nav" aria-label="Main">
            <Link to="/workspace" className="landing-header-nav-link">
              Workspace
            </Link>
            <a href="#how-it-works" className="landing-header-nav-link">
              How it works
            </a>
            <a href="#features" className="landing-header-nav-link">
              Features
            </a>
            <Link to="/settings" className="landing-header-nav-link">
              Settings
            </Link>
          </nav>
          <Link to="/workspace" className="primary landing-header-btn">
            Open workspace
          </Link>
        </div>
      </header>

      <main id="landing-main" className="landing-main" tabIndex={-1}>
        <section className="landing-hero-section" aria-labelledby="landing-hero-title">
          <div className="landing-hero-grid">
            <div className="landing-hero">
              <p className="landing-eyebrow">
                <Sparkles size={14} className="landing-eyebrow-icon" aria-hidden />
                Research workspace &amp; AI agents
              </p>
              <ul className="landing-badges" aria-label="Highlights">
                <li className="landing-badge">
                  <Zap size={14} aria-hidden />
                  In your browser
                </li>
                <li className="landing-badge">
                  <Shield size={14} aria-hidden />
                  Keys stay on device
                </li>
                <li className="landing-badge">
                  <Cpu size={14} aria-hidden />
                  4 agent modes
                </li>
              </ul>
              <h1 id="landing-hero-title" className="landing-title">
                From one topic to{" "}
                <span className="landing-title-gradient">papers, a map, and a report</span> you can share
              </h1>
              <p className="landing-lead">
                You get automated discovery and synthesis, then debate papers, learn with a roadmap, or turn a PDF into a
                short podcast—all in your browser. API keys stay on your machine.
              </p>
              <p className="landing-trust-line">
                <CheckCircle2 size={16} className="landing-trust-icon" aria-hidden />
                No signup required — start with a topic or jump straight to agents.
              </p>
              <div className="landing-actions">
                <Link to="/workspace" className="primary landing-primary">
                  Open workspace
                  <ArrowRight size={18} aria-hidden className="landing-primary-icon" />
                </Link>
                <a href="#features" className="button-ghost landing-secondary">
                  Browse agents
                </a>
                <Link to="/reports" className="button-ghost landing-tertiary">
                  Past runs (this device)
                </Link>
              </div>
              <nav className="landing-chips" aria-label="Quick links to agents">
                <a href="#features" className="landing-chip">
                  All features
                </a>
                <Link to="/debate" className="landing-chip">
                  Debate
                </Link>
                <Link to="/roadmap" className="landing-chip">
                  Roadmap
                </Link>
                <Link to="/podcast" className="landing-chip">
                  Podcast
                </Link>
              </nav>
            </div>

            <div className="landing-hero-visual" aria-hidden="true">
              <div className="landing-orb landing-orb--a" />
              <div className="landing-orb landing-orb--b" />
              <div className="landing-mock-window">
                <div className="landing-mock-titlebar">
                  <span className="landing-mock-dot" />
                  <span className="landing-mock-dot" />
                  <span className="landing-mock-dot" />
                </div>
                <div className="landing-mock-body">
                  <div className="landing-mock-line landing-mock-line--accent" />
                  <div className="landing-mock-line" />
                  <div className="landing-mock-line landing-mock-line--short" />
                  <div className="landing-mock-graph">
                    <span className="landing-mock-node" />
                    <span className="landing-mock-bar" />
                    <span className="landing-mock-node" />
                    <span className="landing-mock-bar" />
                    <span className="landing-mock-node" />
                  </div>
                  <div className="landing-mock-line landing-mock-line--medium" />
                </div>
              </div>
            </div>
          </div>
        </section>

        <MotionReveal>
          <section className="landing-stats" aria-label="Product snapshot">
            <div className="landing-stat landing-stat--interactive">
              <span className="landing-stat-value">Full pipeline</span>
              <span className="landing-stat-label muted">Topic → sources → graph → PDF report</span>
            </div>
            <div className="landing-stat landing-stat--interactive">
              <span className="landing-stat-value">Specialized agents</span>
              <span className="landing-stat-label muted">Debate, roadmap, podcast, and more</span>
            </div>
            <div className="landing-stat landing-stat--interactive">
              <span className="landing-stat-value">You control APIs</span>
              <span className="landing-stat-label muted">Point Settings at your own backends</span>
            </div>
          </section>
        </MotionReveal>

        <div className="landing-section-rule" aria-hidden="true" />

        <section className="landing-how" id="how-it-works" aria-labelledby="landing-how-heading">
          <MotionReveal>
            <h2 id="landing-how-heading" className="landing-section-title">
              How it works
            </h2>
            <p className="landing-section-sub muted">Three steps from idea to output</p>
            <ol className="landing-steps motion-reveal-stagger">
            <li className="landing-step-card">
              <div className="landing-step-icon-wrap" aria-hidden>
                <Search size={22} strokeWidth={1.75} />
              </div>
              <span className="landing-step-num">1</span>
              <h3 className="landing-step-title">Enter a topic</h3>
              <p className="muted landing-step-desc">
                Describe what you want to research. Mantis queues the pipeline and streams progress as it runs.
              </p>
            </li>
            <li className="landing-step-card">
              <div className="landing-step-icon-wrap" aria-hidden>
                <Share2 size={22} strokeWidth={1.75} />
              </div>
              <span className="landing-step-num">2</span>
              <h3 className="landing-step-title">Review evidence &amp; graph</h3>
              <p className="muted landing-step-desc">
                Explore sources, clusters, and insights. See how papers connect before you write or present.
              </p>
            </li>
            <li className="landing-step-card">
              <div className="landing-step-icon-wrap" aria-hidden>
                <FileDown size={22} strokeWidth={1.75} />
              </div>
              <span className="landing-step-num">3</span>
              <h3 className="landing-step-title">Export or extend</h3>
              <p className="muted landing-step-desc">
                Download a PDF report, reopen runs from Reports, or use agents for debate, roadmaps, and podcasts.
              </p>
            </li>
          </ol>
          </MotionReveal>
        </section>

        <section className="landing-setup" aria-labelledby="landing-setup-heading">
          <h2 id="landing-setup-heading" className="sr-only">
            Setup expectations
          </h2>
          <MotionReveal>
          <div className="landing-setup-card">
            <ul className="landing-setup-list">
              <li>
                <CheckCircle2 size={18} className="landing-setup-bullet" aria-hidden />
                <span>
                  <strong>Research pipeline</strong> uses the main API (<code className="landing-inline-code">backend/</code>
                  , port 8000 by default).
                </span>
              </li>
              <li>
                <CheckCircle2 size={18} className="landing-setup-bullet" aria-hidden />
                <span>
                  <strong>Debate, roadmap &amp; podcast</strong> use the agents API (
                  <code className="landing-inline-code">research_agent/</code>, port 8001). Podcast generation expects local{" "}
                  <strong>Ollama</strong> unless you change the integration.
                </span>
              </li>
              <li>
                <CheckCircle2 size={18} className="landing-setup-bullet" aria-hidden />
                <span>
                  Configure URLs in <Link to="/settings">Settings</Link> if your ports differ.
                </span>
              </li>
            </ul>
          </div>
          </MotionReveal>
        </section>

        <section className="landing-features" id="features" aria-labelledby="landing-features-heading">
          <MotionReveal>
          <h2 id="landing-features-heading" className="landing-section-title">
            Features
          </h2>
          <p className="landing-section-sub muted">
            Workspace for full runs, plus specialized agents for PDFs and audio.
          </p>
          <ul className="landing-feature-grid motion-reveal-stagger">
            <li className="landing-feature-card">
              <div className="landing-feature-icon-wrap" aria-hidden>
                <LayoutDashboard size={22} strokeWidth={1.75} />
              </div>
              <h3>Workspace</h3>
              <p className="muted landing-feature-text">
                Run a topic through the full pipeline: sources, graph, and exportable report.
              </p>
              <Link to="/workspace" className="landing-feature-link">
                Go to workspace <span aria-hidden>→</span>
              </Link>
            </li>
            <li className="landing-feature-card">
              <div className="landing-feature-icon-wrap" aria-hidden>
                <MessageSquare size={22} strokeWidth={1.75} />
              </div>
              <h3>Debate agent</h3>
              <p className="muted landing-feature-text">
                Compare two PDFs with structured rounds and a neutral verdict.
              </p>
              <Link to="/debate" className="landing-feature-link">
                Open debate <span aria-hidden>→</span>
              </Link>
            </li>
            <li className="landing-feature-card">
              <div className="landing-feature-icon-wrap" aria-hidden>
                <Map size={22} strokeWidth={1.75} />
              </div>
              <h3>Roadmap agent</h3>
              <p className="muted landing-feature-text">
                Turn papers into a grounded learning path for any topic you choose.
              </p>
              <Link to="/roadmap" className="landing-feature-link">
                Build roadmap <span aria-hidden>→</span>
              </Link>
            </li>
            <li className="landing-feature-card">
              <div className="landing-feature-icon-wrap" aria-hidden>
                <Mic size={22} strokeWidth={1.75} />
              </div>
              <h3>Podcast agent</h3>
              <p className="muted landing-feature-text">Generate a short audio episode from a single research PDF.</p>
              <Link to="/podcast" className="landing-feature-link">
                Create podcast <span aria-hidden>→</span>
              </Link>
            </li>
            <li className="landing-feature-card">
              <div className="landing-feature-icon-wrap" aria-hidden>
                <FileText size={22} strokeWidth={1.75} />
              </div>
              <h3>Reports</h3>
              <p className="muted landing-feature-text">Reopen saved runs on this device and download PDFs.</p>
              <Link to="/reports" className="landing-feature-link">
                Browse reports <span aria-hidden>→</span>
              </Link>
            </li>
          </ul>
          </MotionReveal>
        </section>

        <section className="landing-cta-band" aria-labelledby="landing-cta-heading">
          <MotionReveal>
          <div className="landing-cta-inner">
            <h2 id="landing-cta-heading" className="landing-cta-title">
              Ready for your next topic?
            </h2>
            <p className="landing-cta-lead muted">Open the workspace, enter a few words, and let the run begin.</p>
            <Link to="/workspace" className="primary landing-cta-btn">
              Open workspace
              <ArrowRight size={18} aria-hidden />
            </Link>
          </div>
          </MotionReveal>
        </section>
      </main>

      <footer className="landing-footer">
        <MotionReveal>
        <div className="landing-footer-grid">
          <div className="landing-footer-col">
            <p className="landing-footer-heading">Product</p>
            <ul className="landing-footer-links">
              <li>
                <Link to="/workspace">Workspace</Link>
              </li>
              <li>
                <a href="#how-it-works">How it works</a>
              </li>
              <li>
                <a href="#features">Features</a>
              </li>
              <li>
                <Link to="/reports">Reports</Link>
              </li>
            </ul>
          </div>
          <div className="landing-footer-col">
            <p className="landing-footer-heading">Agents</p>
            <ul className="landing-footer-links">
              <li>
                <Link to="/debate">Debate</Link>
              </li>
              <li>
                <Link to="/roadmap">Roadmap</Link>
              </li>
              <li>
                <Link to="/podcast">Podcast</Link>
              </li>
            </ul>
          </div>
          <div className="landing-footer-col">
            <p className="landing-footer-heading">Resources</p>
            <ul className="landing-footer-links">
              <li>
                <Link to="/settings">Settings &amp; API bases</Link>
              </li>
            </ul>
          </div>
        </div>
        <p className="landing-footer-copy muted">Mantis — research intelligence in your browser.</p>
        </MotionReveal>
      </footer>
    </div>
  );
}
