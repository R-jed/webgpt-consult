---
name: webgpt-consult
description: Use ChatGPT Web's GPT 5.6 Sol Pro or High as a verified second-opinion partner for difficult planning, architecture, debugging, business, product, content-strategy, risk-review, and Skill-design work. Uses adaptive routing: Pro (preferred) > High. Use when the user asks for GPT 5.6 Sol, ChatGPT Pro, a deeper outside judgment, or a file-grounded review. Default to the Codex Chrome plugin for text, model selection, file uploads, waiting, and extraction. Use OpenCLI only when the user explicitly requests it or the Chrome plugin is unavailable and OpenCLI passes preflight.
---

# WebGPT Consult

Ask the best available GPT-5.6 Sol reasoning tier to review a difficult problem with the evidence it needs, then bring the result back into the local Agent workflow. Treat the answer as advisory. The local Agent owns verification, adoption, and final delivery.

## Model routing

Use the strongest supported GPT-5.6 Sol consultation tier available.

**Preferred:** GPT-5.6 Sol Pro

**Fallback:** GPT-5.6 Sol High

If neither Pro nor High can be reliably verified in the model picker, fail closed.

Extra High, Medium, Instant, and unknown models are unsupported and never selected.

The runtime selects based on actual verified picker capability, not assumed subscription tier.

**Downgrade reporting:** When Pro is unavailable and High is used, the execution metadata reports `downgraded=true`. This is expected behavior, not an error.

The historical skill identifier contains "pro", but runtime model routing falls back to High when Pro is unavailable.

## Routing contract

Use the Codex Chrome plugin by default for every consultation, including text-only requests. Read and follow the installed `chrome:control-chrome` Skill before browser work, then read [Chrome workflow](references/chrome-workflow.md).

Use OpenCLI only when one of these is true:

- The user explicitly requests OpenCLI.
- The Codex Chrome plugin is unavailable or disconnected, and `opencli doctor` confirms a working browser bridge.

When OpenCLI is eligible, read [OpenCLI fallback](references/opencli-fallback.md). Do not choose OpenCLI merely because it is installed. Do not use OpenCLI for file uploads.

If neither path is available, prepare the context packet and tell the user exactly which browser connection is missing. Never imply that a consultation completed.

## Requirements

- The default path requires Codex with the Chrome plugin connected.
- The selected Chrome profile must be logged into ChatGPT Web.
- The account must expose Pro or High in the ChatGPT model picker.
- OpenCLI is optional and is not an installation prerequisite.

## Hard gates

### Model truthfulness

The selected model must belong to the verified GPT-5.6 Sol family. Confirm either:

- a GPT-5.6-specific test ID is checked; or
- the picker shows the `GPT-5.6 Sol` family and the exact tier radio has `aria-checked=true`.

Reject legacy GPT 5.5 Pro selectors, `Pro Extended`, bare models without GPT-5.6 family evidence, Extra High, Medium, and ambiguous text outside the model picker. Stop if neither Pro nor High can be confirmed.

### Tier verification

After clicking a candidate tier, capture fresh picker state and verify:

1. The selected tier name appears in a checked `menuitemradio`.
2. The `aria-checked=true` attribute is present on the correct element.
3. The GPT-5.6 Sol family evidence is present in the picker.

A `ref` (DOM reference number) is an action locator for clicking, not proof of model identity. Verification always uses fresh state, not the ref itself.

### Artifact truthfulness

ChatGPT Web cannot read a local path by itself. Upload the actual file, paste its contents, or build a text bundle. Never claim GPT inspected a file when it received only a filename, path, or summary.

### Credential hygiene

Do not send executable credentials: tokens, cookies, passwords, API keys, private keys, OAuth headers, browser profiles, or session dumps. Ordinary user-owned business and project context may be included when it materially improves the judgment.

Run the bundled scanner before submission:

```bash
SKILL_DIR="<path-to-installed-webgpt-consult>"
python3 "$SKILL_DIR/scripts/check_packet_safety.py" packet.md
```

## Workflow

