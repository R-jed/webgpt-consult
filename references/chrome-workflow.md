# Codex Chrome Workflow

Chrome is the browser adapter for WebGPT Consult. It handles navigation, observation, model selection, uploads, Send, waiting, and extraction. Durable project state lives locally.

## 1. Resolve consultation intent

Before opening ChatGPT, decide whether this request is:

- `independent`: a fresh, unanchored second opinion;
- `follow_up`: a clear continuation of one existing consultation.

List local consultation state when useful:

```bash
python3 "$SKILL_DIR/scripts/consult_state.py" --project-root "<project-root>" list
```

Reuse a stored conversation only when there is one clear matching consultation. Explicit continuation or a unique anchor such as a PR, issue, branch, or named artifact is enough. Ambiguous match means fresh chat.

Independent reviews always use a fresh ChatGPT conversation.

## 2. Connect and authenticate

Read the installed Chrome control Skill before browser work. Initialize the extension binding and confirm ChatGPT is signed in and the composer is available.

Do not inspect cookies, local storage, passwords, browser profiles, or session databases.

## 3. Choose the Web conversation

For `follow_up`, try the stored `conversation_url` if one exists.

Reuse it only when:

- it loads successfully;
- it is clearly the intended consultation;
- the conversation is still useful and not context-limited.

If any of those checks fail, create a fresh ChatGPT conversation. Restore continuity from the durable local consultation snapshot plus the current delta and current evidence.

Do not depend on `Branch in new chat`, old message IDs, or browser lineage. Context pressure is resolved by replacing the Web conversation, not by maintaining a branching state machine.

## 4. Verify the model

Open the model picker from a fresh DOM snapshot and apply `scripts/model_router.py` semantics.

Selection policy:

```text
verified usable Pro -> verified usable High -> fail
```

A disabled, ambiguous, generic, legacy, or non-actionable Pro entry must not block a valid High fallback.

After a model click, capture fresh picker state and confirm the selected tier is checked under the GPT-5.6 Sol family. DOM refs are click locators only.

## 5. Prepare and preflight the exact payload

Build the packet from the user's current task and the minimum evidence required for a truthful review.

For an independent review, keep Codex's local judgment private by default. Send it only when the requested review is specifically meant to attack or compare that proposal.

For a follow-up in the same usable Web conversation, prefer a compact delta.

For a fresh replacement conversation, include the durable local consultation snapshot plus the current delta. The snapshot represents locally adopted state, not a transcript or raw Sol output.

Run `scripts/submission_preflight.py` over the exact packet and exact attachment list. Do not proceed unless it returns `ok=true`.

## 6. Fill the composer and upload files

Fill the complete packet. Verify the exact task ID and sentinel are present.

Use the Chrome plugin's real file chooser for attachments. Prefer semantic locators over localized text. Confirm every required attachment is visibly present and no upload is pending or failed.

## 7. Send exactly once

Immediately before Send, confirm:

- intended independent/follow-up mode;
- intended conversation;
- verified GPT-5.6 Sol tier;
- task ID and sentinel;
- composer content;
- required attachment chips;
- preflight passed for this exact payload.

Click Send once.

While generation is active, stay in the same conversation. Do not refresh, retry, or send a duplicate continuation.

If ChatGPT rejects the request because the conversation is too long, do not retry the same payload there. Open a fresh conversation and resend once using the durable local snapshot plus current delta after preflight.

## 8. Extract and verify

When generation stops, read only the latest assistant turn from a fresh snapshot. Save the extracted text locally and run `scripts/result_verifier.py`.

The first two non-empty lines must exactly match the expected sentinel and task ID. A sentinel appearing later in prose or in quoted content does not count.

If verification fails, re-read the latest complete assistant turn once. If it still fails, mark the consultation incomplete.

## 9. Local adoption and state update

Return to the local Codex task before updating durable state.

Compare the external review with local evidence and decide what to adopt, reject, or modify. Only then update the consultation snapshot so it reflects the locally adopted project state.

Saving state is best effort. A save failure does not invalidate a verified consultation. On the next use, a missing or corrupt state file should cause a fresh consultation rather than block the Skill.

## 10. Browser cleanup

Keeping a useful consultation tab open is optional. Closing it does not lose correctness because durable continuity lives in local state. Do not keep unrelated tabs solely as state storage.
