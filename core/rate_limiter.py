"""
Rate limiting and quota management for the AI Agent Framework.

Implements per-user/workflow quotas for RPS, tokens, CPU, outbound calls.
Supports budget alerts and auto-throttle. Uses in-memory storage for simplicity;
extend to Redis for production.

Requires: pip install redis (optional for distributed)
"""

from __future__ import annotations

import time
from typing import Dict, Optional, Tuple
from collections import defaultdict, deque
from dataclasses import dataclass
from contextlib import contextmanager

# For distributed, import redis if available
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

@dataclass
class Quota:
    """Quota configuration."""
    rps: int = 10  # Requests per second
    tokens_per_min: int = 10000
    cpu_time_per_min: float = 60.0  # CPU seconds per minute
    outbound_calls_per_min: int = 50
    budget_alert_threshold: float = 0.8  # Alert at 80% budget usage

class RateLimiter:
    """Rate limiter with sliding window for quotas."""
    def __init__(self, use_redis: bool = False, redis_url: str = "redis://localhost:6379"):
        self.quotas = defaultdict(Quota)
        self._windows: Dict[str, deque] = defaultdict(deque)  # entity -> timestamps
        self._usage: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))  # entity -> metric -> usage
        self.use_redis = use_redis and REDIS_AVAILABLE
        if self.use_redis:
            self.redis_client = redis.from_url(redis_url)
        self.alerts = []  # List of (entity, message)

    def set_quota(self, entity: str, quota: Quota):
        """Set quota for an entity (user_id or workflow_id)."""
        self.quotas[entity] = quota

    @contextmanager
    def acquire(self, entity: str, action: str = "request", cost: Dict[str, float] = None) -> Tuple[bool, Optional[str]]:
        """
        Acquire quota for an action. Returns (allowed, error_msg).
        cost: e.g., {"tokens": 500, "cpu": 2.5, "outbound": 1}
        """
        if cost is None:
            cost = {"tokens": 0, "cpu": 0, "outbound": 0}

        quota = self.quotas[entity]
        now = time.time()
        window_size = 60  # 1 minute sliding window

        # Sliding window for RPS
        self._windows[entity].append(now)
        while self._windows[entity] and self._windows[entity][0] < now - window_size:
            self._windows[entity].popleft()
        rps_current = len(self._windows[entity])
        if rps_current >= quota.rps:
            return False, f"RPS limit exceeded: {rps_current}/{quota.rps}"

        # Check other metrics (reset every minute)
        for metric, value in cost.items():
            if metric == "tokens":
                limit = quota.tokens_per_min
            elif metric == "cpu":
                limit = quota.cpu_time_per_min
            elif metric == "outbound":
                limit = quota.outbound_calls_per_min
            else:
                continue

            # Simple per-minute counter (reset at minute boundary)
            minute_key = int(now // 60)
            if minute_key != self._usage[entity][metric].get("minute", 0):
                self._usage[entity][metric] = {"minute": minute_key, "total": 0}
            self._usage[entity][metric]["total"] += value

            if self._usage[entity][metric]["total"] > limit:
                return False, f"{metric} quota exceeded: {self._usage[entity][metric]['total']}/{limit}"

        # Check budget (simplified: total usage across all)
        total_usage = sum(self._usage[entity][m]["total"] for m in self._usage[entity])
        if total_usage > quota.budget_alert_threshold * 100:  # Assume budget=100 units
            self.alerts.append((entity, f"Budget alert: {total_usage}% used"))

        return True, None

    def get_usage(self, entity: str) -> Dict[str, float]:
        """Get current usage for entity."""
        return {k: v["total"] for k, v in self._usage[entity].items()}

    def auto_throttle(self, entity: str, factor: float = 0.5) -> bool:
        """Auto-throttle by reducing quotas if over budget."""
        usage = self.get_usage(entity)
        if any(u > 1.0 for u in usage.values()):  # Over 100%
            quota = self.quotas[entity]
            self.quotas[entity] = Quota(
                rps=int(quota.rps * factor),
                tokens_per_min=int(quota.tokens_per_min * factor),
                cpu_time_per_min=quota.cpu_time_per_min * factor,
                outbound_calls_per_min=int(quota.outbound_calls_per_min * factor)
            )
            return True
        return False

# Global instance
limiter = RateLimiter(use_redis=False)  # Set use_redis=True in prod

# Cost reporting (integrate with tracing/metrics)
def report_cost(entity: str, costs: Dict[str, float]):
    """Report costs for workflow/agent, integrate with OTEL metrics."""
    from core.tracing import record_agent_cpu, record_memory_hit_rate  # Example
    # Placeholder: send to metrics
    total_cost = sum(costs.values())
    print(f"Cost report for {entity}: {total_cost}")  # Replace with actual reporting

__all__ = ["RateLimiter", "Quota", "limiter", "report_cost"]