1. Write the local Agent's best judgment before consulting. Identify the decision, success standard, evidence, constraints, options, risks, attempts, and unknowns.
2. Build a restorable context packet using [the template](references/context-packet-template.md). Separate facts, local judgment, and unknowns.
3. Select the smallest evidence set that still contains the truth. Use real attachments when structure, formatting, source layout, logs, images, or implementation details matter.
4. Run the safety scanner. Remove credential-like material; keep useful project context.
5. Execute the default [Chrome workflow](references/chrome-workflow.md). Use the optional [OpenCLI fallback](references/opencli-fallback.md) only when the routing contract permits it.
6. Confirm the selected GPT-5.6 Sol tier before sending. Record the model evidence, timestamp, context strategy, attachment names, and sentinel.
7. Wait for the complete assistant turn. A preamble or missing sentinel while the page is still generating means "not ready." Continue the same conversation; do not submit a duplicate request.
8. Extract the complete answer, verify the sentinel, compare it with local evidence, and decide what to adopt, reject, or modify.

## Execution examples

### Pro available (preferred path)

```text
Available: Pro, High
Selected: Pro
downgraded=false
```

### Pro unavailable

```text
Available: High
Selected: High
downgraded=true
```

### No supported tier

```text
Available: Extra High, Medium, Instant
Result: fail closed
```

## Context assembly

Include:

- Exact decision or problem
- Success standard and user intent
- Relevant background and constraints
- Local judgment before consultation
- Evidence and actual artifacts
- Attempts and verbatim errors
- Meaningful options and tradeoffs
- Risks and unknowns
- Requested output: critique, decision, architecture, plan, checklist, or revision

For difficult work, prefer a structured 8,000–15,000-character packet over a short prompt that removes causal details. Ask for a concise reasoning artifact—assumptions, decision frame, evidence weighting, strongest counterargument, tradeoffs, and recommendation—without requesting hidden chain-of-thought.

## Attachments

Use attachments when the answer depends on local Skills, repositories, source files, screenshots, documents, spreadsheets, slides, PDFs, datasets, logs, or rendered output.

When a directory contains many text files, build one reviewable bundle:

```bash
SKILL_DIR="<path-to-installed-webgpt-consult>"
python3 "$SKILL_DIR/scripts/build_attachment_bundle.py" \
  /path/to/artifact-or-directory \
  -o /tmp/webgpt-consult-attachment-bundle.md
```

List every attachment in the packet. Upload original human-readable files first; use a generated Markdown bundle when there are too many files or archives are rejected. Exclude caches, dependencies, build output, `.git`, secrets, and irrelevant binaries.

## Completion contract

A consultation is complete only when all are true:

- A supported GPT-5.6 Sol tier (Pro or High) selection was verified.
- The prompt and every required attachment were visibly present before sending.
- The assistant stopped generating.
- The complete assistant turn was extracted.
- The expected `WEBGPT_CONSULT_RESULT_...` sentinel appears in that assistant turn.

If the user says the result is already visible, re-extract the existing conversation before retrying. Never start a duplicate while the original run may still be active.

## Local integration

Return:

```markdown
## Consultation Result
- Status: completed | failed | skipped
- Requested tier: pro
- Selected tier: pro | high
- Selected model: <display name from picker>
- Downgraded: true | false
- Sentinel verified: yes | no
- Browser path: Codex Chrome | OpenCLI

## What the Model Said
<concise summary>

## Local Adoption Decision
- Adopt:
- Reject:
- Modify:
- Reason:

## Final Answer
<the local Agent's verified recommendation or deliverable>
```

## Failure handling

- **Chrome plugin unavailable:** use OpenCLI only when its preflight succeeds; otherwise stop and report the missing connection.
- **Not logged in:** ask the user to sign in to ChatGPT Web in the selected Chrome profile.
- **No Pro or High available:** stop and report that neither GPT-5.6 Sol Pro nor High was found.
- **Post-selection verification failed:** stop and report which tier was selected but could not be confirmed.
- **Attachment failed:** retry through Chrome's real file chooser, paste small content, or use one Markdown bundle. Do not claim the file was received.
- **Still generating:** keep waiting in the same conversation and inspect targeted completion signals.
- **Missing sentinel after completion:** extract the complete assistant turn once more, including escaped underscores; otherwise mark the consultation incomplete.
- **Low-quality answer:** use only supported parts. The local Agent retains final judgment.
