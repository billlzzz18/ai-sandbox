# Memory Rebuild Runbook

## Symptoms
- Memory index corruption (e.g., read failures, inconsistent data).
- High memory miss rate (<80%, per SLO).
- Errors in logs: "memory corrupt", decryption failures.
- Alerts: memory.hit.rate low, access log anomalies.

## Immediate Actions (P1)
1. **Isolate Namespace**: Quarantine affected namespaces to prevent further corruption.
   - Command: Set TTL to 1s for affected namespace in `core/memory.py`.
2. **Backup Current State**: Snapshot memory store before rebuild.
   - Script: `memory.get_access_logs(namespace='affected') > backup.json`.
3. **Failover**: Switch to secondary memory store if available (DR setup).

## Root Cause Analysis
- Check access logs (`core/memory.py`): Look for bulk writes or key rotation issues.
- OTEL traces: Spans with "memory_operation" errors (decryption, TTL expiry).
- Common causes: Key rotation mid-operation, concurrent writes without locks, storage failure.

## Resolution Steps
1. **Soft Rebuild**: Expire TTL for corrupted entries (soft delete).
   - Use `memory.delete(namespace, key, soft=True)` for affected keys.
2. **Hard Rebuild**: Clear namespace and restore from backup.
   - Script:
     ```
     for key in memory.list_keys(namespace):
         memory.delete(namespace, key, soft=False)
     for entry in backup:
         memory.write(namespace, entry['key'], entry['data'], reason="rebuild")
     ```
3. **Key Rotation**: If encryption issue, rotate keys (`memory.rotate_keys()`).
4. **Validate**: Run evaluation benchmark (`memory.evaluate_benchmark(namespace)`); ensure hit rate >80%.
5. **Monitor**: Watch for 15min; check logs for new errors.

## Prevention
- Add write locks for concurrent access.
- Automated backups every 15m (RPO).
- Integrity checks on read (hash verification).
- Test key rotation in staging.

## Escalation
- If >10% data loss, invoke DR plan (dr_plan.md).
- Business impact: Lost context in workflows; notify if persistent memory affected.

Success Criteria: Hit rate ≥80%, no corruption errors, benchmark accuracy +30%.
Estimated Time: 30-60 minutes.