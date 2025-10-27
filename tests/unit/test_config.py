#!/usr/bin/env python3
"""
Unit tests for configuration system
"""

import unittest
import tempfile
import json
import yaml
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tool_implementations.config_manager import ConfigManager

class TestConfigManager(unittest.TestCase):
    """Test ConfigManager functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_file = self.temp_dir / "test_config.yaml"

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_config_initialization(self):
        """Test ConfigManager initialization"""
        manager = ConfigManager(str(self.temp_dir))

        # Should have default config
        self.assertIsInstance(manager.config, dict)
        self.assertIn('general', manager.config)
        self.assertIn('code_analysis', manager.config)

    def test_config_get_set(self):
        """Test getting and setting config values"""
        manager = ConfigManager(str(self.temp_dir))

        # Test getting default value
        debug_mode = manager.get('general.debug_mode')
        self.assertIsInstance(debug_mode, bool)

        # Test setting value
        manager.set('test_key', 'test_value')
        value = manager.get('test_key')
        self.assertEqual(value, 'test_value')

        # Test nested keys
        manager.set('nested.deep.value', 42)
        nested_value = manager.get('nested.deep.value')
        self.assertEqual(nested_value, 42)

    def test_config_save_load(self):
        """Test saving and loading configuration"""
        manager = ConfigManager(str(self.temp_dir))

        # Set some test values
        manager.set('test.string', 'hello')
        manager.set('test.number', 123)
        manager.set('test.boolean', True)

        # Save config
        success = manager.save()
        self.assertTrue(success)
        self.assertTrue(self.config_file.exists())

        # Create new manager and load
        new_manager = ConfigManager(str(self.temp_dir))

        # Check values were loaded
        self.assertEqual(new_manager.get('test.string'), 'hello')
        self.assertEqual(new_manager.get('test.number'), 123)
        self.assertEqual(new_manager.get('test.boolean'), True)

    def test_config_validation(self):
        """Test configuration validation"""
        manager = ConfigManager(str(self.temp_dir))

        # Valid config should pass
        validation = manager.validate_config()
        self.assertTrue(validation['valid'])
        self.assertEqual(len(validation['errors']), 0)

        # Set invalid values
        manager.set('general.max_concurrent_operations', 0)  # Should be > 0
        manager.set('gemini.temperature', 3.0)  # Should be 0-2

        validation = manager.validate_config()
        self.assertFalse(validation['valid'])
        self.assertGreater(len(validation['errors']), 0)

    def test_custom_patterns(self):
        """Test custom patterns functionality"""
        manager = ConfigManager(str(self.temp_dir))

        # Test loading custom patterns
        patterns = manager.get_custom_patterns()
        self.assertIsInstance(patterns, dict)
        self.assertIn('patterns', patterns)

        # Test saving custom patterns
        test_patterns = {
            'patterns': [
                {
                    'name': 'test_pattern',
                    'regex': 'test.*',
                    'description': 'Test pattern',
                    'severity': 'info'
                }
            ],
            'functions': {}
        }

        success = manager.save_custom_patterns(test_patterns)
        self.assertTrue(success)

        # Load and verify
        loaded_patterns = manager.get_custom_patterns()
        self.assertEqual(len(loaded_patterns['patterns']), 1)
        self.assertEqual(loaded_patterns['patterns'][0]['name'], 'test_pattern')

    def test_session_logging(self):
        """Test session logging functionality"""
        manager = ConfigManager(str(self.temp_dir))

        test_entry = {
            'timestamp': 1234567890,
            'action': 'test_action',
            'data': {'key': 'value'}
        }

        manager.log_session_entry(test_entry)

        history_file = manager.get_session_history_file()
        self.assertTrue(history_file.exists())

        with open(history_file, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn('test_action', content)
        self.assertIn('1234567890', content)

    def test_long_term_logging(self):
        """Test long-term data logging"""
        manager = ConfigManager(str(self.temp_dir))

        test_entry = {
            'timestamp': 1234567890,
            'type': 'test_data',
            'content': {'test': 'value'}
        }

        manager.log_long_term_entry(test_entry, 'test')

        data_file = manager.get_long_term_data_file('test')
        self.assertTrue(data_file.exists())

        with open(data_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        self.assertEqual(len(lines), 1)

        loaded_entry = json.loads(lines[0])
        self.assertEqual(loaded_entry['type'], 'test_data')
        self.assertEqual(loaded_entry['content']['test'], 'value')

    def test_config_defaults(self):
        """Test that all default values are present"""
        manager = ConfigManager(str(self.temp_dir))

        # Check some key defaults
        self.assertEqual(manager.get('general.debug_mode'), False)
        self.assertEqual(manager.get('general.log_level'), 'INFO')
        self.assertEqual(manager.get('code_analysis.default_language'), 'python')
        self.assertEqual(manager.get('gemini.default_model'), 'gemini-1.5-flash')

    def test_config_deep_merge(self):
        """Test deep merging of user config with defaults"""
        # Create a config file with partial overrides
        user_config = {
            'general': {
                'debug_mode': True
            },
            'code_analysis': {
                'default_language': 'javascript'
            }
        }

        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(user_config, f)

        manager = ConfigManager(str(self.temp_dir))

        # Check that user values override defaults
        self.assertEqual(manager.get('general.debug_mode'), True)
        self.assertEqual(manager.get('code_analysis.default_language'), 'javascript')

        # Check that other defaults are preserved
        self.assertEqual(manager.get('general.log_level'), 'INFO')
        self.assertEqual(manager.get('gemini.default_model'), 'gemini-1.5-flash')

if __name__ == '__main__':
    unittest.main()