"""The hybrid detector: threshold rules and the Z-score anomaly detector."""

import time

from app.security.threat_engine import (
    RuleBasedDetector,
    SecurityEvent,
    StatisticalDetector,
    ThreatEngine,
)


def _events(event_type, ip, count, usernames=None, age_seconds=0):
    now = time.time() - age_seconds
    return [
        SecurityEvent(
            event_type=event_type,
            source_ip=ip,
            timestamp=now,
            details={"username": usernames[i] if usernames else "admin"},
        )
        for i in range(count)
    ]


# Rule-based detector


def _rule_alerts(engine):
    return [a for a in engine.get_alerts() if a["detected_by"] == "rule"]


def test_four_failed_logins_from_one_ip_do_not_trigger_a_rule():
    engine = ThreatEngine()
    for _ in range(4):
        engine.record_event("auth_failed", "10.0.0.1", {"username": "admin"})
    assert _rule_alerts(engine) == []


def test_five_failed_logins_from_one_ip_raise_a_brute_force_alert():
    engine = ThreatEngine()
    for _ in range(5):
        engine.record_event("auth_failed", "10.0.0.1", {"username": "admin"})
    alerts = _rule_alerts(engine)
    assert any(a["alert_type"] == "brute_force" and a["severity"] == "critical" for a in alerts)


def test_failed_logins_from_different_ips_are_not_pooled_by_the_rules():
    engine = ThreatEngine()
    for i in range(5):
        engine.record_event("auth_failed", f"10.0.0.{i}", {"username": "admin"})
    assert _rule_alerts(engine) == []


def test_ten_distinct_usernames_from_one_ip_raise_credential_stuffing():
    """Ten different usernames from one address is stuffing, not brute force.

    Both rules watch the same event type, so the first one listed wins. This
    is the case the order was changed for: before the change this same input
    was reported as brute force.
    """
    detector = RuleBasedDetector()
    usernames = [f"user{i}" for i in range(10)]
    events = _events("auth_failed", "10.0.0.1", 10, usernames=usernames)
    alert = detector.check(events, events[-1])
    assert alert is not None
    assert alert.alert_type == "credential_stuffing"
    assert alert.event_count == 10


def test_ten_attempts_on_one_username_are_brute_force_not_stuffing():
    detector = RuleBasedDetector()
    events = _events("auth_failed", "10.0.0.1", 10)
    alert = detector.check(events, events[-1])
    assert alert is not None
    assert alert.alert_type == "brute_force"


def test_events_outside_the_rule_window_do_not_count():
    detector = RuleBasedDetector()
    old = _events("auth_failed", "10.0.0.1", 4, age_seconds=600)  # older than the 300s window
    fresh = _events("auth_failed", "10.0.0.1", 1)
    assert detector.check(old + fresh, fresh[-1]) is None


def test_three_replays_from_one_ip_raise_a_replay_alert():
    engine = ThreatEngine()
    for _ in range(3):
        engine.record_event("replay_detected", "10.0.0.1")
    assert any(a["alert_type"] == "replay_attack" for a in engine.get_alerts())


# Statistical detector


def _detector_with_baseline(rates, event_type="auth_failed"):
    detector = StatisticalDetector()
    detector._rate_history[(event_type, "5min")].extend(rates)
    # A baseline refresh would otherwise fold the spike into the history
    # before the comparison. Pin the last refresh to now.
    detector._last_baseline_update = time.time()
    return detector


def test_spike_above_a_varied_baseline_raises_an_anomaly():
    detector = _detector_with_baseline([1, 2, 1, 2, 1, 2])
    spike = _events("auth_failed", "10.0.0.1", 40)
    alert = detector.check(spike, spike[-1])
    assert alert is not None
    assert alert.alert_type == "anomaly"
    assert alert.detected_by == "statistical"


def test_rate_inside_the_baseline_does_not_alert():
    detector = _detector_with_baseline([1, 2, 1, 2, 1, 2])
    normal = _events("auth_failed", "10.0.0.1", 2)
    assert detector.check(normal, normal[-1]) is None


