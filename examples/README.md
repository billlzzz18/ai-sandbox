# 📚 Usage Examples

This directory contains practical examples showing how to use the AI Agent Sandbox for various scenarios.

## 🚀 Quick Start Examples

### 1. Basic Agent Usage
```python
from core.agent_orchestrator import get_orchestrator

# Get orchestrator instance
orchestrator = get_orchestrator()

# Register a coding agent
communicator = orchestrator.register_agent(
    agent_name="my-coder",
    role="software_developer",
    capabilities=["code_generation", "code_review", "debugging"]
)

# Execute a task
result = orchestrator.execute_task(
    agent_name="my-coder",
    task={
        "action": "write_python",
        "prompt": "Write a function to calculate fibonacci numbers"
    }
)

print(result)
```

### 2. Workflow Execution
```python
from core.workflow_engine.workflow_engine import WorkflowEngine

# Load workflow definition
engine = WorkflowEngine()
engine.load_workflow_definition("code_review", {
    "steps": [
        {
            "name": "analyze_code",
            "agent": "code_analyzer",
            "action": "analyze_code",
            "parameters": {"files": "{{input.files}}"}
        },
        {
            "name": "review_style",
            "agent": "style_reviewer",
            "action": "review_style",
            "dependencies": ["analyze_code"]
        }
    ]
})

# Execute workflow
result = engine.execute_workflow("code_review", {
    "files": ["src/main.py", "src/utils.py"]
})
```

### 3. Memory System Usage
```python
from memory.episodic_memory.episodic_memory import EpisodicMemory
from memory.semantic_memory.knowledge_graph import KnowledgeGraph

# Episodic memory for task experiences
episodic = EpisodicMemory()
experience = Experience(
    task="Code review for authentication module",
    success=True,
    context={"files": 5, "issues_found": 3},
    lessons_learned=["Always check input validation", "Use parameterized queries"],
    performance_metrics={"review_time": 45.2},
    agent_name="security_reviewer",
    task_type="security_review"
)
episodic.store_experience(experience)

# Semantic memory for knowledge
semantic = KnowledgeGraph()
semantic.add_triple("authentication", "requires", "input_validation")
semantic.add_triple("sql_injection", "prevented_by", "parameterized_queries")
```

## 🎯 Agent-Specific Examples

### Code Review Agent
```python
# Comprehensive code review workflow
review_config = {
    "repository": "my-org/my-repo",
    "pull_request": 123,
    "files": ["src/auth.py", "src/database.py"],
    "rules": {
        "security": "high",
        "performance": "medium",
        "maintainability": "high"
    }
}

result = orchestrator.execute_workflow("comprehensive_code_review", review_config)
```

### Learning Agent
```python
# Create personalized learning plan
learning_request = {
    "topic": "Python async programming",
    "current_level": "intermediate",
    "goals": ["Build async web API", "Handle concurrency properly"],
    "time_available": "10 hours/week",
    "preferred_style": "hands-on projects"
}

plan = orchestrator.execute_task(
    agent_name="learning_assistant",
    task={"action": "create_learning_plan", "data": learning_request}
)
```

### Planning Agent
```python
# Project planning with AI assistance
project_spec = {
    "name": "E-commerce Platform",
    "technologies": ["React", "Node.js", "PostgreSQL"],
    "team_size": 5,
    "timeline": "3 months",
    "budget": "medium",
    "requirements": ["User auth", "Product catalog", "Payment integration"]
}

plan = orchestrator.execute_task(
    agent_name="project_planner",
    task={"action": "create_project_plan", "data": project_spec}
)
```

## 🔧 Tool Integration Examples

### GitHub Actions Integration
```yaml
# .github/workflows/ai-code-review.yml
name: AI Code Review
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  ai-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: AI Code Review
        uses: ai-agent-sandbox/code-review-action@v1
        with:
          api-key: ${{ secrets.AI_AGENT_API_KEY }}
          review-depth: comprehensive
          fail-on: high
          custom-rules: .github/code-review-rules.yaml
```

### Custom Tool Development
```python
# tool_implementations/custom_tools/my_custom_tool.py
def analyze_custom_metrics(code_files, config):
    """
    Custom tool for analyzing domain-specific metrics
    """
    results = []

    for file_path in code_files:
        with open(file_path, 'r') as f:
            content = f.read()

        # Custom analysis logic
        metrics = {
            "complexity_score": calculate_complexity(content),
            "test_coverage": estimate_test_coverage(content),
            "documentation_score": check_documentation(content)
        }

        results.append({
            "file": file_path,
            "metrics": metrics,
            "recommendations": generate_recommendations(metrics)
        })

    return {
        "status": "success",
        "analysis": results,
        "summary": aggregate_results(results)
    }
```

## 🌐 API Integration Examples

