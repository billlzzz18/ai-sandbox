# Safe Mode Runbook

## Activation (One-Click)
Safe mode disables third-party plugins, runs only first-party tools, and reduces quotas to prevent cascading failures.

## Symptoms Triggering Safe Mode
- Success rate <95% for 5min.
- Multiple runbooks active (e.g., queue saturation + agent crash).
- Manual trigger via UI or API.

## Activation Steps
1. **API Call**: POST to /safe-mode with {"enabled": true, "reason": "manual"}.
   - This sets config flag `third_party_plugins: false`, reduces quotas to 50% via `core/rate_limiter.py`.
2. **Config Update**: Edit orchestrator config:
   ```
   feature_flags:
     third_party_plugins: false
     parallel_execution: false  # Disable risky features
   quotas:
     rps: 5  # Reduced
   ```
3. **Restart Services**: Rolling restart of agents/orchestrator.
   - Command: `kubectl rollout restart deployment agents`.
4. **Verify**: Check metrics: Plugin calls = 0 for third-party, success rate rising.

## Deactivation
1. **Monitor Recovery**: Wait for success rate ≥99%, queue depth <500.
2. **API Call**: POST to /safe-mode {"enabled": false}.
3. **Gradual Ramp**: Increase quotas 20% every 5min, monitor.
4. **Post-Mortem**: Log reason and duration in incident report.

## Prevention
- Auto-trigger safe mode on SLO breach (error budget >3%).
- Regular drills: Simulate safe mode activation quarterly.

Success Criteria: System stable, no third-party calls, success rate >99%.
Estimated Time: 5-10 minutes activation, 30min recovery.