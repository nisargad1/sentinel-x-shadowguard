import re
from typing import Tuple

class PromptInjectionDetector:
    """
    Detects jailbreaks, prompt injection, role spoofing, and instruction overrides in AI inputs.
    """

    INJECTION_PATTERNS = [
        (r"ignore\s+(?:all\s+)?(?:previous|prior|above)\s+(?:instructions|prompts|directives|rules)", "Direct instruction override", 94),
        (r"disregard\s+(?:all\s+)?(?:safety|guidelines|policies|rules)", "Safety guideline circumvention", 92),
        (r"(?:reveal|display|output|print|show)\s+(?:your\s+)?(?:system\s+prompt|initial\s+prompt|instructions)", "System prompt exfiltration attempt", 88),
        (r"(?:you\s+are\s+now|act\s+as|pretend\s+you\s+are)(?:\s+in)?\s+(?:DAN|unfiltered|jailbroken|root|developer\s+mode)", "Persona jailbreak / DAN mode attempt", 90),
        (r"\bDAN\s+mode\b|\bjailbreak(?:ed)?\b", "Explicit DAN / Jailbreak token", 90),
        (r"(?:curl|fetch|ping|webhook|http|https):\/\/[^\s]+", "Potential data exfiltration callback in untrusted input", 75),
        (r"base64\s*(?:decode|eval|payload)|(?:[A-Za-z0-9+/]{40,}={0,2})", "Obfuscated / Base64 payload delivery", 80),
        (r"bypass\s+(?:all\s+)?(?:security|guardrails?|filters?|gateway|policy|policies)", "Explicit security bypass attempt", 85)
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

        for pattern, desc, risk in cls.INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True, f"Prompt injection / Jailbreak pattern detected: {desc}", risk

        return False, "No prompt injection patterns detected", 0
