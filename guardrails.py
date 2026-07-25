"""
guardrails.py
─────────────
Shared safety layer for LangChain ReAct agents.

Provides three guard layers:
  1. Input Guardrails   – validate and sanitize user input before it
                          reaches the LLM.
  2. Tool Guardrails    – safe parsing of LLM-generated tool arguments,
                          replacing the dangerous eval() pattern.
  3. Output Guardrails  – filter and redact the agent's final response
                          before it is shown to the user.

Usage:
    from guardrails import (
        validate_input,
        safe_parse_tool_input,
        validate_output,
        MAX_AGENT_ITERATIONS,
    )
"""

import ast
import re
import logging

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Shared constants
# ─────────────────────────────────────────────

# Maximum iterations for the ReAct agent loop.
# Prevents infinite loops caused by confused or adversarially prompted LLMs.
MAX_AGENT_ITERATIONS: int = 10

# Maximum length (chars) of a user input string.
MAX_INPUT_LENGTH: int = 1000

# Maximum length (chars) of the agent's output before it is truncated.
MAX_OUTPUT_LENGTH: int = 4000


# ─────────────────────────────────────────────
# Layer 1 – INPUT GUARDRAILS
# ─────────────────────────────────────────────

# Prompt-injection keyword patterns (case-insensitive).
# If any of these are found in the user input, the request is rejected.
_INJECTION_PATTERNS: list[str] = [
    r"ignore\s+(previous|prior|all)\s+instructions",
    r"forget\s+(previous|prior|all|your)\s+instructions",
    r"forget\s+all\s+prior",                # "forget all prior instructions"
    r"disregard\s+(previous|prior|all)\s+instructions",
    r"disregard\s+all\s+previous",          # "disregard all previous instructions"
    r"you\s+are\s+now\s+(?:a|an)",          # "you are now a pirate"
    r"act\s+as\s+(?:a|an|if)",              # "act as a"
    r"pretend\s+(you\s+are|to\s+be)",       # "pretend you are"
    r"jailbreak",
    r"DAN\b",                               # "Do Anything Now" jailbreak
    r"prompt\s+injection",
    r"reveal\s+(your|the)\s+(system\s+)?prompt",
    r"ignore\s+ethical",
    r"bypass\s+(safety|filter|restriction)",
    r"without\s+(any\s+)?(restrictions|limitations|filters)",
    r"no\s+restrictions",
]

_COMPILED_INJECTION_RE = [
    re.compile(p, re.IGNORECASE) for p in _INJECTION_PATTERNS
]


def validate_input(text: str) -> str:
    """
    Validate and sanitize a raw user input string.

    Checks performed:
      - Input is not empty.
      - Input does not exceed MAX_INPUT_LENGTH characters.
      - Input does not contain prompt-injection patterns.

    Returns the original text (unchanged) if all checks pass.

    Raises:
        ValueError: with a user-friendly message if any check fails.
    """
    # 1. Empty input check
    stripped = text.strip()
    if not stripped:
        raise ValueError("La entrada no puede estar vacía.")

    # 2. Length check
    if len(stripped) > MAX_INPUT_LENGTH:
        raise ValueError(
            f"La entrada es demasiado larga ({len(stripped)} caracteres). "
            f"El máximo permitido es {MAX_INPUT_LENGTH} caracteres."
        )

    # 3. Prompt-injection detection
    for pattern in _COMPILED_INJECTION_RE:
        if pattern.search(stripped):
            logger.warning(
                "Prompt injection attempt detected. Pattern: %s | Input: %.100s",
                pattern.pattern,
                stripped,
            )
            raise ValueError(
                "⚠️ Tu consulta contiene instrucciones que no están permitidas. "
                "Por favor, reformula tu pregunta."
            )

    return stripped


# ─────────────────────────────────────────────
# Layer 2 – TOOL GUARDRAILS
# ─────────────────────────────────────────────

def safe_parse_tool_input(tool_name: str, tool_input):
    """
    Safely parse LLM-generated tool arguments.

    Replaces the dangerous `eval(tool_input)` pattern used in the
    multiplica2 dispatch block. Uses ast.literal_eval(), which only
    evaluates Python literals (tuples, numbers, strings) and cannot
    execute arbitrary code.

    Args:
        tool_name:  Name of the tool being invoked (used for logging).
        tool_input: Raw string or value produced by the LLM.

    Returns:
        The parsed Python value (e.g. a tuple of floats for multiplica2).

    Raises:
        ValueError: If the string cannot be safely parsed.
    """
    if not isinstance(tool_input, str):
        # Already a Python object – return as-is
        return tool_input

    try:
        parsed = ast.literal_eval(tool_input)
        logger.debug("safe_parse_tool_input[%s]: %r → %r", tool_name, tool_input, parsed)
        return parsed
    except (ValueError, SyntaxError) as exc:
        logger.warning(
            "safe_parse_tool_input[%s]: failed to parse %r – %s",
            tool_name, tool_input, exc,
        )
        raise ValueError(
            f"No se pudo interpretar el argumento para la herramienta '{tool_name}': "
            f"'{tool_input}'. Asegúrate de que el formato sea correcto."
        ) from exc


# ─────────────────────────────────────────────
# Layer 3 – OUTPUT GUARDRAILS
# ─────────────────────────────────────────────

# Simple regex patterns for PII redaction in the agent's output.
_PII_PATTERNS: list[tuple[str, str]] = [
    # Email addresses
    (r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", "[EMAIL REDACTED]"),
    # Phone numbers (loose: sequences of 7–15 digits, possibly with spaces/dashes)
    (r"\b(?:\+?\d[\d\s\-().]{6,14}\d)\b", "[PHONE REDACTED]"),
]

_COMPILED_PII = [
    (re.compile(p, re.IGNORECASE), repl) for p, repl in _PII_PATTERNS
]

# Blocked content keywords in the final output (hardcoded safety net).
_OUTPUT_BLOCKED_PATTERNS: list[str] = [
    r"\bhate\s+speech\b",
    r"\bself[- ]harm\b",
    r"\bsuicid",
]

_COMPILED_OUTPUT_BLOCKED = [
    re.compile(p, re.IGNORECASE) for p in _OUTPUT_BLOCKED_PATTERNS
]


def validate_output(text: str) -> str:
    """
    Validate and sanitize the agent's final response before displaying it.

    Checks performed:
      - Blocked content patterns trigger a safe replacement message.
      - PII patterns are redacted from the response text.
      - Responses longer than MAX_OUTPUT_LENGTH are truncated.

    Returns the sanitised response string.
    """
    # 1. Blocked content check
    for pattern in _COMPILED_OUTPUT_BLOCKED:
        if pattern.search(text):
            logger.warning(
                "Blocked content detected in agent output. Pattern: %s",
                pattern.pattern,
            )
            return (
                "⚠️ La respuesta del agente contenía contenido que no está permitido "
                "mostrar. Por favor, reformula tu pregunta."
            )

    # 2. PII redaction
    for pattern, replacement in _COMPILED_PII:
        text = pattern.sub(replacement, text)

    # 3. Length cap
    if len(text) > MAX_OUTPUT_LENGTH:
        text = text[:MAX_OUTPUT_LENGTH] + "\n\n… *(respuesta truncada)*"

    return text
