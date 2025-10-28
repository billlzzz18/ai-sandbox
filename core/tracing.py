"""
OpenTelemetry tracing integration for the AI Agent Framework.

This module sets up distributed tracing across components like Bus, Orchestrator,
Agent, Tool, and Memory operations. Uses correlation IDs for end-to-end visibility.

Requires: pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp
"""

from __future__ import annotations

import uuid
from typing import Any, ContextManager, Dict, Optional
from contextlib import contextmanager

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes

# Global tracer provider setup
tracer_provider = TracerProvider(
    resource=Resource(attributes={
        ResourceAttributes.SERVICE_NAME: "ai-agent-framework",
        ResourceAttributes.SERVICE_VERSION: "1.0.0",
    })
)

# Configure exporter (OTLP to collector, e.g., for Jaeger/Grafana)
otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
trace.set_tracer_provider(tracer_provider)

tracer = trace.get_tracer(__name__)

# Correlation ID management
CORRELATION_ID_HEADER = "x-correlation-id"

def generate_correlation_id() -> str:
    """Generate a new UUID for correlation."""
    return str(uuid.uuid4())

@contextmanager
def start_span(
    name: str,
    attributes: Optional[Dict[str, Any]] = None,
    parent_context: Optional[trace.SpanContext] = None
) -> ContextManager[trace.Span]:
    """Context manager for creating a span with optional attributes."""
    ctx = trace.set_span_in_context(trace.SpanContext(), parent_context) if parent_context else trace.set_span_in_context(tracer.start_as_current_span(name))
    with tracer.start_as_current_span(name, context=ctx) as span:
        if attributes:
            span.set_attributes(attributes)
        correlation_id = generate_correlation_id()
        span.set_attribute("correlation.id", correlation_id)
        yield span
        span.end()

def get_current_correlation_id() -> Optional[str]:
    """Get the current correlation ID from the active span."""
    span = trace.get_current_span()
    if span.is_recording():
        return span.get_attribute("correlation.id")
    return None

def propagate_correlation_id(headers: Dict[str, str]) -> Dict[str, str]:
    """Add correlation ID to headers for propagation."""
    corr_id = get_current_correlation_id()
    if corr_id:
        headers[CORRELATION_ID_HEADER] = corr_id
    return headers

# Instrumentation examples for key components

def instrument_loader_load_agent(agent_name: str) -> Dict[str, Any]:
    """Instrumented version of load_agent with tracing."""
    with start_span("load_agent", attributes={"agent.name": agent_name}):
        from loader import load_agent as _load_agent
        try:
            result = _load_agent(agent_name)
            trace.get_current_span().set_attribute("load.success", True)
            return result
        except Exception as e:
            trace.get_current_span().set_attribute("load.success", False)
            trace.get_current_span().record_exception(e)
            raise

def instrument_memory_operation(operation: str, namespace: str, key: Optional[str] = None):
    """Instrument memory operations with tracing."""
    attributes = {
        "memory.operation": operation,
        "memory.namespace": namespace,
    }
    if key:
        attributes["memory.key"] = key
    with start_span("memory_operation", attributes=attributes):
        # Placeholder for actual memory impl
        # e.g., memory.write(namespace, key, value)
        pass  # Simulate operation
        trace.get_current_span().set_attribute("memory.success", True)

def instrument_tool_call(tool_name: str, args: Dict[str, Any]):
    """Instrument tool calls."""
    with start_span("tool_call", attributes={"tool.name": tool_name, "tool.args_count": len(args)}):
        # Placeholder for tool execution
        pass
        trace.get_current_span().set_attribute("tool.success", True)

# Metrics integration (basic counter/gauge using OTEL metrics)
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

metric_reader = PeriodicExportingMetricReader(OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True))
meter_provider = MeterProvider(metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)
meter = metrics.get_meter(__name__)

# Key metrics
queue_depth = meter.create_gauge("queue.depth", description="Current queue depth")
wait_time_p95 = meter.create_histogram("wait.time.p95", unit="ms", description="P95 wait time")
success_rate = meter.create_counter("workflow.success", description="Successful workflows")
agent_cpu = meter.create_gauge("agent.cpu.usage", unit="%", description="Agent CPU usage")
memory_hit_rate = meter.create_gauge("memory.hit.rate", unit="%", description="Memory hit rate")

def record_queue_depth(depth: int):
    queue_depth.record(depth)

def record_wait_time_p95(time_ms: float):
    wait_time_p95.record(time_ms)

def record_success():
    success_rate.add(1, attributes={"type": "workflow"})

def record_agent_cpu(usage: float, agent_name: str):
    agent_cpu.record(usage, attributes={"agent.name": agent_name})

def record_memory_hit_rate(rate: float):
    memory_hit_rate.record(rate)

# SLO definitions (as constants for now; could be loaded from config)
SLO_DEFINITIONS = {
    "success_rate": {"target": 99.0, "period": "30d", "unit": "%"},
    "p95_end_to_end": {"target": 2000, "unit": "ms"},
    "error_budget": {"max": 5.0, "unit": "%"},
    "queue_depth_max": 1000,
    "memory_hit_rate_min": 80.0
}

__all__ = [
    "start_span",
    "get_current_correlation_id",
    "propagate_correlation_id",
    "instrument_loader_load_agent",
    "instrument_memory_operation",
    "instrument_tool_call",
    "record_queue_depth",
    "record_wait_time_p95",
    "record_success",
    "record_agent_cpu",
    "record_memory_hit_rate",
    "SLO_DEFINITIONS"
]