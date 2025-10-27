# core/workflow_engine/workflow_engine.py

import asyncio
import time
import json
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed


class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepType(Enum):
    TASK = "task"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    LOOP = "loop"


@dataclass
class WorkflowStep:
    """Represents a single step in a workflow"""
    name: str
    step_type: StepType
    agent: Optional[str] = None
    action: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    condition: Optional[str] = None
    parallel_steps: List['WorkflowStep'] = field(default_factory=list)
    loop_config: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'step_type': self.step_type.value,
            'agent': self.agent,
            'action': self.action,
            'parameters': self.parameters,
            'dependencies': self.dependencies,
            'condition': self.condition,
            'parallel_steps': [step.to_dict() for step in self.parallel_steps] if self.parallel_steps else [],
            'loop_config': self.loop_config
        }


@dataclass
class WorkflowExecution:
    """Represents the execution state of a workflow"""
    workflow_id: str
    workflow_config: Dict[str, Any]
    status: WorkflowStatus = WorkflowStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    current_step: Optional[str] = None
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'workflow_id': self.workflow_id,
            'status': self.status.value,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'current_step': self.current_step,
            'results': self.results,
            'errors': self.errors,
            'context': self.context
        }


class WorkflowEngine:
    """Engine for executing multi-agent workflows"""

    def __init__(self, agent_orchestrator=None):
        self.orchestrator = agent_orchestrator
        self.active_workflows: Dict[str, WorkflowExecution] = {}
        self.workflow_definitions: Dict[str, Dict[str, Any]] = {}
        self.executor = ThreadPoolExecutor(max_workers=8)
        self.lock = threading.Lock()

    def load_workflow_definition(self, name: str, definition: Dict[str, Any]):
        """Load a workflow definition"""
        self.workflow_definitions[name] = definition

    def execute_workflow(self, workflow_name: str, input_data: Dict[str, Any],
                        workflow_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute a workflow synchronously"""

        if workflow_name not in self.workflow_definitions:
            raise ValueError(f"Workflow '{workflow_name}' not found")

        if workflow_id is None:
            workflow_id = f"{workflow_name}_{int(time.time() * 1000)}"

        # Create workflow execution
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            workflow_config=self.workflow_definitions[workflow_name]
        )

        with self.lock:
            self.active_workflows[workflow_id] = execution

        try:
            # Execute workflow
            execution.start_time = time.time()
            execution.status = WorkflowStatus.RUNNING

            result = self._execute_workflow_sync(execution, input_data)

            execution.status = WorkflowStatus.COMPLETED
            execution.end_time = time.time()
            execution.results['final_result'] = result

            return {
                'success': True,
                'workflow_id': workflow_id,
                'result': result,
                'execution_time': execution.end_time - execution.start_time
            }

        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.end_time = time.time()
            execution.errors.append(str(e))

            return {
                'success': False,
                'workflow_id': workflow_id,
                'error': str(e),
                'execution_time': execution.end_time - execution.start_time if execution.end_time else 0
            }

        finally:
            # Clean up
            with self.lock:
                if workflow_id in self.active_workflows:
                    del self.active_workflows[workflow_id]

    async def execute_workflow_async(self, workflow_name: str, input_data: Dict[str, Any],
                                   workflow_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute a workflow asynchronously"""
        # For now, wrap sync execution in async
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.execute_workflow,
            workflow_name,
            input_data,
            workflow_id
        )

    def _execute_workflow_sync(self, execution: WorkflowExecution, input_data: Dict[str, Any]) -> Any:
        """Execute workflow steps synchronously"""

        workflow_config = execution.workflow_config
        steps_config = workflow_config.get('steps', [])
        context = dict(input_data)  # Copy input data
        execution.context.update(context)

        # Convert step configs to WorkflowStep objects
        steps = []
        for step_config in steps_config:
            step = self._parse_step_config(step_config)
            steps.append(step)

        # Execute steps in order
        for step in steps:
            execution.current_step = step.name

            try:
                result = self._execute_step(step, context, execution)
                context[f"{step.name}_result"] = result
                execution.results[step.name] = result

            except Exception as e:
                execution.errors.append(f"Step '{step.name}' failed: {str(e)}")
                raise

        # Return final result
        return context.get('final_result', context)

    def _parse_step_config(self, config: Dict[str, Any]) -> WorkflowStep:
        """Parse step configuration into WorkflowStep object"""

        step_type_map = {
            'task': StepType.TASK,
            'parallel': StepType.PARALLEL,
            'conditional': StepType.CONDITIONAL,
            'loop': StepType.LOOP
        }

        step_type = step_type_map.get(config.get('step_type', 'task'), StepType.TASK)

        parallel_steps = []
        if step_type == StepType.PARALLEL and 'parallel' in config:
            for parallel_config in config['parallel']:
                parallel_steps.append(self._parse_step_config(parallel_config))

        return WorkflowStep(
            name=config['name'],
            step_type=step_type,
            agent=config.get('agent'),
            action=config.get('action'),
            parameters=config.get('parameters', {}),
            dependencies=config.get('dependencies', []),
            condition=config.get('condition'),
            parallel_steps=parallel_steps,
            loop_config=config.get('loop')
        )

    def _execute_step(self, step: WorkflowStep, context: Dict[str, Any],
                     execution: WorkflowExecution) -> Any:
        """Execute a single workflow step"""

        if step.step_type == StepType.TASK:
            return self._execute_task_step(step, context)

        elif step.step_type == StepType.PARALLEL:
            return self._execute_parallel_step(step, context, execution)

        elif step.step_type == StepType.CONDITIONAL:
            return self._execute_conditional_step(step, context)

        elif step.step_type == StepType.LOOP:
            return self._execute_loop_step(step, context, execution)

        else:
            raise ValueError(f"Unknown step type: {step.step_type}")

    def _execute_task_step(self, step: WorkflowStep, context: Dict[str, Any]) -> Any:
        """Execute a task step by calling an agent"""

        if not self.orchestrator:
            raise RuntimeError("No agent orchestrator configured")

        if not step.agent:
            raise ValueError(f"Step '{step.name}' has no agent specified")

        # Prepare task parameters by resolving context variables
        task_params = self._resolve_parameters(step.parameters, context)

        # Execute task via orchestrator
        result = self.orchestrator.execute_task(step.agent, {
            'action': step.action,
            'parameters': task_params,
            'context': context
        })

        return result

    def _execute_parallel_step(self, step: WorkflowStep, context: Dict[str, Any],
                              execution: WorkflowExecution) -> List[Any]:
        """Execute parallel steps"""

        if not step.parallel_steps:
            return []

        # Submit all parallel steps to executor
        futures = []
        for parallel_step in step.parallel_steps:
            future = self.executor.submit(
                self._execute_step, parallel_step, context.copy(), execution
            )
            futures.append((parallel_step.name, future))

        # Collect results
        results = {}
        for step_name, future in futures:
            try:
                result = future.result(timeout=300)  # 5 minute timeout
                results[step_name] = result
            except Exception as e:
                results[step_name] = {'error': str(e)}

        return results

    def _execute_conditional_step(self, step: WorkflowStep, context: Dict[str, Any]) -> Any:
        """Execute conditional step"""

        if not step.condition:
            raise ValueError(f"Conditional step '{step.name}' has no condition")

        # Evaluate condition (simple expression evaluation)
        try:
            condition_result = self._evaluate_condition(step.condition, context)
            if condition_result:
                # Execute the step
                return self._execute_task_step(step, context)
            else:
                return {'skipped': True, 'reason': 'condition_not_met'}
        except Exception as e:
            raise RuntimeError(f"Failed to evaluate condition '{step.condition}': {e}")

    def _execute_loop_step(self, step: WorkflowStep, context: Dict[str, Any],
                          execution: WorkflowExecution) -> List[Any]:
        """Execute loop step"""

        if not step.loop_config:
            raise ValueError(f"Loop step '{step.name}' has no loop configuration")

        loop_config = step.loop_config
        loop_var = loop_config.get('variable', 'item')
        loop_items = loop_config.get('items', [])

        if not isinstance(loop_items, list):
            # Try to resolve from context
            loop_items = context.get(loop_items, [])

        results = []
        for i, item in enumerate(loop_items):
            # Create loop context
            loop_context = context.copy()
            loop_context[loop_var] = item
            loop_context['loop_index'] = i

            try:
                result = self._execute_task_step(step, loop_context)
                results.append(result)
            except Exception as e:
                results.append({'error': str(e), 'item': item, 'index': i})

        return results

    def _resolve_parameters(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve parameter references from context"""

        resolved = {}

        for key, value in parameters.items():
            if isinstance(value, str) and value.startswith('{{') and value.endswith('}}'):
                # Template variable
                var_name = value[2:-2].strip()
                resolved[key] = context.get(var_name, value)
            elif isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                # Context variable
                var_path = value[2:-1].strip()
                resolved[key] = self._get_nested_value(context, var_path.split('.'))
            else:
                resolved[key] = value

        return resolved

    def _get_nested_value(self, data: Dict[str, Any], path: List[str]) -> Any:
        """Get nested value from dictionary"""
        current = data
        for key in path:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current

    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate a simple condition expression"""
        # Very basic condition evaluation - in production you'd want a proper expression evaluator
        try:
            # Simple variable checks
            if condition.startswith('{{') and condition.endswith('}}'):
                var_name = condition[2:-2].strip()
                value = context.get(var_name)
                return bool(value)
            elif '==' in condition:
                left, right = condition.split('==', 1)
                left_val = self._resolve_condition_value(left.strip(), context)
                right_val = self._resolve_condition_value(right.strip(), context)
                return left_val == right_val
            elif '!=' in condition:
                left, right = condition.split('!=', 1)
                left_val = self._resolve_condition_value(left.strip(), context)
                right_val = self._resolve_condition_value(right.strip(), context)
                return left_val != right_val
            else:
                # Default to truthy check
                return bool(context.get(condition, False))
        except Exception:
            return False

    def _resolve_condition_value(self, value: str, context: Dict[str, Any]) -> Any:
        """Resolve a value in condition evaluation"""
        if value.startswith('{{') and value.endswith('}}'):
            var_name = value[2:-2].strip()
            return context.get(var_name)
        elif value.startswith('${') and value.endswith('}'):
            var_path = value[2:-1].strip()
            return self._get_nested_value(context, var_path.split('.'))
        else:
            # Try to convert to appropriate type
            try:
                return int(value)
            except ValueError:
                try:
                    return float(value)
                except ValueError:
                    if value.lower() in ('true', 'false'):
                        return value.lower() == 'true'
                    return value

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a workflow execution"""
        with self.lock:
            execution = self.active_workflows.get(workflow_id)
            if execution:
                return execution.to_dict()
        return None

    def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow"""
        with self.lock:
            execution = self.active_workflows.get(workflow_id)
            if execution and execution.status == WorkflowStatus.RUNNING:
                execution.status = WorkflowStatus.CANCELLED
                execution.end_time = time.time()
                return True
        return False

    def cleanup(self):
        """Clean up resources"""
        self.executor.shutdown(wait=True)