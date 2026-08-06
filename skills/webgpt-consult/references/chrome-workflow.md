# Codex Chrome Workflow

This file is the canonical executable browser protocol for `webgpt-consult`. It defines the browser actions Codex should perform and the rules that must remain true while those actions run.

Task reasoning and evidence selection belong to Codex. Substantial consultations use `context-packet-template.md`.

The installed Chrome-control Skill is authoritative for the exact browser API available in the current environment. Read its current documentation before browser work. When it exposes the current `node_repl js` + Playwright adapter, use the execution patterns below. If the adapter changes, keep the state, safety, and verification rules in this document while using the documented replacement API.

## Runtime invariants

These rules apply across every stage:

- work from fresh browser state before state-changing actions;
- resolve controls unambiguously and verify uniqueness when a locator could match more than one element;
- after a UI mutation, observe the resulting state again instead of trusting an old locator or promise;
- a browser runtime reset invalidates JavaScript bindings, locators, element references, pending promises, and other transient browser objects;
- a browser runtime reset does not by itself invalidate a verified conversation-scoped model cache;
- never inspect cookies, local storage, passwords, browser profiles, or session databases;
- never Send an empty or unverified composer;
- Send exactly once; an uncertain outcome is recovered from the original conversation;
- only close resources whose Skill ownership is proven by exact handle.

## 1. Initialize the Chrome runtime

1. Read the installed `chrome:control-chrome` Skill completely when that is the Chrome-control entry point in the current environment.
2. Discover the documented JavaScript browser tool when it is not already callable. In the current adapter this may be `node_repl js`.
3. Initialize the browser runtime from the Chrome plugin's own documented absolute `browser-client.mjs` path when that adapter is in use.
4. Select the extension-backed browser binding using the current documented API. In the current adapter this may be `agent.browsers.get("extension")`.
5. Read the browser binding's current documentation before interacting.
6. Inspect the current tab inventory without changing unrelated tabs.
7. Keep browser work in the background unless the user asks to see it.

If a reset, reconnect, or browser-tool restart occurs, reinitialize the runtime and reacquire `agent`, browser objects, tabs, locators, and any other transient objects. Never carry an unresolved Playwright promise into a later browser invocation.

### Action discipline

For any state-changing UI action:

1. inspect current browser state or a targeted DOM snapshot;
2. construct a stable locator from that state;
3. call `count()` when uniqueness is not self-evident;
4. act only when the intended control is unambiguous;
5. take a targeted observation after the UI changes.

Current test IDs and localized text are implementation details, not permanent contracts. Use them only when they match the current UI.

## 2. Resolve browser ownership and conversation continuity

Resolve continuity before model selection or file preparation. A follow-up should not pay the cost or failure surface of fresh-conversation setup when the existing verified conversation is still valid.

### Browser ownership

Treat each browser resource as:

```text
owned   = this Skill created the exact resource during the current Codex conversation and still knows its handle
unowned = it existed beforehand, was user-supplied, merely discovered, or ownership is uncertain
```

Ownership follows the exact handle. Navigating a user tab to ChatGPT does not make it owned. A new conversation URL does not imply a new tab.

Never reconstruct ownership from URL, title, content, project name, or history.

### Verified conversation binding

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

Reuse the bound conversation directly without re-reading the previous sentinel when all of these are true:

- the exact bound tab handle is still live;
- it is still on the retained canonical conversation URL when that URL is available;
- there was no navigation, branch, runtime-reset recovery, or other event that made conversation identity ambiguous;
- the previous submission already completed and its sentinel was verified;
- there is no unresolved `SENT` or `UNKNOWN` submission.

In this path, prior identity is already established. Prepare the new delta and verify only the new submission and result identity.

### Recovery path

If the live fast path is unavailable and a prior verified conversation should still exist:

