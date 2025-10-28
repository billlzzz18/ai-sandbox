# Cookbook: Plugin I/O

## Overview
Handle secure input/output for plugins using v1 manifest scopes and sandbox.

## Example Plugin Manifest (plugin.manifest.json)
```json
{
  "name": "api-caller",
  "version": "1.0.0",
  "scopes": {
    "network": ["api.example.com"],
    "secrets": ["api_key"],
    "cpu_limit": 1.0,
    "memory_limit": 512
  },
  "execution_policy": {
    "sandbox": "subprocess",
    "outbound_policy": "allow-list",
    "tls_pinning": true
  },
  "imports": ["requests", "json"]
}
```

## Workflow Integration
```yaml
steps:
  - id: call-api
    type: tool_call
    tools: ["api-caller"]
    inputs: { url: "https://api.example.com/data", secret: "{{ secrets.api_key }}" }
    outputs: [response_data]
```

## Implementation Notes
- Sandbox (`core/plugin_sandbox.py`) enforces scopes: Network allow-list, secret isolation (JIT tokens from vault).
- I/O Audit: Log inputs/outputs in memory access logs (`core/memory.py`).
- Error Handling: If scope violation, fallback to safe mode (runbooks/safe_mode.md).
- Cost: Outbound calls count toward quotas (`core/rate_limiter.py`).

## Expected Output
`outputs.response_data` with API response, validated against scopes.

## Quickstart
1. Save manifest to plugins/api-caller/manifest.json.
2. Run workflow: `orchestrator execute api-workflow --secrets '{"api_key": "sk-123"}'`.
3. Verify logs: No unauthorized network calls.