### REST API Usage
```bash
# Preview agent configuration
curl -X POST http://localhost:3000/agents/preview \
  -H 'Content-Type: application/json' \
  -d '{
    "rolePath": "role/coder-agent/role.yaml",
    "prompt": "Write a Python function to reverse a string"
  }'

# Execute tool directly
curl -X POST http://localhost:3000/agents/tools/execute \
  -H 'Content-Type: application/json' \
  -d '{
    "rolePath": "role/coder-agent/role.yaml",
    "toolName": "write_python",
    "args": ["reverse_string", "hello world"]
  }'
```

### Webhook Integration
```javascript
// GitHub webhook handler
app.post('/webhooks/github', (req, res) => {
  const event = req.headers['x-github-event'];
  const payload = req.body;

  if (event === 'pull_request' && payload.action === 'opened') {
    // Trigger AI code review
    triggerCodeReview(payload.pull_request);
  }

  res.status(200).send('OK');
});
```

## 🧪 Testing Examples

### Unit Test Example
```python
# tests/unit/test_custom_tool.py
import pytest
from tool_implementations.custom_tools.my_custom_tool import analyze_custom_metrics

class TestCustomMetrics:
    def test_analyze_simple_file(self):
        # Test data
        test_files = ["examples/test_file.py"]
        config = {"threshold": 0.8}

        # Execute
        result = analyze_custom_metrics(test_files, config)

        # Assert
        assert result["status"] == "success"
        assert len(result["analysis"]) == 1
        assert "metrics" in result["analysis"][0]
        assert "complexity_score" in result["analysis"][0]["metrics"]

    def test_empty_file_list(self):
        result = analyze_custom_metrics([], {})
        assert result["status"] == "success"
        assert result["analysis"] == []
```

### Integration Test Example
```python
# tests/integration/test_agent_workflow.py
import pytest
from core.agent_orchestrator import get_orchestrator

class TestAgentWorkflow:
    def setup_method(self):
        self.orchestrator = get_orchestrator()
        # Register test agents
        self.orchestrator.register_agent("test_agent", "tester", ["test_execution"])

    def test_complete_workflow(self):
        # Test full agent workflow
        task = {
            "action": "test_execution",
            "data": {"test_file": "test.py"}
        }

        result = self.orchestrator.execute_task("test_agent", task)

        assert result["success"] is True
        assert "execution_time" in result

    def teardown_method(self):
        self.orchestrator.cleanup()
```

## 📊 Performance Examples

### Benchmarking Agent Performance
```python
import time
from core.agent_orchestrator import get_orchestrator

def benchmark_agent_performance():
    orchestrator = get_orchestrator()

    # Test tasks of different complexities
    tasks = [
        {"action": "simple_calculation", "data": {"x": 5, "y": 10}},
        {"action": "complex_analysis", "data": {"files": ["large_file.py"]}},
        {"action": "ai_generation", "data": {"prompt": "Write a long essay"}}
    ]

    results = {}
    for task in tasks:
        start_time = time.time()
        result = orchestrator.execute_task("benchmark_agent", task)
        execution_time = time.time() - start_time

        results[task["action"]] = {
            "execution_time": execution_time,
            "success": result.get("success", False),
            "output_size": len(str(result))
        }

    return results
```

## 🔧 Configuration Examples

### Advanced Agent Configuration
```yaml
# config/agent_config.yaml
agents:
  code-reviewer:
    enabled: true
    priority: high
    memory:
      episodic: true
      semantic: true
      working_memory_size: 100
    tools:
      - analyze_code
      - review_best_practices
      - check_security
    rules:
      - coding_best_practices
      - security_guidelines

  learning-assistant:
    enabled: true
    priority: medium
    memory:
      episodic: true
      semantic: true
    tools:
      - create_learning_plan
      - evaluate_answer
      - find_analogy
```

### Environment Configuration
```bash
# .env
# API Keys
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key
GEMINI_API_KEY=your-gemini-key

# System Configuration
NODE_ENV=development
LOG_LEVEL=info
MAX_WORKERS=4

# Memory Configuration
EPISODIC_MEMORY_SIZE=10000
SEMANTIC_MEMORY_ENABLED=true
WORKING_MEMORY_SIZE=50

# GitHub Integration
GITHUB_APP_ID=your-app-id
GITHUB_PRIVATE_KEY_PATH=/path/to/private-key.pem
GITHUB_WEBHOOK_SECRET=your-webhook-secret
```

## 🚀 Deployment Examples

### Docker Deployment
```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy application code
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S aiagent -u 1001

USER aiagent

EXPOSE 3000

CMD ["npm", "start"]
```

### Kubernetes Deployment
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-agent-sandbox
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-agent-sandbox
  template:
    metadata:
      labels:
        app: ai-agent-sandbox
    spec:
      containers:
      - name: ai-agent-sandbox
        image: ai-agent-sandbox:latest
        ports:
        - containerPort: 3000
        env:
        - name: NODE_ENV
          value: "production"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

These examples demonstrate the flexibility and power of the AI Agent Sandbox framework. Each example can be adapted and extended based on your specific use case and requirements.