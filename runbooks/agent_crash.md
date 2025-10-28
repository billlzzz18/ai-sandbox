# Agent Crash Runbook

## Symptoms
- Agent process crashes or enters crash loop (e.g., Kubernetes restarts >5/min).
- High error rate in orchestrator logs (e.g., "agent stall", "timeout").
- Metrics: agent.cpu.usage spiking then dropping, workflow success rate <99%.
- Alerts: Crash loop detected, CPU/latency anomalies.

## Immediate Actions (P0)
1. **Acknowledge and Isolate**: Acknowledge alert, scale down affected agents to 1 replica to limit blast radius.
   - Command: `kubectl scale deployment affected-agent --replicas=1`.
2. **Check Logs**: Tail logs for the crashing pod.
   - Command: `kubectl logs -f deployment/affected-agent -c agent`.
3. **Resource Check**: Verify CPU/memory limits not exceeded (use `core/plugin_sandbox.py` limits).
   - Metrics: agent.cpu > limit, memory > self.memory_limit_mb.

## Root Cause Analysis
- Trace via OTEL: Look for spans in `core/tracing.py` with exceptions (e.g., plugin sandbox error).
- Common causes: Plugin scope violation, memory corruption, quota exhaustion, third-party dependency failure.
- Use `core/memory.py` access logs to check for corrupt entries.
- Profile: If CPU spike, check for infinite loops in workflow steps.

## Resolution Steps
1. **Restart Clean**: Delete crashing pods to force restart.
   - Command: `kubectl delete pod <pod-name> --force`.
2. **Safe Mode Activation**: Disable third-party plugins via one-click safe mode (see safe_mode.md).
   - Set feature flag `third_party_plugins: false` in config.
3. **Fix Config**: Increase resources if limit hit; update quotas in `core/rate_limiter.py`.
4. **Patch Code**: If bug (e.g., in `core/workflow_safety.py`), hotfix and deploy.
5. **Monitor Recovery**: Watch metrics for 10min; ensure success rate >99%.

## Prevention
- Add health checks in agents (liveness/readiness probes).
- Circuit breakers for plugins (`core/plugin_sandbox.py`).
- Regular chaos testing: Kill agents randomly.
- Auto-scale based on CPU/latency metrics.

## Escalation
- If crashes continue after restart, page SRE.
- Data impact: Check for lost workflows in DLQ (see dlq_drain.md).

Success Criteria: No crashes for 30min, CPU stable <80%, success rate ≥99%.
Estimated Time: 15-30 minutes.