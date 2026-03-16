# backend/app/security/threat_engine.py
"""
Threat Detection & Anomaly Monitor — Hybrid Approach
Rule-based + Statistical (Z-score) detectors running in parallel.

Κάθε event περνάει και από τους δύο detectors για συγκριτική ανάλυση.
Αποδεικνύει: "Ποια μέθοδος ανίχνευσης είναι πιο αποτελεσματική
για real-time αναγνώριση απειλών;"
"""

import time
import math
import threading
from collections import deque, defaultdict
from dataclasses import dataclass, field, asdict
from typing import Optional


# ── Event & Alert Data Classes ─────────────────────────

@dataclass
class SecurityEvent:
    event_type: str          # auth_failed, auth_success, rate_limited, replay_detected, hmac_failed, ws_auth_failed
    source_ip: str
    timestamp: float         # time.time()
    details: dict = field(default_factory=dict)
    detected_by: str = ""    # "rule", "statistical", "both", ""


@dataclass
class SecurityAlert:
    alert_id: str
    severity: str            # critical, warning, info
    alert_type: str          # brute_force, credential_stuffing, replay_attack, rate_abuse, anomaly
    message: str
    source_ip: str
    timestamp: float
    detected_by: str         # "rule" or "statistical"
    detection_time_ms: float  # χρόνος ανίχνευσης σε ms
    event_count: int = 0
    active: bool = True


# ── Rule-Based Detector ───────────────────────────────

class RuleBasedDetector:
    """
    Configurable threshold rules για γνωστά attack patterns.
    Κάθε rule ελέγχει αριθμό events ανά IP σε χρονικό παράθυρο.
    """

    RULES = {
        "brute_force": {
            "event_type": "auth_failed",
            "threshold": 5,
            "window_sec": 300,       # 5 min
            "severity": "critical",
            "message": "Brute force attack detected: {count} failed logins from {ip} in {window}s",
        },
        "credential_stuffing": {
            "event_type": "auth_failed",
            "threshold": 10,
            "window_sec": 600,       # 10 min
            "severity": "critical",
            "message": "Credential stuffing suspected: {count} failed attempts from {ip} in {window}s",
            "unique_usernames": True,  # πρέπει να είναι διαφορετικά usernames
        },
        "replay_attack": {
            "event_type": "replay_detected",
            "threshold": 3,
            "window_sec": 300,
            "severity": "critical",
            "message": "Replay attack detected: {count} replay attempts from {ip} in {window}s",
        },
        "rate_abuse": {
            "event_type": "rate_limited",
            "threshold": 20,
            "window_sec": 600,
            "severity": "warning",
            "message": "Rate limit abuse: {count} rate-limited requests from {ip} in {window}s",
        },
    }

    def check(self, events: list[SecurityEvent], new_event: SecurityEvent) -> Optional[SecurityAlert]:
        """
        Ελέγχει αν το νέο event ενεργοποιεί κάποιο rule.
        Returns SecurityAlert ή None.
        """
        t0 = time.perf_counter()

        for rule_name, rule in self.RULES.items():
            if new_event.event_type != rule["event_type"]:
                continue

            cutoff = time.time() - rule["window_sec"]
            matching = [
                e for e in events
                if e.event_type == rule["event_type"]
                and e.source_ip == new_event.source_ip
                and e.timestamp >= cutoff
            ]

            # Credential stuffing: μετράμε μοναδικά usernames
            if rule.get("unique_usernames"):
                usernames = set()
                for e in matching:
                    un = e.details.get("username", "")
                    if un:
                        usernames.add(un)
                count = len(usernames)
            else:
                count = len(matching)

            if count >= rule["threshold"]:
                detection_ms = (time.perf_counter() - t0) * 1000
                return SecurityAlert(
                    alert_id=f"rule_{rule_name}_{int(time.time())}_{new_event.source_ip}",
                    severity=rule["severity"],
                    alert_type=rule_name,
                    message=rule["message"].format(
                        count=count, ip=new_event.source_ip, window=rule["window_sec"]
                    ),
                    source_ip=new_event.source_ip,
                    timestamp=time.time(),
                    detected_by="rule",
                    detection_time_ms=round(detection_ms, 4),
                    event_count=count,
                )

        return None


# ── Statistical Detector (Z-Score Anomaly) ────────────

