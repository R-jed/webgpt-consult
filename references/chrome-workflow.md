# Codex Chrome Workflow

This is the browser adapter for WebGPT Consult. Deterministic policy lives in the scripts; Chrome handles navigation, observation, clicks, uploads, Send, waiting, extraction, and conversation branching.

## 1. Resolve conversation continuity before opening ChatGPT

Read `chrome:control-chrome` completely. Determine the current project root, then list registered consultation threads with `scripts/conversation_registry.py`.

Choose one of four modes:

- `continue`: only when an existing thread clearly matches the same workstream or the user explicitly requests continuation;
- `fresh`: for a different project, different workstream, independent review, ambiguous continuity, or deliberate context reset;
- `rollover_branch`: same workstream, but the registered conversation has context-pressure evidence and can branch from the active stable branch base;
- `rollover_fresh`: same workstream, continuity should be preserved, but a reliable Web branch cannot be created or the stored parent cannot be loaded.

For `continue`, navigate to the exact stored ChatGPT conversation URL. For `fresh`, create a new ChatGPT conversation. Never reuse an arbitrary existing ChatGPT tab merely because one is open.

If a stored URL fails to load but verified local workstream continuity can restore the thread, use `rollover_fresh`. If continuity cannot be restored reliably, retire the old workstream and use a new workstream key.

## 2. Connect and confirm authentication

Initialize the Chrome plugin using its documented browser runtime. Use the extension binding. Confirm the account is signed in and the composer is available.

Do not inspect cookies, local storage, passwords, browser profiles, or session databases.

## 3. Detect context pressure without inventing a token counter

ChatGPT Web does not provide a trustworthy exact remaining-context counter for this Skill. Do not infer an exact token balance from message count, scroll height, or elapsed time.

Treat rollover as required when fresh UI evidence shows a context/conversation-length rejection, when the user explicitly requests a continuity-preserving rollover, or when the thread demonstrably stops retaining material prior decisions and continuing in place would make the consultation unreliable.

If a Send attempt is rejected for context length, do not send the same payload again in the same conversation. Build the rollover payload locally and make one rollover attempt.

## 4. Execute a bounded rollover when required

Get the registered plan:

```bash
python3 "$SKILL_DIR/scripts/conversation_registry.py" --project-root "<project-root>" plan-rollover \
  --thread-key "<workstream-key>"
```

The plan returns the current parent conversation URL, immutable `root_task_id`, active `branch_base_task_id`, last successful task ID, and next rollover index.

Before touching the Branch action, build `CONTINUITY_CAPSULE_V1` locally from project evidence plus the verified consultation turns from the active branch base through the latest successful task. Do not ask the overfull Web ChatGPT thread to summarize itself as the source of truth. Validate the capsule with `scripts/continuity_capsule.py`.

### Preferred path: rollover_branch

1. Open the registered current conversation.
2. Locate the assistant turn whose exact second non-empty line is `Task-ID: <branch-base-task-id>`.
3. Open that assistant turn's More actions menu from a fresh DOM snapshot.
4. Choose the current UI action corresponding to `Branch in new chat`. Do not hard-code localized text when a semantic locator or fresh observed text is available.
5. Verify a new ChatGPT conversation opens and its canonical URL differs from the parent URL.
6. Confirm the branch contains the expected baseline turn before composing the new request.
7. Send the rollover packet containing the validated cumulative continuity capsule plus the current delta and evidence.

Branch from the active stable base, not from the latest message. Branching from the latest message retains the long tail and does not reduce context pressure.

### Fallback path: rollover_fresh

If the Branch action is unavailable, the branch-base turn cannot be uniquely verified, the new URL is not created, the inherited baseline is wrong, or the stored parent cannot be loaded, stop the branch attempt. Create a completely fresh ChatGPT conversation and send the same validated continuity capsule as a standalone restorable baseline.

Re-upload any current artifact whose contents matter and are not faithfully represented in the capsule. Do not keep sending into the overfull or unavailable parent conversation.

After a successful `rollover_fresh`, the new assistant result becomes the active `branch_base_task_id`, because the old base is not present in the completely fresh conversation. The original `root_task_id` remains unchanged for lineage auditability.

## 5. Verify the model with deterministic routing

Open the model picker from a fresh DOM snapshot. Capture the picker state needed by `scripts/model_router.py`.

Selection policy is:

```text
verified usable Pro -> verified usable High -> fail
```

A visible but disabled, ambiguous, legacy, generic, or non-actionable Pro entry must not block a valid High fallback.

After any model click, capture fresh state and confirm the exact selected tier is checked under the GPT-5.6 Sol family. A DOM ref is a click locator only.

Extra High, Medium, Instant, GPT-5.5 Pro, generic GPT-5 Pro without GPT-5.6 evidence, and unknown variants are unsupported.

## 6. Run submission preflight

Build the exact packet and exact attachment list before touching Send. Run `scripts/submission_preflight.py` on that set.

For a rollover, the validated continuity capsule must be embedded in the exact packet that is preflighted. Record its SHA-256 in local metadata and in the registry update after success.

Do not proceed unless preflight returns `ok=true`. If a non-text attachment requires manual review, inspect it locally and only then use the explicit confirmation flag. Detected credentials cannot be overridden.

## 7. Fill the composer and upload files

Fill the complete packet. Verify a distinctive packet prefix, exact task ID, and sentinel in the composer.

For uploads, use the Chrome plugin's documented real file chooser. Prefer role/test-id locators over localized visible strings. If visible text is unavoidable, inspect the current UI and derive it from the fresh snapshot instead of hard-coding one language.

Verify every required attachment is visibly present and no upload shows an error or pending state.

## 8. Send exactly once

Immediately before Send, confirm:

- intended conversation mode and URL;
- selected GPT-5.6 Sol tier;
- task ID and sentinel;
- composer content;
- required attachment chips;
- preflight passed for this exact payload;
- for rollover, capsule hash and parent/new URL relationship.

Click Send once.

While generation is active, remain in the same conversation. Observe targeted generation signals such as the stop control or visible generating state. Do not refresh, retry, or send `continue` while the turn is still active.

## 9. Extract and verify

When generation stops, read only the latest assistant turn from a fresh snapshot. Save that extracted assistant text locally and run `scripts/result_verifier.py`.

The first two non-empty lines must exactly match the expected sentinel and task ID. A sentinel appearing later in prose, in quoted user content, or in an earlier turn does not count.

If verification fails, re-read the complete latest assistant turn once. If it still fails, mark the consultation incomplete.

## 10. Persist continuity after success

Once verification passes, capture the current canonical ChatGPT conversation URL.

For an ordinary fresh or continued consultation, update the project registry with the stable workstream key, URL, scope, latest task ID, and one-sentence result summary.

For a branch rollover, record the new URL with:

```text
--rollover --rollover-mode branch
```

plus the exact previous parent URL and validated capsule SHA-256. The active branch base remains unchanged.

For a fresh fallback rollover, use:

```text
--rollover --rollover-mode fresh
```

The registry preserves the immutable root task but resets the active branch base to the new successful task. This keeps future branch operations anchored to a message that actually exists in the current conversation.

Every rollover increments rollover count and preserves recent parent conversation URLs for auditability. The registry is local operational state and must never be uploaded to ChatGPT.

## 11. Browser cleanup

Keep a registered consultation tab only when it is useful for immediate continuation. Closing a tab does not lose continuity because the registry stores the canonical conversation URL. Do not keep unrelated tabs solely as state storage.
