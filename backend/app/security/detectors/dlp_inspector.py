import re
import json
from typing import Tuple, List, Any, Dict

class DLPInspector:
    """
    Data Loss Prevention (DLP) inspector that audits tool responses before they are returned to AI agents.
    Detects API keys, private keys, passwords, bearer tokens, and sensitive PII.
    """

    PATTERNS = [
        ("AWS_ACCESS_KEY", r"\b(AKIA[0-9A-Z]{16,20})\b", 95),
        ("OPENAI_API_KEY", r"\b(sk-[a-zA-Z0-9]{20,48})\b", 95),
        ("GITHUB_TOKEN", r"\b(ghp_[a-zA-Z0-9]{36}|github_pat_[a-zA-Z0-9_]{50,})\b", 95),
        ("GENERIC_API_KEY", r'(?i)(?:api_key|apikey|secret_key|access_token)\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?', 90),
        ("PRIVATE_KEY_MARKER", r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----", 99),
        ("PASSWORD_FIELD", r'(?i)["\']?(?:password|passwd|pwd)["\']?\s*[:=]\s*["\']([^"\']{4,})["\']', 88),
        ("BEARER_TOKEN", r"\bBearer\s+[a-zA-Z0-9\-._~+/]+=*", 85),
        ("JWT_TOKEN", r"\beyJ[a-zA-Z0-9_-]{10,}\.eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\b", 85),
        ("CREDIT_CARD", r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b", 90),
        ("SSN_IDENTIFIER", r"\b\d{3}-\d{2}-\d{4}\b", 85),
    ]

    @classmethod
    def inspect(cls, output_data: Any) -> Tuple[bool, List[str], Any, int]:
        """
        Scans data (dict, list, or string) for sensitive leaks.
        Returns:
            (contains_leak, detected_categories, redacted_output, risk_score)
        """
        if output_data is None:
            return False, [], None, 0

        # Convert to string representation for regex scanning
        if isinstance(output_data, (dict, list)):
            text_repr = json.dumps(output_data)
        else:
            text_repr = str(output_data)

        detected_categories = []
        max_risk = 0
        redacted_text = text_repr

        for name, pattern, risk in cls.PATTERNS:
            matches = list(re.finditer(pattern, text_repr))
            if matches:
                detected_categories.append(name)
                max_risk = max(max_risk, risk)
                # Redact instances in text
                for m in matches:
                    if m.groups():
                        secret_val = m.group(1)
                        mask = f"[REDACTED_{name}]"
                        redacted_text = redacted_text.replace(f'"{secret_val}"', f'"{mask}"').replace(secret_val, mask)
                    else:
                        matched_val = m.group(0)
                        mask = f"[REDACTED_{name}]"
                        redacted_text = redacted_text.replace(f'"{matched_val}"', f'"{mask}"').replace(matched_val, mask)

        contains_leak = len(detected_categories) > 0

        # Reconstruct safe structure if originally dict or list
        if contains_leak and isinstance(output_data, (dict, list)):
            try:
                safe_output = json.loads(redacted_text)
            except Exception:
                safe_output = redacted_text
        else:
            safe_output = redacted_text if contains_leak else output_data

        return contains_leak, detected_categories, safe_output, max_risk

    @classmethod
    def sanitize_for_logging(cls, payload: Any, max_length: int = 150) -> str:
        """
        Ensures log messages and event payloads never store raw secrets.
        """
        if payload is None:
            return ""
        s = str(payload)
        for name, pattern, _ in cls.PATTERNS:
            s = re.sub(pattern, f"[{name}_SANITIZED]", s)
        if len(s) > max_length:
            return s[:max_length] + "... [TRUNCATED]"
        return s
