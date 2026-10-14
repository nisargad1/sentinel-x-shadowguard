import time
import pytest
from app.services.hmac_service import HMACIntegrityService

def setup_function():
    HMACIntegrityService.reset_nonces()

def test_valid_hmac_signature():
    payload = {"user_goal": "Summarize report.pdf", "tool_name": "read_demo_file"}
    ts = int(time.time())
    nonce = "nonce-valid-001"

    sig = HMACIntegrityService.generate_signature(payload, ts, nonce)
    valid, err = HMACIntegrityService.verify_request(payload, ts, nonce, sig)

    assert valid is True
    assert err is None

def test_tampered_payload_rejected():
    payload = {"user_goal": "Summarize report.pdf", "tool_name": "read_demo_file"}
    ts = int(time.time())
    nonce = "nonce-tamper-002"

    sig = HMACIntegrityService.generate_signature(payload, ts, nonce)

    # Attacker alters tool_name to malicious command
    tampered_payload = {"user_goal": "Summarize report.pdf", "tool_name": "execute_shell"}
    valid, err = HMACIntegrityService.verify_request(tampered_payload, ts, nonce, sig)

    assert valid is False
    assert "signature mismatch" in err.lower()

def test_expired_timestamp_rejected():
    payload = {"user_goal": "Summarize report.pdf"}
    stale_ts = int(time.time()) - 400  # Older than 300s window
    nonce = "nonce-stale-003"

    sig = HMACIntegrityService.generate_signature(payload, stale_ts, nonce)
    valid, err = HMACIntegrityService.verify_request(payload, stale_ts, nonce, sig)

    assert valid is False
    assert "expired" in err.lower()

def test_replay_attack_rejected():
    payload = {"action": "read"}
    ts = int(time.time())
    nonce = "nonce-replay-004"

    sig = HMACIntegrityService.generate_signature(payload, ts, nonce)

    # First request succeeds
    valid1, _ = HMACIntegrityService.verify_request(payload, ts, nonce, sig)
    assert valid1 is True

    # Replayed identical request fails
    valid2, err = HMACIntegrityService.verify_request(payload, ts, nonce, sig)
    assert valid2 is False
    assert "replay attack detected" in err.lower()