1. reuse the exact bound handle if it can still be recovered, otherwise open the exact retained conversation URL;
2. inspect the recovered conversation from fresh browser state;
3. verify the immediately relevant prior assistant result against `last_sentinel`;
4. continue only when the conversation identity is unambiguous.

If recovery cannot prove the conversation identity, start fresh only when no unresolved `SENT` or `UNKNOWN` submission remains attached to the old conversation.

Never recover a consultation by guessing from sidebar titles, recent-chat order, browser history, project names, timestamps, or semantic similarity.

If the user says the expected answer is already visible, inspect and verify the existing latest assistant turn before preparing another submission.

### Fresh conversation path

Use this path when the request is new, no valid continuation exists, or a fresh start is required and no unresolved old submission prevents it.

1. create a new tab through the documented Chrome-control API;
2. record the exact new handle as Skill-owned;
3. navigate that tab to `https://chatgpt.com/`;
4. confirm ChatGPT Web is signed in and the composer is usable;
5. start from a fresh chat state rather than reusing an unrelated existing conversation;
6. continue to model verification before preparing evidence or a draft.

Do not take over an unrelated user tab merely to avoid creating a new one. If the user explicitly supplies a ChatGPT tab for this consultation, treat it as unowned and never close it automatically.

If ChatGPT is not signed in, stop and ask the user to sign in in the selected Chrome profile.

### Branch when the thread is too heavy

If the same work should continue but the current Web thread is too context-heavy, use `Branch in new chat` from a useful earlier point when available. A branch is a new conversation identity and requires fresh model verification.

## 3. Resolve and verify the Web model

Allowed policy:

```text
GPT-5.6 Sol Pro
  -> otherwise GPT-5.6 Sol High
  -> otherwise stop
```

Only literal `Pro` and `High` tiers associated with GPT-5.6 Sol are eligible. Reject GPT-5.5 Pro, `Pro Extended`, base-Sol `Extra High`, ambiguous bare `Pro`, Codex reasoning labels, and unrelated models.

### Model-verification decision

```text
Fresh conversation or Branch
  -> verify model in the picker

Same live verified conversation with valid cache
  -> reuse cached tier; do not open picker

Recovered exact same conversation, prior identity re-proven
  -> reuse cached tier unless fresh UI/error evidence contradicts it

Conversation identity changed or cannot be proven
  -> cache invalid; verify the new conversation

Visible conflicting tier or model availability/switch error
  -> re-open picker and verify

User explicitly asks to check or change the tier
  -> re-open picker and verify

Browser runtime reset by itself
  -> reacquire browser objects; do not invalidate model cache by reset alone
```

`UNKNOWN` is a dispatch state, not a model state. It forbids duplicate sending. It does not automatically invalidate `verified_web_model`; the cache remains usable only after the original conversation identity is recovered and re-proven with no contradictory model evidence.

### Fresh or branched conversation

1. take a fresh DOM observation of the current model control;
2. open the model picker using a locator derived from that observation;
3. select GPT-5.6 Sol `Pro` when available, otherwise `High`;
4. re-observe the picker and verify both the GPT-5.6 Sol family and the selected tier;
5. when the UI exposes radio state, require the selected tier to be visibly selected, for example `aria-checked=true`;
6. bind the verified tier to this conversation as `verified_web_model`.

Use the current UI semantically. Do not maintain a hard-coded DOM parser or element-reference table. A current test ID or radio locator can be used when it is supported by the fresh UI observation, but the semantic family + tier verification is the contract.

## 4. Prepare task identity, context, and evidence

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
3. `scripts/build_attachment_bundle.py` when many selected supported Unicode text files are awkward to upload individually or an archive is rejected.

Do not upload a whole repository merely because it is available.

Run `scripts/safety_guard.py` on the exact outgoing prompt or packet and every UTF-8 text attachment. Blocking findings must be removed or redacted. Privacy warnings are reviewed in context rather than automatically deleting task-relevant business or project facts.

