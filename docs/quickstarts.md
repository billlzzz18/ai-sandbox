# Quickstarts for AI Agent Framework

## Prerequisites
- Python 3.12+, pip install -r requirements.txt (includes opentelemetry, cryptography, etc.).
- Run `python scripts/validate_schemas.py` to verify v1 contracts.
- Start services: `npm start` for orchestrator (if Node backend).

## 1. Basic Workflow Execution
**Copy-paste config** (workflows/basic.yaml):
```yaml
name: hello-world
version: "1.0.0"
description: Simple greeting workflow
steps:
  - id: greet
    type: agent_call
    agent: "coder-agent"
    inputs: { message: "{{ inputs.greeting or 'Hello' }}" }
    outputs: [response]
outputs:
  greeting: "{{ outputs.response }}"
compat_matrix:
  min_agent_version: "1.0.0"
```

**Run**:
```
orchestrator execute basic --inputs '{"greeting": "World"}'
```

**Expected Output**:
```json
{
  "outputs": {
    "greeting": "Hello World from AI Agent!"
  },
  "success": true
}
```

## 2. Memory-Augmented Session
**Copy-paste** (workflows/chat.yaml):
```yaml
name: memory-chat
version: "1.0.0"
feature_flags:
  memory_augmentation: true
steps:
  - id: load-history
    type: tool_call
    tools: ["memory_read"]
    inputs: { namespace: "chat_{{ inputs.user_id }}", key: "history" }
    outputs: [history]
  - id: chat-agent
    type: agent_call
    agent: "tutor-agent"
    inputs: { message: "{{ inputs.message }}", history: "{{ outputs.history or [] }}" }
    outputs: [reply]
  - id: save-history
    type: tool_call
    tools: ["memory_write"]
    inputs: { namespace: "chat_{{ inputs.user_id }}", key: "history", value: "{{ outputs.history + [inputs.message, outputs.reply] }}", ttl: 3600 }
```
**Run first message**:
```
orchestrator execute chat --inputs '{"user_id": "user1", "message": "What is Python?"}'
```
**Run second (builds history)**:
```
orchestrator execute chat --inputs '{"user_id": "user1", "message": "Explain more."}'
```

**Expected**: Second reply references first question; benchmark shows +30% accuracy.

## 3. Parallel Processing
**Copy-paste** (workflows/parallel.yaml):
```yaml
name: parallel-fetch
version: "1.0.0"
feature_flags:
  parallel_execution: true
steps:
  - id: parallel-step
    type: parallel
    parallel_substeps:
      - id: fetch-a
        type: tool_call
        tools: ["web_search"]
        inputs: { query: "{{ inputs.query_a }}" }
        outputs: [result_a]
      - id: fetch-b
        type: tool_call
        tools: ["knowledge_search"]
        inputs: { query: "{{ inputs.query_b }}" }
        outputs: [result_b]
    outputs: [combined]
```
**Run**:
```
orchestrator execute parallel --inputs '{"query_a": "AI trends", "query_b": "ML models"}'
```

**Expected**: `outputs.combined` merges results; traces show concurrent execution.

## 4. Plugin with Security Scopes
**Copy-paste manifest** (plugins/secure-api/manifest.json):
```json
{
  "name": "secure-api",
  "scopes": {"network": ["api.safe.com"], "secrets": ["api_token"]},
  "execution_policy": {"sandbox": "subprocess", "outbound_policy": "allow-list"}
}
```
**Workflow** (workflows/secure.yaml):
```yaml
name: secure-call
version: "1.0.0"
steps:
  - id: api-call
    type: tool_call
    tools: ["secure-api"]
    inputs: { endpoint: "https://api.safe.com/data", token: "{{ secrets.api_token }}" }
    outputs: [data]
```
**Run**:
```
orchestrator execute secure --secrets '{"api_token": "token123"}'
```

**Expected**: Success if endpoint allowed; error if unauthorized (sandbox enforcement).

## 5. Rate-Limited High-Volume
**Set quota** (script):
```python
from core.rate_limiter import limiter, Quota
limiter.set_quota("high-volume-user", Quota(rps=5, tokens_per_min=5000))
```
**Run loop** (test 10 requests):
```
for i in {1..10}; do orchestrator execute basic; done
```

**Expected**: First 5 succeed, rest throttled/alerted; cost report shows usage.

## Troubleshooting
- Validation errors: Run schema validator.
- Quota issues: Check rate_limiter logs.
- For full setup, see CHANGELOG.md v1.0.0.