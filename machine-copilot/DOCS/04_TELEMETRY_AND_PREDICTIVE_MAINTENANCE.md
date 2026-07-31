# 04 · Telemetry & Predictive Maintenance

This layer doesn't exist in a generic document-RAG system — it's the CNC-
specific piece that turns Machine Copilot from a smart manual into a fleet
health product.

## `app/telemetry/plc_listener.py`
Production: subscribes to the machine controller's alarm bus (OPC-UA /
MTConnect / vendor PLC tags) and normalizes events into a common
`TelemetryEvent` shape. This scaffold ships a simulator (`simulate_stream`)
so the predictive layer has a real pattern to run against without a
physical machine attached — pass `wear_mode=True` to simulate a machine
trending toward ball-screw failure.

## `app/telemetry/predictive_signals.py`
Deliberately simple and literal rather than a black-box anomaly score: the
one pattern implemented mirrors the manual's own documented lead indicator
(Section 8.2 / SB-2024-011) — rising frequency of `ALM-1104`/`ALM-1105`
positioning-deviation alarms precedes a ball screw failure by ~150-250
operating hours. Every flag returned includes the evidence, the source
reference, and a recommendation, so a plant manager can see exactly why a
machine was flagged rather than trusting an opaque score.

## Where this shows up in the business model
This is the **Enterprise tier** surface (`ui/fleet_dashboard.py`): cross-
machine analytics sold to plant managers on an annual contract, not to
individual machinists. The predictive signal itself is also the data
flywheel argument from the business plan — the more fleet data you
accumulate, the sharper these thresholds and patterns get, and that's not
something a competitor can buy off the shelf.
