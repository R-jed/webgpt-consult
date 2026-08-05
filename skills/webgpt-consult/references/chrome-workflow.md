# Chrome workflow

This reference contains the browser-state rules that should remain deterministic. Prompt design, evidence selection, and consultation style belong to Codex and the user's request.

## 1. Connect and authenticate

Use the Codex Chrome capability to open ChatGPT Web. Confirm that ChatGPT is signed in and the composer is usable.

Do not inspect cookies, local storage, passwords, browser profiles, or session databases.

Treat a Chrome runtime reset, reconnect, or browser-tool restart as loss of all old locators, element references, pending promises, and transient browser bindings. Reacquire browser state before the next interaction. Never reuse an unresolved file-chooser or other browser promise after a reset.

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
```

Do not persist these values outside the current Codex conversation.

When the user's next request clearly continues the same Web consultation:

1. reuse the bound tab handle if still valid;
2. otherwise open the exact retained conversation URL when available;
3. inspect the loaded conversation from fresh browser state;
4. verify the immediately relevant prior assistant response against `last_request_id`;
5. continue only if the identity is unambiguous.

If any step fails, start a fresh ChatGPT conversation. Never search for an old consultation by guessing from sidebar titles, recent-chat order, browser history, project names, timestamps, or semantic similarity.

If the user says the expected answer is already visible, inspect and verify the existing conversation before preparing another request.

If the same consultation should continue but the bound Web conversation is too context-heavy, use `Branch in new chat` from an earlier useful point when that preserves helpful context. If branching is unavailable or unhelpful, start fresh.

Branching is a browser recovery/continuity technique, not a required user-visible consultation mode.

## 4. Select the Web model

Open the ChatGPT Web model picker from fresh browser state.

Use this policy only:

```text
verified GPT-5.6 Sol Pro
  -> otherwise verified GPT-5.6 Sol High
  -> otherwise stop
```

Only literal `Pro` and `High` entries associated with GPT-5.6 Sol are eligible. Reject legacy GPT-5.5 Pro entries, `Pro Extended`, base-Sol `Extra High`, ambiguous bare `Pro` text, Codex reasoning labels, and unrelated model names.

Do not maintain a DOM parser or hard-coded element-reference table in this Skill. Use the current browser UI semantically, then re-observe the picker after selection and verify that the intended GPT-5.6 Sol tier is selected and usable.

Re-verify after a fresh conversation, branch, or browser runtime reset.

## 5. Prepare the consultation

Generate a fresh random request ID for every consultation, including follow-ups in the same Web conversation. Example:

```text
wgpt-a83f9271c4e24d11
```

Codex should construct the prompt directly from the user's current request. There is no fixed packet schema.

The prompt may contain whatever task-relevant structure Codex finds useful. It may also ask ChatGPT Web to inspect uploaded code, documents, logs, images, or other files when that helps.

Prefer minimal disclosure:

- send only context relevant to the current question;
- for code work, use relevant excerpts or selected files before broader directories;
- avoid uploading an entire repository merely because it is available;
- remove unrelated personal/private information;
- never send secrets, authentication material, or payment credentials.

Run `scripts/safety_guard.py` on the exact outgoing prompt text and every UTF-8 text attachment. A blocking finding must be removed or redacted before Send. Review non-blocking privacy warnings when they are relevant to the task.

For binary/non-text files, inspect them locally before upload. The Skill does not attempt to build a general binary DLP system.

If many small text files are genuinely needed and individual uploads become unreliable, Codex may create a temporary Markdown bundle from the selected files using ordinary local tooling. This is a convenience fallback, not a required evidence format or persistent bundling subsystem.

## 6. Fill the composer and upload files

Include this line in the prompt:

```text
Request-ID: <request-id>
```

Also instruct ChatGPT Web to begin its response with that exact line. The rest of the prompt is unconstrained by the Skill.

Use the real file chooser for attachments. Keep the entire chooser lifecycle together: establish the chooser wait, open the add-file UI, resolve the chooser, and set the selected files within the same browser-tool invocation whenever the browser API uses a pending chooser promise. Do not carry a pending chooser across calls or resets.

After every upload UI change, reacquire the composer from fresh browser state. Confirm every required attachment is visibly present and fully uploaded.

Then insert the intended prompt once. Reacquire the composer again and verify its rendered text contains the current `Request-ID` and enough distinctive prompt text to prove the intended request is actually present.

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
- the selected model is verified GPT-5.6 Sol Pro or High;
- the fresh request ID is present in the verified composer text;
- the prompt matches the user's current intent;
- all required attachments are visibly uploaded;
- the exact outgoing prompt and all UTF-8 text attachments passed the blocking safety checks;
- no blocked secret/payment material remains.

Send once.

Set `SENT` only after fresh browser evidence shows submission, such as the new user turn, an emptied composer, or active generation. If the browser state becomes ambiguous during or after the click, set `UNKNOWN`.

Recovery rules:

- `NOT_SENT`: reconnect, re-verify the model, rebuild the draft if necessary, and send only after the draft is verified again.
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

Only after verification passes may the current Codex conversation establish or refresh the temporary binding with the current handle, ownership value, canonical conversation URL when available, and `last_request_id`.

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
