#!/usr/bin/env python3
"""
Configuration Manager for CLI Agent
Handles loading, validation, and management of user configurations.
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
import logging

class ConfigManager:
    """Manages configuration files for the CLI agent system"""

    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir) if config_dir else self._get_default_config_dir()
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "agent_config.yaml"
        self.custom_patterns_file = self.config_dir / "custom_patterns.json"
        self.logger = logging.getLogger(__name__)

        # Default configurations
        self.defaults = self._get_defaults()
        self.config = self._load_config()

    def _get_default_config_dir(self) -> Path:
        """Get default configuration directory"""
        # Try user home first, fallback to local config
        home_config = Path.home() / ".agent-config"
        if home_config.exists() or os.access(Path.home(), os.W_OK):
            return home_config
        else:
            return Path("config")

    def _get_defaults(self) -> Dict[str, Any]:
        """Get default configuration values"""
        return {
            'general': {
                'debug_mode': False,
                'log_level': 'INFO',
                'max_concurrent_operations': 5,
                'timeout_seconds': 300
            },
            'code_analysis': {
                'default_language': 'python',
                'syntax_check_enabled': True,
                'quality_metrics_enabled': True,
                'max_file_size_mb': 10,
                'exclude_patterns': ['*.min.js', '*.min.css', 'node_modules/**', '.git/**', '__pycache__/**']
            },
            'pattern_analysis': {
                'design_patterns_enabled': True,
                'anti_patterns_enabled': True,
                'custom_patterns_file': 'custom_patterns.json',
                'max_pattern_matches': 100,
                'pattern_search_timeout': 60
            },
            'best_practices': {
                'standards_to_check': ['solid', 'dry', 'kiss', 'language_specific'],
                'score_thresholds': {
                    'excellent': 90,
                    'good': 70,
                    'needs_improvement': 50
                },
                'generate_reports': True,
                'report_format': 'text'
            },
            'gemini': {
                'api_key_env_var': 'GEMINI_API_KEY',
                'project_env_var': 'GOOGLE_CLOUD_PROJECT',
                'default_model': 'gemini-1.5-flash',
                'max_tokens': 4096,
                'temperature': 0.7,
                'retry_attempts': 3,
                'retry_delay_seconds': 1
            },
            'memory': {
                'short_term_history_file': 'session_history.log',
                'long_term_data_file': 'agent_sessions.jsonl',
                'max_history_entries': 1000,
                'cleanup_old_entries_days': 30
            },
            'tools': {
                'default_execution_mode': 'auto',
                'allow_file_operations': True,
                'allow_network_operations': True,
                'sandbox_enabled': False,
                'execution_timeout_seconds': 60
            },
            'ui': {
                'color_output': True,
                'verbose_output': False,
                'progress_bars': True,
                'table_format': 'fancy'
            },
            'integrations': {
                'git_enabled': True,
                'github_api_enabled': False,
                'vscode_integration': True,
                'external_tools_path': '~/.agent-tools'
            },
            'security': {
                'allow_code_execution': False,
                'validate_inputs': True,
                'sanitize_outputs': True,
                'max_command_length': 1000
            },
            'performance': {
                'cache_enabled': True,
                'cache_ttl_seconds': 3600,
                'parallel_processing': True,
                'memory_limit_mb': 512
            }
        }

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file with defaults fallback"""
        config = self.defaults.copy()

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f) or {}

                # Deep merge user config with defaults
                config = self._deep_merge(config, user_config)
                self.logger.info(f"Loaded configuration from {self.config_file}")

            except Exception as e:
                self.logger.warning(f"Failed to load config file {self.config_file}: {e}")
                self.logger.info("Using default configuration")

        return config

    def _deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries"""
        result = base.copy()

        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-separated key"""
        keys = key.split('.')
        value = self.config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> None:
        """Set configuration value by dot-separated key"""
        keys = key.split('.')
        config = self.config

        # Navigate to the parent dict
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Set the value
        config[keys[-1]] = value

    def save(self) -> bool:
        """Save current configuration to file"""
        try:
            # Create directory if it doesn't exist
            self.config_dir.mkdir(parents=True, exist_ok=True)

            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)

            self.logger.info(f"Saved configuration to {self.config_file}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            return False

    def reload(self) -> bool:
        """Reload configuration from file"""
        try:
            self.config = self._load_config()
            self.logger.info("Configuration reloaded")
            return True
        except Exception as e:
            self.logger.error(f"Failed to reload configuration: {e}")
            return False

    def validate_config(self) -> Dict[str, Any]:
        """Validate current configuration"""
        errors = []
        warnings = []

        # Validate general settings
        if self.get('general.max_concurrent_operations', 0) < 1:
            errors.append("general.max_concurrent_operations must be >= 1")

        if self.get('general.timeout_seconds', 0) <= 0:
            errors.append("general.timeout_seconds must be > 0")

        # Validate code analysis settings
        max_file_size = self.get('code_analysis.max_file_size_mb', 0)
        if max_file_size <= 0 or max_file_size > 100:
            warnings.append("code_analysis.max_file_size_mb should be between 1-100 MB")

        # Validate Gemini settings
        gemini_max_tokens = self.get('gemini.max_tokens', 0)
        if gemini_max_tokens <= 0 or gemini_max_tokens > 32768:
            warnings.append("gemini.max_tokens should be between 1-32768")

        temperature = self.get('gemini.temperature', 0)
        if not 0 <= temperature <= 2:
            errors.append("gemini.temperature must be between 0.0 and 2.0")

        # Validate memory settings
        max_history = self.get('memory.max_history_entries', 0)
        if max_history < 10:
            warnings.append("memory.max_history_entries should be at least 10")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

    def get_custom_patterns(self) -> Dict[str, Any]:
        """Load custom patterns configuration"""
        if self.custom_patterns_file.exists():
            try:
                with open(self.custom_patterns_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load custom patterns: {e}")

        return {'patterns': [], 'functions': {}}

    def save_custom_patterns(self, patterns: Dict[str, Any]) -> bool:
        """Save custom patterns configuration"""
        try:
            with open(self.custom_patterns_file, 'w', encoding='utf-8') as f:
                json.dump(patterns, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save custom patterns: {e}")
            return False

    def get_session_history_file(self) -> Path:
        """Get path to session history file"""
        history_file = self.get('memory.short_term_history_file', 'session_history.log')
        return self.config_dir / history_file

    def get_long_term_data_file(self, data_type: str = 'sessions') -> Path:
        """Get path to long-term data file"""
        data_file = self.get('memory.long_term_data_file', 'agent_sessions.jsonl')
        # Replace placeholder with data type
        data_file = data_file.replace('{data}', data_type)
        return self.config_dir / data_file

    def log_session_entry(self, entry: Dict[str, Any]) -> None:
        """Log an entry to session history"""
        try:
            history_file = self.get_session_history_file()
            timestamp = entry.get('timestamp', '')

            with open(history_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {json.dumps(entry, ensure_ascii=False)}\n")

            # Cleanup old entries if needed
            self._cleanup_history_file()

        except Exception as e:
            self.logger.error(f"Failed to log session entry: {e}")

    def log_long_term_entry(self, entry: Dict[str, Any], data_type: str = 'sessions') -> None:
        """Log an entry to long-term data file"""
        try:
            data_file = self.get_long_term_data_file(data_type)

            with open(data_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')

        except Exception as e:
            self.logger.error(f"Failed to log long-term entry: {e}")

    def _cleanup_history_file(self) -> None:
        """Clean up old entries from session history file"""
        try:
            max_entries = self.get('memory.max_history_entries', 1000)
            history_file = self.get_session_history_file()

            if not history_file.exists():
                return

            # Read all lines
            with open(history_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            if len(lines) > max_entries:
                # Keep only the most recent entries
                lines = lines[-max_entries:]

                with open(history_file, 'w', encoding='utf-8') as f:
                    f.writelines(lines)

        except Exception as e:
            self.logger.warning(f"Failed to cleanup history file: {e}")

    def create_default_config(self) -> bool:
        """Create default configuration file"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)

            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.defaults, f, default_flow_style=False, allow_unicode=True)

            self.logger.info(f"Created default configuration at {self.config_file}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to create default config: {e}")
            return False

    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults"""
        self.config = self.defaults.copy()
        self.logger.info("Configuration reset to defaults")

    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of current configuration"""
        return {
            'config_file': str(self.config_file),
            'config_dir': str(self.config_dir),
            'custom_patterns_file': str(self.custom_patterns_file),
            'has_custom_config': self.config_file.exists(),
            'validation': self.validate_config()
        }


def get_config_manager(config_dir: Optional[str] = None) -> ConfigManager:
    """Factory function to get a ConfigManager instance"""
    return ConfigManager(config_dir)


def init_config_directory(config_dir: Optional[str] = None) -> ConfigManager:
    """Initialize configuration directory and create default config"""
    manager = ConfigManager(config_dir)
    if not manager.config_file.exists():
        manager.create_default_config()
    return manager


if __name__ == '__main__':
    # CLI interface for configuration management
    import argparse

    parser = argparse.ArgumentParser(description='Agent Configuration Manager')
    parser.add_argument('--config-dir', help='Configuration directory')
    parser.add_argument('--init', action='store_true', help='Initialize default configuration')
    parser.add_argument('--validate', action='store_true', help='Validate current configuration')
    parser.add_argument('--summary', action='store_true', help='Show configuration summary')
    parser.add_argument('--reset', action='store_true', help='Reset to default configuration')

    args = parser.parse_args()

    manager = ConfigManager(args.config_dir)

    if args.init:
        success = manager.create_default_config()
        print(f"Default configuration {'created' if success else 'creation failed'}")

    elif args.validate:
        validation = manager.validate_config()
        if validation['valid']:
            print("✅ Configuration is valid")
        else:
            print("❌ Configuration has errors:")
            for error in validation['errors']:
                print(f"  - {error}")

        if validation['warnings']:
            print("⚠️  Warnings:")
            for warning in validation['warnings']:
                print(f"  - {warning}")

    elif args.summary:
        summary = manager.get_config_summary()
        print("Configuration Summary:")
        print(f"  Config file: {summary['config_file']}")
        print(f"  Config directory: {summary['config_dir']}")
        print(f"  Has custom config: {summary['has_custom_config']}")
        print(f"  Valid: {summary['validation']['valid']}")

    elif args.reset:
        manager.reset_to_defaults()
        print("Configuration reset to defaults")

    else:
        parser.print_help()