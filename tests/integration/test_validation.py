#!/usr/bin/env python3
"""
Integration tests for validation system
"""

import unittest
import subprocess
import sys
import tempfile
import yaml
import json
from pathlib import Path

class TestValidationSystem(unittest.TestCase):
    """Test the validation system end-to-end"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.original_cwd = Path.cwd()

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_validation_script_execution(self):
        """Test that validation script runs without errors"""
        # Run validation script from project root
        result = subprocess.run(
            [sys.executable, 'validate.py'],
            capture_output=True,
            text=True,
            timeout=30
        )

        self.assertEqual(result.returncode, 0,
                        f"Validation script failed: {result.stderr}")
        self.assertIn('All configuration files are valid', result.stdout)

    def test_role_validation(self):
        """Test role validation with valid and invalid files"""
        # Create test role directory
        role_dir = self.temp_dir / 'role'
        role_dir.mkdir()

        # Create valid role
        valid_role = {
            'name': 'test-agent',
            'version': '1.0.0',
            'description': 'Test agent',
            'imports': {
                'prompts': ['../../prompt/coding/coder_agent_prompt.yaml'],
                'rules': ['../../rule/standard_behavioral_rules.md'],
                'tools': ['../../tool_definitions/file_system/read_file.yaml']
            }
        }

        with open(role_dir / 'valid_role.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(valid_role, f)

        # Create invalid role (missing required fields)
        invalid_role = {
            'name': 'invalid-agent'
            # Missing version, description, imports
        }

        with open(role_dir / 'invalid_role.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(invalid_role, f)

        # Run validation and check it catches the invalid role
        result = subprocess.run(
            [sys.executable, 'validate.py'],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=self.original_cwd
        )

        # Should fail due to invalid role
        self.assertNotEqual(result.returncode, 0)

    def test_tool_validation(self):
        """Test tool validation"""
        # Create test tool directory
        tool_dir = self.temp_dir / 'tool_definitions' / 'test_category'
        tool_dir.mkdir(parents=True)

        # Create valid tool
        valid_tool = {
            'name': 'test_tool',
            'description': 'Test tool description',
            'parameters': [
                {
                    'name': 'param1',
                    'type': 'string',
                    'description': 'Test parameter',
                    'required': True
                }
            ]
        }

        with open(tool_dir / 'valid_tool.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(valid_tool, f)

        # This would require schema validation, but for now just test file creation
        self.assertTrue((tool_dir / 'valid_tool.yaml').exists())

    def test_prompt_validation(self):
        """Test prompt validation"""
        # Create test prompt directory
        prompt_dir = self.temp_dir / 'prompt' / 'test_category'
        prompt_dir.mkdir(parents=True)

        # Create valid prompt
        valid_prompt = {
            'name': 'test-prompt',
            'persona': {
                'role': 'Test Agent',
                'tone': 'Professional and helpful',
                'expertise': 'Testing'
            },
            'prompt': 'You are a test agent.'
        }

        with open(prompt_dir / 'valid_prompt.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(valid_prompt, f)

        # Create invalid prompt (missing required fields)
        invalid_prompt = {
            'name': 'invalid-prompt'
            # Missing persona and prompt
        }

        with open(prompt_dir / 'invalid_prompt.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(invalid_prompt, f)

        # Test validation logic directly
        from validate import _yaml_load

        # Valid prompt should load correctly
        with open(prompt_dir / 'valid_prompt.yaml', 'r', encoding='utf-8') as f:
            data = _yaml_load(f.read())

        self.assertEqual(data['name'], 'test-prompt')
        self.assertIn('persona', data)
        self.assertIn('prompt', data)

    def test_config_validation(self):
        """Test config file validation"""
        # Create test config directory
        config_dir = self.temp_dir / 'config'
        config_dir.mkdir()

        # Create valid config
        valid_config = {
            'general': {
                'debug_mode': False,
                'log_level': 'INFO'
            },
            'code_analysis': {
                'default_language': 'python'
            }
        }

        with open(config_dir / 'agent_config.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(valid_config, f)

        # Create valid JSON config
        json_config = {
            'patterns': [
                {
                    'name': 'test_pattern',
                    'regex': 'test.*',
                    'description': 'Test pattern'
                }
            ]
        }

        with open(config_dir / 'custom_patterns.json', 'w', encoding='utf-8') as f:
            json.dump(json_config, f)

        # Test loading
        from validate import _yaml_load

        with open(config_dir / 'agent_config.yaml', 'r', encoding='utf-8') as f:
            yaml_data = _yaml_load(f.read())

        self.assertEqual(yaml_data['general']['debug_mode'], False)

        with open(config_dir / 'custom_patterns.json', 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        self.assertEqual(len(json_data['patterns']), 1)

    def test_schema_validation(self):
        """Test JSON schema validation"""
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema not available")

        # Test role schema validation
        with open('schemas/role_schema.json', 'r') as f:
            role_schema = json.load(f)

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

        # Should not raise exception
        jsonschema.validate(valid_role, role_schema)

        # Invalid role should raise exception
        invalid_role = {
            'name': 'test-agent'
            # Missing required fields
        }

        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(invalid_role, role_schema)

    def test_validation_output_format(self):
        """Test validation script output format"""
        result = subprocess.run(
            [sys.executable, 'validate.py'],
            capture_output=True,
            text=True,
            timeout=30
        )

        # Check output format
        self.assertIn('--- Running Configuration Validator ---', result.stdout)
        self.assertIn('Validating roles in', result.stdout)
        self.assertIn('Validating tools in', result.stdout)
        self.assertIn('Validating prompts in', result.stdout)
        self.assertIn('Validating rules in', result.stdout)
        self.assertIn('Validating config files in', result.stdout)

        if result.returncode == 0:
            self.assertIn('All configuration files are valid', result.stdout)
        else:
            self.assertIn('Found', result.stdout)
            self.assertIn('errors', result.stdout)

if __name__ == '__main__':
    unittest.main()