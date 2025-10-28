# Cookbook: Rollback Patterns

## Overview
Rollback failed workflows using replay journal and idempotency for safe recovery.

## Example
On failure, rollback to last successful step:
```python
from core.workflow_safety import get_workflow_safety

safety = get_workflow_safety("failed_workflow")
is_replay, outputs = safety.execute_step("retry_step", inputs, dedupe_key="hash_inputs")
if is_replay:
    print("Rolled back to previous state")
else:
    # New execution
    pass
```

## Workflow YAML Integration
```yaml
steps:
  - id: critical-step
    type: agent_call
    agent: "processor"
    inputs: { data: "{{ inputs.data }}" }
    outputs: [result]
  - id: rollback-check
    type: conditional
    condition: "{{ outputs.result.status == 'failed' }}"
    true_branch:
      - id: rollback
        type: tool_call
        tools: ["replay_journal"]
        inputs: { workflow_id: "{{ workflow_id }}", from_step: "{{ previous_step_id }}" }
```

## Implementation Notes
- Use append-only journal in `core/workflow_safety.py` for replay.
- Idempotency: Dedupe keys prevent duplicate side effects.
- Safety: Outbox ensures exactly-once delivery during rollback.
- Integrate with runbooks (e.g., agent_crash.md for crash recovery).

## Expected Output
Restored state from journal, no data loss.

## Quickstart
1. Simulate failure in workflow.
2. Run: `python -c "from core.workflow_safety import get_workflow_safety; safety = get_workflow_safety('test'); safety.replay_journal()"`
3. Verify outputs match previous successful run.