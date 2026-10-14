import hmac
import hashlib
import json
import time
from typing import Dict, Any, Tuple, Optional
from app.core.config import settings

class HMACIntegrityService:
    """
    Cryptographic HMAC-SHA256 request verification service ensuring payload
    integrity and replay protection for AI agent tool execution requests.
    """

    # In-memory nonce replay cache (maps nonce -> creation timestamp)
    _seen_nonces: Dict[str, float] = {}

    @classmethod
    def get_secret(cls) -> bytes:
        return settings.HMAC_SECRET_KEY.encode("utf-8")

    @classmethod
    def canonicalize(cls, payload: Dict[str, Any], timestamp: int, nonce: str) -> bytes:
        """
        Creates a deterministic canonical byte string from payload, timestamp, and nonce.
        Sorts dictionary keys and removes whitespace.
        """
        compact_payload = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        canonical_str = f"TS:{timestamp}|NONCE:{nonce}|PAYLOAD:{compact_payload}"
        return canonical_str.encode("utf-8")

    @classmethod
    def generate_signature(cls, payload: Dict[str, Any], timestamp: int, nonce: str) -> str:
        """
        Generates HMAC-SHA256 hexadecimal signature.
        """
        canonical_bytes = cls.canonicalize(payload, timestamp, nonce)
        signature = hmac.new(cls.get_secret(), canonical_bytes, hashlib.sha256).hexdigest()
        return signature

    @classmethod
    def verify_request(
        cls,
        payload: Dict[str, Any],
        timestamp: int,
        nonce: str,
        provided_signature: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Validates HMAC signature, checks timestamp freshness, and enforces nonce uniqueness.
        Returns:
            (is_valid, error_reason)
        """
        current_time = time.time()

        # 1. Check timestamp freshness (reject stale/future requests)
        drift = abs(current_time - timestamp)
        if drift > settings.HMAC_MAX_DRIFT_SECONDS:
            return False, f"Request timestamp expired or out of bounds (drift: {drift:.1f}s, max: {settings.HMAC_MAX_DRIFT_SECONDS}s)"

        # 2. Check nonce replay attack
        cls._prune_expired_nonces(current_time)
        if nonce in cls._seen_nonces:
            return False, f"Replay attack detected: Nonce '{nonce}' has already been processed"

        # 3. Compute expected signature and constant-time compare
        expected_signature = cls.generate_signature(payload, timestamp, nonce)
        if not hmac.compare_digest(expected_signature, provided_signature):
            return False, "Cryptographic signature mismatch: payload has been altered in transit"

        # 4. Record nonce to prevent future replay
        cls._seen_nonces[nonce] = current_time
        return True, None

    @classmethod
    def _prune_expired_nonces(cls, current_time: float) -> None:
        """
        Removes nonces older than the maximum permitted drift window.
        """
        expired = [
            n for n, ts in cls._seen_nonces.items()
            if (current_time - ts) > (settings.HMAC_MAX_DRIFT_SECONDS * 2)
        ]
        for n in expired:
            del cls._seen_nonces[n]

    @classmethod
    def reset_nonces(cls) -> None:
        """Helper for test suites and dev resets."""
        cls._seen_nonces.clear()
