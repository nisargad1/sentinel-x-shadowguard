import re
from typing import Tuple

class CommandInjectionDetector:
    """
    Detects attempts to execute arbitrary shell commands via tool arguments.
    """

    # Shell delimiters and chaining operators
    SHELL_OPERATORS = [
        r"[;&|`$]",             # ; & | ` $
        r"\$\(.*\)",            # $(command)
        r"`.*`",                # `command`
        r"\|\|",                # ||
        r"&&",                  # &&
    ]

    # Malicious commands commonly executed by threat actors
    SUSPICIOUS_COMMANDS = [
        r"\b(?:bash|sh|zsh|csh|tcsh)\b",
        r"\b(?:cmd|powershell|pwsh)\.exe\b",
        r"\b(?:curl|wget|nc|netcat|ncat)\b",
        r"\b(?:whoami|id|uname|ifconfig|ipconfig)\b",
        r"\b(?:cat\s+/etc/passwd|type\s+c:\\)\b",
        r"\b(?:rm\s+-rf|del\s+/f|format)\b",
        r"\b(?:chmod|chown)\b",
        r"\b(?:eval|exec|system|popen)\b",
        r"\b(?:base64\s+-d|certutil)\b"
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

        # Check for command operator chaining
        has_operator = any(re.search(op, text) for op in cls.SHELL_OPERATORS)
        
        # Check for specific command binaries
        matched_command = None
        for cmd_pattern in cls.SUSPICIOUS_COMMANDS:
            match = re.search(cmd_pattern, text, re.IGNORECASE)
            if match:
                matched_command = match.group(0)
                break

        if matched_command and has_operator:
            return True, f"Critical command injection detected: shell operator with invocation '{matched_command}'", 98
        elif matched_command:
            return True, f"Prohibited shell binary/command detected: '{matched_command}'", 88
        elif any(re.search(r"[;&|`]\s*[a-zA-Z]", text) for _ in [0]):
            return True, f"Suspicious shell command chaining sequence detected in arguments", 80

        return False, "No command injection patterns detected", 0
