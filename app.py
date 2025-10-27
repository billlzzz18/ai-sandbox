#!/usr/bin/env python3
"""AI Agent Sandbox - Main Python Engine

This is the main Python engine for the AI Agent Sandbox. It provides:
- Dynamic agent loading from YAML configurations
- Tool execution and management
- LLM integration with prompt improvement
- Session management and logging
"""
from __future__ import annotations

import sys
import os
import json
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path
import subprocess
import time

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from tool_implementations.api_stubs import run_gemini_cli
    from tool_implementations import index
except ImportError:
    # Fallback for when tools are not available
    def run_gemini_cli(prompt, **kwargs):
        return {"status": "error", "error": "Gemini CLI not available"}

    class MockIndex:
        MASTER_TOOL_MAP = {}
    index = MockIndex()

class Agent:
    """AI Agent with configurable tools and behavior"""

    def __init__(self, config: Dict[str, Any]):
        self.name = config.get('name', 'Unknown Agent')
        self.description = config.get('description', '')
        self.persona = config.get('persona', {})
        self.rules = config.get('rules', [])
        self.tools = config.get('tools', [])
        self.prompt_template = config.get('prompt_template', '')

    def run_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool by name"""
        if tool_name not in index.MASTER_TOOL_MAP:
            return {"status": "error", "error": f"Tool '{tool_name}' not found"}

        try:
            tool_func = index.MASTER_TOOL_MAP[tool_name]
            result = tool_func(**kwargs)
            return result
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def improve_prompt(self, raw_prompt: str) -> str:
        """Improve prompt using Gemini CLI"""
        improvement_prompt = f"""
        As an expert AI assistant, improve this prompt to be more effective and clear:

        Original prompt: {raw_prompt}

        Please provide an improved version that is:
        - More specific and actionable
        - Includes relevant context
        - Follows best practices for AI interaction
        """

        result = run_gemini_cli(improvement_prompt)
        if result.get('status') == 'success':
            return result.get('output', raw_prompt)
        return raw_prompt

    def generate_response(self, user_input: str) -> str:
        """Generate response using agent's persona and tools"""
        # Improve the prompt first
        improved_prompt = self.improve_prompt(user_input)

        # Build context from persona and rules
        context = f"""
        You are {self.name}.
        {self.description}

        Your persona: {json.dumps(self.persona, indent=2)}

        Rules you must follow:
        {chr(10).join(f"- {rule}" for rule in self.rules)}

        User request: {improved_prompt}
        """

        # Use Gemini CLI to generate response
        result = run_gemini_cli(context)
        if result.get('status') == 'success':
            return result.get('output', 'I apologize, but I could not generate a response.')
        else:
            return f"I encountered an error: {result.get('error', 'Unknown error')}"

