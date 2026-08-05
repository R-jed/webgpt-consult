# Codex Chrome Workflow

Chrome is the browser adapter for WebGPT Consult. It handles navigation, observation, model selection, uploads, Send, waiting, extraction, and optional conversation branching.

Web conversation continuity is transient. The Skill does not maintain a local consultation registry or persistent reviewer memory.

## 1. Resolve consultation intent

Before opening ChatGPT, decide whether this request is:

- `independent`: a fresh second opinion;
- `follow_up`: a clear continuation of the current consultation.

Use a fresh ChatGPT conversation for a different project, a materially different question, an architecture reset, or any request that benefits from an unanchored independent review.

Reuse the current Web conversation only when the continuation is obvious and the conversation is still active and useful.

If continuity is ambiguous, start fresh.

## 2. Connect and authenticate

Read the installed Chrome control Skill before browser work. Initialize the extension binding and confirm ChatGPT is signed in and the composer is available.

Do not inspect cookies, local storage, passwords, browser profiles, or session databases.

## 3. Choose the Web conversation

For `independent`, create a fresh ChatGPT conversation.

For `follow_up`, reuse the currently active consultation conversation only when:

- it is clearly the intended review thread;
- it loads successfully;
- its context is still useful;
- it is not visibly confused or context-limited.

Do not search for or restore old conversations from local state files. If the current conversation is lost or cannot be identified confidently, start fresh.

## 4. Handle context pressure

If the current Web conversation becomes too long, visibly forgetful, or otherwise context-limited, prefer ChatGPT Web's `Branch in new chat` from an earlier still-relevant message.

Choose a branch point that preserves useful shared context without carrying an unnecessary long tail.

Important: the new branch inherits all conversation history before the selected message. Branching from a near-limit final message may preserve most of the context pressure.

After branching:

1. confirm the new branch is active;
2. re-open and verify the model picker;
3. send a fresh packet containing the current task and minimum necessary evidence;
4. continue the review in the branch.

If no suitable earlier branch point exists, `Branch in new chat` is unavailable, or the branch is unreliable, start a completely fresh ChatGPT conversation.

Branching is a continuity convenience. The current packet must still contain enough evidence for a truthful review.

## 5. Verify the model

Open the model picker from a fresh DOM snapshot and apply `scripts/model_router.py` semantics.

Selection policy:

```text
verified usable Pro -> verified usable High -> fail
```

A disabled, ambiguous, generic, legacy, or non-actionable Pro entry must not block a valid High fallback.

After a model click, capture fresh picker state and confirm the selected tier is checked under the GPT-5.6 Sol family. DOM refs are click locators only.

Re-verify model identity whenever a new conversation or branch is opened.

## 6. Prepare and preflight the exact payload

Build the packet from the user's current task and the minimum evidence required for a truthful review.

For an independent review, keep Codex's local judgment private by default. Send it only when the user specifically wants Sol to attack, compare, or revise that proposal.

For a clear follow-up in the same useful Web conversation, send a compact current delta and any new evidence.

For a branch or fresh conversation, rebuild the packet from the current task. Reintroduce prior facts only when they remain necessary for the current review.

Run `scripts/submission_preflight.py` over the exact packet and exact attachment list. Do not proceed unless it returns `ok=true`.

## 7. Fill the composer and upload files

Fill the complete packet. Verify the exact task ID and sentinel are present.

Use the Chrome plugin's real file chooser for attachments. Prefer semantic locators over localized text. Confirm every required attachment is visibly present and no upload is pending or failed.

## 8. Send exactly once

Immediately before Send, confirm:

- intended independent/follow-up mode;
- intended conversation or branch;
- verified GPT-5.6 Sol tier;
- task ID and sentinel;
- composer content;
- required attachment chips;
- preflight passed for this exact payload.

Click Send once.

While generation is active, stay in the same conversation. Do not refresh, retry, or send a duplicate continuation.

If ChatGPT rejects the request because the conversation is too long, do not retry the same payload there. Branch from an earlier useful point or start fresh, re-run preflight for the exact new payload, and send once.

## 9. Extract and verify

When generation stops, read only the latest assistant turn from a fresh snapshot. Save the extracted text locally only as part of the current task workflow when needed and run `scripts/result_verifier.py`.

The first two non-empty lines must exactly match the expected sentinel and task ID. A sentinel appearing later in prose or in quoted content does not count.

If verification fails, re-read the latest complete assistant turn once. If it still fails, mark the consultation incomplete.

## 10. Local adoption

Return to the local Codex task.

Compare the external review with local evidence and decide what to adopt, reject, or modify.

Do not create a persistent reviewer-memory file or consultation-state database after adoption.

## 11. Browser cleanup

Keeping the current consultation tab open is optional and useful only for an immediate follow-up.

Do not treat an open browser tab as durable project state. If it is later unavailable, start fresh from the current task and evidence.
