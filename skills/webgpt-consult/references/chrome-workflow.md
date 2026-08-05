# Chrome workflow

This file defines the deterministic browser protocol for `webgpt-consult`. Task reasoning and evidence selection belong to Codex. Substantial consultations use `context-packet-template.md`.

## 1. Connect and authenticate

Use the Codex Chrome capability to open ChatGPT Web. Confirm that ChatGPT is signed in and the composer is usable.

Do not inspect cookies, local storage, passwords, browser profiles, or session databases.

A Chrome runtime reset, reconnect, or browser-tool restart invalidates old locators, element references, pending promises, and transient browser objects. Reacquire browser state before the next UI action. Never carry an unresolved file-chooser or another browser promise across calls or resets.

For state-changing actions, work from fresh browser state. Resolve the intended control unambiguously, perform one action, then observe the resulting state again.

## 2. Browser ownership

Treat each browser resource as:

```text
owned   = this Skill created the exact resource during the current Codex conversation and still knows its handle
unowned = it existed beforehand, was user-supplied, merely discovered, or ownership is uncertain
```

Ownership follows the exact handle. Navigating a user tab to ChatGPT does not make it owned. A new conversation URL does not imply a new tab.

Never reconstruct ownership from URL, title, content, project name, or history.

## 3. Conversation continuity

A verified completed consultation may retain:

```text
review_tab_handle
review_tab_owned_by_skill
review_conversation_url
last_task_id
last_sentinel
verified_web_model
model_verified_conversation_url
```

Keep this state only in the current Codex conversation.

### Live fast path

Normal follow-ups should be cheap.

Reuse the bound conversation directly without re-reading the previous sentinel when all of these are true:

- the exact bound tab handle is still live;
- it is still on the retained canonical conversation URL when that URL is available;
- there was no navigation, branch, runtime-reset recovery, or other event that made conversation identity ambiguous;
- the previous submission already completed and its sentinel was verified;
- there is no unresolved `SENT` or `UNKNOWN` submission.

In this fast path, prior identity has already been established. Prepare the new delta and verify only the new submission/result identity.

### Recovery path

If the live fast path is unavailable:

1. reuse the exact bound handle if it can still be recovered, otherwise open the exact retained conversation URL;
2. inspect the recovered conversation from fresh browser state;
3. verify the immediately relevant prior assistant result against `last_sentinel`;
4. continue only when the identity is unambiguous.

If recovery cannot prove the conversation identity, start fresh only when no unresolved `SENT` or `UNKNOWN` submission remains attached to the old conversation.

Never recover a consultation by guessing from sidebar titles, recent-chat order, browser history, project names, timestamps, or semantic similarity.

If the user says the answer is already visible, inspect and verify the existing latest assistant turn before preparing another request.

If the same work should continue but the current Web thread is too context-heavy, use `Branch in new chat` from a useful earlier point when available. A branch is a new conversation identity and requires a new model verification.

## 4. Verify the Web model efficiently

Allowed policy:

```text
GPT-5.6 Sol Pro
  -> otherwise GPT-5.6 Sol High
  -> otherwise stop
```

Only literal `Pro` and `High` tiers associated with GPT-5.6 Sol are eligible. Reject GPT-5.5 Pro, `Pro Extended`, base-Sol `Extra High`, ambiguous bare `Pro`, Codex reasoning labels, and unrelated models.

### New or branched conversation

1. open the model picker from fresh browser state;
2. select GPT-5.6 Sol `Pro` when available, otherwise `High`;
3. re-observe the picker and verify the selected tier;
4. bind that tier to this conversation as `verified_web_model`.

Use the current UI semantically. Do not maintain a hard-coded DOM parser or element-reference table.

### Follow-up in the same conversation

Do not reopen the picker per message.

When conversation identity is still verified and `verified_web_model` belongs to that conversation, reuse the cached tier. The live fast path does not need any model-menu work.

A recovered conversation may also reuse the cached tier after identity is re-established with its exact URL/handle and prior sentinel, provided no fresh UI/error evidence contradicts it.

A Chrome runtime reset alone does not invalidate the model cache.

Re-open the picker only when:

- a fresh conversation or branch was created;
- conversation identity changed or cannot be proven;
- no valid cache exists;
- visible UI shows another model/tier;
- ChatGPT reports a model availability/switch error;
- the user explicitly asks to check or change the tier.

## 5. Prepare task identity, context, and evidence

Every Web submission gets a fresh identity:

```text
task_id:  webgpt-consult-YYYYMMDD-HHMMSS-<nonce>
sentinel: WEBGPT_CONSULT_RESULT_YYYYMMDD_HHMMSS_<same-nonce>
```

For a simple question, a direct prompt is enough, but it must contain the sentinel and require ChatGPT Web to start its reply with that exact sentinel.

For substantial first-turn work, use the full `CONTEXT_PACKET_V1`. For second and later turns in the same verified conversation, use its delta form unless earlier context is stale, ambiguous, or contradicted.

Choose the smallest evidence set that preserves the truth. A local path is never evidence by itself.

Evidence preference:

1. original selected human-readable files when upload is reliable;
2. faithful excerpts when only a small part matters;
3. `scripts/build_attachment_bundle.py` when many selected UTF-8 text files are awkward to upload individually or an archive is rejected.

