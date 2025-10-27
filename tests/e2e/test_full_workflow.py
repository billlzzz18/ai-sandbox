#!/usr/bin/env python3
"""
End-to-end tests for full system workflow
"""

import unittest
import subprocess
import sys
import tempfile
import time
from pathlib import Path

class TestFullWorkflow(unittest.TestCase):
    """Test complete system workflows"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.original_cwd = Path.cwd()

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_validation_workflow(self):
        """Test complete validation workflow"""
        # Run validation
        result = subprocess.run(
            [sys.executable, 'validate.py'],
            capture_output=True,
            text=True,
            timeout=60
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn('All configuration files are valid', result.stdout)

        # Check that all expected sections are present
        expected_sections = [
            'Validating roles in',
            'Validating tools in',
            'Validating prompts in',
            'Validating rules in',
            'Validating config files in'
        ]

        for section in expected_sections:
            self.assertIn(section, result.stdout)

    def test_config_workflow(self):
        """Test configuration system workflow"""
        from tool_implementations.config_manager import ConfigManager

        # Test with custom config directory
        config_dir = self.temp_dir / 'test_config'
        config_dir.mkdir()

        manager = ConfigManager(str(config_dir))

        # Test full workflow: set, save, reload, validate
        manager.set('test.workflow.value', 'success')
        success = manager.save()
        self.assertTrue(success)

        # Create new manager instance
        new_manager = ConfigManager(str(config_dir))
        value = new_manager.get('test.workflow.value')
        self.assertEqual(value, 'success')

        # Test validation
        validation = new_manager.validate_config()
        self.assertTrue(validation['valid'])

    def test_tool_execution_workflow(self):
        """Test tool execution workflow"""
        # Test that tools can be imported and executed
        try:
            from tool_implementations.code_analysis import CodeAnalyzer
            from tool_implementations.frameworks.value_effort import process_value_effort

            # Test code analysis
            analyzer = CodeAnalyzer()
            result = analyzer.analyze_code("def test(): pass")
            self.assertIn('syntax_errors', result)

            # Test framework tool
            input_data = {
                'items': [{'id': '1', 'title': 'Test', 'impact': 0.8, 'effort': 0.3}],
                'prefs': {'ui': {'style': 'cards'}}
            }
            result = process_value_effort(input_data)
            self.assertEqual(result['layout'], 'quadrant')
            self.assertEqual(result['framework'], 'value_effort')

        except ImportError as e:
            self.fail(f"Tool import failed: {e}")

    def test_router_workflow(self):
        """Test Q4 router workflow"""
        # Test Python router
        try:
            from adapters.python.router import route_tool

            # Test force mode
            result = route_tool({
                'mode': 'force',
                'framework_hint': 'value_effort'
            })
            self.assertIsNotNone(result)
            self.assertEqual(result['name'], 'value_effort')

            # Test bucket-based routing (SWOT)
            result = route_tool({
                'buckets': {
                    'S': [{'id': '1'}],
                    'W': [{'id': '2'}],
                    'O': [{'id': '3'}],
                    'T': [{'id': '4'}]
                }
            })
            self.assertIsNotNone(result)
            self.assertEqual(result['name'], 'swot')

        except ImportError as e:
            self.fail(f"Router import failed: {e}")

    def test_logging_workflow(self):
        """Test logging system workflow"""
        from tool_implementations.config_manager import ConfigManager

        config_dir = self.temp_dir / 'test_config'
        config_dir.mkdir()

        manager = ConfigManager(str(config_dir))

        # Test session logging
        test_entry = {
            'timestamp': time.time(),
            'action': 'test_workflow',
            'result': 'success'
        }

        manager.log_session_entry(test_entry)

        # Verify file was created and contains data
        history_file = manager.get_session_history_file()
        self.assertTrue(history_file.exists())

        with open(history_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('test_workflow', content)

        # Test long-term logging
        manager.log_long_term_entry(test_entry, 'workflow_test')

        data_file = manager.get_long_term_data_file('workflow_test')
        self.assertTrue(data_file.exists())

        with open(data_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 1)

    def test_comprehensive_test_runner(self):
        """Test the comprehensive test runner"""
        from tests.test_framework import ComprehensiveTestRunner

        runner = ComprehensiveTestRunner()
        results = runner.run_all_tests()

        # Should have results for all components
        expected_components = ['tools', 'prompts', 'roles', 'config', 'validation', 'logging']
        for component in expected_components:
            self.assertIn(component, results)
            self.assertIn('total_tests', results[component])
            self.assertIn('passed', results[component])
            self.assertIn('failed', results[component])

        # Generate report
        report = runner.generate_report(results)
        self.assertIn('Comprehensive System Test Report', report)
        self.assertIn('OVERALL SUMMARY', report)

    def test_error_handling_workflow(self):
        """Test error handling throughout the system"""
        from tool_implementations.config_manager import ConfigManager

        # Test with invalid config directory
        manager = ConfigManager('/nonexistent/path')

        # Should still work with defaults
        value = manager.get('general.debug_mode')
        self.assertIsInstance(value, bool)

        # Test invalid config values
        manager.set('general.max_concurrent_operations', -1)
        validation = manager.validate_config()
        self.assertFalse(validation['valid'])
        self.assertGreater(len(validation['errors']), 0)

    def test_schema_validation_workflow(self):
        """Test JSON schema validation workflow"""
        try:
            import jsonschema

            # Test role schema
            with open('schemas/role_schema.json', 'r') as f:
                role_schema = json.load(f)

            # Valid role data
            valid_role = {
                'name': 'test-agent',
                'version': '1.0.0',
                'description': 'Test agent',
                'imports': {
                    'prompts': ['test.yaml'],
                    'rules': ['test.md'],
                    'tools': ['test.yaml']
                }
            }

            # Should validate without error
            jsonschema.validate(valid_role, role_schema)

        except ImportError:
            self.skipTest("jsonschema not available")

    def test_file_structure_integrity(self):
        """Test that all expected files and directories exist"""
        expected_dirs = [
            'role', 'tool_definitions', 'prompt', 'rule', 'config',
            'schemas', 'tool_implementations', 'adapters', 'core',
            'tests', 'template'
        ]

        for dir_name in expected_dirs:
            self.assertTrue(Path(dir_name).exists(), f"Directory {dir_name} not found")
            self.assertTrue(Path(dir_name).is_dir(), f"{dir_name} is not a directory")

        # Check key files
        key_files = [
            'validate.py',
            'package.json',
            'schemas/role_schema.json',
            'schemas/tool_schema.json',
            'config/agent_config.yaml',
            'config/custom_patterns.json'
        ]

        for file_path in key_files:
            self.assertTrue(Path(file_path).exists(), f"File {file_path} not found")
            self.assertTrue(Path(file_path).is_file(), f"{file_path} is not a file")

if __name__ == '__main__':
    unittest.main()