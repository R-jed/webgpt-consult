# Continuity Capsule Template

Use this only when a consultation workstream must roll into a new ChatGPT branch or fresh conversation because the current thread has context pressure.

The capsule must be cumulative from the workstream's stable branch base through the latest successful consultation. It is a compact restorable state, not a transcript summary.

```markdown
CONTINUITY_CAPSULE_V1
Base-Task-ID: <stable branch-base task id>
Last-Task-ID: <latest successful task id before rollover>
Material-Reusable-Context-Omitted: no

## WORKSTREAM
<stable workstream key and one-sentence scope>

## BASELINE
<the original problem, success condition, and baseline state that still matter>

## USER_INTENT
<durable user goals and preferences relevant to this workstream>

## STANDING_CONSTRAINTS
<constraints that still govern the solution>

## ACCEPTED_DECISIONS
<decisions adopted so far, with short reasons when causally important>

## REJECTED_OR_DEFERRED_PATHS
<approaches rejected or deferred, and why, so the new branch does not repeat dead ends>

## OPEN_QUESTIONS
<unresolved questions, risks, assumptions, and disputed points>

## EVIDENCE_INDEX
<current artifact names, commits, PRs, versions, tests, measurements, or other evidence identifiers that matter>

## CURRENT_STATE
<what is true now after all work since the branch base>

## CURRENT_ASK
<the exact decision or review requested after rollover>

## COVERAGE_ATTESTATION
<briefly state what source material was checked to build this capsule and why the Agent believes all material reusable context is represented>
```

Keep the capsule under 12,000 characters unless there is a concrete reason to change the validator limit. Do not include credentials, the local conversation registry, browser state, cookies, or unrelated project history.
