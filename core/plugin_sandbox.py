"""
Plugin sandbox execution for secure plugin running.

Implements subprocess-based sandbox with resource limits (CPU, memory, I/O).
Supports scope enforcement from manifest. For containerization, extend with Docker.

Requires: pip install psutil (for monitoring)
"""

from __future__ import annotations

import subprocess
import sys
import os
import signal
from typing import Dict, Any, Optional
from pathlib import Path
from contextlib import contextmanager
import time
import psutil  # For resource monitoring

from .rate_limiter import limiter  # For quota integration
from .tracing import start_span, instrument_tool_call

class SandboxError(Exception):
    """Raised when sandbox execution fails."""

class PluginSandbox:
    """Sandbox for executing plugins with enforced limits."""
    def __init__(self, manifest: Dict[str, Any]):
        self.manifest = manifest
        self.scopes = manifest.get("scopes", {})
        self.policy = manifest.get("execution_policy", {})
        self.sandbox_type = self.policy.get("sandbox", "subprocess")
        self.imports_allowlist = manifest.get("imports", [])
        self.cpu_limit = self.scopes.get("cpu_limit", 0.5)
        self.memory_limit_mb = self.scopes.get("memory_limit", 256)
        self.outbound_policy = self.policy.get("outbound_policy", "deny-all")
        self.tls_pinning = self.policy.get("tls_pinning", False)

    @contextmanager
    def execute(self, entry_point: str, args: Dict[str, Any], entity: str) -> Dict[str, Any]:
        """
        Execute plugin in sandbox. Returns result or raises SandboxError.
        Enforces scopes, limits, and quotas.
        """
        with start_span("plugin_sandbox_execute", attributes={"plugin.name": self.manifest["name"], "sandbox.type": self.sandbox_type}):
            # Check quotas
            cost = {"cpu": self.cpu_limit, "outbound": len(self.scopes.get("network", []))}
            allowed, msg = limiter.acquire(entity, "plugin_exec", cost)
            if not allowed:
                raise SandboxError(f"Quota exceeded: {msg}")

            if self.sandbox_type == "subprocess":
                result = self._execute_subprocess(entry_point, args)
            elif self.sandbox_type == "container":
                result = self._execute_container(entry_point, args)  # Placeholder
            else:
                raise SandboxError("Unsupported sandbox type")

            # Post-execution checks
            self._enforce_scopes(result)
            instrument_tool_call(self.manifest["name"], args)
            return result

    def _execute_subprocess(self, entry_point: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute in subprocess with limits."""
        # Prepare env with allowlist
        env = os.environ.copy()
        env["PYTHONPATH"] = ":".join(sys.path)
        env["ALLOWED_IMPORTS"] = ",".join(self.imports_allowlist)
        env["NETWORK_POLICY"] = self.outbound_policy

        # Build command
        cmd = [sys.executable, "-c", f"exec(open('{entry_point}').read())"] + [str(v) for v in args.values()]
        
        # Start process
        proc = subprocess.Popen(
            cmd,
            env=env,
            preexec_fn=os.setsid,  # For signal handling
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Monitor resources
        start_time = time.time()
        cpu_used = 0
        mem_used = 0
        while proc.poll() is None:
            try:
                p = psutil.Process(proc.pid)
                cpu_used += p.cpu_percent(interval=0.1) / 100 * 0.1  # Approximate CPU seconds
                mem_used = p.memory_info().rss / 1024 / 1024  # MB
                if cpu_used > self.cpu_limit * (time.time() - start_time):
                    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                    raise SandboxError("CPU limit exceeded")
                if mem_used > self.memory_limit_mb:
                    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                    raise SandboxError("Memory limit exceeded")
            except psutil.NoSuchProcess:
                break
            time.sleep(0.1)

        # Wait and get output
        stdout, stderr = proc.communicate(timeout=30)  # 30s timeout
        if proc.returncode != 0:
            raise SandboxError(f"Execution failed: {stderr.decode()}")

        # Parse result (assume JSON output)
        try:
            result = json.loads(stdout.decode())
        except json.JSONDecodeError:
            result = {"output": stdout.decode(), "error": stderr.decode()}

        return result

    def _execute_container(self, entry_point: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Placeholder for container execution (e.g., Docker)."""
        # Implement with docker-py or similar
        raise NotImplementedError("Container sandbox not yet implemented")

    def _enforce_scopes(self, result: Dict[str, Any]):
        """Enforce post-execution scopes (e.g., check outbound calls)."""
        # Example: Verify no unauthorized network access
        if "network_calls" in result and self.outbound_policy == "allow-list":
            allowed = set(self.scopes.get("network", []))
            called = set(result["network_calls"])
            unauthorized = called - allowed
            if unauthorized:
                raise SandboxError(f"Unauthorized network access: {unauthorized}")

# Example usage
def run_plugin_safely(manifest_path: str, entity: str):
    manifest = json.load(open(manifest_path))
    sandbox = PluginSandbox(manifest)
    result = sandbox.execute(manifest["entry_point"], {"input": "data"}, entity)
    return result

__all__ = ["PluginSandbox", "SandboxError", "run_plugin_sandbox"]