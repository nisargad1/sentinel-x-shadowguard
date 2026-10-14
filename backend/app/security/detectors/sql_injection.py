import re
from typing import Tuple

class SQLInjectionDetector:
    """
    Detects SQL injection signatures, tautologies, UNION attacks, and SQL comments.
    """

    SQL_PATTERNS = [
        (r"(\bUNION\b\s+(?:ALL\s+)?\bSELECT\b)", "UNION SELECT attack", 95),
        (r"('|\")\s*(?:OR|AND)\s+('|\")?1('|\")?\s*=\s*('|\")?1", "Tautology/Boolean SQL injection (' OR 1=1)", 90),
        (r"('|\")\s*(?:OR|AND)\s+[\w\d_]+\s*=\s*[\w\d_]+", "Logical condition injection", 85),
        (r"(;|\b)\s*(?:DROP|ALTER|TRUNCATE|DELETE|UPDATE|INSERT)\s+(?:TABLE|DATABASE|FROM|INTO)", "Destructive SQL statement injection", 96),
        (r"(--|#|/\*|\*/)", "SQL comment termination syntax", 75),
        (r"(\bSLEEP\s*\(\s*\d+\s*\)|\bBENCHMARK\s*\(|\bWAITFOR\s+DELAY\b)", "Blind time-based SQL injection", 92),
        (r"(\bEXEC\s*\(|\bxp_cmdshell\b)", "Extended procedure execution", 98)
    ]

    @classmethod
    def inspect(cls, input_str: str) -> Tuple[bool, str, int]:
        """
        Returns:
            (is_violation, details, risk_score)
        """
        if not input_str or not isinstance(input_str, str):
            return False, "Safe input", 0

        text = input_str.strip()

        for pattern, desc, risk in cls.SQL_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True, f"SQL injection detected: {desc}", risk

        return False, "No SQL injection detected", 0
