"""
Integration Test for NLU HTTP Endpoints and Server.
"""
import pytest
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nlu_model.engine import NLUEngine
from nlu_model.validator import validate_machine_command
from nlu_model.execution_adapter import OrionExecutionAdapter

def test_full_pipeline_web_search():
    engine = NLUEngine()
    query = "Hey, open Chrome and search for the best AI tools."
    cmd = engine.understand(query)
    
    assert cmd.intent == "open_application_and_search"
    assert cmd.confidence >= 0.90
    
    # Check multi-language code generation
    assert cmd.generated_code.json_cmd is not None
    assert "https://www.google.com/search?q=" in cmd.generated_code.python
    assert "best+ai+tools" in cmd.generated_code.python.lower() or "best ai tools" in cmd.generated_code.python.lower()
    assert "chrome" in cmd.generated_code.shell.lower()
    
    # Check validator
    val = validate_machine_command(cmd.model_dump())
    assert val.is_valid is True

def test_full_pipeline_hinglish_slang():
    engine = NLUEngine()
    query = "bhai mere laptop ka calculator khol de"
    cmd = engine.understand(query)
    
    assert cmd.intent == "open_application"
    assert cmd.parameters.get("app") == "calculator"
    assert cmd.risk_level == "NORMAL"
    assert not cmd.requires_confirmation

def test_full_pipeline_marathi():
    engine = NLUEngine()
    query = "calculator chalu kara lavkar"
    cmd = engine.understand(query)
    
    assert cmd.intent == "open_application"
    assert cmd.parameters.get("app") == "calculator"
    assert cmd.detected_language == "mr"

def test_full_pipeline_ambiguous_delete():
    engine = NLUEngine()
    adapter = OrionExecutionAdapter()
    
    query = "Delete the old project."
    cmd = engine.understand(query)
    
    assert cmd.ambiguity_detected is True
    assert cmd.clarification_question is not None
    
    # Ensure execution adapter blocks it without clarification
    exec_res = adapter.execute_command(cmd, user_confirmed=False)
    assert exec_res.success is False
    assert exec_res.error == "AmbiguityError"

def test_full_pipeline_critical_safety():
    engine = NLUEngine()
    adapter = OrionExecutionAdapter()
    
    query = "shutdown the workstation"
    cmd = engine.understand(query)
    
    assert cmd.risk_level == "CRITICAL"
    assert cmd.requires_confirmation is True
    
    # Ensure unconfirmed execution is blocked
    exec_res = adapter.execute_command(cmd, user_confirmed=False)
    assert exec_res.success is False
    assert exec_res.error == "ConfirmationRequired"
