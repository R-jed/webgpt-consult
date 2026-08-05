# GPT-5.6 Sol Pro Context Packet Template

Use this format for substantial ChatGPT Web consultations. It retains the proven `CONTEXT_PACKET_V1` structure from `gpt56-sol-pro-consult`, with identifiers adapted for `webgpt-consult`.

Use enough context to preserve the causal truth of the problem. For genuinely difficult work, roughly 8,000 to 15,000 characters can be appropriate when a shorter prompt would remove important constraints, evidence, attempts, or tradeoffs. This is guidance, not a quota. Do not pad a packet.

````markdown
CONTEXT_PACKET_V1

```json
{
  "task_id": "webgpt-consult-YYYYMMDD-HHMMSS-<nonce>",
  "sentinel": "WEBGPT_CONSULT_RESULT_YYYYMMDD_HHMMSS_<same-nonce>",
  "task_type": "architecture_review|business_consult|content_strategy|skill_design|risk_review|debugging|code_review|other",
  "context_strategy": "problem_first_full_context",
  "credential_status": "no_executable_credentials",
  "context_hash": "<sha256 of markdown body>",
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

First line must be: WEBGPT_CONSULT_RESULT_YYYYMMDD-HHMMSS_<same-nonce>

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
- For second-opinion work, fill `LOCAL_JUDGMENT` before consultation when a local view already exists. This creates a concrete position for the Web model to challenge and makes later adopt/reject/modify decisions auditable.
- Omit `LOCAL_JUDGMENT` when the user wants an independent first view or when no meaningful local judgment exists yet.
- Separate facts, local judgment, and unknowns. Do not present assumptions as evidence.
- Sections with no useful information may be omitted instead of filled with boilerplate.
- `credential_status` must reflect the actual local safety check.
- `context_hash`, when present, must be a real SHA-256 of the final Markdown body used for the consultation. It is an integrity/audit marker; result completion still depends on the sentinel and Chrome verification.
- Generate a fresh `task_id` and sentinel for every Web submission.
- Treat the Web answer as advisory. Codex verifies important claims against local evidence before final delivery.

## Follow-up in the same verified conversation

Do not resend the full packet when the existing conversation already contains the relevant background. Reuse the same verified conversation and send a compact delta packet with a fresh identity:

````markdown
CONTEXT_PACKET_V1

```json
{
  "task_id": "webgpt-consult-YYYYMMDD-HHMMSS-<nonce>",
  "sentinel": "WEBGPT_CONSULT_RESULT_YYYYMMDD-HHMMSS_<same-nonce>",
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

First line must be: WEBGPT_CONSULT_RESULT_YYYYMMDD-HHMMSS_<same-nonce>
````

Reuse prior context already present in the verified conversation. Restate older material only when it is stale, ambiguous, contradicted by new evidence, or essential to the new question.

## Evidence rules

- A local path is not evidence by itself. Upload the actual file, paste the relevant content, or provide a faithful excerpt/bundle.
- Prefer the smallest evidence set that preserves the truth of the problem.
- Prefer original human-readable files when they can be uploaded reliably. Use the bundled helper when many selected text files are awkward to upload individually or an archive is rejected.
- Preserve verbatim errors, measurements, source details, and important constraints when wording or structure matters.
- Do not strip task-relevant user-owned business/project facts merely because they are private. Remove unrelated private information and block executable credentials/payment secrets.
- Run the local safety guard on the exact outgoing packet and every UTF-8 text attachment before Send.
