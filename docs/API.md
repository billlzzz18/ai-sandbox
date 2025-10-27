# 🔌 API Documentation

## Overview

The AI Agent Sandbox provides both REST API and programmatic interfaces for interacting with agents, tools, and workflows.

## Base URL
```
http://localhost:3000
```

## Authentication

All API endpoints require authentication via API key header:
```
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### Agent Management

#### Preview Agent Configuration
Get agent configuration and capabilities without executing tasks.

```http
POST /agents/preview
```

**Request Body:**
```json
{
  "rolePath": "role/coder-agent/role.yaml",
  "prompt": "Optional prompt for prompt improvement"
}
```

**Response:**
```json
{
  "agent": {
    "name": "coder-agent",
    "description": "AI-powered coding assistant",
    "persona": {
      "role": "Senior Software Developer",
      "expertise": ["Python", "JavaScript", "TypeScript"]
    },
    "rulesCount": 3,
    "rules": ["coding_best_practices.md", "security_guidelines.md"],
    "tools": [
      {
        "name": "write_python",
        "description": "Generate Python code",
        "executionEnvironment": "api",
        "defaultMode": "auto",
        "implemented": true
      }
    ]
  },
  "prompts": {
    "original": "Write a hello world function",
    "refined": "As an expert developer, write a well-documented hello world function with proper error handling and type hints."
  }
}
```

#### Execute Tool
Execute a specific tool through an agent.

```http
POST /agents/tools/execute
```

**Request Body:**
```json
{
  "rolePath": "role/coder-agent/role.yaml",
  "toolName": "write_python",
  "args": ["function_name", "additional_args"]
}
```

**Response:**
```json
{
  "result": {
    "status": "success",
    "code": "def hello_world():\n    print('Hello, World!')\n    return True",
    "language": "python",
    "execution_time": 1.23
  }
}
```

#### List Available Agents
Get list of all configured agents.

```http
GET /agents
```

**Response:**
```json
{
  "agents": [
    {
      "name": "coder-agent",
      "role": "Software Developer",
      "capabilities": ["code_generation", "code_review", "debugging"],
      "status": "idle"
    },
    {
      "name": "planning-agent",
      "role": "Project Manager",
      "capabilities": ["task_planning", "resource_allocation"],
      "status": "busy"
    }
  ]
}
```

### Workflow Management

#### Execute Workflow
Run a predefined workflow with input parameters.

```http
POST /workflows/execute
```

**Request Body:**
```json
{
  "workflowName": "code_review",
  "input": {
    "repository": "owner/repo",
    "pullRequest": 123,
    "files": ["src/main.py", "src/utils.py"]
  },
  "options": {
    "async": false,
    "timeout": 300
  }
}
```

**Response:**
```json
{
  "workflowId": "workflow_123456",
  "status": "completed",
  "result": {
    "issues": [
      {
        "file": "src/main.py",
        "line": 15,
        "severity": "medium",
        "message": "Consider using type hints for better code clarity",
        "suggestion": "def calculate_total(items: List[float]) -> float:"
      }
    ],
    "summary": {
      "total_files": 2,
      "issues_found": 3,
      "severity_breakdown": {
        "high": 0,
        "medium": 2,
        "low": 1
      }
    }
  },
  "execution_time": 45.67
}
```

#### Get Workflow Status
Check status of a running workflow.

```http
GET /workflows/{workflowId}/status
```

**Response:**
```json
{
  "workflowId": "workflow_123456",
  "status": "running",
  "progress": {
    "current_step": 2,
    "total_steps": 5,
    "current_step_name": "security_analysis"
  },
  "start_time": "2024-01-15T10:30:00Z",
  "estimated_completion": "2024-01-15T10:32:30Z"
}
```

### Memory System

#### Query Episodic Memory
Retrieve past task experiences.

```http
POST /memory/episodic/query
```

**Request Body:**
```json
{
  "query": "code review",
  "agent_filter": "coder-agent",
  "limit": 5,
  "date_range": {
    "start": "2024-01-01",
    "end": "2024-01-31"
  }
}
```

**Response:**
```json
{
  "experiences": [
    {
      "task": "Code review for authentication module",
      "success": true,
      "performance_metrics": {
        "execution_time": 45.2,
        "issues_found": 3
      },
      "lessons_learned": [
        "Always check input validation",
        "Use parameterized queries for SQL"
      ],
      "timestamp": "2024-01-15T09:30:00Z"
    }
  ]
}
```

#### Query Semantic Memory
Search knowledge graph for concepts and relationships.

```http
POST /memory/semantic/query
```

**Request Body:**
```json
{
  "query": "WHAT is authentication",
  "depth": 2,
  "limit": 10
}
```

**Response:**
```json
{
  "results": [
    {
      "subject": "authentication",
      "predicate": "requires",
      "object": "password_hashing",
      "confidence": 0.95
    },
    {
      "subject": "authentication",
      "predicate": "prevents",
      "object": "unauthorized_access",
      "confidence": 0.98
    }
  ]
}
```

### GitHub Integration

#### Webhook Handler
Handle GitHub webhook events.

```http
POST /webhooks/github
X-GitHub-Event: pull_request
X-Hub-Signature-256: sha256=...
```

**Request Body:** (GitHub webhook payload)

**Response:**
```json
{
  "status": "processed",
  "action": "pull_request_opened",
  "workflow_triggered": "workflow_123456"
}
```

#### Get Repository Analysis
Get comprehensive repository analysis.

```http
GET /github/repos/{owner}/{repo}/analysis
```

**Query Parameters:**
- `branch=main` - Branch to analyze
- `depth=full` - Analysis depth (basic|standard|full)

**Response:**
```json
{
  "repository": "owner/repo",
  "branch": "main",
  "analysis": {
    "code_quality": {
      "score": 8.5,
      "issues": 12,
      "recommendations": 5
    },
    "security": {
      "vulnerabilities": 0,
      "warnings": 2,
      "compliance_score": 95
    },
    "performance": {
      "complexity_score": 3.2,
      "optimization_opportunities": 3
    },
    "maintainability": {
      "technical_debt_ratio": 0.15,
      "documentation_coverage": 85
    }
  },
  "last_updated": "2024-01-15T10:00:00Z"
}
```

### System Management

#### Health Check
Check system health and status.

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "uptime": 3600,
  "components": {
    "database": "healthy",
    "message_bus": "healthy",
    "agents": "healthy",
    "memory": "healthy"
  }
}
```

