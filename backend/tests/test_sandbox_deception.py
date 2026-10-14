import pytest
from app.sandbox.deception_fs import deception_fs

def test_deception_sandbox_files():
    assert deception_fs.has_file("/etc/passwd")
    assert deception_fs.has_file("/fake_credentials.txt")

    # Read passwd honeypot
    res = deception_fs.read_file("../../../etc/passwd")
    assert res["is_simulated"] is True
    assert "CANARY-SENTINEL-X-TRAP-VERIFIED" in res["canary_signature"]
    assert "shadowguard_canary" in res["content"]

    # Read credentials decoy
    res_cred = deception_fs.read_file("/credentials")
    assert "SHADOWGUARD HONEYPOT DECOY CREDENTIALS" in res_cred["content"]
    assert "AKIAIOSFODNN7EXAMPLE_DECOY" in res_cred["content"]