def test_flat_baseline_never_alerts_because_std_is_zero():
    detector = _detector_with_baseline([3, 3, 3, 3])
    spike = _events("auth_failed", "10.0.0.1", 40)
    assert detector.check(spike, spike[-1]) is None


def test_statistical_detector_alerts_on_cold_start_after_three_events():
    """Documents a known limit, not a desired property.

    A fresh engine has no baseline. The detector seeds one from the first
    events it sees, all within the same burst, so by the third suspicious
    event the "history" is [1, 1, 2] and a rate of 3 is already more than
    two standard deviations above it. In other words the statistical path
    raises an anomaly on the third failed login after startup, regardless of
    the source. This is the false-positive cost the thesis compared against
    the rule-based path; it is left as is and stated in THREAT_MODEL.md.
    """
    engine = ThreatEngine()
    for i in range(3):
        engine.record_event("auth_failed", f"10.0.0.{i}", {"username": "admin"})
    statistical = [a for a in engine.get_alerts() if a["detected_by"] == "statistical"]
    assert len(statistical) == 1
    assert statistical[0]["alert_type"] == "anomaly"


def test_benign_event_types_are_ignored_by_the_statistical_detector():
    detector = _detector_with_baseline([1, 2, 1, 2], event_type="auth_success")
    burst = _events("auth_success", "10.0.0.1", 40)
    assert detector.check(burst, burst[-1]) is None


# Engine bookkeeping


def test_comparison_counts_rule_and_statistical_detections_separately():
    engine = ThreatEngine()
    for _ in range(5):
        engine.record_event("auth_failed", "10.0.0.1", {"username": "admin"})
    comparison = engine.get_comparison()
    assert comparison["rule_total_detections"] >= 1
    assert comparison["total_events_analyzed"] == 5
    assert comparison["rule_only_detections"] + comparison["both_detected"] >= 1


def test_events_older_than_the_ttl_are_evicted():
    engine = ThreatEngine()
    stale = SecurityEvent("auth_failed", "10.0.0.1", time.time() - 7200)
    engine._events.append(stale)
    engine.record_event("auth_success", "10.0.0.2")
    assert all(e["timestamp"] > time.time() - ThreatEngine.EVENT_TTL for e in engine.get_events())


def test_stats_count_events_by_type():
    engine = ThreatEngine()
    engine.record_event("auth_failed", "10.0.0.1")
    engine.record_event("auth_failed", "10.0.0.1")
    engine.record_event("hmac_failed", "10.0.0.1")
    stats = engine.get_stats()
    assert stats["event_counts"] == {"auth_failed": 2, "hmac_failed": 1}
    assert stats["total_events"] == 3


def test_a_slow_stuffing_run_was_classified_correctly_even_before_the_reorder():
    """Bounds the claim made about the rule-order bug.

    An independent review on 2026-09-11 asked for proof of the original
    wording, "credential stuffing could never fire". The wording was wrong.
    The two rules have different windows — five minutes for brute force, ten
    for stuffing — so an attacker whose recent rate had fallen below five
    still reached the stuffing rule under the old order. Six attempts, then a
    pause, then four more, is that shape: ten distinct usernames inside the
    ten-minute window, only four inside the trailing five.

    What the old order actually broke is the common case, which the test above
    covers. This one records why "never" was too strong.
    """
    now = time.time()
    offsets = [599, 598, 597, 596, 595, 594, 3, 2, 1, 0]
    events = [
        SecurityEvent("auth_failed", "10.0.0.1", now - o, {"username": f"u{i}"})
        for i, o in enumerate(offsets)
    ]

    detector = RuleBasedDetector()
    assert detector.check(events, events[-1]).alert_type == "credential_stuffing"

    original_order = RuleBasedDetector()
    original_order.RULES = {
        "brute_force": RuleBasedDetector.RULES["brute_force"],
        "credential_stuffing": RuleBasedDetector.RULES["credential_stuffing"],
    }
    assert original_order.check(events, events[-1]).alert_type == "credential_stuffing"
