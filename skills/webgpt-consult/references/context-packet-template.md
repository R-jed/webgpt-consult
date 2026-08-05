# GPT-5.6 Sol Pro Context Packet Template

Use this format for substantial ChatGPT Web consultations. It follows the proven GPT 5.6 Sol Pro consultation packet structure, with only the identifiers adapted for `webgpt-consult`.

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

The packet format is reusable. The user's request remains authoritative.

- Change `task_type` when another label describes the task better.
- Change `required_output` and `RETURN_FORMAT` when the user asks for a different deliverable.
- `LOCAL_JUDGMENT` may be omitted when an independent first view is more useful.
- Sections with no useful information may be omitted instead of filled with boilerplate.
- `credential_status` must reflect the actual local safety check.
- Generate a fresh `task_id` and `sentinel` for every Web submission.

## Follow-up in the same verified conversation

Do not resend the full packet when the existing conversation already contains the relevant background. Reuse the same verified conversation and send a compact delta packet with a fresh identity:

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

Reuse prior context already present in the verified conversation. Restate older material only when it is stale, ambiguous, or essential to the new question.

## Evidence rules

- A local path is not evidence by itself. Upload the actual file, paste the relevant content, or provide a faithful excerpt.
- Prefer the smallest source set that preserves the truth of the problem.
- Preserve verbatim errors, measurements, and important constraints when wording matters.
- Remove unrelated private information and never include blocked secrets, authentication material, or payment credentials.
- Run the local safety guard on the exact outgoing packet and every UTF-8 text attachment before Send.
