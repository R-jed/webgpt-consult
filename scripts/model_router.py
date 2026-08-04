#!/usr/bin/env python3
"""Model router for GPT 5.6 Sol Pro/High consultations."""

from __future__ import annotations

import re
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Supported tiers – ordered by priority (highest first)
# ---------------------------------------------------------------------------

TIER_PRO = "Pro"
TIER_HIGH = "High"

SUPPORTED_TIERS: tuple[str, ...] = (TIER_PRO, TIER_HIGH)
ALLOWED_TIER_LABELS: frozenset[str] = frozenset({TIER_PRO, TIER_HIGH})


# ---------------------------------------------------------------------------
# Identification constants
# ---------------------------------------------------------------------------

GPT56_PRO_TESTIDS: tuple[str, ...] = (
    "data-testid=model-switcher-gpt-5-6-pro",
    "data-testid=model-switcher-gpt-5-pro",
)

LEGACY_PRO_HINTS: tuple[str, ...] = (
    "gpt-5-5-pro",
    "GPT 5.5 Pro",
    "GPT-5.5 Pro",
    "Pro Extended",
    "进阶专业",
)

GPT56_FAMILY_HINTS: tuple[str, ...] = ("GPT-5.6 Sol", "GPT 5.6 Sol")

PRO_LABEL_RE = re.compile(r"(?<![A-Za-z0-9])Pro(?![A-Za-z0-9])", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ModelCandidate:
    tier: str
    display_name: str
    ref: str | None
    checked: bool
    family: str | None
    evidence: str


@dataclass(frozen=True)
class ModelSelection:
    requested_tier: str
    selected_tier: str
    display_name: str
    ref: str | None
    downgraded: bool
    evidence: str


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class ModelRoutingError(RuntimeError):
    """Raised when no supported model candidate can be identified."""


# ---------------------------------------------------------------------------
# Pure helper functions
# ---------------------------------------------------------------------------

def _extract_ref(line: str) -> str | None:
    match = re.search(r"\[(\d+)\]", line)
    return match.group(1) if match else None


def _has_gpt56_family(text: str) -> bool:
    return any(hint in text for hint in GPT56_FAMILY_HINTS)


def _is_legacy_pro(text: str) -> bool:
    return any(hint in text for hint in LEGACY_PRO_HINTS)


def _block_has_testid(text: str) -> bool:
    return any(tid in text for tid in GPT56_PRO_TESTIDS)


def _find_section_family(lines: list[str], candidate_index: int) -> str | None:
    """Walk backwards from a candidate line to find its enclosing family section.

    A family section header is a ``role=menuitem`` line (possibly followed by
    an indented family-name line).  We walk backward looking for a section
    header whose own line OR the immediately following line contains a GPT-5.6
    Sol family hint.
    """
    for i in range(candidate_index - 1, -1, -1):
        line = lines[i]
        if "role=menuitem" in line and "role=menuitemradio" not in line:
            # Check this line and the next one (indented family name)
            context = line
            if i + 1 < len(lines):
                context += "\n" + lines[i + 1]
            if _has_gpt56_family(context):
                return "GPT-5.6 Sol"
            return None  # section header found but no family → stop
    return None


def _extract_tier_label(line: str) -> str | None:
    """Extract the tier label text from a menuitemradio first line.

    Only accepts exact labels in ``ALLOWED_TIER_LABELS`` after stripping
    surrounding whitespace.  Extra High, Ultra High, High Plus, Pro Max,
    and all other variants are rejected by the allowlist.
    """
    # Strip the DOM attributes to get the visible label text.
    # Typical line:  [42] <div role=menuitemradio ...>High
    # We look for the content after the last '>' that is not a tag.
    label = line.rsplit(">", 1)[-1].strip() if ">" in line else line.strip()
    if label in ALLOWED_TIER_LABELS:
        return label
    return None


def _parse_candidate_from_block(
    block: str,
    lines: list[str],
    candidate_line_index: int,
) -> ModelCandidate | None:
    """Parse a single menuitemradio block into a ModelCandidate, or None.

    Only Pro and High are supported.  Extra High, Medium, and unknown tiers
    are rejected even if present in the picker.

    The ``block`` is up to 6 lines starting at the candidate line.
    Tier text is only checked on the **first line** so that subsequent
    menuitemradio lines in the lookahead do not cause false matches.

    ``family`` is resolved from the **nearest preceding section header**, not
    from the entire picker state, so cross-family leakage is impossible.

    Tier matching uses an allowlist (``ALLOWED_TIER_LABELS``) so that
    "Extra High", "Ultra High", "Pro Max", etc. are rejected at parse time
    without substring hacks.
    """
    first_line = block.splitlines()[0] if block.splitlines() else ""

    if "role=menuitemradio" not in block and not _block_has_testid(first_line):
        return None

    checked = "aria-checked=true" in first_line
    ref = _extract_ref(first_line)

    family = _find_section_family(lines, candidate_line_index)

    # --- Pro detection ---
    if _is_legacy_pro(first_line):
        return None  # legacy Pro variants are never valid

    if _block_has_testid(first_line):
        # GPT-5.6 specific testid → definitely Pro
        return ModelCandidate(
            tier=TIER_PRO,
            display_name="Pro",
            ref=ref,
            checked=checked,
            family=family,
            evidence=f"testid={first_line}",
        )

    # Bare Pro or High: extract exact label and check against allowlist.
    tier_label = _extract_tier_label(first_line)
    if tier_label == TIER_PRO:
        if family:
            return ModelCandidate(
                tier=TIER_PRO,
                display_name="Pro",
                ref=ref,
                checked=checked,
                family=family,
                evidence=f"menuitemradio Pro + family",
            )
        return None  # bare Pro without family → reject

    if tier_label == TIER_HIGH:
        if family:
            return ModelCandidate(
                tier=TIER_HIGH,
                display_name="High",
                ref=ref,
                checked=checked,
                family=family,
                evidence=f"menuitemradio High + family",
            )
        return None  # bare High without family → reject

    # Extra High, Medium, Instant, and all other tiers are unsupported
    return None


# ---------------------------------------------------------------------------
# Core public pure functions
# ---------------------------------------------------------------------------

def discover_model_candidates(menu_state: str) -> list[ModelCandidate]:
    """Parse a model-switcher menu state into a list of valid candidates.

    Only Pro and High candidates are returned. Extra High, Medium, Instant,
    and unknown models are excluded.

    Family evidence is resolved per-candidate from the nearest preceding
    section header, never from the full picker state.
    """
    lines = menu_state.splitlines()
    candidates: list[ModelCandidate] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if "role=menuitemradio" in line or _block_has_testid(line):
            block = "\n".join(lines[i : i + 6])
            candidate = _parse_candidate_from_block(block, lines, i)
            if candidate is not None:
                candidates.append(candidate)
        i += 1
    return candidates


def select_best_model(candidates: list[ModelCandidate]) -> ModelSelection:
    """Pick the highest-priority candidate from a non-empty list."""
    if not candidates:
        raise ModelRoutingError(
            "No verified GPT-5.6 Sol Pro or High tier is available."
        )

    best: ModelCandidate | None = None
    for tier in SUPPORTED_TIERS:
        for c in candidates:
            if c.tier == tier:
                if best is None:
                    best = c
                break  # first match for this tier wins

    if best is None:
        raise ModelRoutingError(
            "No verified GPT-5.6 Sol Pro or High tier is available."
        )

    downgraded = best.tier != TIER_PRO
    return ModelSelection(
        requested_tier=TIER_PRO,
        selected_tier=best.tier,
        display_name=best.display_name,
        ref=best.ref,
        downgraded=downgraded,
        evidence=best.evidence,
    )


def resolve_model_from_state(menu_state: str) -> ModelSelection:
    """End-to-end: parse menu state → pick best model."""
    candidates = discover_model_candidates(menu_state)
    return select_best_model(candidates)


def selection_is_confirmed(state: str, selection: ModelSelection) -> bool:
    """Check whether the chosen model is actually checked/active in the live state.

    Returns True when confirmed, False otherwise.
    Only raises ValueError for genuinely invalid inputs (None state, etc.).
    ref is an action locator only – it does not prove model identity.
    Verification always uses fresh state evidence.

    This reuses ``discover_model_candidates`` so that discovery and
    confirmation share identical candidate-local parsing semantics –
    no separate lookahead window, no ref-based truth.
    """
    if not state:
        raise ValueError("selection_is_confirmed requires a non-empty state string.")

    candidates = discover_model_candidates(state)
    return any(
        candidate.tier == selection.selected_tier
        and candidate.family == "GPT-5.6 Sol"
        and candidate.checked
        for candidate in candidates
    )
