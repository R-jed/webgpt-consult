#!/usr/bin/env python3
"""Deterministic model policy for GPT-5.6 Sol Pro/High consultations."""

from __future__ import annotations

import re
from dataclasses import dataclass

TIER_PRO = "Pro"
TIER_HIGH = "High"
SUPPORTED_TIERS = (TIER_PRO, TIER_HIGH)
ALLOWED_TIER_LABELS = frozenset(SUPPORTED_TIERS)
GPT56_PRO_TESTIDS = ("data-testid=model-switcher-gpt-5-6-pro",)
GPT56_FAMILY_HINTS = ("GPT-5.6 Sol", "GPT 5.6 Sol", "5.6 Sol")
LEGACY_PRO_HINTS = ("gpt-5-5-pro", "GPT 5.5 Pro", "GPT-5.5 Pro", "Pro Extended")


@dataclass(frozen=True)
class ModelCandidate:
    tier: str
    display_name: str
    ref: str | None
    checked: bool
    family: str | None
    evidence: str
    enabled: bool = True

    @property
    def actionable(self) -> bool:
        return self.enabled and self.ref is not None

    @property
    def usable(self) -> bool:
        """A selected tier may lack a click ref; an unselected tier needs one."""
        return self.enabled and (self.checked or self.ref is not None)


@dataclass(frozen=True)
class ModelSelection:
    requested_tier: str
    selected_tier: str
    display_name: str
    ref: str | None
    downgraded: bool
    evidence: str


class ModelRoutingError(RuntimeError):
    pass


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
    for i in range(candidate_index - 1, -1, -1):
        line = lines[i]
        if "role=menuitem" in line and "role=menuitemradio" not in line:
            context = line + ("\n" + lines[i + 1] if i + 1 < len(lines) else "")
            return "GPT-5.6 Sol" if _has_gpt56_family(context) else None
    return None


def _visible_label(line: str) -> str:
    return line.rsplit(">", 1)[-1].strip() if ">" in line else line.strip()


def _extract_tier_label(line: str) -> tuple[str, str] | None:
    """Accept only literal Pro/High tiers, either standalone or compact with GPT-5.6 Sol."""
    label = _visible_label(line)
    if label in ALLOWED_TIER_LABELS:
        return label, label

    if _has_gpt56_family(label):
        for family_hint in sorted(GPT56_FAMILY_HINTS, key=len, reverse=True):
            if family_hint not in label:
                continue
            suffix = label.split(family_hint, 1)[1].strip(" :-–—·")
            if suffix in ALLOWED_TIER_LABELS:
                return suffix, label
    return None


def _is_enabled(line: str) -> bool:
    lowered = line.lower()
    return not (
        "aria-disabled=true" in lowered
        or 'aria-disabled="true"' in lowered
        or re.search(r"(?:^|\s)disabled(?:\s|=|>|$)", lowered)
    )


def _parse_candidate(line: str, lines: list[str], index: int) -> ModelCandidate | None:
    if "role=menuitemradio" not in line and not _block_has_testid(line):
        return None
    if _is_legacy_pro(line):
        return None

    family = "GPT-5.6 Sol" if _has_gpt56_family(line) else _find_section_family(lines, index)
    checked = "aria-checked=true" in line or 'aria-checked="true"' in line
    enabled = _is_enabled(line)
    ref = _extract_ref(line)

    if _block_has_testid(line):
        return ModelCandidate(
            TIER_PRO,
            TIER_PRO,
            ref,
            checked,
            "GPT-5.6 Sol",
            f"gpt56_testid:{line.strip()}",
            enabled,
        )

    tier_info = _extract_tier_label(line)
    if tier_info and family:
        tier, display_name = tier_info
        return ModelCandidate(
            tier,
            display_name,
            ref,
            checked,
            family,
            f"menuitemradio:{display_name}->{tier}+family",
            enabled,
        )
    return None


def discover_model_candidates(menu_state: str) -> list[ModelCandidate]:
    lines = menu_state.splitlines()
    return [candidate for i, line in enumerate(lines) if (candidate := _parse_candidate(line, lines, i)) is not None]


def select_best_model(candidates: list[ModelCandidate]) -> ModelSelection:
    for tier in SUPPORTED_TIERS:
        same_tier = [
            c for c in candidates
            if c.tier == tier and c.family == "GPT-5.6 Sol" and c.usable
        ]
        candidate = next((c for c in same_tier if c.checked and c.enabled), None)
        if candidate is None:
            candidate = next((c for c in same_tier if c.actionable), None)
        if candidate is not None:
            return ModelSelection(
                requested_tier=TIER_PRO,
                selected_tier=candidate.tier,
                display_name=candidate.display_name,
                ref=candidate.ref,
                downgraded=candidate.tier != TIER_PRO,
                evidence=candidate.evidence,
            )
    raise ModelRoutingError("No verified and usable GPT-5.6 Sol Pro or High tier is available.")


def resolve_model_from_state(menu_state: str) -> ModelSelection:
    return select_best_model(discover_model_candidates(menu_state))


def selection_is_confirmed(state: str, selection: ModelSelection) -> bool:
    if not state:
        raise ValueError("selection_is_confirmed requires a non-empty state string.")
    return any(
        c.tier == selection.selected_tier
        and c.family == "GPT-5.6 Sol"
        and c.checked
        and c.enabled
        for c in discover_model_candidates(state)
    )
