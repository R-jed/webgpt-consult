# Codex Chrome Workflow

This is the browser adapter for WebGPT Consult. Deterministic policy lives in the scripts; Chrome handles navigation, observation, clicks, uploads, Send, waiting, and extraction.

## 1. Resolve conversation continuity before opening ChatGPT

Read `chrome:control-chrome` completely. Determine the current project root, then list registered consultation threads with `scripts/conversation_registry.py`.

Choose one of two modes:

- `continue`: only when an existing thread clearly matches the same workstream or the user explicitly requests continuation;
- `fresh`: for a different project, different workstream, independent review, ambiguous continuity, stale thread, or deliberate context reset.

For `continue`, navigate to the exact stored ChatGPT conversation URL. For `fresh`, create a new ChatGPT conversation. Never reuse an arbitrary existing ChatGPT tab merely because one is open.

If a stored URL fails to load or is not the intended conversation, retire it and open a fresh conversation. Carry forward only a short verified local continuity summary.

## 2. Connect and confirm authentication

Initialize the Chrome plugin using its documented browser runtime. Use the extension binding. Confirm the account is signed in and the composer is available.

Do not inspect cookies, local storage, passwords, browser profiles, or session databases.

## 3. Verify the model with deterministic routing

Open the model picker from a fresh DOM snapshot. Capture the picker state needed by `scripts/model_router.py`.

Selection policy is:

```text
verified usable Pro -> verified usable High -> fail
```

A visible but disabled, ambiguous, legacy, generic, or non-actionable Pro entry must not block a valid High fallback.

After any model click, capture fresh state and confirm the exact selected tier is checked under the GPT-5.6 Sol family. A DOM ref is a click locator only.

Extra High, Medium, Instant, GPT-5.5 Pro, generic GPT-5 Pro without GPT-5.6 evidence, and unknown variants are unsupported.

## 4. Run submission preflight

Build the exact packet and exact attachment list before touching Send. Run `scripts/submission_preflight.py` on that set.

Do not proceed unless it returns `ok=true`. If a non-text attachment requires manual review, inspect it locally and only then use the explicit confirmation flag. Detected credentials cannot be overridden.

## 5. Fill the composer and upload files

Fill the complete packet. Verify a distinctive packet prefix, exact task ID, and sentinel in the composer.

For uploads, use the Chrome plugin's documented real file chooser. Prefer role/test-id locators over localized visible strings. If visible text is unavoidable, inspect the current UI and derive it from the fresh snapshot instead of hard-coding one language.

Verify every required attachment is visibly present and no upload shows an error or pending state.

## 6. Send exactly once

Immediately before Send, confirm:

- intended conversation mode and URL;
- selected GPT-5.6 Sol tier;
- task ID and sentinel;
- composer content;
- required attachment chips;
- preflight passed for this exact payload.

Click Send once.

While generation is active, remain in the same conversation. Observe targeted generation signals such as the stop control or visible generating state. Do not refresh, retry, or send `continue` while the turn is still active.

## 7. Extract and verify

When generation stops, read only the latest assistant turn from a fresh snapshot. Save that extracted assistant text locally and run `scripts/result_verifier.py`.

The first two non-empty lines must exactly match the expected sentinel and task ID. A sentinel appearing later in prose, in quoted user content, or in an earlier turn does not count.

If verification fails, re-read the complete latest assistant turn once. If it still fails, mark the consultation incomplete.

## 8. Persist continuity after success

Once verification passes, capture the current canonical ChatGPT conversation URL. Update the project registry with:

- stable workstream key;
- conversation URL;
- short workstream scope;
- latest task ID;
- one-sentence decision/result summary.

Do this for both fresh and continued consultations. The registry is local operational state and must never be uploaded to ChatGPT.

## 9. Browser cleanup

Keep a registered consultation tab only when it is useful for immediate continuation. Closing a tab does not lose continuity because the registry stores the canonical conversation URL. Do not keep unrelated tabs solely as state storage.
