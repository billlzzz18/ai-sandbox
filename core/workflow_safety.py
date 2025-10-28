"""
Workflow safety and idempotency module for the AI Agent Framework.

Implements step-level dedupe keys, replay journal (append-only log), exactly-once semantics
via outbox pattern/job tokens, and deterministic templating (seed freezing, clock injection,
content-addressed artifacts).

Uses in-memory for demo; extend to durable storage (e.g., Kafka for outbox).
"""

from __future__ import annotations

import time
import hashlib
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from contextlib import contextmanager
import random
import uuid

from .tracing import start_span, record_success
from .memory import memory  # For storing journal/replays
from .rate_limiter import limiter

@dataclass
class StepExecution:
    """Step execution record for idempotency."""
    step_id: str
    dedupe_key: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    executed_at: datetime
    status: str  # "success", "failed", "replayed"
    job_token: str

class WorkflowSafetyError(Exception):
    """Raised for workflow safety violations."""

class WorkflowSafety:
    """Manages idempotency and safety for workflows."""
    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id
        self.journal: List[StepExecution] = []  # Append-only replay journal
        self.outbox: Dict[str, Any] = {}  # Outbox for exactly-once
        self.seed = int(time.time())  # Freeze random seed for determinism
        random.seed(self.seed)
        self.clock_injected = datetime.now().isoformat()  # Inject clock

    @contextmanager
    def execute_step(self, step_id: str, inputs: Dict[str, Any], dedupe_key: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Execute step with idempotency check. Returns (is_replay, outputs).
        dedupe_key: Content-addressed hash of inputs for dedupe.
        """
        with start_span("workflow_step_execute", attributes={"workflow.id": self.workflow_id, "step.id": step_id}):
            # Generate dedupe key if not provided (content-addressed)
            if not dedupe_key:
                dedupe_key = self._content_address(inputs)

            # Check idempotency (replay if exists)
            existing = self._find_step(dedupe_key)
            if existing:
                record_success()  # Count as success for replay
                return True, existing.outputs  # Replay

            # Outbox pattern for exactly-once: Prepare job token
            job_token = str(uuid.uuid4())
            outbox_entry = {"step_id": step_id, "dedupe_key": dedupe_key, "inputs": inputs, "job_token": job_token}
            self.outbox[job_token] = outbox_entry

            # Deterministic templating: Inject seed and clock
            deterministic_inputs = inputs.copy()
            deterministic_inputs["__seed"] = self.seed
            deterministic_inputs["__clock"] = self.clock_injected

            # Simulate execution (replace with actual step logic)
            outputs = self._simulate_step(step_id, deterministic_inputs)

            # Record in journal (append-only)
            execution = StepExecution(
                step_id=step_id,
                dedupe_key=dedupe_key,
                inputs=inputs,
                outputs=outputs,
                executed_at=datetime.now(),
                status="success",
                job_token=job_token
            )
            self.journal.append(execution)

            # Persist to memory for durability
            memory.write(f"workflow_{self.workflow_id}_journal", f"step_{len(self.journal)}", execution.__dict__, reason="workflow_safety")

            # Remove from outbox on success
            del self.outbox[job_token]

            record_success()
            return False, outputs

    def _find_step(self, dedupe_key: str) -> Optional[StepExecution]:
        """Find existing step by dedupe key."""
        for exec in self.journal:
            if exec.dedupe_key == dedupe_key:
                return exec
        # Check memory for persisted journal
        persisted = memory.read(f"workflow_{self.workflow_id}_journal", dedupe_key, "idempotency_check")
        if persisted:
            return StepExecution(**persisted)
        return None

    def _content_address(self, data: Any) -> str:
        """Generate content-addressed key (SHA-256 hash)."""
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def _simulate_step(self, step_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate step execution (deterministic based on seed/clock)."""
        # Use injected seed for random ops
        random.seed(self.seed)
        # Example: Deterministic "random" output
        simulated_output = {
            "result": random.randint(1, 100),
            "processed_at": self.clock_injected
        }
        # Quota check
        limiter.acquire(self.workflow_id, "step_exec", {"tokens": len(str(inputs))})
        return simulated_output

    def replay_journal(self, from_step: Optional[int] = None) -> List[StepExecution]:
        """Replay journal from step for recovery."""
        start = from_step or 0
        return self.journal[start:]

    def get_outbox(self) -> Dict[str, Any]:
        """Get pending outbox entries for exactly-once delivery."""
        return self.outbox.copy()

# Global registry (per workflow)
workflows_safety: Dict[str, WorkflowSafety] = {}

def get_workflow_safety(workflow_id: str) -> WorkflowSafety:
    if workflow_id not in workflows_safety:
        workflows_safety[workflow_id] = WorkflowSafety(workflow_id)
    return workflows_safety[workflow_id]

__all__ = ["WorkflowSafety", "WorkflowSafetyError", "get_workflow_safety", "StepExecution"]