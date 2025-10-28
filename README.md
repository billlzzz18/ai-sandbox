# AI Agent Framework - Playbook Generator v1

A production-ready AI agent framework with Playbook Generator v1, featuring enterprise-grade reliability, security, observability, and cost controls. Built for Phase D deployment with comprehensive tooling for multi-language ecosystems.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ (npm)
- Python 3.12+ (pip/uv)
- PHP 8.1+ (Composer)
- Ruby 3.0+ (Bundler)
- Google Gemini API key

### Installation

```bash
# Install Node.js dependencies
npm install

# Install Python dependencies
pip install -e .  # or uv pip install -e .

# Install PHP dependencies
composer install

# Install Ruby dependencies
bundle install

# For monorepo support
pnpm install
```

### Run Playbook Generator v1

```bash
# Set your Gemini API key
export GEMINI_API_KEY="your-api-key-here"

# Run the Playbook Generator
cd playbook_generator_v1 && python main.py
```

## 📋 Features

### Core Components
- **Playbook Generator v1**: AI-powered workflow generation with Gemini 2.5-flash
- **Atomic Tools**: Think_And_Plan, Memory/File/Search/Code operations, Playbook saver
- **Orchestrator**: Tool calling loops with correlation tracking
- **Real Artifact Generation**: Task decompositions, unit tests, documentation, API specs

### Production Hardening (Phase C→D)
- **Contract & Versioning**: v1 schemas with compatibility matrix
- **Observability**: OpenTelemetry tracing + metrics + SLO monitoring
- **Plugin Security**: Sandbox execution, scopes, JIT tokens
- **Memory Governance**: Namespaced storage, encryption, TTL policies
- **Workflow Safety**: Dedupe keys, replay journals, exactly-once semantics
- **Cost Control**: Rate limiting, quotas, auto-throttling
- **Runbooks & DR**: Incident response playbooks, backup/restore procedures

### Multi-Language Support
- **Node.js**: Express server with REST API
- **Python**: CLI tools and agent implementations
- **PHP**: Agent loader and utilities
- **Ruby**: Configuration management and tools
- **pnpm**: Monorepo workspace management

## 🏗️ Architecture

```
├── cli/                    # Multi-language CLI implementations
│   ├── python/            # Python agent framework
│   ├── php/               # PHP utilities
│   └── ruby/              # Ruby configuration tools
├── core/                  # Production hardening modules
│   ├── memory.py          # Encrypted, namespaced memory
│   ├── plugin_sandbox.py  # Secure plugin execution
│   ├── rate_limiter.py    # Cost control & throttling
│   ├── tracing.py         # OpenTelemetry observability
│   └── workflow_safety.py # Idempotency & replay
├── playbook_generator_v1/ # Main application
│   ├── main.py           # Orchestrator with Gemini integration
│   └── *.txt|*.md|*.json # Generated artifacts
├── schemas/               # v1 contract definitions
│   ├── workflow.schema.yaml
│   ├── memory.api.json
│   └── plugin.manifest.json
├── docs/                  # Documentation & cookbooks
├── runbooks/              # Operational procedures
├── public/                # Web UI assets
└── tests/                 # Test suites
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run linting
flake8 core/ playbook_generator_v1/ scripts/ tests/
pylint core/ playbook_generator_v1/ scripts/ tests/

# Validate schemas
python scripts/validate_schemas.py
```

## 📚 Documentation

### Cookbooks
- [Parallel Patterns](docs/cookbook/parallel_patterns.md)
- [Conditional Branching](docs/cookbook/conditional_branch.md)
- [Plugin I/O](docs/cookbook/plugin_io.md)
- [Memory-Augmented Agents](docs/cookbook/memory_augmented.md)
- [Rollback Strategies](docs/cookbook/rollback.md)

### Quickstarts
- [Getting Started](docs/quickstarts.md)

### Operational Runbooks
- [Queue Saturation](runbooks/queue_saturation.md)
- [DLQ Drain](runbooks/dlq_drain.md)
- [Agent Crash Recovery](runbooks/agent_crash.md)
- [Memory Index Rebuild](runbooks/memory_rebuild.md)
- [Safe Mode](runbooks/safe_mode.md)
- [DR Plan](runbooks/dr_plan.md)

## 🔒 Security

- **Plugin Sandboxing**: Subprocess/container isolation with resource limits
- **Memory Encryption**: AES-256 at rest, TLS 1.3 in transit
- **Access Control**: Namespaced permissions, audit logging
- **Rate Limiting**: Per-user quotas with auto-throttling
- **Input Validation**: Schema-based validation for all inputs

## 📊 Observability

- **Tracing**: End-to-end correlation IDs across Bus→Orchestrator→Agent→Tool→Memory
- **Metrics**: Queue depth, p95/p99 latency, success rates, resource usage
- **SLOs**: ≥99% success rate, ≤2s p95 end-to-end, ≤5% error budget
- **Dashboards**: Live traces, flame graphs, cost monitoring

## 🚀 Deployment

### Phase D Readiness Checklist
- ✅ v1 contracts published with adapters
- ✅ SLO monitoring (30d success rate tracking)
- ✅ Soak/chaos testing (no data loss)
- ✅ Security review (CIS baseline compliance)
- ✅ Cost controls (budget throttling active)

### Environment Variables
```bash
# Required
GEMINI_API_KEY=your-gemini-api-key
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317  # Optional

# Optional
REDIS_URL=redis://localhost:6379                    # For rate limiting
MEMORY_ENCRYPTION_KEY=your-32-byte-key             # For memory encryption
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all linting passes
5. Submit a pull request

## 📄 License

See [LICENSE](LICENSE) for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/your-org/ai-agent-framework/issues)
- **Documentation**: [Full Docs](docs/)
- **Runbooks**: [Operational Procedures](runbooks/)

---

**Built for Enterprise AI Agent Orchestration** - Production-ready with comprehensive tooling for reliability, security, and observability.
