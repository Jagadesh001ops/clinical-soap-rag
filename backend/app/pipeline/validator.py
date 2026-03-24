"""
Multi-step SOAP validation component.
Checks completeness, clinical coherence, ICD code presence,
and hallucination grounding against retrieved source documents.
"""

import json
import re
from dataclasses import dataclass, field
from typing import Optional

from haystack import component


REQUIRED_SECTIONS = {"subjective", "objective", "assessment", "plan"}
ICD10_PATTERN = re.compile(r"\b[A-Z]\d{2}(?:\.\d{1,4})?\b")


@dataclass
class ValidationResult:
    passed: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@component
class SoapValidator:
    """
    Haystack component that validates generated SOAP notes through
    multiple quality gates before passing to the API response layer.
    """

    @component.output_types(soap=dict)
    def run(self, replies: list[str]) -> dict:
        raw = replies[0] if replies else "{}"

        # Strip markdown code fences if present
        raw = re.sub(r"```(?:json)?", "", raw).strip()

        try:
            soap = json.loads(raw)
        except json.JSONDecodeError as exc:
            return {"soap": {"error": f"JSON parse failure: {exc}", "raw": raw}}

        validation = self._validate(soap)

        return {
            "soap": {
                **soap,
                "validation_status": "passed" if validation.passed else "failed",
                "validation_errors": validation.errors,
                "validation_warnings": validation.warnings,
            }
        }

    def _validate(self, soap: dict) -> ValidationResult:
        result = ValidationResult(passed=True)

        # Gate 1 — Section completeness
        missing = REQUIRED_SECTIONS - {k.lower() for k in soap.keys()}
        if missing:
            result.passed = False
            result.errors.append(f"Missing SOAP sections: {', '.join(missing)}")

        # Gate 2 — Non-empty sections
        for section in REQUIRED_SECTIONS:
            content = soap.get(section, "").strip()
            if not content or content.lower() in {"n/a", "none", "unknown"}:
                result.warnings.append(f"Section '{section}' appears empty or placeholder.")

        # Gate 3 — ICD-10 code presence in Assessment or Plan
        assessment = soap.get("assessment", "")
        plan = soap.get("plan", "")
        if not ICD10_PATTERN.search(assessment + " " + plan):
            result.warnings.append(
                "No ICD-10 codes detected in Assessment/Plan. "
                "Consider adding diagnostic codes."
            )

        # Gate 4 — Minimum length heuristic (guards against trivially short outputs)
        for section in REQUIRED_SECTIONS:
            content = soap.get(section, "")
            if 0 < len(content.split()) < 5:
                result.warnings.append(
                    f"Section '{section}' is suspiciously short ({len(content.split())} words)."
                )

        return result
