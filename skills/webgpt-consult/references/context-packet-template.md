# Context packet guide

Use this when a consultation is complex enough that ChatGPT Web benefits from a structured handoff. It is guidance for Codex, not a required schema for every request.

Simple questions and short follow-ups should stay simple. When the same verified Web conversation already contains the needed context, send only the new information and the current ask.

## When to use a packet

A structured packet is useful when the task has several constraints, source files, prior attempts, competing options, important risks, or enough background that a short prompt would lose causal details.

It is also useful when starting fresh after a long conversation or when branching from an earlier point and the latest state needs to be restated clearly.

## Adaptive template

Keep only the sections that improve the current consultation.

```markdown
Request-ID: <request-id>

## TASK
<What needs to be decided, explained, reviewed, debugged, designed, or produced?>

## SUCCESS CONDITION
<What would make the answer useful?>

## BACKGROUND
<Only the background the Web model actually needs.>

## USER INTENT AND CONSTRAINTS
<Goals, non-negotiables, environment, compatibility requirements, limits.>

## CURRENT DELTA
<For a follow-up, branch, or restarted conversation: what changed since the earlier review?>

## EVIDENCE
<Relevant facts, source excerpts, logs, measurements, screenshots, documents, or attachment names.>

## ATTEMPTS SO FAR
<What has already been tried and what happened?>

## CURRENT JUDGMENT
<Optional. Include when the user wants ChatGPT Web to critique, compare, attack, or improve an existing position. Omit when an independent view is more useful.>

## OPTIONS AND RISKS
<Optional. Meaningful alternatives, tradeoffs, known failure modes, and unknowns.>

## ASK
<The exact question for this consultation.>

## RESPONSE PREFERENCE
<Optional. Examples: concise recommendation, code review, architecture critique, decision memo, checklist, rewrite.>

Begin your response with exactly:
Request-ID: <request-id>
```

## Follow-up rule

Do not resend a full packet just because a template exists.

For a second or later turn in the same verified Web conversation, prefer a delta prompt such as:

```markdown
Request-ID: <new-request-id>

## CURRENT DELTA
<What changed or what new evidence appeared?>

## ASK
<What should be examined now?>

Begin your response with exactly:
Request-ID: <new-request-id>
```

Reuse prior context already present in that conversation. Restate older material only when it is ambiguous, outdated, or essential to the new question.

## Evidence rules

- A local path is not evidence by itself. Upload the file, paste the relevant content, or provide a faithful excerpt.
- Prefer the smallest source set that preserves the truth of the problem.
- Keep filenames and attachment names clear enough that the Web model can refer to them precisely.
- Preserve verbatim errors, measurements, and important constraints when wording matters.
- Remove unrelated personal information and never include blocked secrets, authentication material, or payment credentials.

The template must never force Codex into a fixed reviewer persona, fixed task taxonomy, fixed output format, or mandatory local-judgment step. The user's request remains authoritative.