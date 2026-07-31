"""Predictive maintenance — turns a raw telemetry event window into a
plain-language fleet-health signal.

The one pattern implemented here mirrors the manual's own documented lead
indicator (Section 8.2 / SB-2024-011): rising frequency of ALM-1104/1105
positioning-deviation alarms precedes a ball screw failure by ~150-250
operating hours. This is intentionally simple and literal — the goal is a
signal you can defend in front of a customer ("here's exactly why we're
flagging this machine"), not a black-box anomaly score.
"""
from collections import Counter
from .plc_listener import TelemetryEvent

BALL_SCREW_WEAR_CODES = {"ALM-1104", "ALM-1105"}
WEAR_ALERT_THRESHOLD = 3  # occurrences within the window that trigger a flag


def analyze_window(events: list[TelemetryEvent]) -> dict:
    alarm_events = [e for e in events if e.event_type == "alarm" and e.code]
    code_counts = Counter(e.code for e in alarm_events)

    wear_signal_count = sum(count for code, count in code_counts.items() if code in BALL_SCREW_WEAR_CODES)

    flags = []
    if wear_signal_count >= WEAR_ALERT_THRESHOLD:
        flags.append({
            "signal": "ball_screw_wear_risk",
            "evidence": f"{wear_signal_count} positioning-deviation alarms (ALM-1104/1105) in this window",
            "reference": "apex3200_manual.md Section 8.2 / SB-2024-011",
            "recommendation": "Schedule a ball screw inspection before the next production run.",
        })

    avg_temp = sum(e.bearing_temp_c for e in events) / len(events) if events else 0
    if avg_temp > 78:
        flags.append({
            "signal": "elevated_bearing_temperature",
            "evidence": f"average bearing temp {avg_temp:.1f}C over window (alarm threshold 85C)",
            "reference": "apex3200_manual.md Section 3.2 (ALM-4022)",
            "recommendation": "Check coolant jacket flow before temperature reaches the ALM-4022 threshold.",
        })

    return {
        "window_size": len(events),
        "alarm_counts": dict(code_counts),
        "flags": flags,
    }