For BOM-declared UTF-16 or UTF-32 text sources, use the bundle helper or a faithful local UTF-8 normalization so their actual text is safety-scanned before Send. Do not treat a non-UTF-8 encoding as permission to bypass the text safety boundary.

The bundle helper accepts UTF-8 plus BOM-declared UTF-8, UTF-16, and UTF-32 through strict decoding, normalizes bundled content to UTF-8, never guesses legacy charsets, never uses replacement decoding, and performs its own final blocking scan. It fails closed on incomplete evidence unless partial bundling was explicitly requested.

Inspect binary and non-text files locally before upload.

## 5. Upload evidence with one file-chooser lifecycle

Read the installed Chrome-control Skill's current file-upload documentation before uploading.

Use the real file chooser. When the current adapter exposes Playwright, keep chooser-wait creation, add-file interaction, chooser resolution, and `setFiles(...)` inside one JavaScript browser invocation.

### Current adapter example

The following is an execution pattern, not a permanent DOM contract. Build the locators from fresh UI state and change test IDs or localized text when the current UI differs.

```js
const chooserPromise = tab.playwright.waitForEvent("filechooser", { timeoutMs: 15000 });

const addButton = tab.playwright.getByTestId("composer-plus-btn");
if (await addButton.count() !== 1) {
  throw new Error("Expected one composer add-files button");
}
await addButton.click();

// Derive this locator from the current menu observation; localized text may differ.
const fileMenuItem = tab.playwright.getByText("添加照片和文件", { exact: true });
if (await fileMenuItem.count() !== 1) {
  throw new Error("Expected one add-files menu item");
}
await fileMenuItem.click();

const chooser = await chooserPromise;
await chooser.setFiles(["/path/to/file.md"]);
```

### Required invariants

- never split `waitForEvent("filechooser")` and `chooser.setFiles(...)` across browser calls;
- never reuse a pending chooser promise after a reset or later JavaScript invocation;
- after upload UI changes, reacquire affected locators from fresh browser state;
- confirm every required attachment filename or chip is visibly present and fully uploaded;
- if multiple individual uploads are unstable, use the canonical bundle helper for the selected supported text evidence rather than claiming an archive or local path was reviewed.

## 6. Populate and verify the composer

After all uploads finish, reacquire the composer from fresh browser state because attachment UI changes can invalidate earlier locators.

1. use the Chrome-control Skill's supported text-entry method once to insert the complete prompt or packet;
2. reacquire the composer;
3. read rendered composer text from the fresh locator;
4. require the current sentinel and enough distinctive request text to identify the intended submission;
5. for `CONTEXT_PACKET_V1`, also require the packet prefix and current `task_id`.

If an uploaded Markdown or text preview leaves the composer empty and the fresh UI exposes exactly one associated `Show in text field`, `在文本字段中显示`, or equivalent action, use that action once. Reacquire and verify the composer again.

Do not cycle through `fill`, `type`, clipboard paste, or unrelated input methods after a verified failure. An attachment card or filename is not composer text.

If the intended text is still missing or ambiguous, stop. Never Send an empty or unverified composer.

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

## 8. Send exactly once

Immediately before Send, confirm:

- the intended conversation is active;
- model state is valid from fresh verification or the conversation-scoped cache;
- the current sentinel and, for a packet, `task_id` are in the verified composer text;
- all required attachment chips are present;
- the outgoing prompt and every textual attachment have passed the applicable blocking safety path;
- no blocked credential or payment material remains.

Do not reopen the model picker solely for this pre-send gate when the same verified conversation has a valid cached tier.

Click Send once, then classify the outcome from fresh evidence.