class StatisticalDetector:
    """
    Z-score anomaly detection σε sliding windows.
    Alert condition: current_rate > mean + 2σ (configurable threshold).

    Windows: 5min, 15min, 1h
    Baseline: υπολογίζεται από ιστορικά δεδομένα, ανανεώνεται περιοδικά.
    """

    WINDOWS = {
        "5min": 300,
        "15min": 900,
        "1h": 3600,
    }
    Z_THRESHOLD = 2.0  # πόσα σ πάνω από τον μέσο όρο

    def __init__(self):
        # Ιστορικό rates ανά window — χρησιμοποιείται για baseline
        # key = (event_type, window_name), value = deque of rates
        self._rate_history: dict[tuple[str, str], deque] = defaultdict(
            lambda: deque(maxlen=100)
        )
        self._last_baseline_update: float = 0
        self._baseline_interval: float = 60  # ανανέωση baseline κάθε 60s

    def check(self, events: list[SecurityEvent], new_event: SecurityEvent) -> Optional[SecurityAlert]:
        """
        Z-score anomaly detection.
        Μετράει το current rate events ανά window και συγκρίνει με το baseline.
        """
        t0 = time.perf_counter()
        now = time.time()

        # Ελέγχουμε μόνο suspicious event types
        suspicious_types = {"auth_failed", "rate_limited", "replay_detected", "hmac_failed", "ws_auth_failed"}
        if new_event.event_type not in suspicious_types:
            return None

        for window_name, window_sec in self.WINDOWS.items():
            cutoff = now - window_sec
            matching = [
                e for e in events
                if e.event_type == new_event.event_type
                and e.timestamp >= cutoff
            ]
            current_rate = len(matching)

            history_key = (new_event.event_type, window_name)
            history = self._rate_history[history_key]

            # Ανανέωση baseline
            if now - self._last_baseline_update > self._baseline_interval:
                history.append(current_rate)
                self._last_baseline_update = now

            # Χρειάζονται τουλάχιστον 3 data points για στατιστική ανάλυση
            if len(history) < 3:
                history.append(current_rate)
                continue

            # Υπολογισμός Z-score
            mean = sum(history) / len(history)
            variance = sum((x - mean) ** 2 for x in history) / len(history)
            std_dev = math.sqrt(variance) if variance > 0 else 0

            if std_dev == 0:
                continue

            z_score = (current_rate - mean) / std_dev

            if z_score > self.Z_THRESHOLD:
                detection_ms = (time.perf_counter() - t0) * 1000
                return SecurityAlert(
                    alert_id=f"stat_{new_event.event_type}_{window_name}_{int(now)}",
                    severity="warning",
                    alert_type="anomaly",
                    message=(
                        f"Statistical anomaly: {new_event.event_type} rate={current_rate} "
                        f"in {window_name} window (z-score={z_score:.2f}, "
                        f"mean={mean:.1f}, std={std_dev:.1f})"
                    ),
                    source_ip=new_event.source_ip,
                    timestamp=now,
                    detected_by="statistical",
                    detection_time_ms=round(detection_ms, 4),
                    event_count=current_rate,
                )

        return None


# ── ThreatEngine (Core Singleton) ─────────────────────

