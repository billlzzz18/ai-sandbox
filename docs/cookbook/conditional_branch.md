# Cookbook: Conditional Branching

## Overview
Branch workflows based on conditions using Jinja2 templating in schema v1.

## Example Workflow YAML
```yaml
name: conditional-decision
version: "1.0.0"
steps:
  - id: check-condition
    type: conditional
    condition: "{{ inputs.user_score > 0.8 }}"
    true_branch:
      - id: approve
        type: agent_call
        agent: "approval-agent"
        inputs: { user: "{{ inputs.user_id }}" }
        outputs: [approval_status]
    false_branch:
      - id: review
        type: tool_call
        tools: ["manual_review_tool"]
        inputs: { details: "{{ inputs.details }}" }
        outputs: [review_notes]
  - id: finalize
    type: agent_call
    agent: "finalizer-agent"
    inputs: { status: "{{ outputs.approval_status or outputs.review_notes }}" }
```

## Implementation Notes
- Conditions are evaluated deterministically with injected clock/seed from `core/workflow_safety.py`.
- Ensure branches are idempotent (use dedupe keys).
- Quotas: Branching counts as single step RPS, but aggregate costs.

## Expected Output
`outputs.status` with branch result.

## Quickstart
Copy YAML to workflow file, execute: `orchestrator run conditional-decision --inputs '{"user_score": 0.9, "user_id": "123"}'`.
Test false branch with score <0.8.