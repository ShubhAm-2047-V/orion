"""
Engine Registry and Plugin Discovery System for JARVIS.
"""
import os
import importlib
from typing import Dict, List, Optional, Any
from engines.base import BaseEngine
from engines.shared.logging import get_logger

logger = get_logger("registry")

class EngineRegistry:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EngineRegistry, cls).__new__(cls)
            cls._instance.engines: Dict[str, BaseEngine] = {}
            cls._instance.capability_index: Dict[str, List[BaseEngine]] = {}
        return cls._instance

    def register(self, engine: BaseEngine) -> None:
        if not isinstance(engine, BaseEngine):
            raise TypeError("Engine must inherit from BaseEngine")
        
        if not engine.initialized:
            try:
                engine.initialize()
            except Exception as e:
                logger.error(f"Failed to initialize engine '{engine.engine_id}': {e}")
                return

        self.engines[engine.engine_id] = engine

        # Index engine capabilities
        for cap in engine.capabilities:
            if cap not in self.capability_index:
                self.capability_index[cap] = []
            if engine not in self.capability_index[cap]:
                self.capability_index[cap].append(engine)

        logger.info(f"Registered engine '{engine.engine_id}' ({engine.name}) with capabilities: {engine.capabilities}")

    def unregister(self, engine_id: str) -> None:
        if engine_id in self.engines:
            engine = self.engines.pop(engine_id)
            engine.shutdown()
            for cap, engine_list in list(self.capability_index.items()):
                if engine in engine_list:
                    engine_list.remove(engine)
            logger.info(f"Unregistered engine '{engine_id}'")

    def get(self, engine_id: str) -> Optional[BaseEngine]:
        return self.engines.get(engine_id)

    def list(self) -> List[BaseEngine]:
        return list(self.engines.values())

    def find_by_capability(self, capability: str) -> List[BaseEngine]:
        return self.capability_index.get(capability, [])

    def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        results = {}
        for engine_id, engine in self.engines.items():
            try:
                results[engine_id] = engine.health_check()
            except Exception as e:
                results[engine_id] = {"status": "error", "error": str(e)}
        return results

    def discover_and_register_all(self) -> None:
        """Dynamically scans the engines/ directory and auto-registers plugins."""
        engines_dir = os.path.dirname(__file__)
        for item in os.listdir(engines_dir):
            item_path = os.path.join(engines_dir, item)
            if os.path.isdir(item_path) and not item.startswith("__") and item not in ["shared", "adapters"]:
                engine_file = os.path.join(item_path, "engine.py")
                if os.path.exists(engine_file):
                    module_name = f"engines.{item}.engine"
                    try:
                        module = importlib.import_module(module_name)
                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)
                            if (isinstance(attr, type) and 
                                issubclass(attr, BaseEngine) and 
                                attr is not BaseEngine):
                                instance = attr()
                                self.register(instance)
                    except Exception as e:
                        logger.error(f"Error loading engine plugin '{module_name}': {e}")