class ThreatEngine:
    """
    Κεντρικός κινητήρας ανίχνευσης απειλών.
    In-memory event/alert store με TTL-based cleanup.
    Κάθε event περνάει και από τους 2 detectors (rule + statistical)
    για συγκριτική ανάλυση στη διπλωματική.
    """

    EVENT_TTL = 3600  # 1 ώρα
    MAX_EVENTS = 10000
    MAX_ALERTS = 500

    def __init__(self):
        self._events: deque[SecurityEvent] = deque(maxlen=self.MAX_EVENTS)
        self._alerts: list[SecurityAlert] = []
        self._lock = threading.Lock()

        self._rule_detector = RuleBasedDetector()
        self._statistical_detector = StatisticalDetector()

        # Comparative analysis counters
        self._comparison = {
            "rule_only": 0,
            "statistical_only": 0,
            "both": 0,
            "neither": 0,
            "total_events": 0,
            "rule_total_ms": 0.0,
            "statistical_total_ms": 0.0,
            "rule_detections": 0,
            "statistical_detections": 0,
        }

        # WebSocket clients for real-time alerts
        self._ws_clients: set = set()

    def record_event(
        self,
        event_type: str,
        source_ip: str,
        details: dict | None = None,
    ) -> SecurityEvent:
        """
        Καταγράφει ένα security event και το περνάει από τους 2 detectors.
        Thread-safe.
        """
        event = SecurityEvent(
            event_type=event_type,
            source_ip=source_ip,
            timestamp=time.time(),
            details=details or {},
        )

        with self._lock:
            self._events.append(event)
            self._cleanup_old_events()
            self._comparison["total_events"] += 1

            events_list = list(self._events)

        # Run both detectors
        rule_alert = self._rule_detector.check(events_list, event)
        stat_alert = self._statistical_detector.check(events_list, event)

        # Track comparison
        with self._lock:
            if rule_alert:
                self._comparison["rule_total_ms"] += rule_alert.detection_time_ms
                self._comparison["rule_detections"] += 1
            if stat_alert:
                self._comparison["statistical_total_ms"] += stat_alert.detection_time_ms
                self._comparison["statistical_detections"] += 1

            if rule_alert and stat_alert:
                self._comparison["both"] += 1
                event.detected_by = "both"
                # Κρατάμε και τα δύο alerts
                self._add_alert(rule_alert)
                stat_alert.alert_id += "_dup"
                self._add_alert(stat_alert)
            elif rule_alert:
                self._comparison["rule_only"] += 1
                event.detected_by = "rule"
                self._add_alert(rule_alert)
            elif stat_alert:
                self._comparison["statistical_only"] += 1
                event.detected_by = "statistical"
                self._add_alert(stat_alert)
            else:
                self._comparison["neither"] += 1

        return event

    def _add_alert(self, alert: SecurityAlert) -> None:
        """Προσθέτει alert και ενημερώνει WS clients."""
        self._alerts.append(alert)
        if len(self._alerts) > self.MAX_ALERTS:
            self._alerts = self._alerts[-self.MAX_ALERTS:]

        # Async notify WS clients (best effort)
        import asyncio
        alert_data = asdict(alert)
        for ws in list(self._ws_clients):
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.ensure_future(
                        ws.send_json({"type": "security_alert", "data": alert_data})
                    )
            except Exception:
                self._ws_clients.discard(ws)

    def _cleanup_old_events(self) -> None:
        """Αφαιρεί events παλαιότερα από EVENT_TTL."""
        cutoff = time.time() - self.EVENT_TTL
        while self._events and self._events[0].timestamp < cutoff:
            self._events.popleft()

    # ── API methods ────────────────────────────────────

    def get_alerts(self) -> list[dict]:
        with self._lock:
            return [asdict(a) for a in self._alerts[-100:]]

    def get_events(self, event_type: str | None = None, limit: int = 100) -> list[dict]:
        with self._lock:
            events = list(self._events)
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        return [asdict(e) for e in events[-limit:]]

    def get_stats(self) -> dict:
        with self._lock:
            events = list(self._events)

        stats: dict[str, int] = defaultdict(int)
        for e in events:
            stats[e.event_type] += 1

        return {
            "event_counts": dict(stats),
            "total_events": len(events),
            "active_alerts": sum(1 for a in self._alerts if a.active),
            "total_alerts": len(self._alerts),
        }

    def get_comparison(self) -> dict:
        """Επιστρέφει δεδομένα σύγκρισης rule-based vs statistical."""
        with self._lock:
            comp = dict(self._comparison)

        # Υπολογισμός μέσου χρόνου ανίχνευσης
        rule_avg_ms = (
            comp["rule_total_ms"] / comp["rule_detections"]
            if comp["rule_detections"] > 0
            else 0
        )
        stat_avg_ms = (
            comp["statistical_total_ms"] / comp["statistical_detections"]
            if comp["statistical_detections"] > 0
            else 0
        )

        return {
            "rule_only_detections": comp["rule_only"],
            "statistical_only_detections": comp["statistical_only"],
            "both_detected": comp["both"],
            "neither_detected": comp["neither"],
            "total_events_analyzed": comp["total_events"],
            "rule_avg_detection_ms": round(rule_avg_ms, 4),
            "statistical_avg_detection_ms": round(stat_avg_ms, 4),
            "rule_total_detections": comp["rule_detections"],
            "statistical_total_detections": comp["statistical_detections"],
        }

    def register_ws_client(self, ws) -> None:
        self._ws_clients.add(ws)

    def unregister_ws_client(self, ws) -> None:
        self._ws_clients.discard(ws)


# ── Singleton ─────────────────────────────────────────

_ENGINE: ThreatEngine | None = None


def get_threat_engine() -> ThreatEngine:
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = ThreatEngine()
    return _ENGINE
