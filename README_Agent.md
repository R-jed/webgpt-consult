# README for AI agents

This file is for AI agents that find or support `webgpt-consult`. Human users should read [README.md](README.md) or [README_en.md](README_en.md).

The Skill lets Codex use Chrome to ask GPT-5.6 Sol Pro or High for a second opinion, keep the same Web conversation across follow-up turns, send real supporting files, and recover safely when browser work is interrupted.

## Install

Current project:

```bash
npx skills add R-jed/webgpt-consult
```

Global Codex install:

```bash
npx skills add R-jed/webgpt-consult -g -a codex
```

Update:

```bash
npx skills update webgpt-consult
```

Add `-g` when updating a global installation. Do not invent another installer or setup flow.

## Invoke

The user-facing command is:

```text
/webgpt-consult <consultation request>
```

Implicit invocation is disabled.

## Read order

Before doing browser work, resolve the installed Skill root and read these files in order:

```text
1. <SKILL_ROOT>/SKILL.md
2. <SKILL_ROOT>/references/chrome-workflow.md
3. <SKILL_ROOT>/references/context-packet-template.md   for a substantial consultation
```

Also read the installed Chrome-control Skill's current documentation before using its browser API.

Use each file for one clear purpose:

| File | What it tells you |
| --- | --- |
| `SKILL.md` | What the Skill is allowed to do, how to choose evidence, when a consultation is complete, and what to do on failure |
| `references/chrome-workflow.md` | The executable Chrome protocol: opening or recovering the right conversation, model checks, file upload, composer checks, Send recovery, result checks, and cleanup |
| `references/context-packet-template.md` | The full `CONTEXT_PACKET_V1` format and the shorter follow-up form |
| `scripts/safety_guard.py` | What outgoing UTF-8 text is blocked or warned about |
| `scripts/build_attachment_bundle.py` | How several selected text files are turned into one safe UTF-8 Markdown bundle |

Do not rebuild the runtime rules from this README. The files above are the source of truth.

## Rules that must stay true

- Use Codex-controlled Chrome for the Web consultation.
- For a fresh or branched conversation, use verified GPT-5.6 Sol Pro when available, otherwise verified High, otherwise stop.
- Decide whether an existing verified conversation can be reused before opening the model picker.
- For a normal follow-up in the same verified conversation, reuse the existing model and conversation state.
- If no valid conversation exists, create a new Skill-owned ChatGPT tab instead of taking over an unrelated user tab.
- A local path is not evidence. Deliver the real file, faithful content, or a generated bundle.
- Scan outgoing text for blocked secrets before Send.
- Send once. If the Send result is uncertain, recover the original conversation before doing anything else.
- `UNKNOWN` means the Send outcome is unclear. It does not automatically mean the verified model cache is wrong.
- Keep conversation bindings and recovery state only in the current Codex conversation. Do not create a persistent consultation database.
- Only close browser resources that this Skill can prove it created.
- Treat the Web answer as advice. Codex still checks important claims against local facts before final delivery.

## How much context to send

For a simple question, use a compact prompt.

For a difficult first-turn review, architecture decision, debugging problem, product question, risk review, or similar task, use the full `CONTEXT_PACKET_V1` when losing context would hurt the answer. Keep facts, local judgment, assumptions, evidence, previous attempts, options, and risks separate when they matter.

A difficult packet may be around 8,000 to 15,000 characters when that information is genuinely useful. This is guidance, not a target.

For later turns in the same verified Web conversation, normally send only what changed, the new evidence, and the next question. Use the follow-up delta form and a fresh task identity.

## Files and safety

Prefer original selected files when they can be uploaded reliably.

When many relevant text files are awkward to upload one by one, use:

```bash
python3 "<SKILL_ROOT>/scripts/build_attachment_bundle.py" \
  /path/to/selected/source \
  -o /tmp/webgpt-consult-bundle.md
```

The helper accepts UTF-8 and BOM-declared UTF-8, UTF-16, or UTF-32 text. It decodes strictly, outputs UTF-8, does not guess legacy encodings, and does not replace bad bytes with guessed characters.

The bundle records one `sha256` for the exact UTF-8 content placed in each code fence, together with encoding, `source_bytes`, `included_bytes`, and status. It stops by default if size limits would make the evidence incomplete. `--allow-partial` is an explicit opt-in and partial evidence must be described as partial.

Do not automatically package or upload an entire repository.

## Validation assets

The package includes automated tests and browser acceptance scenarios:

```text
<SKILL_ROOT>/tests/
<SKILL_ROOT>/evals/evals.json
```

The tests cover the safety guard, bundle behavior, the executable Chrome protocol, multi-turn model reuse, Send recovery, document boundaries, and other stable contracts. The eval file covers realistic browser situations such as empty composer recovery, uncertain Send recovery, Chrome reset, High fallback, fresh conversation creation, and reusing an answer that is already visible.

## Do not claim unsupported behavior

Do not say that the Skill stores long-term reviewer memory, automatically uploads a whole repository, requires a full context packet for every question, reopens the model picker on every follow-up, guesses unknown text encodings, recovers conversations by guessing from sidebar titles, or owns user-created browser tabs.

## Third-party notices

Third-party copyright and license notices are recorded in [skills/webgpt-consult/THIRD_PARTY_NOTICES.md](skills/webgpt-consult/THIRD_PARTY_NOTICES.md).
