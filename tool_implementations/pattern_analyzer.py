# tools/pattern_analyzer.py

import re
from typing import Dict, List, Any, Optional, Pattern
from collections import defaultdict


class PatternAnalyzer:
    """Pattern analysis tool for code and text"""

    def __init__(self):
        self.common_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'url': r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
            'function_def': r'def\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\(',
            'class_def': r'class\s+[a-zA-Z_][a-zA-Z0-9_]*',
            'import_statement': r'^(?:from\s+[a-zA-Z_][a-zA-Z0-9_.]*\s+)?import\s+',
            'comment': r'#.*$',
            'docstring': r'""".*?"""',
            'variable_assignment': r'[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*',
            'function_call': r'[a-zA-Z_][a-zA-Z0-9_]*\s*\(',
        }

    def analyze_text(self, text: str, custom_patterns: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Analyze text for patterns"""
        patterns = {**self.common_patterns}
        if custom_patterns:
            patterns.update(custom_patterns)

        results = {}
        lines = text.splitlines()

        for pattern_name, pattern_regex in patterns.items():
            try:
                compiled_pattern = re.compile(pattern_regex, re.MULTILINE | re.IGNORECASE)
                matches = compiled_pattern.findall(text)

                line_numbers = []
                for i, line in enumerate(lines, 1):
                    if compiled_pattern.search(line):
                        line_numbers.append(i)

                results[pattern_name] = {
                    'count': len(matches),
                    'matches': matches[:10],  # Limit to first 10 matches
                    'line_numbers': line_numbers[:10],  # Limit to first 10 lines
                    'total_lines': len(line_numbers)
                }

            except re.error as e:
                results[pattern_name] = {
                    'error': f'Invalid regex pattern: {e}',
                    'count': 0,
                    'matches': [],
                    'line_numbers': [],
                    'total_lines': 0
                }

        return results

    def analyze_patterns(self, code: str, patterns: Optional[List[str]] = None) -> Dict[str, Any]:
        """Analyze code for design patterns and anti-patterns"""
        if patterns is None:
            patterns = ['singleton', 'factory', 'observer', 'decorator']

        results = {
            'design_patterns': {},
            'anti_patterns': {},
            'summary': {
                'total_patterns_found': 0,
                'complexity_score': 0
            }
        }

        # Simple pattern detection (would need more sophisticated analysis in real implementation)
        for pattern in patterns:
            if pattern.lower() in code.lower():
                results['design_patterns'][pattern] = ['Found in code']

        # Basic anti-pattern detection
        if 'global ' in code:
            results['anti_patterns']['global_variables'] = ['Global variables detected']
        if code.count('except:') > code.count('except Exception:'):
            results['anti_patterns']['bare_except'] = ['Bare except clauses found']

        results['summary']['total_patterns_found'] = len(results['design_patterns']) + len(results['anti_patterns'])

        return results

    def find_code_smells(self, code: str) -> Dict[str, List[int]]:
        """Find common code smells and return line numbers"""
        lines = code.splitlines()
        smells = defaultdict(list)

        for i, line in enumerate(lines, 1):
            # Long lines
            if len(line) > 100:
                smells['long_line'].append(i)

            # Multiple statements on one line
            if line.count(';') > 1:
                smells['multiple_statements'].append(i)

            # Deep nesting (basic check)
            indent_level = len(line) - len(line.lstrip())
            if indent_level > 24:  # More than 6 levels of 4-space indentation
                smells['deep_nesting'].append(i)

            # Magic numbers
            magic_numbers = re.findall(r'\b\d{2,}\b', line)
            if magic_numbers and not any(word in line.lower() for word in ['import', 'def', 'class', 'if', 'for', 'while']):
                smells['magic_numbers'].append(i)

            # Unused variables (basic check - variables assigned but not used in next few lines)
            # This is a simplified check
            if re.search(r'[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*[^=]', line):
                var_match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*[^=]', line)
                if var_match:
                    var_name = var_match.group(1)
                    # Check if variable is used in the next 5 lines
                    used = False
                    for j in range(min(5, len(lines) - i)):
                        next_line = lines[i + j]
                        if re.search(r'\b' + re.escape(var_name) + r'\b', next_line):
                            used = True
                            break
                    if not used and var_name not in ['self', 'cls']:
                        smells['potentially_unused_variable'].append(i)

        return dict(smells)

    def extract_functions_and_classes(self, code: str) -> Dict[str, List[Dict[str, Any]]]:
        """Extract function and class definitions with their signatures"""
        functions = []
        classes = []

        # Find function definitions
        func_pattern = r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*?)\):'
        for match in re.finditer(func_pattern, code, re.MULTILINE):
            func_name = match.group(1)
            params = match.group(2).strip()
            line_num = code[:match.start()].count('\n') + 1

            functions.append({
                'name': func_name,
                'parameters': params,
                'line_number': line_num,
                'signature': f'def {func_name}({params}):'
            })

        # Find class definitions
        class_pattern = r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(\([^)]*\))?\s*:'
        for match in re.finditer(class_pattern, code, re.MULTILINE):
            class_name = match.group(1)
            inheritance = match.group(2) if match.group(2) else ''
            line_num = code[:match.start()].count('\n') + 1

            classes.append({
                'name': class_name,
                'inheritance': inheritance,
                'line_number': line_num,
                'signature': f'class {class_name}{inheritance}:'
            })

        return {
            'functions': functions,
            'classes': classes
        }


def pattern_analyzer(*args, **kwargs):
    """Main function for pattern analysis tool"""
    analyzer = PatternAnalyzer()

    if 'text' in kwargs:
        return analyzer.analyze_text(kwargs['text'], kwargs.get('custom_patterns'))
    elif 'code' in kwargs:
        if 'find_smells' in kwargs and kwargs['find_smells']:
            return analyzer.find_code_smells(kwargs['code'])
        elif 'extract_definitions' in kwargs and kwargs['extract_definitions']:
            return analyzer.extract_functions_and_classes(kwargs['code'])
        else:
            return analyzer.analyze_text(kwargs['code'])
    else:
        return {"error": "No text or code provided"}