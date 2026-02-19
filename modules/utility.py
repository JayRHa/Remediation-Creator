"""Core service utilities for script generation, validation, and upload."""

from __future__ import annotations

import base64
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import requests
from openai import AzureOpenAI, OpenAI

from modules.prompts import DETECTION_SCRIPT_PROMPT, REMEDIATION_SCRIPT_PROMPT

GRAPH_BASE_URL = "https://graph.microsoft.com/beta/"
DEFAULT_TIMEOUT_SECONDS = 45

_DETECTION_MUTATION_MARKERS = (
    r"\bSet-",
    r"\bNew-",
    r"\bRemove-",
    r"\bRename-",
    r"\bStart-",
    r"\bStop-",
    r"\bRestart-",
    r"\bInvoke-",
    r"\breg\s+add\b",
    r"\bsc\s+config\b",
)


@dataclass(slots=True)
class ScriptArtifact:
    """Generated detection/remediation script bundle."""

    description: str
    mode: str
    detection_script: str
    remediation_script: str
    created_at: str
    fingerprint: str


@dataclass(slots=True)
class ValidationReport:
    """Validation output for generated scripts."""

    errors: list[str]
    warnings: list[str]
    infos: list[str]

    @property
    def is_valid(self) -> bool:
        return not self.errors


