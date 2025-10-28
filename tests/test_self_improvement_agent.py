"""Test cases for self-improvement agent feedback loop system."""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from loader import load_agent, load_tool


class TestSelfImprovementAgent:
    """Test the self-improvement agent's error handling and learning capabilities."""

    def test_agent_configuration_loading(self):
        """Test that the self-improvement agent configuration loads correctly."""
        agent_config = load_agent("self_improvement_agent")

        assert agent_config is not None
        assert agent_config["name"] == "self-improvement-agent"
        assert "imports" in agent_config
        assert "tools" in agent_config["imports"]
        assert "rules" in agent_config["imports"]
        assert "prompts" in agent_config["imports"]

        # Check for required tools
        tool_names = [tool.split("/")[-1].replace(".yaml", "") for tool in agent_config["imports"]["tools"]]
        required_tools = [
            "error_analysis", "feedback_loop", "parallel_processing",
            "batch_operations", "lifecycle_management"
        ]

        for tool in required_tools:
            assert tool in tool_names, f"Required tool '{tool}' not found in agent configuration"

    def test_error_analysis_tool_exists(self):
        """Test that error analysis tool configuration exists."""
        tool_config = load_tool("error_analysis")

        assert tool_config is not None
        assert tool_config["name"] == "error_analysis"
        assert tool_config["execution_policy"]["default_mode"] == "auto"

    def test_feedback_loop_tool_exists(self):
        """Test that feedback loop tool configuration exists."""
        tool_config = load_tool("feedback_loop")

        assert tool_config is not None
        assert tool_config["name"] == "feedback_loop"
        assert tool_config["execution_policy"]["default_mode"] == "auto"

    def test_lifecycle_management_tool_exists(self):
        """Test that lifecycle management tool configuration exists."""
        tool_config = load_tool("lifecycle_management")

        assert tool_config is not None
        assert tool_config["name"] == "lifecycle_management"
        assert tool_config["execution_policy"]["default_mode"] == "auto"

    def test_parallel_processing_tool_exists(self):
        """Test that parallel processing tool configuration exists."""
        tool_config = load_tool("parallel_processing")

        assert tool_config is not None
        assert tool_config["name"] == "parallel_processing"
        assert tool_config["execution_policy"]["default_mode"] == "auto"

    def test_batch_operations_tool_exists(self):
        """Test that batch operations tool configuration exists."""
        tool_config = load_tool("batch_operations")

        assert tool_config is not None
        assert tool_config["name"] == "batch_operations"
        assert tool_config["execution_policy"]["default_mode"] == "manual"

    def test_simulated_error_scenario(self):
        """Test simulated error scenario and agent response."""
        # This would normally test the actual agent behavior
        # For now, we test that the required components exist

        # Load agent
        agent_config = load_agent("self_improvement_agent")
        assert agent_config is not None

        # Load error analysis tool
        error_tool = load_tool("error_analysis")
        assert error_tool is not None

        # Load feedback loop tool
        feedback_tool = load_tool("feedback_loop")
        assert feedback_tool is not None

        # Load lifecycle management tool
        lifecycle_tool = load_tool("lifecycle_management")
        assert lifecycle_tool is not None

        # Verify all components are properly configured
        assert all([
            agent_config,
            error_tool,
            feedback_tool,
            lifecycle_tool
        ]), "All required components for self-improvement must be present"

    def test_agent_rules_include_self_improvement(self):
        """Test that agent rules include self-improvement guidelines."""
        agent_config = load_agent("self_improvement_agent")

        assert agent_config is not None
        assert "imports" in agent_config
        assert "rules" in agent_config["imports"]

        # Check that self-improvement rules are included
        rule_files = agent_config["imports"]["rules"]
        self_improvement_rules_found = any(
            "self_improvement_rules" in rule for rule in rule_files
        )

        assert self_improvement_rules_found, "Self-improvement rules must be included in agent configuration"


if __name__ == "__main__":
    # Run basic tests
    test_instance = TestSelfImprovementAgent()

    try:
        test_instance.test_agent_configuration_loading()
        print("✓ Agent configuration loading test passed")

        test_instance.test_error_analysis_tool_exists()
        print("✓ Error analysis tool test passed")

        test_instance.test_feedback_loop_tool_exists()
        print("✓ Feedback loop tool test passed")

        test_instance.test_lifecycle_management_tool_exists()
        print("✓ Lifecycle management tool test passed")

        test_instance.test_parallel_processing_tool_exists()
        print("✓ Parallel processing tool test passed")

        test_instance.test_batch_operations_tool_exists()
        print("✓ Batch operations tool test passed")

        test_instance.test_simulated_error_scenario()
        print("✓ Simulated error scenario test passed")

        test_instance.test_agent_rules_include_self_improvement()
        print("✓ Agent rules test passed")

        print("\n🎉 All self-improvement agent tests passed!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)