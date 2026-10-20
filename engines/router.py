"""
Engine Router and Orchestrator for Single-Engine and Multi-Engine Workflows.
Optimized with LRU intent resolution caching and fast capability indexing.
"""
from typing import Dict, Any, List, Optional
from engines.base import BaseEngine, Action, ActionResult, ExecutionPlan
from engines.registry import EngineRegistry
from engines.permissions import PermissionManager
from engines.shared.cache import TTLCache
from engines.shared.errors import CapabilityNotFoundError, RouterError
from engines.shared.logging import get_logger
import time

logger = get_logger("router")

class EngineRouter:
    def __init__(self, registry: Optional[EngineRegistry] = None, permission_mgr: Optional[PermissionManager] = None):
        self.registry = registry or EngineRegistry()
        self.permission_mgr = permission_mgr or PermissionManager()
        self.cache = TTLCache()
        self._intent_cache: Dict[str, str] = {}  # LRU Fast-path intent cache: intent -> engine_id

    def route_request(self, user_request: str, context: Optional[Dict[str, Any]] = None) -> List[ActionResult]:
        """
        Main entry point for routing requests. Identifies target engine(s), validates permissions,
        and executes single or multi-engine pipelines.
        """
        context = context or {}
        logger.info(f"Routing request: '{user_request}'")

        # Split request into multi-engine workflow steps if pipeline delimiters are present
        steps = self._split_into_steps(user_request)

        results: List[ActionResult] = []
        pipeline_context = dict(context)

        for step_idx, step_text in enumerate(steps):
            step_result = self._execute_single_step(step_text, pipeline_context)
            results.append(step_result)

            if not step_result.success:
                logger.warning(f"Step {step_idx + 1} failed: {step_result.message}. Stopping pipeline.")
                break

            # Forward step output to context for downstream engines
            if step_result.data:
                pipeline_context[f"step_{step_idx + 1}_output"] = step_result.data

        return results

    def _split_into_steps(self, user_request: str) -> List[str]:
        """Splits request into sequential engine steps if pipeline delimiters are present."""
        if " then " in user_request.lower():
            return [s.strip() for s in user_request.split(" then ") if s.strip()]
        if " -> " in user_request:
            return [s.strip() for s in user_request.split(" -> ") if s.strip()]
        return [user_request]

    def _execute_single_step(self, step_text: str, context: Dict[str, Any]) -> ActionResult:
        # Find engine that can handle this step
        target_engine = self._resolve_engine(step_text, context)
        if not target_engine:
            return ActionResult(
                success=False,
                action_id="err_no_engine",
                engine_id="router",
                message=f"No engine found capable of handling request: '{step_text}'",
                error="CapabilityNotFoundError"
            )

        logger.info(f"Resolved request to engine '{target_engine.engine_id}' ({target_engine.name})")

        # Plan execution
        plan_req = {"intent": step_text, "context": context}
        exec_plan = target_engine.plan(plan_req)

        if not exec_plan.actions:
            return ActionResult(
                success=False,
                action_id="err_empty_plan",
                engine_id=target_engine.engine_id,
                message="Engine generated an empty execution plan."
            )

        # Execute actions sequentially
        step_results = []
        for action in exec_plan.actions:
            # Check permissions
            self.permission_mgr.authorize(action.capability, action.parameters)

            # Pass sandboxed context
            action.context = context

            act_res = target_engine.execute(action)
            step_results.append(act_res)

            if not act_res.success:
                return act_res

        return step_results[-1]

    def _resolve_engine(self, intent: str, context: Dict[str, Any]) -> Optional[BaseEngine]:
        intent_clean = intent.strip()
        intent_lower = intent_clean.lower()

        # Fast-Path 1: Check LRU Intent Cache (O(1) lookup)
        if intent_lower in self._intent_cache:
            engine_id = self._intent_cache[intent_lower]
            engine = self.registry.get(engine_id)
            if engine:
                return engine

        # Fast-Path 2: Check all registered engines using can_handle()
        for engine in self.registry.list():
            if engine.can_handle(intent_clean, context):
                self._cache_intent_mapping(intent_lower, engine.engine_id)
                return engine

        # Fallback 3: Direct keyword fallback routing
        engine_id = None
        if "whatsapp" in intent_lower:
            engine_id = "whatsapp"
        elif "email" in intent_lower or "gmail" in intent_lower or "mail" in intent_lower:
            engine_id = "email"
        elif "chrome" in intent_lower or "browser" in intent_lower or "http" in intent_lower or "website" in intent_lower:
            engine_id = "browser"
        elif "search" in intent_lower or "google" in intent_lower:
            engine_id = "search"
        elif "file" in intent_lower or "temp" in intent_lower or "trash" in intent_lower or "recycle" in intent_lower:
            engine_id = "file"
        elif "voice" in intent_lower or "listen" in intent_lower or "speak" in intent_lower or "mic" in intent_lower:
            engine_id = "voice"
        elif "calendar" in intent_lower or "date" in intent_lower or "time" in intent_lower or "schedule" in intent_lower:
            engine_id = "calendar"
        elif "settings" in intent_lower or "wifi" in intent_lower or "bluetooth" in intent_lower:
            engine_id = "settings"
        elif "status" in intent_lower or "diagnostics" in intent_lower or "lock" in intent_lower or "sleep" in intent_lower or "shutdown" in intent_lower or "restart" in intent_lower:
            engine_id = "system"
        else:
            engine_id = "system"

        engine = self.registry.get(engine_id)
        if engine:
            self._cache_intent_mapping(intent_lower, engine.engine_id)
        return engine

    def _cache_intent_mapping(self, intent_lower: str, engine_id: str) -> None:
        if len(self._intent_cache) > 200:
            self._intent_cache.clear()
        self._intent_cache[intent_lower] = engine_id
