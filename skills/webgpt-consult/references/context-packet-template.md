# GPT-5.6 Sol Context Packet Template

Use this template for substantial ChatGPT Web consultations. Simple questions and short follow-ups in an already verified conversation may use a smaller delta prompt instead of repeating the whole packet.

````markdown
Request-ID: wgpt-<random>

CONTEXT_PACKET_V1

```json
{
  "task_id": "webgpt-consult-YYYYMMDD-HHMMSS",
  "sentinel": "WEBGPT_CONSULT_RESULT_YYYYMMDD_HHMMSS",
  "task_type": "architecture_review|business_consult|content_strategy|skill_design|risk_review|other",
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

First line must be:
Request-ID: wgpt-<random>

Second line must be:
WEBGPT_CONSULT_RESULT_YYYYMMDD_HHMMSS

Then use:
1. Reasoning brief: assumptions, frame, evidence, counterargument, tradeoffs
2. Direct judgment
3. Biggest flaw
4. Required changes
5. What to ignore
6. Final adoption recommendation
````

## Follow-up in the same verified conversation

Do not resend the full packet when the existing ChatGPT Web conversation already contains the relevant background. Use the same conversation and send only the new delta with a fresh Request-ID. Include a fresh sentinel when the follow-up is substantial enough to benefit from the full completion contract.

Example:

```markdown
Request-ID: wgpt-<new-random>
Sentinel: WEBGPT_CONSULT_RESULT_YYYYMMDD_HHMMSS

## CURRENT_DELTA
<What changed, what new evidence appeared, or what was implemented?>

## ASK
<What should GPT-5.6 Sol examine now?>

Begin your response with exactly:
Request-ID: wgpt-<new-random>
WEBGPT_CONSULT_RESULT_YYYYMMDD_HHMMSS
```

## Evidence rules

- A local path is not evidence by itself. Upload the actual file, paste the relevant content, or provide a faithful excerpt.
- Prefer the smallest source set that preserves the truth of the problem.
- Preserve verbatim errors, measurements, and important constraints when wording matters.
- Remove unrelated private information and never include blocked secrets, authentication material, or payment credentials.
- Run the local safety guard on the exact outgoing packet and UTF-8 text attachments before Send.
