# DLQ Drain Runbook

## Symptoms
- Dead-letter queue (DLQ) size >0.1% of total workflows (SLO violation).
- Failed workflows accumulating in DLQ (e.g., Kafka topic or SQS queue).
- Alerts: DLQ depth increasing, workflow success rate <99%.

## Immediate Actions (P1)
1. **Acknowledge Alert**: Confirm in monitoring tool (Grafana/OTEL dashboard).
2. **Isolate DLQ**: Pause new failures from entering DLQ to prevent overflow.
   - Command: Temporarily disable auto-DLQ routing in orchestrator config.
3. **Inspect DLQ Entries**: Sample first 10-50 entries.
   - For Kafka: `kafka-console-consumer --bootstrap-server localhost:9092 --topic dlq --from-beginning --max-messages 50`
   - For SQS: Use AWS CLI `aws sqs receive-message --queue-url https://sqs.us-east-1.amazonaws.com/...`
4. **Categorize Failures**: Group by error type (e.g., plugin timeout, memory quota exceeded, network error).
   - Use tracing correlation IDs to trace back to root cause.

## Root Cause Analysis
- Query OTEL traces for failing spans (e.g., tool_call with error).
- Check metrics: High error rates in specific agents/tools.
- Review logs: Search for "DLQ" or error patterns in orchestrator logs.
- Common causes: Third-party plugin failures, quota exhaustion, transient API errors.

## Resolution Steps
1. **Retry Non-Permanent Failures**: For transient errors (e.g., network 5xx), retry in batches of 100.
   - Use idempotency from `core/workflow_safety.py` (dedupe keys) to avoid duplicates.
   - Script example:
     ```
     for msg in dlq_batch:
         if msg.error_type in ['TransientNetwork', 'RateLimit']:
             replay_workflow(msg.correlation_id, overrides={'retry_count': msg.retry_count + 1})
     ```
2. **Fix Permanent Errors**: For quota/memory issues, increase limits or fix code.
   - Update quotas via `core/rate_limiter.py`.
   - Patch plugins if scope violations.
3. **Manual Review**: For unique cases (e.g., data corruption), manual replay with debugger.
   - Use workflow debugger to override inputs/outputs.
4. **Drain DLQ**: Process remaining entries, monitor success rate >95%.
   - Target: DLQ size = 0 within 1 hour.
5. **Verify**: Run e2e test on golden flows post-drain.

## Prevention
- Implement circuit breakers for flaky tools/plugins (`core/plugin_sandbox.py`).
- Add exponential backoff/retry logic in orchestrator.
- Monitor DLQ depth proactively; alert at 0.05%.
- Regular chaos testing for failure injection.

## Escalation
- If DLQ >1% after 30min, escalate to engineering lead.
- Data loss risk: If >10k entries, invoke DR plan for backup restore.

Success Criteria: DLQ = 0, success rate ≥99%, no recurrence in 24h.
Estimated Time: 30-60 minutes.