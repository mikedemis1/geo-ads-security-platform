// frontend/geo-ads-frontend/src/App.js
import "./App.css";
import { useState, useEffect, useCallback, useRef } from "react";
import LoginPage from "./LoginPage";
import VisualBoard from "./VisualBoard";
import SecurityDashboard from "./SecurityDashboard";

const TOKEN_KEY = "geo_ads_token";
const REFRESH_KEY = "geo_ads_refresh";
const API = "http://localhost:8000";

function App() {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY));
  const [activeTab, setActiveTab] = useState("stadium");
  const refreshTimerRef = useRef(null);

  // ── Auto-refresh token before expiration ───────────
  const scheduleRefresh = useCallback((accessToken) => {
    if (refreshTimerRef.current) clearTimeout(refreshTimerRef.current);

    try {
      // Decode JWT payload to get exp
      const payload = JSON.parse(atob(accessToken.split(".")[1]));
      const expiresAt = payload.exp * 1000;
      const refreshIn = expiresAt - Date.now() - 120000; // refresh 2min before expiry

      if (refreshIn > 0) {
        refreshTimerRef.current = setTimeout(async () => {
          const refreshToken = localStorage.getItem(REFRESH_KEY);
          if (!refreshToken) return;

          try {
            const res = await fetch(`${API}/auth/refresh`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ refresh_token: refreshToken }),
            });
            if (res.ok) {
              const data = await res.json();
              localStorage.setItem(TOKEN_KEY, data.access_token);
              setToken(data.access_token);
              scheduleRefresh(data.access_token);
            } else {
              // Refresh failed — force logout
              handleLogout();
            }
          } catch {
            // Network error — will retry on next render
          }
        }, refreshIn);
      }
    } catch {
      // Invalid token format
    }
  }, []);

  useEffect(() => {
    if (token) scheduleRefresh(token);
    return () => {
      if (refreshTimerRef.current) clearTimeout(refreshTimerRef.current);
    };
  }, [token, scheduleRefresh]);

  function handleLogin(newToken, refreshToken) {
    localStorage.setItem(TOKEN_KEY, newToken);
    if (refreshToken) localStorage.setItem(REFRESH_KEY, refreshToken);
    setToken(newToken);
  }

  function handleLogout() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
    setToken(null);
    setActiveTab("stadium");
  }

  // ── Token validity check on mount ────────────────
  useEffect(() => {
    if (!token) return;

    // Quick server-side check — try a protected endpoint
    fetch(`${API}/layout`, {
      headers: { Authorization: `Bearer ${token}` },
    }).then((r) => {
      if (r.status === 401) {
        // Token invalid (expired, wrong secret, etc.) — try refresh
        const rt = localStorage.getItem(REFRESH_KEY);
        if (rt) {
          fetch(`${API}/auth/refresh`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ refresh_token: rt }),
          })
            .then((r2) => (r2.ok ? r2.json() : Promise.reject()))
            .then((data) => {
              localStorage.setItem(TOKEN_KEY, data.access_token);
              setToken(data.access_token);
            })
            .catch(() => handleLogout());
        } else {
          handleLogout();
        }
      }
    }).catch(() => {
      // Network error — keep current token, backend might be starting up
    });
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  if (!token) return <LoginPage onLogin={handleLogin} />;

  return (
    <div className="app-root">
      {/* ── Top Bar ──────────────────────────────── */}
      <div className="app-topbar">
        <div className="topbar-brand">
          <div className="topbar-logo-mark">GA</div>
          <span className="topbar-name">GEO-ADS</span>
          <span className="topbar-sep">|</span>
          <span className="topbar-sub">Arena Operations</span>
        </div>

        <div className="topbar-right">
          {/* Tab Switcher */}
          <div className="topbar-tabs">
            <button
              className={`topbar-tab-btn ${activeTab === "stadium" ? "topbar-tab-active" : ""}`}
              onClick={() => setActiveTab("stadium")}
            >
              STADIUM
            </button>
            <button
              className={`topbar-tab-btn ${activeTab === "security" ? "topbar-tab-active" : ""}`}
              onClick={() => setActiveTab("security")}
            >
              SECURITY
            </button>
          </div>

          <button className="logout-btn" onClick={handleLogout}>
            LOGOUT
          </button>
        </div>
      </div>

      {/* ── Content ──────────────────────────────── */}
      {activeTab === "stadium" ? (
        <VisualBoard token={token} onLogout={handleLogout} />
      ) : (
        <SecurityDashboard token={token} onLogout={handleLogout} />
      )}
    </div>
  );
}

export default App;
