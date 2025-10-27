# tools/code_analysis.py

import ast
import re
from typing import Dict, List, Any, Optional
from pathlib import Path


class CodeAnalyzer:
    """Code analysis tool for Python code"""

    def __init__(self):
        self.metrics = {}

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a Python file and return metrics"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            metrics = {
                'lines_of_code': len(content.splitlines()),
                'functions': len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]),
                'classes': len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]),
                'imports': len([node for node in ast.walk(tree) if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom)]),
                'complexity': self._calculate_complexity(tree),
                'file_path': file_path
            }

            return metrics

        except Exception as e:
            return {"error": f"Failed to analyze file {file_path}: {str(e)}"}

    def analyze_code(self, code: str) -> Dict[str, Any]:
        """Analyze a code string and return metrics"""
        try:
            tree = ast.parse(code)

            metrics = {
                'lines_of_code': len(code.splitlines()),
                'functions': len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]),
                'classes': len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]),
                'imports': len([node for node in ast.walk(tree) if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom)]),
                'complexity': self._calculate_complexity(tree),
                'syntax_errors': [],  # No syntax errors if parsing succeeded
                'potential_bugs': [],  # Would need more sophisticated analysis
                'quality_metrics': {
                    'maintainability_index': 100,  # Simplified metric
                    'test_coverage': 0  # Would need test files
                }
            }

            return metrics

        except SyntaxError as e:
            return {
                "error": f"Syntax error in code: {str(e)}",
                'syntax_errors': [str(e)],
                'potential_bugs': [],
                'quality_metrics': {}
            }
        except Exception as e:
            return {
                "error": f"Failed to analyze code: {str(e)}",
                'syntax_errors': [],
                'potential_bugs': [],
                'quality_metrics': {}
            }

    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.Try)):
                complexity += 1
            elif isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And):
                complexity += len(node.values) - 1

        return complexity

    def find_patterns(self, code: str, patterns: List[str]) -> Dict[str, List[int]]:
        """Find code patterns and return line numbers"""
        results = {}
        lines = code.splitlines()

        for pattern in patterns:
            results[pattern] = []
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    results[pattern].append(i)

        return results


def analyze_code(*args, **kwargs):
    """Main function for code analysis tool"""
    analyzer = CodeAnalyzer()

    if 'file_path' in kwargs:
        return analyzer.analyze_file(kwargs['file_path'])
    elif 'code' in kwargs:
        return analyzer.analyze_code(kwargs['code'])
    else:
        return {"error": "No file_path or code provided"}