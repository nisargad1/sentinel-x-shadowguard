import pytest
from app.security.detectors.dlp_inspector import DLPInspector

def test_dlp_detects_and_redacts_api_key():
    dirty_output = {
        "status": "SUCCESS",
        "api_key": "AKIA1234567890ABCDEF",
        "openai": "sk-abcdefghijklmnopqrstuvwxyz1234567890",
        "notes": "calendar event"
    }

    leak, categories, safe_out, risk = DLPInspector.inspect(dirty_output)
    assert leak is True
    assert "AWS_ACCESS_KEY" in categories
    assert "OPENAI_API_KEY" in categories
    assert risk >= 90
    assert "[REDACTED_AWS_ACCESS_KEY]" in str(safe_out)
    assert "[REDACTED_OPENAI_API_KEY]" in str(safe_out)
    assert "AKIA1234567890ABCDEF" not in str(safe_out)

def test_dlp_detects_password_fields():
    dirty_output = {"db": "postgres", "password": "SuperSecretPassWord123!"}
    leak, categories, safe_out, risk = DLPInspector.inspect(dirty_output)
    assert leak is True
    assert "PASSWORD_FIELD" in categories
    assert "SuperSecretPassWord123!" not in str(safe_out)

def test_dlp_clean_output_passes_unmodified():
    clean_output = {"events": ["Standup", "Review"], "time": "10:00"}
    leak, categories, safe_out, risk = DLPInspector.inspect(clean_output)
    assert leak is False
    assert len(categories) == 0
    assert safe_out == clean_output
