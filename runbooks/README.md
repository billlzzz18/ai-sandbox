# Runbooks for AI Agent Framework

This directory contains operational runbooks for common failure scenarios, safe-mode activation, and disaster recovery (DR) procedures. Runbooks are designed for quick reference during incidents.

## Available Runbooks

- [queue_saturation.md](queue_saturation.md): Handling queue backlog and backpressure.
- [dlq_drain.md](dlq_drain.md): Draining dead-letter queues.
- [agent_crash.md](agent_crash.md): Recovering from agent crashes or loops.
- [memory_rebuild.md](memory_rebuild.md): Rebuilding corrupted memory indices.
- [safe_mode.md](safe_mode.md): Activating one-click safe mode.
- [dr_plan.md](dr_plan.md): Disaster recovery plan (RPO 15m, RTO 60m).

## Usage

Runbooks are Markdown for readability. For automation, integrate with tools like PagerDuty or custom scripts.

Last updated: 2025-10-28