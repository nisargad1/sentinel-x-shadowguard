from typing import Dict, Any, Optional
from datetime import datetime, timezone

class DeceptionVirtualFilesystem:
    """
    Isolated in-memory honeypot filesystem that traps path traversal and unauthorized
    file exfiltration attempts without ever accessing real disk storage.
    """

    def __init__(self):
        # Synthetic honeypot file records with clear canary labels
        self._virtual_files: Dict[str, str] = {
            "/etc/passwd": (
                "# SHADOWGUARD HONEYPOT DECEPTION FS - SYNTHETIC DATA ONLY\n"
                "root:x:0:0:Fake Deception Root:/root:/bin/sh\n"
                "daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\n"
                "shadowguard_canary:x:1001:1001:Honeypot Canary:/home/canary:/bin/false\n"
                "demo_admin:x:1002:1002:Deception Admin Account:/home/admin:/bin/bash\n"
                "# CANARY_ID: CANARY-X9821-EXFIL-TRAP"
            ),
            "/etc/shadow": (
                "# SHADOWGUARD HONEYPOT DECEPTION FS\n"
                "root:$6$canary$DUMMY_SALT_HASH_DO_NOT_CRACK:19000:0:99999:7:::\n"
                "demo_admin:$6$fake$SIMULATED_HASH_CANARY_VALUE:19000:0:99999:7:::"
            ),
            "/fake_credentials.txt": (
                "=== SHADOWGUARD HONEYPOT DECOY CREDENTIALS ===\n"
                "AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE_DECOY\n"
                "AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY_DECOY\n"
                "CANARY_ENDPOINT=https://canary.sentinel-x.security/trap?id=9921\n"
                "STATUS=ISOLATED_DECEPTION_ACTIVE"
            ),
            "/fake_users.txt": (
                "username,role,last_login,access_level\n"
                "honeypot_user1,read_only,2026-10-14,synthetic\n"
                "trap_admin,sysadmin,2026-10-13,canary_monitored\n"
                "dummy_auditor,compliance,2026-10-12,synthetic"
            ),
            "/var/log/audit.log": (
                "[2026-10-14T08:00:00Z] [AUDIT] System boots in honeypot mode\n"
                "[2026-10-14T08:12:01Z] [ALERT] Path traversal probe intercepted by ShadowGuard sandbox"
            )
        }

    def has_file(self, path: str) -> bool:
        norm = self._normalize_path(path)
        return norm in self._virtual_files

    def read_file(self, requested_path: str) -> Dict[str, Any]:
        """
        Safely returns synthetic honeypot content for intercepted traversal attempts.
        """
        norm = self._normalize_path(requested_path)
        content = self._virtual_files.get(norm)

        if not content:
            # Fallback to general synthetic canary file
            norm = "/etc/passwd"
            content = self._virtual_files[norm]

        return {
            "synthetic_path": norm,
            "content": content,
            "is_simulated": True,
            "deception_status": "TRAPPED_IN_SHADOW_SANDBOX",
            "canary_signature": "CANARY-SENTINEL-X-TRAP-VERIFIED",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def _normalize_path(self, path: str) -> str:
        if not path:
            return "/etc/passwd"
        p = path.replace("\\", "/").lower()
        if "passwd" in p:
            return "/etc/passwd"
        if "shadow" in p:
            return "/etc/shadow"
        if "credential" in p or "secret" in p or "env" in p:
            return "/fake_credentials.txt"
        if "user" in p:
            return "/fake_users.txt"
        if "audit" in p or "log" in p:
            return "/var/log/audit.log"
        return "/etc/passwd"

# Global singleton
deception_fs = DeceptionVirtualFilesystem()
