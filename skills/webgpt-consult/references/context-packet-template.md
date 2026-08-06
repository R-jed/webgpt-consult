# GPT-5.6 Sol Pro Context Packet Template

Use this format for substantial ChatGPT Web consultations. It retains the proven `CONTEXT_PACKET_V1` structure from `gpt56-sol-pro-consult`, with identifiers adapted for `webgpt-consult` and a compact delta form for verified follow-up turns.

Use enough context to preserve the causal truth of the problem. For genuinely difficult work, roughly 8,000 to 15,000 characters can be appropriate when a shorter prompt would remove important constraints, evidence, attempts, or tradeoffs. This is guidance, not a quota. Do not pad a packet.

## Canonical full packet

````markdown
CONTEXT_PACKET_V1

```json
{
  "task_id": "webgpt-consult-YYYYMMDD-HHMMSS-<nonce>",
  "sentinel": "WEBGPT_CONSULT_RESULT_YYYYMMDD_HHMMSS_<same-nonce>",
  "task_type": "architecture_review|business_consult|content_strategy|skill_design|risk_review|debugging|code_review|other",
  "context_strategy": "problem_first_full_context",
  "credential_status": "no_executable_credentials",
  "context_hash": "<sha256 of exact UTF-8 packet body after this metadata block>",
  "required_output": [
    "reasoning_brief",
    "direct_judgment",
    "biggest_flaw",
    "specific_revisions",
    "adoption_decision"
  ]
}
```

## TASK

## BACKGROUND

## USER_INTENT

## LOCAL_JUDGMENT

## EVIDENCE

## ATTEMPTS_SO_FAR

## OPTIONS

## RISKS

## ASK

Please act as a strict reviewer and deep reasoning partner. Find the biggest flaw first, then give the strongest revised path. Do not provide generic encouragement. Do not reveal hidden chain-of-thought; instead output a concise reasoning brief with assumptions, decision frame, evidence weighting, counterarguments, and tradeoffs.

## RETURN_FORMAT

First line must be: WEBGPT_CONSULT_RESULT_YYYYMMDD_HHMMSS_<same-nonce>

Then use:
1. Reasoning brief: assumptions, frame, evidence, counterargument, tradeoffs
2. Direct judgment
3. Biggest flaw
4. Required changes
5. What to ignore
6. Final adoption recommendation
````

## Adaptation rules

The user's request remains authoritative.

- Use the full format for substantial first-turn reviews, decisions, architecture work, difficult debugging, and other tasks where context loss would damage the answer.
- Change `task_type`, `required_output`, and `RETURN_FORMAT` when the requested deliverable calls for it.
- For second-opinion work, fill `LOCAL_JUDGMENT` when a meaningful local view already exists. Keep it separate from facts and unknowns so the Web model can challenge a concrete position.
- Omit `LOCAL_JUDGMENT` when the user wants an independent first view or no meaningful local judgment exists yet.
- Separate facts, local judgment, assumptions, and unknowns. Do not present assumptions as evidence.
- Preserve verbatim errors, measurements, source details, and important constraints when wording or structure matters.
- Omit sections with no useful information instead of filling them with boilerplate.
- `credential_status` must reflect the actual local safety check.
- Generate a fresh `task_id` and sentinel for every Web submission.
- Treat the Web answer as advisory. Codex verifies important claims against local evidence before final delivery.

Evidence selection, attachment truthfulness, credential handling, and upload behavior are governed by `SKILL.md` and `chrome-workflow.md`. A local path by itself never counts as evidence.

## Follow-up delta packet

Do not resend the full packet when the verified conversation already contains the relevant background. Use a fresh identity and send only the new state, evidence, and ask unless older context is stale, ambiguous, contradicted, or essential to the new question.

````markdown
CONTEXT_PACKET_V1

```json
{
  "task_id": "webgpt-consult-YYYYMMDD-HHMMSS-<nonce>",
  "sentinel": "WEBGPT_CONSULT_RESULT_YYYYMMDD_HHMMSS_<same-nonce>",
  "task_type": "follow_up",
  "context_strategy": "same_conversation_delta",
  "credential_status": "no_executable_credentials"
}
```

## CURRENT_DELTA
<What changed, what new evidence appeared, or what was implemented?>

## ASK
<What should GPT-5.6 Sol examine now?>

## RETURN_FORMAT

First line must be: WEBGPT_CONSULT_RESULT_YYYYMMDD_HHMMSS_<same-nonce>
````

Reuse prior context already present in the verified conversation. Restate older material only when doing so restores accuracy or prevents ambiguity.

## Integrity rules

- `task_id` and sentinel identify one Web submission. Use the same nonce in both and generate a new pair for every submission.
- If `context_hash` is populated, compute SHA-256 over the exact UTF-8 packet body that follows the closing metadata code fence. This avoids self-referential hashing.
- `context_hash` is an integrity and audit marker. It does not replace browser verification, attachment verification, or sentinel verification.
- The first non-empty assistant line must match the current sentinel exactly as required by the Chrome workflow.
- A follow-up delta inherits only context that is still valid in the verified conversation. Correct stale or contradicted context explicitly.
