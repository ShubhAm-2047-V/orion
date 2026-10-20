"""
Pydantic Schemas & Predefined JSON Validation Schemas for Machine Language Outputs.
"""
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field

class EntityItem(BaseModel):
    name: str
    value: Any
    entity_type: str = "string"
    confidence: float = 1.0

class GeneratedCode(BaseModel):
    json_cmd: str = Field(..., description="Formatted JSON command")
    python: str = Field(..., description="Python execution script")
    javascript: str = Field(..., description="JavaScript execution script")
    sql: Optional[str] = Field(None, description="SQL query if applicable")
    shell: str = Field(..., description="PowerShell / Shell command")

class MachineCommand(BaseModel):
    raw_input: str
    normalized_input: str
    detected_language: str = "en"
    intent: str
    engine: str
    action: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    entities: List[EntityItem] = Field(default_factory=list)
    
    # Ambiguity and conversational context
    ambiguity_detected: bool = False
    clarification_question: Optional[str] = None
    missing_parameters: List[str] = Field(default_factory=list)
    is_complete: bool = True
    
    # Safety and risk controls
    risk_level: str = "NORMAL"  # NORMAL, SENSITIVE, CRITICAL
    requires_confirmation: bool = False
    is_safe: bool = True
    safety_notes: Optional[str] = None
    
    # Multi-language code representation
    generated_code: Optional[GeneratedCode] = None
    explanation: str = ""

# Predefined JSON Schema for validating MachineCommand outputs
MACHINE_COMMAND_JSON_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "MachineCommand",
    "type": "object",
    "properties": {
        "raw_input": {"type": "string"},
        "normalized_input": {"type": "string"},
        "detected_language": {"type": "string", "enum": ["en", "hi", "mr", "hinglish", "unknown"]},
        "intent": {"type": "string"},
        "engine": {"type": "string"},
        "action": {"type": "string"},
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "parameters": {"type": "object"},
        "ambiguity_detected": {"type": "boolean"},
        "clarification_question": {"type": ["string", "null"]},
        "missing_parameters": {
            "type": "array",
            "items": {"type": "string"}
        },
        "is_complete": {"type": "boolean"},
        "risk_level": {"type": "string", "enum": ["NORMAL", "SENSITIVE", "CRITICAL"]},
        "requires_confirmation": {"type": "boolean"},
        "is_safe": {"type": "boolean"},
        "explanation": {"type": "string"}
    },
    "required": [
        "raw_input", "intent", "engine", "action", 
        "confidence", "parameters", "risk_level"
    ]
}
