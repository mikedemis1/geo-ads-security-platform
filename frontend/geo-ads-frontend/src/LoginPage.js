import React, { useState } from "react";
import "./LoginPage.css";

const BACKEND_BASE_URL =
  process.env.REACT_APP_BACKEND_BASE_URL || "http://127.0.0.1:8000";

export default function LoginPage({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await fetch(`${BACKEND_BASE_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      if (res.status === 429) {
        setError("Πολλές αποτυχημένες προσπάθειες. Δοκιμάστε ξανά σε 1 λεπτό.");
        return;
      }
      if (!res.ok) {
        setError("Λάθος username ή password.");
        return;
      }
      const data = await res.json();
      onLogin(data.access_token, data.refresh_token);
    } catch {
      setError("Δεν ήταν δυνατή η σύνδεση με τον server.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-root">
      <div className="login-card">
        <div className="login-logo">
          <div className="login-logo-mark">
            <span className="login-logo-letters">GA</span>
          </div>
          <h1 className="login-title">GEO·ADS</h1>
          <p className="login-subtitle">Real-Time Geo-Targeted Ad Platform</p>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          <div className="login-field">
            <label className="login-label">Username</label>
            <input
              className="login-input"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="admin"
              autoFocus
              required
            />
          </div>

          <div className="login-field">
            <label className="login-label">Password</label>
            <input
              className="login-input"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </div>

          {error && <p className="login-error">{error}</p>}

          <button className="login-btn" type="submit" disabled={loading}>
            {loading ? <span className="login-spinner" /> : "Sign In"}
          </button>
        </form>

        <p className="login-footer">
          Stadium Advertising Control System · v2.0
        </p>
      </div>
    </div>
  );
}
