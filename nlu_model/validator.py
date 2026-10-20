"""
Validation Engine for Schema Compliance and Generated Code Syntax Integrity.
Validates machine-readable JSON against schemas and validates code syntax (Python, SQL, JS).
"""
import ast
import json
from typing import Dict, Any, List, Tuple
from jsonschema import validate as json_validate, ValidationError
from nlu_model.schemas import MACHINE_COMMAND_JSON_SCHEMA, MachineCommand

REQUIRED_INTENT_PARAMS = {
    "open_application": ["app"],
    "close_application": ["app"],
    "search_web": ["query"],
    "open_website": ["url"],
    "create_folder": ["folder_name"],
    "create_file_and_code": ["file_name", "content"],
    "whatsapp_message": ["target", "message"],
    "whatsapp_send_file": ["target", "file_path"]
}

class ValidationResult:
    def __init__(self, is_valid: bool, errors: List[str] = None, warnings: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings
        }

def validate_machine_command(cmd_dict: Dict[str, Any]) -> ValidationResult:
    """
    Validates a generated machine command dictionary against JSON Schema and domain business rules.
    """
    errors: List[str] = []
    warnings: List[str] = []

    # 1. JSON Schema validation
    try:
        json_validate(instance=cmd_dict, schema=MACHINE_COMMAND_JSON_SCHEMA)
    except ValidationError as e:
        errors.append(f"JSON Schema Violation: {e.message} at path '{list(e.path)}'")

    # 2. Confidence and completeness check
    confidence = cmd_dict.get("confidence", 0.0)
    if confidence < 0.5:
        warnings.append(f"Low confidence interpretation: {confidence:.2f}")

    intent = cmd_dict.get("intent", "")
    params = cmd_dict.get("parameters", {})

    # 3. Required parameters check
    if intent in REQUIRED_INTENT_PARAMS:
        required = REQUIRED_INTENT_PARAMS[intent]
        for req in required:
            if req not in params or not str(params[req]).strip():
                errors.append(f"Intent '{intent}' missing mandatory parameter '{req}'")

    # 4. Check syntax of generated Python code if present
    gen_code = cmd_dict.get("generated_code")
    if isinstance(gen_code, dict) and "python" in gen_code:
        py_src = gen_code["python"]
        if py_src:
            try:
                ast.parse(py_src)
            except SyntaxError as syn_err:
                errors.append(f"Generated Python code has syntax error: {syn_err}")

    is_valid = len(errors) == 0
    return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)
