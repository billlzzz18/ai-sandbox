# Cookbook: Memory-Augmented Agents

## Overview
Augment agents with persistent memory for better context and accuracy (+30% per benchmarks).

## Example Workflow
```yaml
name: memory-chat
version: "1.0.0"
feature_flags:
  memory_augmentation: true
steps:
  - id: load-context
    type: tool_call
    tools: ["memory_read"]
    inputs: { namespace: "user_{{ inputs.user_id }}", key: "chat_history" }
    outputs: [history]
  - id: augmented-agent
    type: agent_call
    agent: "chat-agent"
    inputs: { message: "{{ inputs.message }}", context: "{{ outputs.history or [] }}" }
    outputs: [response]
  - id: save-response
    type: tool_call
    tools: ["memory_write"]
    inputs: { namespace: "user_{{ inputs.user_id }}", key: "chat_history", value: "{{ outputs.history + [inputs.message, outputs.response] }}", ttl: 3600 }
```

## Implementation Notes
- Use `core/memory.py` for read/write with TTL and encryption.
- Benchmark: Run `memory.evaluate_benchmark('chat_workflow', use_memory=True)` vs False to verify improvements.
- Safety: Namespaced per user/workflow; audit logs for access.

## Expected Output
`outputs.response` with context-aware reply.

## Quickstart
Execute: `orchestrator run memory-chat --inputs '{"user_id": "123", "message": "Hello"}'`.
Subsequent calls build history.