class AgentManager:
    """Manages agent loading and execution"""

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.agents: Dict[str, Agent] = {}

    def load_agent(self, role_path: str) -> Optional[Agent]:
        """Load agent from YAML configuration"""
        try:
            full_path = self.base_path / role_path
            with open(full_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            # Load imports
            imports = config.get('imports', {})

            # Load persona from prompts
            persona = {}
            for prompt_path in imports.get('prompts', []):
                prompt_full_path = self.base_path / role_path / ".." / prompt_path
                if prompt_full_path.exists():
                    with open(prompt_full_path, 'r', encoding='utf-8') as f:
                        prompt_data = yaml.safe_load(f)
                        if 'persona' in prompt_data:
                            persona.update(prompt_data['persona'])

            # Load rules
            rules = []
            for rule_path in imports.get('rules', []):
                rule_full_path = self.base_path / role_path / ".." / rule_path
                if rule_full_path.exists():
                    with open(rule_full_path, 'r', encoding='utf-8') as f:
                        rules.append(f.read())

            # Load tools
            tools = []
            for tool_path in imports.get('tools', []):
                tool_full_path = self.base_path / role_path / ".." / tool_path
                if tool_full_path.exists():
                    tools.append(str(tool_full_path))

            # Build agent config
            agent_config = {
                'name': config.get('name', Path(role_path).stem),
                'description': config.get('description', ''),
                'persona': persona,
                'rules': rules,
                'tools': tools
            }

            agent = Agent(agent_config)
            self.agents[agent.name] = agent
            return agent

        except Exception as e:
            print(f"Error loading agent from {role_path}: {e}")
            return None

    def run_interactive_session(self, agent_name: str):
        """Run interactive session with an agent"""
        if agent_name not in self.agents:
            print(f"Agent '{agent_name}' not found. Available agents: {list(self.agents.keys())}")
            return

        agent = self.agents[agent_name]
        print(f"🤖 Starting interactive session with {agent.name}")
        print(f"📝 {agent.description}")
        print("Type 'quit' or 'exit' to end the session.\n")

        while True:
            try:
                user_input = input("You: ").strip()
                if user_input.lower() in ['quit', 'exit']:
                    print("👋 Session ended.")
                    break

                if not user_input:
                    continue

                print("🤔 Thinking...")
                response = agent.generate_response(user_input)
                print(f"{agent.name}: {response}\n")

            except KeyboardInterrupt:
                print("\n👋 Session interrupted.")
                break
            except Exception as e:
                print(f"❌ Error: {e}\n")

def main() -> int:
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='AI Agent Sandbox')
    parser.add_argument('--agent', '-a', help='Agent role file to load')
    parser.add_argument('--interactive', '-i', action='store_true', help='Run interactive session')
    parser.add_argument('--list-agents', '-l', action='store_true', help='List available agents')
    parser.add_argument('--list-assistants', action='store_true', help='List available AI assistants')
    parser.add_argument('--assistant', help='Specify AI assistant to use (gemini, codex, kilo_code, qwen, claude_code, github_copilot, open_code)')

    args = parser.parse_args()

    manager = AgentManager()

    if args.list_agents:
        # List all available agents
        role_dir = Path('role')
        if role_dir.exists():
            agents = [f for f in role_dir.rglob('*.yaml') if f.is_file()]
            print("Available agents:")
            for agent_file in agents:
                print(f"  - {agent_file.relative_to(role_dir)}")
        return 0

    if args.list_assistants:
        # List all available AI assistants
        assistants = [
            'gemini - Google Gemini CLI',
            'codex - GitHub Codex CLI',
            'kilo_code - Kilo Code CLI',
            'qwen - Qwen CLI',
            'claude_code - Claude Code CLI',
            'github_copilot - GitHub Copilot CLI',
            'open_code - Open Code CLI'
        ]
        print("Available AI assistants:")
        for assistant in assistants:
            print(f"  - {assistant}")
        print("\nTo use an assistant, set the corresponding environment variable:")
        print("  GEMINI_API_KEY - for Gemini")
        print("  OPENAI_API_KEY - for Codex")
        print("  KILO_CODE_API_KEY - for Kilo Code")
        print("  QWEN_API_KEY - for Qwen")
        print("  ANTHROPIC_API_KEY - for Claude Code")
        print("  GITHUB_TOKEN - for GitHub Copilot")
        print("  OPEN_CODE_API_KEY - for Open Code")
        return 0

    if not args.agent:
        print("Please specify an agent with --agent or use --list-agents to see available agents.")
        print("Use --list-assistants to see available AI assistants.")
        print("Example: python app.py --agent role/coder-agent/role.yaml --interactive --assistant gemini")
        return 1

    # Load the agent
    agent = manager.load_agent(args.agent)
    if not agent:
        print(f"Failed to load agent from {args.agent}")
        return 1

    # Set assistant preference if specified
    if args.assistant:
        print(f"Using AI assistant: {args.assistant}")
        # This would be passed to tools that support assistant selection

    if args.interactive:
        manager.run_interactive_session(agent.name)
    else:
        # Single query mode
        print(f"Agent {agent.name} loaded successfully.")
        print("Use --interactive flag for interactive mode.")

    return 0

if __name__ == "__main__":
    sys.exit(main())
