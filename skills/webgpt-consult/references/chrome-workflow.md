# Chrome workflow

This reference contains browser-state rules that should remain deterministic. Prompt design, evidence selection, and consultation style belong to Codex and the user's request.

## 1. Connect and authenticate

Use the Codex Chrome capability to open ChatGPT Web. Confirm that ChatGPT is signed in and the composer is usable.

Do not inspect cookies, local storage, passwords, browser profiles, or session databases.

Treat a Chrome runtime reset, reconnect, or browser-tool restart as loss of all old locators, element references, pending promises, and transient browser objects. Reacquire browser state before the next interaction. Never reuse an unresolved file-chooser or other browser promise after a reset.

For state-changing UI actions, work from fresh browser state. Prefer a stable semantic locator, confirm it resolves unambiguously when that is not self-evident, perform one action, then observe the resulting state again.

## 2. Track browser ownership

Treat every browser resource as either `owned` or `unowned`.

```text
owned   = this Skill created it during the current Codex conversation and still knows the exact handle
unowned = it existed beforehand, was supplied by the user, was merely discovered, or ownership is uncertain
```

Ownership follows the exact browser handle. Navigating an existing user tab to ChatGPT does not make it owned. A new conversation URL does not imply a new tab.

Never infer ownership later from URL, title, content, project name, or history.

## 3. Resolve conversation continuity

After a successful consultation, the current Codex conversation may retain:

```text
review_tab_handle
review_tab_owned_by_skill
review_conversation_url
last_request_id
verified_web_model
model_verified_conversation_url
```

Do not persist these values outside the current Codex conversation.

When the user's next request clearly continues the same Web consultation:

1. reuse the bound tab handle if still valid;
2. otherwise open the exact retained conversation URL when available;
3. inspect the loaded conversation from fresh browser state;
4. verify the immediately relevant prior assistant response against `last_request_id`;
5. continue only if the identity is unambiguous.

If any step fails, start a fresh ChatGPT conversation only when no unresolved `SENT` or `UNKNOWN` request remains attached to the previous one. Never search for an old consultation by guessing from sidebar titles, recent-chat order, browser history, project names, timestamps, or semantic similarity.

If the user says the expected answer is already visible, inspect and verify the existing conversation before preparing another request.

If the same consultation should continue but the bound Web conversation is too context-heavy, use `Branch in new chat` from an earlier useful point when that preserves helpful context. If branching is unavailable or unhelpful, start fresh.

Branching creates a new conversation identity and therefore invalidates the previous conversation's model cache.

## 4. Verify the Web model efficiently

Use this policy only:

```text
GPT-5.6 Sol Pro
  -> otherwise GPT-5.6 Sol High
  -> otherwise stop
```

Only literal `Pro` and `High` entries associated with GPT-5.6 Sol are eligible. Reject legacy GPT-5.5 Pro entries, `Pro Extended`, base-Sol `Extra High`, ambiguous bare `Pro` text, Codex reasoning labels, and unrelated model names.

### First turn in a conversation

For a fresh ChatGPT conversation or a newly branched conversation:

1. open the model picker from fresh browser state;
2. select GPT-5.6 Sol `Pro` when available, otherwise `High`;
3. re-observe the picker and verify the selected tier;
4. remember that verified tier as `verified_web_model` for this conversation.

Do not maintain a DOM parser or hard-coded element-reference table. Use the current browser UI semantically.

### Follow-up turns in the same conversation

Do not reopen the model picker on every consult.

When the continuation has been verified as the same bound conversation and `verified_web_model` is already associated with that conversation, reuse the cached tier. A normal second, third, or later message in the same conversation should not pay the browser/token cost of repeated picker inspection.

The cached model remains valid when:

- the exact bound handle is reused; or
- the exact canonical conversation URL is reopened;
- the prior response identity is verified with `last_request_id`;
- no fresh UI or error state contradicts the cached tier.

A browser runtime reset alone does not invalidate this cache. Reacquire browser objects, recover the same conversation, verify its identity, and continue using the cached tier.

### Re-verification triggers

Open the picker again only when one of these occurs:

- a fresh conversation is created;
- `Branch in new chat` creates a new conversation;
- the canonical conversation identity changes;
- the binding cannot prove this is the same conversation;
- no verified model cache exists;
- fresh visible UI indicates a different model/tier;
- ChatGPT reports a model availability or model-switch error;
- the user explicitly requests a tier check or change.

A cheap visible contradiction is enough to invalidate the cache; absence of repeated picker evidence is not.

## 5. Prepare the consultation

Generate a fresh random request ID for every consultation, including follow-ups in the same Web conversation. Example:

```text
wgpt-a83f9271c4e24d11
```

Codex may write a simple prompt directly or use `context-packet-template.md` when a structured handoff materially improves the answer.

Use the packet guide for complex tasks with several constraints, artifacts, prior attempts, options, risks, or important background. Keep only useful sections.

For a second or later turn in the same verified conversation, prefer a delta prompt with the new evidence and current ask. Do not resend the full background simply because a packet template exists.

Prefer minimal disclosure:

