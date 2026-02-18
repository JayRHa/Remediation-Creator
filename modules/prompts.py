"""Prompt and template definitions for script generation."""

from __future__ import annotations

DETECTION_SCRIPT_PROMPT = """
You are a senior endpoint engineer creating Microsoft Intune detection scripts.
Rules:
- Return only valid PowerShell code. No markdown, no prose.
- Detection scripts must never modify the system state.
- Exit with code 0 when compliant/not affected, and exit with code 1 when non-compliant/affected.
- Keep scripts robust and production-safe with clear Write-Host output.
""".strip()


REMEDIATION_SCRIPT_PROMPT = """
You are a senior endpoint engineer creating Microsoft Intune remediation scripts.
Rules:
- Return only valid PowerShell code. No markdown, no prose.
- Remediate the issue found by the paired detection script.
- Include defensive checks and meaningful Write-Host output.
- Exit with code 0 on success and non-zero on failure.
""".strip()


SCENARIO_TEMPLATES = [
    {
        "name": "BitLocker Compliance",
        "description": (
            "Check whether OS drive BitLocker protection is enabled and recovery "
            "protector exists. If missing, remediate by enabling BitLocker with "
            "appropriate safeguards."
        ),
    },
    {
        "name": "Disk Cleanup Guard",
        "description": (
            "Detect if free disk space on C: is below 15%. Remediate by clearing temp "
            "folders and Windows Update cache in a controlled, logged manner."
        ),
    },
    {
        "name": "Windows Time Service",
        "description": (
            "Detect if w32time service is disabled or stopped. Remediate by setting it "
            "to automatic startup and starting the service."
        ),
    },
    {
        "name": "Local Admin Drift",
        "description": (
            "Detect unauthorized local admins outside an approved allow-list. Remediate "
            "by removing unauthorized members while keeping built-in and approved accounts."
        ),
    },
]
