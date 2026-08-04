# Validation

## Deterministic policy validation

Canonical commands for a connected local checkout:

```text
python -m unittest discover -s tests -p 'test_*.py' -v
python -m py_compile scripts/*.py
```

### Confirmed baseline before context-rollover iteration

Local review run on 2026-08-04:

```text
13 tests passed
Python syntax compilation passed
```

That baseline covered:

- common credential blocking;
- corrected absolute-path matching;
- disabled/non-actionable Pro fallback to High;
- rejection of generic GPT-5 Pro as GPT-5.6 evidence;
- exact sentinel and task-ID binding;
- direct text-attachment credential blocking;
- binary manual-review gate;
- multiple project workstreams in the conversation registry;
- canonical git-root identity across project subdirectories;
- conversation rollover history when a workstream moves to a new ChatGPT URL;
- missing bundle input failure;
- Markdown fence collision handling.

### Context-rollover delta validation

The current deterministic test file defines 22 tests after the context-window rollover work.

A fresh GitHub clone could not be executed from the review runtime because outbound DNS resolution for `github.com` was unavailable. The final changed rollover policy was therefore executed directly from the final source definitions in the review runtime instead of claiming a fresh-clone full-suite pass.

Confirmed on the final rollover delta:

```text
conversation_registry.py syntax: passed
continuity_capsule.py syntax: passed
8 targeted rollover assertions: passed
```

The targeted assertions verified:

- a complete continuity capsule validates and produces a SHA-256;
- an empty required capsule section fails validation;
- initial workstream creation sets both immutable `root_task_id` and active `branch_base_task_id`;
- normal continuation preserves the active branch base;
- `rollover_branch` preserves root and active branch base while incrementing lineage;
- `rollover_fresh` preserves root but resets the active branch base to the first successful task in the fresh conversation;
- the next rollover plan uses that new active branch base;
- silently changing an active workstream to another ChatGPT URL without explicit rollover is rejected.

Additional tests now present in `tests/test_deterministic_closure.py` cover required rollover mode/hash, parent/new URL requirements, immutable direct branch-base semantics, and the existing deterministic safety/model/bundle contracts. Run the canonical commands above on a connected local checkout before declaring the current HEAD fully local-suite validated.

The registry uses atomic writes and a cross-process lock to avoid lost updates when multiple Codex sessions write local conversation state concurrently.

GitHub Actions is configured to run the deterministic suite on Python 3.10 and 3.12. A visible successful status for the current push has not been observed from this review environment, so CI is not claimed as passed here.

## Real browser validation

Repository tests cannot prove ChatGPT Web DOM compatibility or the live semantics of the Branch action. Before calling a release browser-validated, run a real Codex + Chrome pass and record:

```text
Codex version:
Chrome plugin version:
macOS version:
ChatGPT locale:
Pro selection and confirmation: pending
High fallback and confirmation: pending
Fresh conversation creation: pending
Same-workstream continuation: pending
Different-workstream isolation: pending
Text attachment preflight/upload: pending
Binary manual-review path: pending
Exact result verification: pending
Registry record/reopen after tab closure: pending
Concurrent registry update smoke test: pending
Context-length rejection detection: pending
Branch from active branch-base task: pending
Branch child URL/baseline verification: pending
Validated continuity capsule transfer: pending
Repeated branch rollover remains bounded: pending
Branch unavailable -> rollover_fresh: pending
Fresh rollover resets active branch base: pending
```

A Web UI change can require workflow adaptation even when all deterministic tests remain green.
