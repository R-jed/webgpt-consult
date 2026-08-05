# Codex Chrome Workflow

Chrome is the browser adapter for WebGPT Consult. It handles navigation, observation, model selection, uploads, Send, waiting, extraction, optional conversation continuation, and optional conversation branching.

Web conversation continuity is temporary. The Skill does not maintain a local review registry or persistent reviewer memory.

## 1. Choose the review mode

Before opening or continuing ChatGPT Web, choose exactly one mode:

- `independent`: fresh conversation for a new or deliberately unanchored second opinion;
- `continuation`: continue the current useful review conversation;
- `branch`: continue the same review from an earlier useful message because the current conversation has context pressure.

Use `independent` for a different project, a materially different question, an architecture reset, or any request that benefits from a fresh reviewer view.

Use `continuation` only when the relationship to the active Web review is obvious and the current Codex session still has a verifiable binding to that review.

Use `branch` only when the same review should continue but the currently bound conversation has accumulated too much history.

If the correct path is unclear, use `independent`.

## 2. Connect and authenticate

Read the installed Chrome control Skill before browser work. Initialize the extension binding and confirm ChatGPT is signed in and the composer is available.

Do not inspect cookies, local storage, passwords, browser profiles, or session databases.

## 3. Session-scoped conversation binding

The browser side needs a deterministic locator for `continuation` without creating durable project memory.

After a review has completed and exact result verification has passed, retain the smallest available binding in the current Codex conversation only:

```text
review_tab_handle: <Chrome plugin tab/page handle when exposed>
review_conversation_url: <exact canonical chatgpt.com conversation URL when exposed>
last_task_id: <verified Task-ID>
last_sentinel: <verified sentinel>
```

Do not write this binding to disk. Do not place it in the repository. Do not maintain it across separate Codex conversations.

The tab handle and URL are only locators. The prior Task-ID and sentinel prove that the loaded Web conversation is the intended review thread.

### Establishing a binding

After a successful `independent` review:

1. wait until result verification passes;
2. observe the current browser tab/page handle if the Chrome capability exposes one;
3. observe the exact canonical ChatGPT conversation URL if available;
4. retain those locators together with the verified Task-ID and sentinel in the current Codex working context.

Do not establish a binding from an incomplete or unverified Web result.

### Resolving a binding for `continuation`

Resolve in this order:

1. try the previously bound Chrome tab/page handle;
2. if the handle is stale or unavailable, open the exact canonical ChatGPT conversation URL retained by the current Codex session;
3. inspect the conversation from a fresh DOM view;
4. confirm that the immediately relevant prior assistant result contains the expected previous Task-ID and sentinel;
5. only then treat the conversation as the valid continuation target.

If any identity check fails, switch to `independent`.

Never locate a prior review by guessing from sidebar titles, recent-chat order, project names, browser history, approximate timestamps, or semantic similarity.

If multiple candidate conversations exist, treat the binding as ambiguous and switch to `independent`.

## 4. Open the correct Web conversation

### `independent`

Create a fresh ChatGPT conversation.

A successful verified result from this conversation replaces any previous session-scoped binding.

### `continuation`

Resolve the session binding using Section 3.

Reuse the resolved review conversation only when:

- the prior Task-ID and sentinel match;
- it loads successfully;
- its context remains useful;
- it is not visibly confused or context-limited.

If any condition fails, switch to `independent`.

### `branch`

Start from the currently verified bound conversation.

Choose an earlier still-relevant message in that review and use `Branch in new chat`.

A branch inherits all conversation history before the selected message. Branching from a near-limit final message may preserve most of the context pressure, so choose the earliest point that still preserves genuinely useful shared context.

After branching:

1. confirm the new branch is active;
2. re-open and verify the model picker;
3. prepare a current packet rather than relying on inherited history alone;
4. send and verify the new review result;
5. replace the previous session binding with the new branch handle/URL and new verified Task-ID/sentinel.

If no suitable branch point exists, branching is unavailable, or the new branch is unreliable, switch to `independent`.

If the previous Web review is lost and cannot be identified confidently, start fresh. Do not build a local recovery mechanism for old Web conversations.

## 5. Verify the model

Open the model picker from a fresh DOM view and apply `scripts/model_router.py` semantics.

Selection policy:

```text
verified usable Pro -> verified usable High -> fail
```

A disabled, ambiguous, generic, legacy, or non-actionable Pro entry must not block a valid High fallback.

After a model click, capture fresh picker context and confirm the selected tier is checked under the GPT-5.6 Sol family. DOM refs are click locators only.

Re-verify model identity whenever a fresh conversation or branch is opened.

## 6. Prepare and preflight the exact payload

Build the packet from the user's current task and the minimum evidence required for a truthful review.

For `independent`, keep Codex's local judgment private by default. Send it only when the user specifically wants Sol to attack, compare, or revise that proposal.

For `continuation`, send a compact current delta and any new evidence. Do not resend historical material that the current conversation already contains unless it remains necessary.

For `branch`, send the current task and minimum necessary evidence again. Treat inherited branch history as useful context, not as proof that the reviewer has every current fact.

Run `scripts/submission_preflight.py` over the exact packet and exact attachment list. Do not proceed unless it returns `ok=true`.

## 7. Fill the composer and upload files

Fill the complete packet. Verify the exact task ID and sentinel are present.

Use the Chrome plugin's real file chooser for attachments. Prefer semantic locators over localized text. Confirm every required attachment is visibly present and no upload is pending or failed.

## 8. Send exactly once

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

## 9. Extract and verify

When generation stops, read only the latest assistant turn from a fresh DOM view. Save the extracted text locally only as part of the current task workflow when needed and run `scripts/result_verifier.py`.

The first two non-empty lines must exactly match the expected sentinel and task ID. A sentinel appearing later in prose or in quoted content does not count.

If verification fails, re-read the latest complete assistant turn once. If it still fails, mark the review incomplete.

Only a verified result may establish or refresh the session-scoped conversation binding.

## 10. Local adoption

Return to the local Codex task.

Compare the external review with local evidence and decide what to adopt, reject, modify, or leave unresolved.

Do not create persistent reviewer memory after adoption.

## 11. Browser cleanup

Keeping the currently bound review tab open is useful for an immediate `continuation` or possible `branch`, but it is not required for correctness because the current Codex session may also retain the exact conversation URL temporarily.

Do not treat the tab or URL as durable project state. If the current Codex session later loses the binding or cannot verify it, use `independent` and rebuild the current review from the current task and evidence.
