"""Simulated PLC/sensor telemetry stream.

Real deployment: this module subscribes to the machine controller's alarm
bus (OPC-UA / MTConnect / vendor-specific PLC tag stream) and normalizes
events into the same dict shape used here, so `predictive_signals.py` and
the fleet dashboard never need to know the wire protocol.

This scaffold simulates a plausible event stream for a single machine so
the predictive-maintenance layer has something real to run against without
a physical machine attached.
"""
import random
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Iterator

ALARM_POOL = [
    ("ALM-4021", "high"),
    ("ALM-4022", "high"),
    ("ALM-4030", "medium"),
    ("ALM-1104", "medium"),
    ("ALM-1105", "medium"),
]


@dataclass
class TelemetryEvent:
    machine_id: str
    timestamp: str
    event_type: str  # "alarm" | "sensor"
    code: str | None
    severity: str | None
    spindle_load_pct: float
    bearing_temp_c: float


def simulate_stream(machine_id: str, n_events: int, wear_mode: bool = False) -> Iterator[TelemetryEvent]:
    """wear_mode=True skews toward ALM-1104/1105 to simulate a ball screw
    approaching end-of-life, so predictive_signals.py has a real pattern
    to detect in the demo."""
    for _ in range(n_events):
        spindle_load = round(random.uniform(60, 110), 1)
        bearing_temp = round(random.uniform(45, 80), 1)

        emit_alarm = random.random() < (0.35 if wear_mode else 0.12)
        code, severity = (None, None)
        if emit_alarm:
            if wear_mode and random.random() < 0.7:
                code, severity = random.choice([("ALM-1104", "medium"), ("ALM-1105", "medium")])
            else:
                code, severity = random.choice(ALARM_POOL)

        yield TelemetryEvent(
            machine_id=machine_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type="alarm" if code else "sensor",
            code=code,
            severity=severity,
            spindle_load_pct=spindle_load,
            bearing_temp_c=bearing_temp,
        )


def run_live(machine_id: str, poll_seconds: float = 2.0, wear_mode: bool = False):
    """Blocking generator for a real deployment loop — yields one event
    every `poll_seconds`. Not used by the demo dashboard (which calls
    simulate_stream directly for speed) but shows the intended production
    entrypoint."""
    while True:
        event = next(simulate_stream(machine_id, 1, wear_mode=wear_mode))
        yield event
        time.sleep(poll_seconds)


if __name__ == "__main__":
    for e in simulate_stream("M-101", 5):
        print(asdict(e))
