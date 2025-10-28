# Queue Saturation Runbook

## Symptoms
- Queue depth exceeds threshold (e.g., >1000 messages, per SLO queue_depth_max).
- p95 end-to-end latency >2s.
- Workflow backpressure: New submissions queued or rejected.
- Alerts: queue.depth high, wait.time.p95 spiking, success rate dropping <99%.

## Immediate Actions (P0)
1. **Acknowledge Alert**: Confirm in Grafana dashboard or OTEL collector.
2. **Scale Resources**: Increase agent replicas to handle load.
   - Command: `kubectl scale deployment agents --replicas=20` (adjust based on CPU).
3. **Throttle Ingress**: Reduce RPS at gateway using `core/rate_limiter.py`.
   - Set temporary quota: `limiter.set_quota('global', Quota(rps=50))`.
4. **Check Dependencies**: Verify downstream services (memory, plugins) not bottlenecked.
   - Metrics: memory.hit.rate <80%, plugin sandbox timeouts.

## Root Cause Analysis
- Use OTEL traces (`core/tracing.py`) to identify slow spans (e.g., tool_call >5s).
- Flame graphs in Grafana for hot paths (Orchestrator→Agent).
- Logs: Search for "backpressure" or "queue full" in orchestrator.
- Common causes: High concurrent workflows, slow plugins, memory index corruption.

## Resolution Steps
1. **Relieve Pressure**: Pause non-critical workflows; prioritize via queue priority.
   - Use workflow safety (`core/workflow_safety.py`) for idempotent pause/resume.
2. **Optimize Bottlenecks**: If plugins slow, disable third-party (see safe_mode.md).
3. **Partition Queues**: If single queue, split by workflow type (e.g., short/long-running).
4. **Drain Excess**: Process backlog with increased workers; monitor DLQ (see dlq_drain.md).
5. **Post-Mortem**: Analyze metrics for saturation point; update auto-scale rules.

## Prevention
- Implement backpressure signals from agents to orchestrator.
- Auto-scale based on queue depth + CPU (target p95 <1.5s).
- Capacity planning: Load test with 2x expected concurrent workflows.
- Regular maintenance: Clean expired memory entries (`core/memory.py` TTL).

## Escalation
- If depth >2000 after 10min scaling, page SRE lead.
- Business impact: Delayed workflows; notify stakeholders if >1h.

Success Criteria: Queue depth <500, p95 <1s, success rate ≥99%.
Estimated Time: 20-45 minutes.