class Utility:
    """Backend service facade for AI generation and Graph upload."""

    def __init__(
        self,
        model_name: str,
        graph_auth_header: dict[str, str] | None = None,
        provider: str = "azure",
        api_key: str = "",
        azure_openai_endpoint: str = "",
        azure_openai_api_version: str = "2024-10-21",
    ):
        self.provider = provider.lower().strip()
        self.model_name = model_name.strip()
        self.graph_auth_header = graph_auth_header or {}

        if not self.model_name:
            raise ValueError("Model/deployment name is required.")

        if self.provider == "openai":
            if not api_key.strip():
                raise ValueError("OPENAI_API_KEY is required for OpenAI provider.")
            self.client = OpenAI(api_key=api_key)
        elif self.provider == "azure":
            if not api_key.strip():
                raise ValueError("AZURE_OPENAI_KEY is required for Azure provider.")
            if not azure_openai_endpoint.strip():
                raise ValueError("AZURE_OPENAI_ENDPOINT is required for Azure provider.")
            self.client = AzureOpenAI(
                api_key=api_key,
                api_version=azure_openai_api_version,
                azure_endpoint=azure_openai_endpoint,
            )
        else:
            raise ValueError("Unsupported provider. Use 'azure' or 'openai'.")

    def generate(
        self,
        description: str,
        include_remediation: bool,
        temperature: float = 0.2,
        max_tokens: int = 1600,
        extra_requirements: str = "",
    ) -> ScriptArtifact:
        """Generate detection and optionally remediation scripts."""
        if not description.strip():
            raise ValueError("Description cannot be empty.")

        detection_prompt = self._build_detection_prompt(description, extra_requirements)
        detection_script = self._invoke_gpt_call(
            user=detection_prompt,
            system=DETECTION_SCRIPT_PROMPT,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        remediation_script = ""
        mode = "Detection only"
        if include_remediation:
            remediation_prompt = self._build_remediation_prompt(
                description=description,
                detection_script=detection_script,
                extra_requirements=extra_requirements,
            )
            remediation_script = self._invoke_gpt_call(
                user=remediation_prompt,
                system=REMEDIATION_SCRIPT_PROMPT,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            mode = "Detection and Remediation"

        return ScriptArtifact(
            description=description.strip(),
            mode=mode,
            detection_script=detection_script.strip(),
            remediation_script=remediation_script.strip(),
            created_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ"),
            fingerprint=self._fingerprint(detection_script, remediation_script),
        )

    def validate_scripts(self, detection_script: str, remediation_script: str = "") -> ValidationReport:
        """Run lightweight static validation checks for generated scripts."""
        errors: list[str] = []
        warnings: list[str] = []
        infos: list[str] = []

        detection = detection_script.strip()
        remediation = remediation_script.strip()

        if not detection:
            errors.append("Detection script is empty.")
            return ValidationReport(errors=errors, warnings=warnings, infos=infos)

        detection_exits = self._extract_exit_codes(detection)
        if 0 not in detection_exits or 1 not in detection_exits:
            warnings.append(
                "Detection script should include both exit 0 and exit 1 paths for Intune compliance logic."
            )

        risky_commands = self._find_detection_mutations(detection)
        if risky_commands:
            warnings.append(
                "Detection script appears to mutate the system. Check these commands: "
                + ", ".join(sorted(risky_commands))
            )

        if "Write-Host" not in detection:
            infos.append("Detection script has no Write-Host output. Consider adding operator-friendly status text.")

        if remediation:
            remediation_exits = self._extract_exit_codes(remediation)
            if 0 not in remediation_exits:
                warnings.append("Remediation script should include exit 0 on successful remediation.")
            if "try" not in remediation.lower() or "catch" not in remediation.lower():
                infos.append("Remediation script has no explicit try/catch block.")
            if "Write-Host" not in remediation:
                infos.append("Remediation script has no Write-Host output.")

        return ValidationReport(errors=errors, warnings=warnings, infos=infos)

    def build_upload_payload(
        self,
        script_name: str,
        description: str,
        scope: str,
        detection_script: str,
        remediation_script: str = "",
        run_as_32_bit: bool = True,
        enforce_signature_check: bool = False,
        publisher: str = "Remediation Creator Next",
    ) -> dict[str, Any]:
        """Build a Graph-ready upload payload for device health scripts."""
        clean_name = script_name.strip()
        if not clean_name:
            raise ValueError("Script name is required.")
        if not detection_script.strip():
            raise ValueError("Detection script is required for upload.")

        normalized_scope = "system" if scope.lower().startswith("system") else "user"

        payload = {
            "displayName": clean_name,
            "description": description.strip(),
            "publisher": publisher,
            "runAs32Bit": run_as_32_bit,
            "runAsAccount": normalized_scope,
            "enforceSignatureCheck": enforce_signature_check,
            "detectionScriptContent": self._b64(detection_script),
            "remediationScriptContent": self._b64(remediation_script) if remediation_script.strip() else "",
            "roleScopeTagIds": ["0"],
        }
        return payload

    def upload_payload(self, payload: dict[str, Any], endpoint: str = "deviceManagement/deviceHealthScripts") -> dict[str, Any]:
        """Upload a prepared payload to Microsoft Graph."""
        if not self.graph_auth_header or "Authorization" not in self.graph_auth_header:
            raise ValueError("Graph authentication header is missing. Authenticate first.")

        uri = GRAPH_BASE_URL + endpoint
        response = requests.post(
            uri,
            headers=self.graph_auth_header,
            json=payload,
            timeout=DEFAULT_TIMEOUT_SECONDS,
        )

        if response.status_code >= 400:
            raise RuntimeError(
                f"Graph upload failed ({response.status_code}): {response.text[:500]}"
            )

        if response.content:
            try:
                return response.json()
            except ValueError:
                return {"status": "ok", "raw": response.text}
        return {"status": "ok"}

    @staticmethod
    def pretty_json(data: dict[str, Any]) -> str:
        return json.dumps(data, indent=2, ensure_ascii=True)

    def _invoke_gpt_call(
        self,
        user: str,
        system: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

        # GPT-5 style chat models are often exposed through the Responses API.
        if self._prefer_responses_api():
            try:
                return self._invoke_with_responses(
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            except Exception:
                # Fall back to chat completions for compatibility with classic deployments.
                pass

        return self._invoke_with_chat_completions(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def _prefer_responses_api(self) -> bool:
        lower_model = self.model_name.lower()
        return lower_model.startswith("gpt-5")

    def _invoke_with_responses(
        self,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> str:
        try:
            response = self.client.responses.create(
                model=self.model_name,
                input=messages,
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
        except Exception as exc:
            if self._is_temperature_default_only_error(exc):
                response = self.client.responses.create(
                    model=self.model_name,
                    input=messages,
                    max_output_tokens=max_tokens,
                )
            else:
                raise

        output_text = getattr(response, "output_text", None)
        if isinstance(output_text, str) and output_text.strip():
            return output_text.strip()

        extracted = self._extract_text_from_responses_output(getattr(response, "output", None))
        if extracted:
            return extracted
        raise RuntimeError("Responses API returned no text output.")

    def _invoke_with_chat_completions(
        self,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                messages=messages,
            )
        except Exception as exc:
            message = str(exc)
            if "max_tokens" in message and "max_completion_tokens" in message and self._is_temperature_default_only_error(exc):
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    max_completion_tokens=max_tokens,
                    messages=messages,
                )
            elif "max_tokens" in message and "max_completion_tokens" in message:
                try:
                    response = self.client.chat.completions.create(
                        model=self.model_name,
                        temperature=temperature,
                        max_completion_tokens=max_tokens,
                        messages=messages,
                    )
                except Exception as exc2:
                    if self._is_temperature_default_only_error(exc2):
                        response = self.client.chat.completions.create(
                            model=self.model_name,
                            max_completion_tokens=max_tokens,
                            messages=messages,
                        )
                    else:
                        raise
            elif self._is_temperature_default_only_error(exc):
                try:
                    response = self.client.chat.completions.create(
                        model=self.model_name,
                        max_tokens=max_tokens,
                        messages=messages,
                    )
                except Exception as exc2:
                    if "max_tokens" in str(exc2) and "max_completion_tokens" in str(exc2):
                        response = self.client.chat.completions.create(
                            model=self.model_name,
                            max_completion_tokens=max_tokens,
                            messages=messages,
                        )
                    else:
                        raise
            else:
                raise

        content = response.choices[0].message.content
        if isinstance(content, str) and content.strip():
            return content.strip()
        if isinstance(content, list):
            chunks: list[str] = []
            for item in content:
                text = item.get("text") if isinstance(item, dict) else getattr(item, "text", "")
                if isinstance(text, str) and text:
                    chunks.append(text)
            merged = "".join(chunks).strip()
            if merged:
                return merged
        raise RuntimeError("Model returned an empty response.")

    @staticmethod
    def _extract_text_from_responses_output(output_items: Any) -> str:
        if output_items is None:
            return ""
        chunks: list[str] = []
        for item in output_items:
            item_type = item.get("type") if isinstance(item, dict) else getattr(item, "type", "")
            if item_type != "message":
                continue
            content = item.get("content") if isinstance(item, dict) else getattr(item, "content", [])
            for block in content:
                block_type = block.get("type") if isinstance(block, dict) else getattr(block, "type", "")
                text = block.get("text") if isinstance(block, dict) else getattr(block, "text", "")
                if block_type == "output_text" and isinstance(text, str):
                    chunks.append(text)
        return "".join(chunks).strip()

    @staticmethod
    def _is_temperature_default_only_error(exc: Exception) -> bool:
        text = str(exc).lower()
        return (
            "temperature" in text
            and (
                "unsupported value" in text
                or "unsupported parameter" in text
                or "default (1)" in text
                or "only the default" in text
            )
        )

    @staticmethod
    def _build_detection_prompt(description: str, extra_requirements: str) -> str:
        prompt = (
            "Create a Microsoft Intune Endpoint Analytics detection script for Windows devices.\n\n"
            f"Description:\n{description.strip()}\n\n"
            "Output constraints:\n"
            "- Output must be valid PowerShell only\n"
            "- No markdown, no explanation text\n"
            "- Include clear status output\n"
        )
        if extra_requirements.strip():
            prompt += f"\nAdditional requirements:\n{extra_requirements.strip()}\n"
        return prompt

    @staticmethod
    def _build_remediation_prompt(description: str, detection_script: str, extra_requirements: str) -> str:
        prompt = (
            "Create a Microsoft Intune Endpoint Analytics remediation script for Windows devices.\n\n"
            f"Description:\n{description.strip()}\n\n"
            "Detection script context:\n"
            f"{detection_script.strip()}\n\n"
            "Output constraints:\n"
            "- Output must be valid PowerShell only\n"
            "- No markdown, no explanation text\n"
            "- Include robust error handling and status output\n"
        )
        if extra_requirements.strip():
            prompt += f"\nAdditional requirements:\n{extra_requirements.strip()}\n"
        return prompt

    @staticmethod
    def _extract_exit_codes(script: str) -> set[int]:
        codes = re.findall(r"\bexit\s+([0-9]+)\b", script, flags=re.IGNORECASE)
        return {int(code) for code in codes}

    @staticmethod
    def _find_detection_mutations(script: str) -> set[str]:
        found = set()
        for marker in _DETECTION_MUTATION_MARKERS:
            if re.search(marker, script, flags=re.IGNORECASE):
                found.add(marker.replace("\\b", ""))
        return found

    @staticmethod
    def _fingerprint(detection_script: str, remediation_script: str) -> str:
        digest = hashlib.sha256(
            (detection_script.strip() + "\n--\n" + remediation_script.strip()).encode("utf-8")
        ).hexdigest()
        return digest[:12]

    @staticmethod
    def _b64(script: str) -> str:
        return base64.b64encode(script.encode("utf-8")).decode("utf-8")
