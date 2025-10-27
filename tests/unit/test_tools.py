#!/usr/bin/env python3
"""
Unit tests for tool implementations
"""

import unittest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestToolImplementations(unittest.TestCase):
    """Test tool implementations"""

    def test_code_analysis_import(self):
        """Test code analysis module can be imported"""
        try:
            from tool_implementations.code_analysis import CodeAnalyzer
            analyzer = CodeAnalyzer()
            self.assertIsInstance(analyzer, CodeAnalyzer)
        except ImportError as e:
            self.fail(f"Failed to import CodeAnalyzer: {e}")

    def test_pattern_analyzer_import(self):
        """Test pattern analyzer module can be imported"""
        try:
            from tool_implementations.pattern_analyzer import PatternAnalyzer
            analyzer = PatternAnalyzer()
            self.assertIsInstance(analyzer, PatternAnalyzer)
        except ImportError as e:
            self.fail(f"Failed to import PatternAnalyzer: {e}")

    def test_config_manager_import(self):
        """Test config manager module can be imported"""
        try:
            from tool_implementations.config_manager import ConfigManager
            manager = ConfigManager()
            self.assertIsInstance(manager, ConfigManager)
        except ImportError as e:
            self.fail(f"Failed to import ConfigManager: {e}")

    def test_framework_tools_import(self):
        """Test framework tools can be imported"""
        framework_tools = [
            'tool_implementations.frameworks.value_effort',
            'tool_implementations.frameworks.eisenhower',
            'tool_implementations.frameworks.swot'
        ]

        for module_name in framework_tools:
            with self.subTest(module=module_name):
                try:
                    __import__(module_name)
                except ImportError as e:
                    self.fail(f"Failed to import {module_name}: {e}")

    def test_code_analysis_basic_functionality(self):
        """Test basic code analysis functionality"""
        from tool_implementations.code_analysis import CodeAnalyzer

        analyzer = CodeAnalyzer()

        # Test with empty input
        result = analyzer.analyze_code("")
        self.assertIn('syntax_errors', result)
        self.assertIn('potential_bugs', result)
        self.assertIn('quality_metrics', result)

    def test_pattern_analyzer_basic_functionality(self):
        """Test basic pattern analysis functionality"""
        from tool_implementations.pattern_analyzer import PatternAnalyzer

        analyzer = PatternAnalyzer()

        # Test with empty input
        result = analyzer.analyze_patterns("")
        self.assertIn('design_patterns', result)
        self.assertIn('anti_patterns', result)
        self.assertIn('summary', result)

    def test_config_manager_basic_functionality(self):
        """Test basic config manager functionality"""
        from tool_implementations.config_manager import ConfigManager

        manager = ConfigManager()

        # Test getting default values
        debug_mode = manager.get('general.debug_mode')
        self.assertIsInstance(debug_mode, bool)

        # Test setting values
        manager.set('test_key', 'test_value')
        value = manager.get('test_key')
        self.assertEqual(value, 'test_value')

class TestFrameworkTools(unittest.TestCase):
    """Test framework-specific tools"""

    def test_value_effort_framework(self):
        """Test value-effort framework processing"""
        from tool_implementations.frameworks.value_effort import process_value_effort

        input_data = {
            'items': [
                {'id': '1', 'title': 'High impact, low effort', 'impact': 0.9, 'effort': 0.2},
                {'id': '2', 'title': 'Low impact, high effort', 'impact': 0.1, 'effort': 0.9}
            ],
            'prefs': {'ui': {'style': 'cards', 'theme': 'neutral'}}
        }

        result = process_value_effort(input_data)

        self.assertEqual(result['layout'], 'quadrant')
        self.assertEqual(result['framework'], 'value_effort')
        self.assertIn('cards', result)
        self.assertIn('quadrants', result)
        self.assertEqual(len(result['cards']), 2)

    def test_eisenhower_framework(self):
        """Test Eisenhower matrix framework processing"""
        from tool_implementations.frameworks.eisenhower import process_eisenhower

        input_data = {
            'items': [
                {'id': '1', 'title': 'Urgent and important', 'urgency': 0.9, 'importance': 0.9},
                {'id': '2', 'title': 'Not urgent, not important', 'urgency': 0.1, 'importance': 0.1}
            ],
            'prefs': {'ui': {'style': 'cards', 'theme': 'neutral'}}
        }

        result = process_eisenhower(input_data)

        self.assertEqual(result['layout'], 'quadrant')
        self.assertEqual(result['framework'], 'eisenhower')
        self.assertIn('cards', result)
        self.assertIn('quadrants', result)

    def test_swot_framework(self):
        """Test SWOT framework processing"""
        from tool_implementations.frameworks.swot import process_swot

        input_data = {
            'buckets': {
                'S': [{'id': '1', 'title': 'Strength 1'}],
                'W': [{'id': '2', 'title': 'Weakness 1'}],
                'O': [{'id': '3', 'title': 'Opportunity 1'}],
                'T': [{'id': '4', 'title': 'Threat 1'}]
            },
            'prefs': {'ui': {'style': 'cards', 'theme': 'neutral'}}
        }

        result = process_swot(input_data)

        self.assertEqual(result['layout'], 'swot_grid')
        self.assertEqual(result['framework'], 'SWOT')
        self.assertIn('sections', result)
        self.assertIn('S', result['sections'])
        self.assertIn('W', result['sections'])
        self.assertIn('O', result['sections'])
        self.assertIn('T', result['sections'])

if __name__ == '__main__':
    unittest.main()