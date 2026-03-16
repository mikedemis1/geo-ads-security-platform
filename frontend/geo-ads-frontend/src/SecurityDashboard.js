// frontend/geo-ads-frontend/src/SecurityDashboard.js
import { useState, useEffect, useRef, useCallback } from "react";
import "./SecurityDashboard.css";

const API = "http://localhost:8000";
const WS_URL = "ws://localhost:8000";

function SecurityDashboard({ token, onLogout }) {
  const [alerts, setAlerts] = useState([]);
  const [events, setEvents] = useState([]);
  const [stats, setStats] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [wsStatus, setWsStatus] = useState("disconnected");
  const wsRef = useRef(null);
  const refreshTimer = useRef(null);

  // ── Fetch REST data ────────────────────────────────
  const fetchData = useCallback(async () => {
    const headers = { Authorization: `Bearer ${token}` };
    try {
      const [alertsRes, eventsRes, statsRes, compRes] = await Promise.all([
        fetch(`${API}/security/alerts`, { headers }),
        fetch(`${API}/security/events?limit=200`, { headers }),
        fetch(`${API}/security/stats`, { headers }),
        fetch(`${API}/security/comparison`, { headers }),
      ]);
      // If any response is 401, token is invalid → force logout
      if ([alertsRes, eventsRes, statsRes, compRes].some((r) => r.status === 401)) {
        if (onLogout) onLogout();
        return;
      }
      if (alertsRes.ok) setAlerts(await alertsRes.json());
      if (eventsRes.ok) setEvents(await eventsRes.json());
      if (statsRes.ok) setStats(await statsRes.json());
      if (compRes.ok) setComparison(await compRes.json());
    } catch (err) {
      console.error("[SecurityDashboard] fetch error:", err);
    }
  }, [token, onLogout]);

  // ── WebSocket for real-time alerts ─────────────────
  useEffect(() => {
    const ws = new WebSocket(`${WS_URL}/ws/security?token=${token}`);
    wsRef.current = ws;

    ws.onopen = () => setWsStatus("connected");
    ws.onclose = () => setWsStatus("disconnected");
    ws.onerror = () => setWsStatus("error");

    ws.onmessage = (msg) => {
      try {
        const data = JSON.parse(msg.data);
        if (data.type === "security_snapshot") {
          setAlerts(data.data || []);
        } else if (data.type === "security_alert") {
          setAlerts((prev) => [...prev, data.data]);
          // Auto-refresh stats on new alert
          fetchData();
        }
      } catch (e) {
        console.error("[WS] parse error:", e);
      }
    };

    return () => ws.close();
  }, [token, fetchData]);

  // ── Periodic refresh ───────────────────────────────
  useEffect(() => {
    fetchData();
    refreshTimer.current = setInterval(fetchData, 5000);
    return () => clearInterval(refreshTimer.current);
  }, [fetchData]);

  // ── Time helpers ───────────────────────────────────
  const fmtTime = (ts) => {
    if (!ts) return "--";
    const d = new Date(ts * 1000);
    return d.toLocaleTimeString("el-GR", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  };

  const fmtAgo = (ts) => {
    if (!ts) return "";
    const sec = Math.floor(Date.now() / 1000 - ts);
    if (sec < 60) return `${sec}s ago`;
    if (sec < 3600) return `${Math.floor(sec / 60)}m ago`;
    return `${Math.floor(sec / 3600)}h ago`;
  };

  // ── Build timeline buckets (5-min windows) ─────────
  const buildTimeline = () => {
    if (!events.length) return [];
    const now = Math.floor(Date.now() / 1000);
    const buckets = [];
    for (let i = 11; i >= 0; i--) {
      const start = now - (i + 1) * 300;
      const end = now - i * 300;
      const count = events.filter((e) => e.timestamp >= start && e.timestamp < end).length;
      const label = new Date(end * 1000).toLocaleTimeString("el-GR", { hour: "2-digit", minute: "2-digit" });
      buckets.push({ label, count, start, end });
    }
    return buckets;
  };

  const timeline = buildTimeline();
  const maxBucket = Math.max(1, ...timeline.map((b) => b.count));

  // ── Severity helpers ───────────────────────────────
  const severityClass = (sev) => {
    if (sev === "critical") return "sev-critical";
    if (sev === "warning") return "sev-warning";
    return "sev-info";
  };

  const eventIcon = (type) => {
    const icons = {
      auth_failed: "\u26D4",
      auth_success: "\u2705",
      rate_limited: "\u26A0",
      replay_detected: "\uD83D\uDD04",
      hmac_failed: "\uD83D\uDD12",
      ws_auth_failed: "\uD83D\uDEAB",
    };
    return icons[type] || "\u2022";
  };

  return (
    <div className="sec-dashboard">
      {/* ── Header ──────────────────────────────── */}
      <div className="sec-header">
        <div className="sec-header-left">
          <span className="sec-header-icon">SHIELD</span>
          <div>
            <h1 className="sec-title">THREAT DETECTION</h1>
            <span className="sec-subtitle">Anomaly Monitor &middot; Hybrid Analysis</span>
          </div>
        </div>
        <div className="sec-header-right">
          <div className={`sec-ws-badge ws-${wsStatus}`}>
            <span className="sec-ws-dot" />
            <span className="sec-ws-label">{wsStatus === "connected" ? "LIVE" : wsStatus.toUpperCase()}</span>
          </div>
          <button className="sec-refresh-btn" onClick={fetchData}>REFRESH</button>
        </div>
      </div>

      {/* ── Grid Layout ─────────────────────────── */}
      <div className="sec-grid">

        {/* Panel 1: Active Alerts */}
        <div className="sec-panel sec-panel-alerts">
          <div className="sec-panel-header">
            <span className="sec-panel-dot sev-critical" />
            ACTIVE ALERTS
            <span className="sec-panel-count">{alerts.filter((a) => a.active).length}</span>
          </div>
          <div className="sec-alert-list">
            {alerts.length === 0 && (
              <div className="sec-empty">No alerts &mdash; system nominal</div>
            )}
            {[...alerts].reverse().slice(0, 50).map((alert, i) => (
              <div key={alert.alert_id || i} className={`sec-alert-item ${severityClass(alert.severity)}`}>
                <div className="sec-alert-top">
                  <span className={`sec-sev-badge ${severityClass(alert.severity)}`}>
                    {alert.severity?.toUpperCase()}
                  </span>
                  <span className="sec-alert-type">{alert.alert_type}</span>
                  <span className="sec-alert-time">{fmtAgo(alert.timestamp)}</span>
                </div>
                <div className="sec-alert-msg">{alert.message}</div>
                <div className="sec-alert-meta">
                  <span>IP: {alert.source_ip}</span>
                  <span>Detector: {alert.detected_by}</span>
                  <span>{alert.detection_time_ms?.toFixed(3)} ms</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Panel 2: Event Timeline */}
        <div className="sec-panel sec-panel-timeline">
          <div className="sec-panel-header">
            EVENT TIMELINE
            <span className="sec-panel-count">{stats?.total_events || 0} total</span>
          </div>
          <div className="sec-timeline">
            {timeline.map((bucket, i) => (
              <div key={i} className="sec-tl-col">
                <div className="sec-tl-bar-wrap">
                  <div
                    className="sec-tl-bar"
                    style={{ height: `${(bucket.count / maxBucket) * 100}%` }}
                    title={`${bucket.count} events`}
                  >
                    {bucket.count > 0 && <span className="sec-tl-count">{bucket.count}</span>}
                  </div>
                </div>
                <span className="sec-tl-label">{bucket.label}</span>
              </div>
            ))}
          </div>

          {/* Event type breakdown */}
          {stats && (
            <div className="sec-type-grid">
              {Object.entries(stats.event_counts || {}).map(([type, count]) => (
                <div key={type} className="sec-type-chip">
                  <span className="sec-type-icon">{eventIcon(type)}</span>
                  <span className="sec-type-name">{type}</span>
                  <span className="sec-type-count">{count}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Panel 3: Detection Comparison */}
        <div className="sec-panel sec-panel-comparison">
          <div className="sec-panel-header">
            DETECTION COMPARISON
            <span className="sec-panel-sub">Rule-Based vs Statistical</span>
          </div>
          {comparison ? (
            <div className="sec-comp-body">
              <table className="sec-comp-table">
                <thead>
                  <tr>
                    <th>Metric</th>
                    <th>Rule-Based</th>
                    <th>Statistical</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Detections</td>
                    <td className="sec-val-rule">{comparison.rule_total_detections}</td>
                    <td className="sec-val-stat">{comparison.statistical_total_detections}</td>
                  </tr>
                  <tr>
                    <td>Exclusive</td>
                    <td className="sec-val-rule">{comparison.rule_only_detections}</td>
                    <td className="sec-val-stat">{comparison.statistical_only_detections}</td>
                  </tr>
                  <tr>
                    <td>Avg Response</td>
                    <td className="sec-val-rule">{comparison.rule_avg_detection_ms?.toFixed(4)} ms</td>
                    <td className="sec-val-stat">{comparison.statistical_avg_detection_ms?.toFixed(4)} ms</td>
                  </tr>
                  <tr>
                    <td>Both Detected</td>
                    <td colSpan={2} className="sec-val-both">{comparison.both_detected}</td>
                  </tr>
                  <tr>
                    <td>Undetected</td>
                    <td colSpan={2} className="sec-val-neither">{comparison.neither_detected}</td>
                  </tr>
                </tbody>
              </table>

              <div className="sec-comp-bars">
                <div className="sec-comp-bar-row">
                  <span className="sec-comp-label">Rule</span>
                  <div className="sec-comp-bar-wrap">
                    <div
                      className="sec-comp-bar bar-rule"
                      style={{
                        width: `${
                          comparison.total_events_analyzed > 0
                            ? ((comparison.rule_total_detections / Math.max(1, comparison.total_events_analyzed)) * 100)
                            : 0
                        }%`,
                      }}
                    />
                  </div>
                  <span className="sec-comp-pct">
                    {comparison.total_events_analyzed > 0
                      ? ((comparison.rule_total_detections / comparison.total_events_analyzed) * 100).toFixed(1)
                      : 0}%
                  </span>
                </div>
                <div className="sec-comp-bar-row">
                  <span className="sec-comp-label">Stat</span>
                  <div className="sec-comp-bar-wrap">
                    <div
                      className="sec-comp-bar bar-stat"
                      style={{
                        width: `${
                          comparison.total_events_analyzed > 0
                            ? ((comparison.statistical_total_detections / Math.max(1, comparison.total_events_analyzed)) * 100)
                            : 0
                        }%`,
                      }}
                    />
                  </div>
                  <span className="sec-comp-pct">
                    {comparison.total_events_analyzed > 0
                      ? ((comparison.statistical_total_detections / comparison.total_events_analyzed) * 100).toFixed(1)
                      : 0}%
                  </span>
                </div>
              </div>

              <div className="sec-comp-total">
                {comparison.total_events_analyzed} events analyzed
              </div>
            </div>
          ) : (
            <div className="sec-empty">Loading comparison data...</div>
          )}
        </div>

        {/* Panel 4: Event Log */}
        <div className="sec-panel sec-panel-log">
          <div className="sec-panel-header">
            EVENT LOG
            <span className="sec-panel-count">{events.length} recent</span>
          </div>
          <div className="sec-event-log">
            {events.length === 0 && (
              <div className="sec-empty">No events recorded yet</div>
            )}
            {[...events].reverse().slice(0, 100).map((evt, i) => (
              <div key={i} className={`sec-log-row ${evt.detected_by ? "sec-log-detected" : ""}`}>
                <span className="sec-log-icon">{eventIcon(evt.event_type)}</span>
                <span className="sec-log-type">{evt.event_type}</span>
                <span className="sec-log-ip">{evt.source_ip}</span>
                <span className="sec-log-time">{fmtTime(evt.timestamp)}</span>
                {evt.detected_by && (
                  <span className={`sec-log-badge badge-${evt.detected_by}`}>
                    {evt.detected_by}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default SecurityDashboard;
