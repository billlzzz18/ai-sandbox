---
name: "gemini-agent-rules"
version: "1.0.0"
description: "กฎเกณฑ์เฉพาะสำหรับการทำงานกับ Gemini CLI"
---
## Gemini CLI Integration Rules

### Environment Setup
- Always ensure GEMINI_API_KEY and GOOGLE_CLOUD_PROJECT environment variables are set before operations
- Use proper authentication methods as required by Gemini CLI
- Handle rate limiting and API quota management appropriately

### Command Execution
- Use Gemini CLI commands through proper shell execution
- Parse CLI output correctly for integration with the agent framework
- Handle both interactive and non-interactive modes appropriately

### Code Generation
- Generate clean, well-formatted code compatible with Gemini's capabilities
- Use appropriate language-specific formatting and conventions
- Ensure generated code is executable and follows best practices

### Error Handling
- Implement proper error handling for CLI failures and API errors
- Provide meaningful error messages to users
- Retry failed operations when appropriate

### Tool Integration
- Integrate with existing tool ecosystem while leveraging Gemini's unique capabilities
- Maintain consistency with other agents in the framework
- Document tool usage and limitations clearly