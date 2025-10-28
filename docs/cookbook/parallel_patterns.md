# Cookbook: Parallel Patterns

## Overview
Execute multiple steps concurrently using feature flag `parallel_execution: true` in workflow schema.

## Example Workflow YAML (v1)
```yaml
name: parallel-analysis
version: "1.0.0"
feature_flags:
  parallel_execution: true
steps:
  - id: step-1
    type: parallel
    parallel_substeps:
      - id: data-fetch
        type: tool_call
        tools: ["data_fetcher"]
        inputs: { url: "{{ inputs.url }}" }
      - id: model-predict
        type: agent_call
        agent: "predictor-agent"
        inputs: { data: "{{ inputs.data }}" }
    outputs: [results]
```

## Implementation Notes
- Use `core/workflow_safety.py` for idempotent parallel steps (dedupe keys).
- Monitor with OTEL traces for branch divergence.
- Quotas: Parallel steps count as 1 RPS but multiply token cost.

## Expected Output
Combined results from substeps in `outputs.results`.

Quickstart: Copy YAML, run `orchestrator execute parallel-analysis --inputs '{"url": "api.com", "data": {}}'`.