Do not upload a whole repository merely because it is available.

Run `scripts/safety_guard.py` on the exact outgoing prompt/packet and every UTF-8 text attachment. Blocking findings must be removed or redacted. Privacy warnings are reviewed in context rather than automatically deleting task-relevant business/project facts.

The bundle helper performs its own final blocking scan and fails closed on incomplete evidence unless partial bundling was explicitly requested.

Inspect binary/non-text files locally before upload.

## 6. Upload files and verify the composer

Use the real file chooser.

When the browser API exposes a pending chooser promise, keep the entire lifecycle in one browser-tool invocation:

```text
create chooser wait
-> open add-file UI
-> resolve chooser
-> set selected files
```

Never split a pending chooser lifecycle across browser calls or resets.

After every upload UI change:

1. reacquire the composer from fresh browser state;
2. confirm every required attachment is visibly present and fully uploaded;
3. insert the intended prompt/packet once;
4. reacquire the composer again;
5. verify rendered composer text contains the current sentinel and enough distinctive text to identify the intended submission;
6. for `CONTEXT_PACKET_V1`, also verify the packet prefix and current `task_id`.

If an uploaded Markdown/text preview leaves the composer empty and the fresh UI exposes exactly one associated `Show in text field`, `在文本字段中显示`, or equivalent action, use that action once. Reacquire and verify the composer again.

Do not cycle through multiple fill/type/clipboard methods after a verified failure. An attachment chip or filename is not composer text.

Never Send an empty or unverified composer. Never claim a file was reviewed unless its real content was delivered.

## 7. Create the transient submission record

Before Send, retain this session-only record in the current Codex conversation:

```text
current_task_id
current_sentinel
current_context_strategy
current_attachment_names
current_dispatch_state: NOT_SENT
current_conversation_url
```

`current_attachment_names` must reflect the files actually visible in the composer, including a generated bundle when one is used.

This record exists only to recover the in-flight submission. Do not write it to disk or turn it into consultation history.

## 8. Send once

Immediately before Send, confirm:

- the intended conversation is active;
- model state is valid from fresh verification or the conversation-scoped cache;
- the current sentinel and, for a packet, `task_id` are in the verified composer text;
- all required attachment chips are present;
- the outgoing prompt and UTF-8 text attachments passed blocking safety checks;
- no blocked credential/payment material remains.

Do not reopen the model picker solely for this pre-send gate when the same verified conversation has a valid cached tier.

Track dispatch state:

```text
NOT_SENT = Send definitely has not been clicked
SENT     = fresh evidence shows the submission occurred
UNKNOWN  = reset/disconnect/timeout happened during or after Send before submission could be proven
```

Click Send once.

Set `SENT` only after fresh evidence such as the new user turn, an emptied composer, or active generation. Any ambiguous click outcome becomes `UNKNOWN`.

Recovery:

- `NOT_SENT`: reacquire state, rebuild the draft if needed, re-check the model only if its cache was invalidated, then Send once after verification.
- `SENT`: recover the same conversation and wait/extract. Never resend.
- `UNKNOWN`: recover the exact bound handle or `current_conversation_url`, then look for the task/sentinel, user turn, or generation/result evidence. Never create a replacement consultation or click Send again while uncertainty remains.

If an `UNKNOWN` submission cannot be recovered unambiguously, mark it incomplete rather than risking a duplicate.

## 9. Wait for completion

Stay in the same conversation while generation is active. Use fresh targeted observations rather than repeatedly rebuilding the full page state.

A visible stop-generating control, thinking/generating status, or an incomplete assistant turn while generation controls remain active means the response is not complete.

While generation is active, do not resend, refresh, start a replacement consultation, close the tab, or send `continue`.

Long Pro responses can take substantial time. Continue observing the same submission until completion or a real browser failure triggers dispatch-state recovery.

## 10. Verify result and refresh the binding

After generation stops, inspect only the latest assistant turn from fresh browser state. Do not count a sentinel echoed in the user's prompt as completion evidence.

The first non-empty assistant line must exactly equal the current sentinel and substantive content must follow.

If verification fails, read the complete latest assistant turn once more. If the sentinel still does not match or the result is truncated, mark the consultation incomplete.

Only after verification succeeds:

1. refresh the conversation binding with the current handle, ownership, canonical URL, `last_task_id`, `last_sentinel`, and verified/cached model;
2. mark the current submission complete;
3. clear the transient `current_*` record.

If the consultation is deliberately marked failed/incomplete and no unresolved Send outcome remains, clear the transient record then as well.

## 11. Cleanup

Binding replacement happens before cleanup:

```text
verified result
-> replacement binding established and confirmed
-> inspect superseded resource
```

If old and new bindings use the same handle, keep it open.

If handles differ, close the old one only when it is proven Skill-owned.

A failed temporary candidate may be closed only when:

- it is proven Skill-owned;
- it did not become the active binding;
- its exact handle is still known;
- no submission is generating there;
- its dispatch state is not `UNKNOWN`.

Never use `pkill`, `killall`, generic Chrome termination, process scanning, a cleanup daemon, or a persistent tab registry.

If ownership, generation, or dispatch state is uncertain, leave the resource open.
