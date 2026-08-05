# Chrome workflow

This reference contains the browser-state rules that should remain deterministic. Prompt design, evidence selection, and consultation style belong to Codex and the user's request.

## 1. Connect and authenticate

Use the Codex Chrome capability to open ChatGPT Web. Confirm that ChatGPT is signed in and the composer is usable.

Do not inspect cookies, local storage, passwords, browser profiles, or session databases.

## 2. Track browser ownership when a tab/page is obtained

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

Only literal `Pro` and `High` entries associated with GPT-5.6 Sol are eligible. Do not map Codex model labels, reasoning levels, localized reasoning labels, or unrelated model names into these tiers.

Do not maintain a DOM parser or hard-coded element-reference table in this Skill. Use the current browser UI semantically, then re-observe the picker after selection and verify that the intended GPT-5.6 Sol tier is selected and usable.

Re-verify after a fresh conversation or branch.

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

Run `scripts/safety_guard.py` over text that may contain sensitive values. If it blocks, redact or remove the value locally and scan again.

For binary/non-text files, inspect them locally before upload. The Skill does not attempt to build a general binary DLP system.

## 6. Fill the composer and upload files

Include this line in the prompt:

```text
Request-ID: <request-id>
```

Also instruct ChatGPT Web to begin its response with that exact line. The rest of the prompt is unconstrained by the Skill.

Use the real file chooser for attachments. Confirm required attachment chips are visible and uploads have completed successfully.

Never claim a source or file was reviewed unless it was actually included or uploaded.

## 7. Send once

Immediately before Send, confirm:

- the intended Web conversation is active;
- the selected model is verified GPT-5.6 Sol Pro or High;
- the fresh request ID is present;
- the prompt matches the user's current intent;
- all required attachments are visibly uploaded;
- no blocked secret/payment material remains.

Send once.

While generation is active, do not refresh, duplicate the request, or close that tab.

## 8. Verify the result and bind the conversation

When generation stops, inspect only the latest assistant turn from fresh browser state.

The first non-empty line must exactly equal:

```text
Request-ID: <request-id>
```

There must also be substantive content after that line.

If the ID does not match, re-read the latest completed assistant turn once. If it still does not match, treat the consultation as incomplete.

Only after verification passes may the current Codex conversation establish or refresh the temporary binding with the current handle, ownership value, canonical conversation URL when available, and `last_request_id`.

## 9. Cleanup

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
- no request is still generating there.

Never use `pkill`, `killall`, generic Chrome termination, process scanning, a background cleanup daemon, or a persistent tab registry.

If state is uncertain, leave the tab alone.