#### System Statistics
Get comprehensive system statistics.

```http
GET /stats
```

**Response:**
```json
{
  "system": {
    "uptime": 86400,
    "version": "2.0.0",
    "active_connections": 15
  },
  "agents": {
    "total": 8,
    "active": 6,
    "idle": 2,
    "error": 0
  },
  "workflows": {
    "total_executed": 1250,
    "success_rate": 0.94,
    "average_execution_time": 45.2
  },
  "memory": {
    "episodic_entries": 15420,
    "semantic_triples": 8750,
    "working_memory_items": 45
  },
  "performance": {
    "cpu_usage": 45.2,
    "memory_usage": 2.1,
    "response_time_avg": 125
  }
}
```

### Configuration Management

#### Get Configuration
Retrieve current system configuration.

```http
GET /config
```

**Response:**
```json
{
  "agents": {
    "max_concurrent": 10,
    "default_timeout": 300,
    "memory_limits": {
      "episodic": 10000,
      "working": 100
    }
  },
  "workflows": {
    "max_parallel": 5,
    "default_timeout": 600,
    "retry_policy": {
      "max_attempts": 3,
      "backoff_factor": 2
    }
  },
  "integrations": {
    "github": {
      "enabled": true,
      "webhooks": true,
      "rate_limit": 5000
    }
  }
}
```

#### Update Configuration
Update system configuration (admin only).

```http
PUT /config
```

**Request Body:**
```json
{
  "agents": {
    "max_concurrent": 15
  }
}
```

## Error Handling

All API endpoints return standardized error responses:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": "rolePath",
      "issue": "File not found"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123456"
  }
}
```

### Common Error Codes
- `VALIDATION_ERROR` - Invalid request parameters
- `AUTHENTICATION_ERROR` - Invalid or missing API key
- `AUTHORIZATION_ERROR` - Insufficient permissions
- `NOT_FOUND` - Resource not found
- `RATE_LIMITED` - Too many requests
- `INTERNAL_ERROR` - Server error
- `AGENT_UNAVAILABLE` - Requested agent is not available

## Rate Limiting

API requests are rate limited based on your plan:

- **Free Tier**: 100 requests/hour
- **Pro Tier**: 10,000 requests/hour
- **Enterprise**: Custom limits

Rate limit headers are included in all responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## SDKs and Libraries

### Python SDK
```python
from ai_agent_sdk import Client

client = Client(api_key="your-api-key")

# Execute a tool
result = client.agents.execute_tool(
    role_path="role/coder-agent/role.yaml",
    tool_name="write_python",
    args=["hello_world"]
)

# Run a workflow
result = client.workflows.execute(
    name="code_review",
    input={"files": ["main.py"]}
)
```

### JavaScript SDK
```javascript
import { AIAgentClient } from 'ai-agent-sdk';

const client = new AIAgentClient({
  apiKey: 'your-api-key'
});

// Preview agent
const preview = await client.agents.preview({
  rolePath: 'role/coder-agent/role.yaml',
  prompt: 'Write a sorting function'
});

// Execute workflow
const result = await client.workflows.execute('code_review', {
  repository: 'owner/repo',
  pullRequest: 123
});
```

## Webhooks

Configure webhooks to receive real-time notifications:

### Supported Events
- `agent.task_completed` - Agent task finished
- `workflow.completed` - Workflow execution finished
- `memory.updated` - Memory system updated
- `github.pr_reviewed` - GitHub PR review completed

### Webhook Payload Example
```json
{
  "event": "workflow.completed",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "workflow_id": "workflow_123456",
    "status": "success",
    "result": { ... },
    "execution_time": 45.67
  }
}
```

## Best Practices

### Error Handling
```javascript
try {
  const result = await client.agents.executeTool(params);
  console.log('Success:', result);
} catch (error) {
  if (error.code === 'RATE_LIMITED') {
    // Wait and retry
    await delay(error.retryAfter);
    return retryRequest();
  } else if (error.code === 'AGENT_UNAVAILABLE') {
    // Try different agent
    return tryAlternativeAgent();
  }
  throw error;
}
```

### Pagination
For endpoints that return lists, use pagination:
```javascript
const results = [];
let page = 1;
let hasMore = true;

while (hasMore) {
  const response = await client.getExperiences({
    page,
    limit: 50,
    query: 'code review'
  });

  results.push(...response.items);
  hasMore = response.hasMore;
  page++;
}
```

### Timeouts
Set appropriate timeouts for long-running operations:
```javascript
const result = await client.workflows.execute('complex_analysis', input, {
  timeout: 300000, // 5 minutes
  onProgress: (progress) => {
    console.log(`Progress: ${progress.percent}%`);
  }
});
```

This API documentation covers the core functionality. For more advanced features and detailed examples, see the [Usage Examples](../examples/README.md) and [Contributing Guide](../CONTRIBUTING.md).