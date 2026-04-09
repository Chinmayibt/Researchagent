import React, { useEffect, useState } from "react";
import { Link, Outlet, useLocation } from "react-router-dom";
import { Menu, X } from "lucide-react";
import Sidebar from "./Sidebar";
import NavLinkList from "./NavLinkList";

export default function AppShell() {
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    if (!mobileOpen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setMobileOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [mobileOpen]);

  useEffect(() => {
    if (mobileOpen) document.body.style.overflow = "hidden";
    else document.body.style.overflow = "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [mobileOpen]);

  return (
    <div className="app-shell">
      <header className="mobile-app-header">
        <Link to="/" className="mobile-app-brand">
          Mantis
        </Link>
        <button
          type="button"
          className="mobile-nav-toggle"
          onClick={() => setMobileOpen(true)}
          aria-expanded={mobileOpen}
          aria-controls="mobile-nav-drawer"
        >
          <Menu size={22} strokeWidth={2} aria-hidden />
          <span className="sr-only">Open menu</span>
        </button>
      </header>

      {mobileOpen ? (
        <>
          <div
            className="mobile-nav-backdrop"
            aria-hidden
            onClick={() => setMobileOpen(false)}
          />
          <aside
            id="mobile-nav-drawer"
            className="mobile-nav-drawer"
            role="dialog"
            aria-modal="true"
            aria-label="Main menu"
          >
            <div className="mobile-nav-drawer-head">
              <span className="mobile-nav-drawer-title">Navigate</span>
              <button
                type="button"
                className="mobile-nav-drawer-close"
                onClick={() => setMobileOpen(false)}
                aria-label="Close menu"
              >
                <X size={22} aria-hidden />
              </button>
            </div>
            <NavLinkList onNavigate={() => setMobileOpen(false)} />
          </aside>
        </>
      ) : null}

      <Sidebar />
      <div className="app-outlet" key={location.pathname}>
        <Outlet />
      </div>
    </div>
  );
}
