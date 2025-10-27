# tools/standard_tools.py

import os
import subprocess
import tempfile

def read_file(*args, **kwargs):
    """Read file content from filesystem"""
    file_path = kwargs.get('file_path', args[0] if args else '')
    if not file_path:
        return {"status": "error", "error": "No file path provided"}

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"[TOOL EXECUTED] read_file: {file_path} ({len(content)} chars)")
        return {"status": "success", "content": content}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def write_file(*args, **kwargs):
    """Write content to file"""
    file_path = kwargs.get('file_path', args[0] if args else '')
    content = kwargs.get('content', args[1] if len(args) > 1 else '')

    if not file_path:
        return {"status": "error", "error": "No file path provided"}

    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[TOOL EXECUTED] write_file: {file_path} ({len(content)} chars)")
        return {"status": "success", "message": "File written successfully."}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def delete_file(*args, **kwargs):
    """Delete file from filesystem"""
    file_path = kwargs.get('file_path', args[0] if args else '')
    if not file_path:
        return {"status": "error", "error": "No file path provided"}

    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"[TOOL EXECUTED] delete_file: {file_path}")
            return {"status": "success", "message": "File deleted."}
        else:
            return {"status": "error", "error": "File not found"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def execute_code(*args, **kwargs):
    """Execute code in a safe environment"""
    code = kwargs.get('code', args[0] if args else '')
    language = kwargs.get('language', 'python')

    if not code:
        return {"status": "error", "error": "No code provided"}

    try:
        if language.lower() == 'python':
            # Execute Python code
            result = subprocess.run(
                ['python3', '-c', code],
                capture_output=True,
                text=True,
                timeout=30
            )
            output = result.stdout
            error = result.stderr
        else:
            return {"status": "error", "error": f"Unsupported language: {language}"}

        print(f"[TOOL EXECUTED] execute_code: {language} ({len(code)} chars)")
        return {
            "status": "success",
            "output": output,
            "error": error,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"status": "error", "error": "Code execution timed out"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def open_in_vscode(*args, **kwargs):
    """Open file in VS Code"""
    file_path = kwargs.get('file_path', args[0] if args else '')
    if not file_path:
        return {"status": "error", "error": "No file path provided"}

    try:
        # Try to open with code command (VS Code CLI)
        result = subprocess.run(['code', file_path], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[TOOL EXECUTED] open_in_vscode: {file_path}")
            return {"status": "success", "message": "Opened in VS Code."}
        else:
            return {"status": "error", "error": "VS Code not available"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def search(*args, **kwargs):
    """Search for text in files"""
    query = kwargs.get('query', args[0] if args else '')
    path = kwargs.get('path', '.')

    if not query:
        return {"status": "error", "error": "No search query provided"}

    try:
        # Use grep for searching
        result = subprocess.run(
            ['grep', '-r', '-n', query, path],
            capture_output=True,
            text=True
        )

        results = []
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.split(':', 2)
                    if len(parts) >= 3:
                        results.append({
                            'file': parts[0],
                            'line': int(parts[1]),
                            'content': parts[2]
                        })

        print(f"[TOOL EXECUTED] search: '{query}' in {path} ({len(results)} matches)")
        return {"status": "success", "results": results}
    except Exception as e:
        return {"status": "error", "error": str(e)}
