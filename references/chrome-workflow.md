# Codex Chrome Workflow

Chrome is the browser adapter for WebGPT Consult. It handles navigation, observation, model selection, uploads, Send, waiting, extraction, and optional conversation branching.

Web conversation continuity is temporary. The Skill does not maintain a local review registry or persistent reviewer memory.

## 1. Choose the review mode

Before opening or continuing ChatGPT Web, choose exactly one mode:

- `independent`: fresh conversation for a new or deliberately unanchored second opinion;
- `continuation`: continue the current useful review conversation;
- `branch`: continue the same review from an earlier useful message because the current conversation has context pressure.

Use `independent` for a different project, a materially different question, an architecture reset, or any request that benefits from a fresh reviewer view.

Use `continuation` only when the relationship to the active Web review is obvious.

Use `branch` only when the same review should continue but the current conversation has accumulated too much history.

If the correct path is unclear, use `independent`.

## 2. Connect and authenticate

Read the installed Chrome control Skill before browser work. Initialize the extension binding and confirm ChatGPT is signed in and the composer is available.

Do not inspect cookies, local storage, passwords, browser profiles, or session databases.

## 3. Open the correct Web conversation

### `independent`

Create a fresh ChatGPT conversation.

### `continuation`

Reuse the currently active review conversation only when:

- it is clearly the intended review thread;
- it loads successfully;
- its context remains useful;
- it is not visibly confused or context-limited.

If any condition fails, switch to `independent`.

### `branch`

Choose an earlier still-relevant message in the current review and use `Branch in new chat`.

A branch inherits all conversation history before the selected message. Branching from a near-limit final message may preserve most of the context pressure, so choose the earliest point that still preserves genuinely useful shared context.

After branching:

1. confirm the new branch is active;
2. re-open and verify the model picker;
3. prepare a current packet rather than relying on inherited history alone;
4. continue the review in the branch.

If no suitable branch point exists, branching is unavailable, or the new branch is unreliable, switch to `independent`.

If the previous Web review is lost and cannot be identified confidently, start fresh. Do not build a local recovery mechanism for old Web conversations.

## 4. Verify the model

Open the model picker from a fresh DOM view and apply `scripts/model_router.py` semantics.

Selection policy:

```text
verified usable Pro -> verified usable High -> fail
```

A disabled, ambiguous, generic, legacy, or non-actionable Pro entry must not block a valid High fallback.

After a model click, capture fresh picker context and confirm the selected tier is checked under the GPT-5.6 Sol family. DOM refs are click locators only.

Re-verify model identity whenever a fresh conversation or branch is opened.

## 5. Prepare and preflight the exact payload

Build the packet from the user's current task and the minimum evidence required for a truthful review.

For `independent`, keep Codex's local judgment private by default. Send it only when the user specifically wants Sol to attack, compare, or revise that proposal.

For `continuation`, send a compact current delta and any new evidence. Do not resend historical material that the current conversation already contains unless it remains necessary.

For `branch`, send the current task and minimum necessary evidence again. Treat inherited branch history as useful context, not as proof that the reviewer has every current fact.

Run `scripts/submission_preflight.py` over the exact packet and exact attachment list. Do not proceed unless it returns `ok=true`.

## 6. Fill the composer and upload files

Fill the complete packet. Verify the exact task ID and sentinel are present.

Use the Chrome plugin's real file chooser for attachments. Prefer semantic locators over localized text. Confirm every required attachment is visibly present and no upload is pending or failed.

## 7. Send exactly once

Immediately before Send, confirm:

- intended review mode;
- intended conversation or branch;
- verified GPT-5.6 Sol tier;
- task ID and sentinel;
- composer content;
- required attachment chips;
- preflight passed for this exact payload.

Click Send once.

While generation is active, stay in the same conversation. Do not refresh, retry, or send a duplicate request.

If ChatGPT rejects the request because the conversation is too long, do not retry the same payload there. Use `branch` from an earlier useful point or switch to `independent`, re-run preflight for the exact new payload, and send once.

## 8. Extract and verify

When generation stops, read only the latest assistant turn from a fresh DOM view. Save the extracted text locally only as part of the current task workflow when needed and run `scripts/result_verifier.py`.

The first two non-empty lines must exactly match the expected sentinel and task ID. A sentinel appearing later in prose or in quoted content does not count.

If verification fails, re-read the latest complete assistant turn once. If it still fails, mark the review incomplete.

## 9. Local adoption

Return to the local Codex task.

Compare the external review with local evidence and decide what to adopt, reject, modify, or leave unresolved.

Do not create persistent reviewer memory after adoption.

## 10. Browser cleanup

Keeping the current review tab open is optional and useful only for an immediate `continuation` or possible `branch`.

Do not treat an open browser tab as project memory. If it is later unavailable, use `independent` and rebuild the current review from the current task and evidence.
