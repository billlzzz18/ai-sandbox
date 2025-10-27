# 🤝 Contributing to AI Agent Sandbox

Thank you for your interest in contributing to the AI Agent Sandbox! We welcome contributions from developers of all skill levels and backgrounds. This document provides guidelines and information to help you contribute effectively.

## 📋 Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Community](#community)

## 🤝 Code of Conduct

This project follows a [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a welcoming environment for all contributors. By participating, you agree to uphold this code.

## 🚀 Getting Started

### Prerequisites
- **Python 3.8+** for core engine and tools
- **Node.js 16+** for Express server and web components
- **Git** for version control
- **GitHub account** for collaboration

### Quick Start
```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/ai-agent-sandbox.git
cd ai-agent-sandbox

# Set up development environment
./scripts/setup-env.sh

# Install dependencies
npm install
pip install -r requirements.txt

# Run validation
python validate.py

# Run tests
npm test
pytest tests/
```

## 🛠️ Development Setup

### Environment Configuration
1. Copy environment template:
   ```bash
   cp .env.example .env
   ```

2. Configure your environment variables:
   ```bash
   # Edit .env file with your API keys and settings
   nano .env
   ```

3. Set up pre-commit hooks:
   ```bash
   pip install pre-commit
   pre-commit install
   ```

### Development Tools
- **VS Code** with recommended extensions
- **Docker** for containerized development
- **Postman** for API testing
- **GitHub CLI** for streamlined Git operations

## 💡 How to Contribute

### Types of Contributions
- 🐛 **Bug Fixes** - Fix issues and bugs
- ✨ **Features** - Add new functionality
- 📚 **Documentation** - Improve docs and guides
- 🧪 **Tests** - Add or improve test coverage
- 🎨 **UI/UX** - Improve user interfaces
- 🔧 **Tools** - Create new agent tools
- 🤖 **Agents** - Develop new AI agents

### Finding Issues to Work On
1. Check [GitHub Issues](https://github.com/ai-agent-sandbox/issues)
2. Look for `good first issue` or `help wanted` labels
3. Check the [Project Board](https://github.com/ai-agent-sandbox/projects) for planned work
4. Join our [Discord](https://discord.gg/ai-agent-sandbox) for discussions

## 🔄 Development Workflow

### 1. Choose an Issue
- Comment on the issue to indicate you're working on it
- Wait for assignment or confirmation

### 2. Create a Branch
```bash
# Create and switch to a feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description
```

### 3. Make Changes
- Follow coding standards
- Write tests for new functionality
- Update documentation
- Keep commits atomic and descriptive

### 4. Test Your Changes
```bash
# Run all tests
npm test
pytest tests/

# Run validation
python validate.py

# Manual testing
# ... test your changes manually
```

### 5. Submit a Pull Request
- Ensure your branch is up to date with main
- Fill out the PR template completely
- Request review from maintainers

## 📝 Coding Standards

### Python Code Style
```python
# Follow PEP 8
# Use type hints
def function_name(param: str) -> bool:
    """Docstring describing function."""
    return True

# Use descriptive variable names
user_profile = get_user_profile(user_id)
# Not: up = gu(user)
```

### JavaScript/Node.js Style
```javascript
// Use async/await over promises
async function processData(data) {
  try {
    const result = await validateData(data);
    return await transformData(result);
  } catch (error) {
    logger.error('Data processing failed', error);
    throw error;
  }
}

// Use const/let over var
const config = loadConfiguration();
let counter = 0;
```

### YAML Configuration Style
```yaml
# Use consistent indentation (2 spaces)
# Add comments for complex configurations
agent:
  name: coder-agent
  version: "1.0.0"
  # Description of agent capabilities
  capabilities:
    - code_generation
    - code_review
```

### Commit Message Format
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Testing
- `chore`: Maintenance

Examples:
```
feat(coder-agent): add TypeScript support
fix(validation): handle empty YAML files gracefully
docs(readme): update installation instructions
```

## 🧪 Testing

### Test Structure
```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── e2e/           # End-to-end tests
└── fixtures/      # Test data
```

### Running Tests
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/unit/test_config.py

# Run with coverage
pytest --cov=src --cov-report=html tests/

# Run tests in verbose mode
pytest -v tests/
```

### Writing Tests
```python
import pytest
from src.agent_orchestrator import AgentOrchestrator

class TestAgentOrchestrator:
    def test_agent_registration(self):
        orchestrator = AgentOrchestrator()
        # Test implementation
        assert True

    @pytest.mark.asyncio
    async def test_async_operation(self):
        # Async test example
        result = await some_async_function()
        assert result is not None
```

## 📚 Documentation

### Documentation Standards
- Use Markdown for all documentation
- Include code examples where helpful
- Keep screenshots up to date
- Use consistent formatting

### API Documentation
```javascript
/**
 * Processes agent requests
 * @param {Object} request - The request object
 * @param {string} request.agentId - ID of the requesting agent
 * @param {Object} request.payload - Request payload
 * @returns {Promise<Object>} Response object
 */
async function processAgentRequest(request) {
  // Implementation
}
```

## 🔄 Submitting Changes

### Pull Request Process
1. **Create PR** from your feature branch to `main`
2. **Fill out PR template** completely
3. **Request review** from appropriate maintainers
4. **Address feedback** and make requested changes
5. **Merge** once approved

### PR Review Process
- At least one maintainer approval required
- All CI checks must pass
- No merge conflicts
- Up-to-date with main branch

### After Merge
- Delete your feature branch
- PR will be automatically closed
- Changes will be deployed according to release process

## 🌐 Community

### Communication Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General discussions and Q&A
- **Discord**: Real-time chat and community support
- **Newsletter**: Monthly updates and announcements

### Getting Help
1. Check existing documentation
2. Search GitHub Issues
3. Ask in Discord
4. Create a new Issue if needed

### Recognition
Contributors are recognized through:
- GitHub contributor statistics
- Mention in release notes
- Community shoutouts
- Contributor badges

## 🙏 Thank You

Your contributions help make AI Agent Sandbox better for everyone. We appreciate your time and effort in helping build this community-driven project!

---

For questions or support, please reach out through any of our [communication channels](#community).