- send only context relevant to the current question;
- for code work, use relevant excerpts or selected files before broader directories;
- avoid uploading an entire repository merely because it is available;
- remove unrelated personal/private information;
- never send secrets, authentication material, or payment credentials.

Run `scripts/safety_guard.py` on the exact outgoing prompt text and every UTF-8 text attachment. A blocking finding must be removed or redacted before Send. Review non-blocking privacy warnings when relevant.

For binary/non-text files, inspect them locally before upload. The Skill does not attempt to build a general binary DLP system.

If many small text files are genuinely needed and individual uploads become unreliable, Codex may create a temporary Markdown bundle from the selected files using ordinary local tooling.

## 6. Fill the composer and upload files

Include this line in the prompt:

```text
Request-ID: <request-id>
```

Also instruct ChatGPT Web to begin its response with that exact line.

Use the real file chooser for attachments. Keep the entire chooser lifecycle together: establish the chooser wait, open the add-file UI, resolve the chooser, and set the selected files within the same browser-tool invocation whenever the browser API uses a pending chooser promise. Do not carry a pending chooser across calls or resets.

After every upload UI change, reacquire the composer from fresh browser state. Confirm every required attachment is visibly present and fully uploaded.

Then insert the intended prompt once. Reacquire the composer again and verify its rendered text contains the current `Request-ID` and enough distinctive prompt text to prove the intended request is present.

If an uploaded text/Markdown preview leaves the composer empty and the current UI exposes exactly one associated `Show in text field`, `在文本字段中显示`, or equivalent action, use that recovery action once, then reacquire and verify the composer again. Do not cycle through multiple text-entry methods.

Never click Send with an empty or unverified composer. Never claim a source or file was reviewed unless it was actually included or uploaded.

## 7. Send once and track dispatch state

Track the current request with one transient state:

```text
NOT_SENT = Send definitely has not been clicked
SENT     = fresh browser evidence shows the request was submitted
UNKNOWN  = reset, disconnect, or timeout occurred during/after the Send action before submission could be confirmed
```

Immediately before Send, confirm:

- the intended Web conversation is active;
- model state is valid, either from fresh verification for a new conversation or from the verified model cache for the same conversation;
- the fresh request ID is present in the verified composer text;
- the prompt matches the user's current intent;
- all required attachments are visibly uploaded;
- the exact outgoing prompt and all UTF-8 text attachments passed the blocking safety checks;
- no blocked secret/payment material remains.

Do not open the model picker solely for this pre-send check when the same verified conversation has a valid cached tier.

Send once.

Set `SENT` only after fresh browser evidence shows submission, such as the new user turn, an emptied composer, or active generation. If browser state becomes ambiguous during or after the click, set `UNKNOWN`.

Recovery rules:

- `NOT_SENT`: reconnect, recover the conversation, rebuild the draft if necessary, and send only after the draft is verified again. Re-check the picker only if a model-cache invalidation trigger occurred.
- `SENT`: recover the same conversation and wait/extract. Never send the request again.
- `UNKNOWN`: recover the same tab or exact conversation URL and look for submission/generation evidence. Never create a replacement consultation or click Send again while the outcome remains uncertain.

If an `UNKNOWN` request cannot be recovered unambiguously, mark the consultation incomplete rather than risking a duplicate.

## 8. Wait for completion

Stay in the same conversation while generation is active. Use fresh, targeted browser observations rather than repeatedly rebuilding the full page state.

A visible stop-generating control, thinking/generating status, or an incomplete assistant turn while generation controls remain visible means the response is still active.

While generation is active, do not resend, refresh, start a replacement consultation, close the tab, or send a `continue` message.

Long-running Pro responses may take substantial time. Continue observing the same request until generation completes or a real browser failure requires recovery under the dispatch rules above.

## 9. Verify the result and bind the conversation

When generation stops, inspect only the latest assistant turn from fresh browser state. Do not treat the user's echoed request ID as success.

The first non-empty line must exactly equal:

```text
Request-ID: <request-id>
```

There must also be substantive content after that line.

If the ID does not match, re-read the complete latest assistant turn once. If it still does not match or appears truncated, treat the consultation as incomplete.

Only after verification passes may the current Codex conversation establish or refresh the temporary binding with the current handle, ownership value, canonical conversation URL when available, `last_request_id`, and the current verified/cached Web model tier.

The model cache belongs to the verified conversation identity, not to the browser runtime or an individual request.

## 10. Cleanup

Binding replacement must happen before cleanup:

```text
verified result
  -> new binding established and confirmed
  -> inspect superseded browser resource
```

If the old and new bindings use the same handle, keep the tab open.

If the handles differ, close the old tab only when it is proven Skill-owned. Leave user-owned or ownership-unknown tabs alone.

A failed temporary candidate may be closed only when:

- it is proven Skill-owned;
- it did not become the current binding;
- its exact handle is still known;
- no request is still generating there;
- its dispatch state is not `UNKNOWN`.

Never use `pkill`, `killall`, generic Chrome termination, process scanning, a background cleanup daemon, or a persistent tab registry.

If state is uncertain, leave the tab alone.
