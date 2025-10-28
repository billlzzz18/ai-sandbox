# Disaster Recovery Plan

## Overview
DR plan for AI Agent Framework. Targets: RPO (Recovery Point Objective) 15min (max data loss), RTO (Recovery Time Objective) 60min (downtime).

## Scope
- Primary site failure (e.g., AWS region outage).
- Data: Memory store, workflow journal, outbox.
- Services: Orchestrator, agents, plugins, queues.

## Components
- **Backup Strategy**: Automated snapshots every 15min.
  - Memory: `core/memory.py` export to S3 (encrypted).
  - Journal/Outbox: Append-only logs to durable storage (Kafka/S3).
  - Config/Schemas: Git repo sync.
- **Secondary Site**: Multi-region setup (e.g., AWS us-east-1 primary, us-west-2 secondary).
- **Failover**: DNS switch + service restart.

## Activation Triggers
- Primary site unavailable >5min.
- Data loss >10% (e.g., memory corruption affecting workflows).
- Manual: SRE approval.

## Recovery Steps
1. **Detection (0-5min)**: Alerts from Grafana (site down, RPO breach).
2. **Assessment (5-10min)**: Verify failure scope (e.g., `ping primary-endpoint` fails).
3. **Failover (10-30min)**:
   - Switch traffic: Update Route53 DNS to secondary (TTL 60s).
   - Restore Data: Replay last 15min backups.
     - Memory: `memory.write` from S3 snapshot.
     - Journal: Replay from `core/workflow_safety.py` outbox.
     - Queues: Re-ingest DLQ to secondary.
   - Start Services: `kubectl apply -f secondary-k8s-manifests`.
4. **Validation (30-50min)**: Run e2e golden flows; check SLOs (success ≥99%).
5. **Post-Failover (50-60min)**: Notify stakeholders, monitor for 1h.
6. **Failback**: Once primary recovered, sync data, switch back (plan 2h window).

## Testing
- Quarterly DR drill: Simulate region failure, measure RTO/RPO.
- Chaos: Inject failures with Chaos Mesh.

## Roles
- SRE: Execute failover.
- On-call: Initial assessment.
- Engineering: Post-mortem.

## Risks & Mitigations
- Data Sync Lag: Use eventual consistency; idempotency ensures no duplicates.
- Secondary Capacity: Pre-scale secondary to 120% primary load.
- Cost: ~2x normal during failover.

Success Criteria: Services up in <60min, data loss <15min, SLOs met post-recovery.
Contact: SRE @ #incidents Slack.