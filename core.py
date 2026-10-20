"""
JARVIS Core Orchestrator & Brain.
"""
from typing import Dict, Any, List, Optional
from engines.registry import EngineRegistry
from engines.router import EngineRouter
from engines.permissions import PermissionManager
from engines.bus import EventBus
from engines.shared.memory import MemoryManager
from engines.shared.config import ConfigManager
from engines.shared.logging import get_logger
from nlp_engine import translate_to_command

logger = get_logger("core")

class JARVISCore:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(JARVISCore, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        logger.info("Initializing JARVIS Core orchestrator...")
        self.config = ConfigManager()
        self.memory = MemoryManager()
        self.bus = EventBus()
        self.permissions = PermissionManager()
        self.registry = EngineRegistry()

        # Discover and register all engine plugins
        self.registry.discover_and_register_all()

        # Initialize engine router
        self.router = EngineRouter(registry=self.registry, permission_mgr=self.permissions)

        self._initialized = True
        logger.info(f"JARVIS Core online with {len(self.registry.list())} active engines.")

    def process_request(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Main processing method for JARVIS.
        1. Translates intent via NLP engine
        2. Logs to memory context
        3. Routes request to appropriate specialized engines
        4. Publishes events
        5. Formats natural language output response
        """
        if not user_input or not user_input.strip():
            return ""

        # 1. Translate intent via NLU Engine and NLP translator
        try:
            from nlu_model.engine import NLUEngine
            nlu_cmd = NLUEngine().understand(user_input, context=context)
            translated_cmd = nlu_cmd.action if nlu_cmd.action != "unknown" else translate_to_command(user_input)
            if nlu_cmd.parameters.get("app"):
                translated_cmd = f"{translated_cmd} {nlu_cmd.parameters['app']}".strip()
            elif nlu_cmd.parameters.get("query"):
                translated_cmd = f"{translated_cmd} {nlu_cmd.parameters['query']}".strip()
        except Exception:
            nlu_cmd = None
            translated_cmd = translate_to_command(user_input)
        
        # 2. Record conversation memory
        memory_meta = {"translated": translated_cmd}
        if nlu_cmd:
            memory_meta["intent"] = nlu_cmd.intent
            memory_meta["risk_level"] = nlu_cmd.risk_level
            memory_meta["confidence"] = nlu_cmd.confidence

        self.memory.add_conversation("user", user_input, memory_meta)
        self.bus.publish("user_request", {"raw": user_input, "translated": translated_cmd, "nlu": nlu_cmd.model_dump() if nlu_cmd else {}})

        # 3. Route request to specialized engines
        results = self.router.route_request(translated_cmd, context=context)

        # 4. Synthesize final output response
        if not results:
            response = "No response generated."
        elif len(results) == 1:
            res = results[0]
            response = res.message if res.success else f"Error: {res.message}"
        else:
            response_lines = []
            for i, res in enumerate(results, 1):
                status_str = "Success" if res.success else "Failed"
                response_lines.append(f"Step {i} ({res.engine_id}): {res.message}")
            response = "\n".join(response_lines)

        # Record assistant memory
        self.memory.add_conversation("assistant", response)
        self.bus.publish("core_response", {"response": response})

        return response