| State | Trigger | Allowed action |
| --- | --- | --- |
| `NOT_SENT` | Send definitely has not been clicked | Reacquire state, rebuild the draft if needed, re-verify only invalidated state, then Send once after all checks pass |
| `SENT` | Fresh evidence shows the new user turn, emptied composer, or active generation | Stay with the same conversation; wait or extract; never resend |
| `UNKNOWN` | Reset, disconnect, or timeout occurs during or after the click before submission can be proven | Recover the original conversation and determine whether the submission exists; never send a replacement while uncertainty remains |

Set `SENT` only after fresh submission evidence. Any ambiguous click outcome becomes `UNKNOWN`.

## 9. Recover an interrupted submission

Recovery depends on dispatch state.

### `NOT_SENT`

1. reacquire the intended conversation and browser state;
2. rebuild the draft when needed;
3. verify the model only when its conversation-scoped cache is invalid;
4. re-check attachments, composer identity, and safety state;
5. Send once.

### `SENT`

1. recover the exact bound handle or `current_conversation_url`;
2. stay with that conversation;
3. wait for generation or extract the completed result;
4. never click Send again for the same submission.

### `UNKNOWN`

1. recover the exact bound handle when available, otherwise the exact `current_conversation_url`;
2. re-prove the conversation identity from the exact binding and immediately relevant prior sentinel when recovery requires it;
3. look for the new user turn, current task identity, active generation, or completed result;
4. if submission evidence exists, continue as `SENT`;
5. if the original outcome cannot be established unambiguously, mark the consultation incomplete.

Never create a replacement consultation or click Send again while `UNKNOWN` remains unresolved.

`UNKNOWN` does not independently invalidate the cached model. Conversation identity recovery determines whether the existing model cache still belongs to the recovered conversation.

## 10. Wait for generation and verify the result

Stay in the same conversation while generation is active. Use fresh targeted observations instead of repeatedly rebuilding the full page state.

Current active-generation signals may include:

- a visible stop-generating control such as `data-testid=stop-button`;
- visible thinking or generating status;
- an incomplete assistant turn while generation controls remain active.

These are observation examples, not permanent DOM contracts.

While generation is active, do not resend, refresh, start a replacement consultation, close the tab, or send `continue`.

Long Pro responses can take substantial time. Continue observing the same submission until completion or a real browser failure triggers dispatch-state recovery.

After generation stops:

1. inspect only the latest assistant turn from fresh browser state;
2. do not count a sentinel echoed in the user's prompt as completion evidence;
3. require the first non-empty assistant line to equal the current sentinel exactly;
4. require substantive response content after the sentinel;
5. if verification fails, read the complete latest assistant turn once more;
6. if the sentinel still does not match or the result is truncated, mark the consultation incomplete.

Do not normalize the sentinel into another protocol or accept a partial or fuzzy match.

## 11. Refresh the binding and clean up safely

Only after result verification succeeds:

1. refresh the conversation binding with the current handle, ownership, canonical URL, `last_task_id`, `last_sentinel`, and verified or cached model;
2. confirm the replacement binding represents the verified conversation;
3. mark the current submission complete;
4. clear the transient `current_*` record;
5. then inspect any superseded resource for cleanup eligibility.

If the consultation is deliberately marked failed or incomplete and no unresolved Send outcome remains, clear the transient record then as well.

### Cleanup decision matrix

| Condition | Cleanup decision |
| --- | --- |
| old and new bindings use the same handle | keep it open |
| old handle differs and is proven Skill-owned, idle, and not `UNKNOWN` | may close after replacement binding is established |
| user-created or ownership-unknown resource | leave open |
| generation may still be active | leave open |
| dispatch state is `UNKNOWN` | leave open |
| exact old handle is no longer known | leave open |

A failed temporary candidate may be closed only when it is proven Skill-owned, did not become the active binding, its exact handle is still known, no generation is active there, and its dispatch state is not `UNKNOWN`.

Never use `pkill`, `killall`, generic Chrome termination, process scanning, a cleanup daemon, or a persistent tab registry.

Conversation titles, sidebar order, content similarity, or project names are never sufficient evidence for identity or cleanup.