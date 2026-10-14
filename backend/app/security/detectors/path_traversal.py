import os
import re
from typing import Tuple, Optional
import urllib.parse

# Sensitive files that indicate deception/honeypot routing candidates
SENSITIVE_TARGETS = [
    r"etc[/\\]passwd",
    r"etc[/\\]shadow",
    r"etc[/\\]hosts",
    r"proc[/\\]self",
    r"windows[/\\]system32",
    r"winnt[/\\]system32",
    r"boot\.ini",
    r"credentials",
    r"\.env",
    r"\.aws[/\\]credentials",
    r"id_rsa",
    r"id_ed25519"
]

class PathTraversalDetector:
    """
    Detects directory traversal, root escape, canonical bypass, and null-byte injection.
    Flags candidates for the Shadow Deception Simulator.
    """

    @classmethod
    def inspect(cls, target_path: str, base_dir: Optional[str] = None) -> Tuple[bool, str, int, bool, str]:
        """
        Returns:
            (is_violation, details, risk_score, should_deceive, virtual_target)
        """
        if not target_path or not isinstance(target_path, str):
            return False, "Safe path", 0, False, ""

        raw_input = target_path.strip()
        decoded = urllib.parse.unquote(raw_input)

        # 1. Null-byte injection check
        if "\x00" in raw_input or "%00" in raw_input.lower():
            return True, "Null-byte injection detected in path parameter", 95, False, ""

        # 2. Check for explicit path traversal sequences (encoded or decoded)
        traversal_patterns = [
            r"\.\.[/\\]",              # ../ or ..\
            r"[/\\]\.\.",              # /.. or \..
            r"^\.\.$",                 # exact ..
            r"%2e%2e",                 # URL encoded ..
            r"\.\.%2f",                # Mixed ..%2f
            r"%252e%252e",             # Double-encoded ..
            r"\.{3,}[/\\]",            # .../ or ....\
        ]

        has_traversal_syntax = False
        for pattern in traversal_patterns:
            if re.search(pattern, raw_input, re.IGNORECASE) or re.search(pattern, decoded, re.IGNORECASE):
                has_traversal_syntax = True
                break

        # 3. Check for targeted sensitive system files
        is_sensitive_target = False
        for target in SENSITIVE_TARGETS:
            if re.search(target, decoded, re.IGNORECASE):
                is_sensitive_target = True
                break

        # 4. Canonical path resolution check
        if base_dir:
            try:
                safe_base = os.path.abspath(base_dir)
                resolved = os.path.abspath(os.path.join(safe_base, decoded.lstrip("/\\")))
                if not resolved.startswith(safe_base):
                    has_traversal_syntax = True
            except Exception:
                has_traversal_syntax = True

        # Decision & Deception routing logic
        if has_traversal_syntax or is_sensitive_target:
            # Normalize target for deception lookup
            virtual_target = "/etc/passwd" if "passwd" in decoded.lower() else (
                "/fake_credentials.txt" if ("credential" in decoded.lower() or "secret" in decoded.lower() or "env" in decoded.lower()) else (
                    "/etc/shadow" if "shadow" in decoded.lower() else "/etc/passwd"
                )
            )
            reason = f"Path traversal attack detected: '{raw_input}' violates filesystem perimeter"
            risk = 92 if is_sensitive_target else 85
            return True, reason, risk, True, virtual_target

        return False, "Path is structurally valid", 0, False, ""
