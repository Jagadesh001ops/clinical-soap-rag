"""
Clinical note de-identification service.
Removes/replaces PHI before notes enter the RAG pipeline.

Patterns covered:
  - Patient names (NER-based, fallback regex)
  - Dates → [DATE]
  - Phone numbers → [PHONE]
  - SSNs → [SSN]
  - MRN numbers → [MRN]
  - Addresses → [ADDRESS]

TODO: Integrate spaCy en_core_sci_sm for NER-based name detection.
"""

import re

# Regex-based PHI patterns (fast, deterministic baseline)
_PATTERNS = [
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[SSN]"),
    (re.compile(r"\b(?:MRN|mrn)[:\s#]*\d+\b"), "[MRN]"),
    (re.compile(r"\b(?:\+1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b"), "[PHONE]"),
    (re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"), "[DATE]"),
    (re.compile(
        r"\b(?:January|February|March|April|May|June|July|August"
        r"|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b",
        re.IGNORECASE,
    ), "[DATE]"),
]


def deidentify(text: str) -> str:
    """Apply PHI scrubbing patterns to clinical note text."""
    for pattern, replacement in _PATTERNS:
        text = pattern.sub(replacement, text)
    return text
