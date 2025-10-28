# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-28
### Added
- Core schemas for v1 contracts:
  - `schemas/workflow.schema.yaml`: Defines workflow structure with steps, inputs/outputs, feature flags (parallel_execution, memory_augmentation).
  - `schemas/memory.api.json`: Memory operations (write/read/delete/search/list_namespaces) with namespace, TTL, audit logging.
  - `schemas/plugin.manifest.json`: Plugin manifests with scopes (network, filesystem, secrets), execution_policy (sandbox, outbound), compat_matrix.
- Compatibility matrix in each schema for min/max versions, deprecations (e.g., legacy_scopes removal by 2025-12-31), feature flags (e.g., jit_tokens, encryption_at_rest).
- Schema evolution support: Deprecations with dates, adapters planned for v2.
- OpenTelemetry tracing module (`core/tracing.py`): Spans for load_agent, memory_operation, tool_call; correlation IDs; metrics (queue_depth, wait_time_p95, success_rate, agent_cpu, memory_hit_rate).
- SLO definitions: Success rate ≥99%/30d, p95 end-to-end ≤2s, error budget ≤5%, queue_depth_max=1000, memory_hit_rate_min=80%.

### Fixed
- 2 failing unit tests in `tests/test_self_improvement_agent.py` (agent configuration loading and rules inclusion) by updating assertions to match "imports" structure.

### Deprecated
- None in v1.

### Security
- Default deny-all scopes in plugin manifests.
- Sandbox defaults to subprocess.

[1.0.0]: https://example.com/compare/v0.9.0...v1.0.0