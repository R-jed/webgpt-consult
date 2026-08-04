# Validation

## Canonical deterministic validation

Run on a connected checkout:

```text
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -m py_compile scripts/*.py
```

The current v1.2 simplification defines 15 deterministic unit tests covering:

- credential blocking and path-warning correctness;
- verified Pro -> High model routing boundaries;
- rejection of generic GPT-5 Pro identity evidence;
- exact sentinel and task-ID result binding;
- direct text-attachment credential blocking;
- binary manual-review gating;
- durable consultation-state save/load and Web URL replacement;
- corrupt state isolation;
- separate checkout identity isolation;
- consultation-state schema validation;
- strict attachment-bundle missing-input and fence handling.

## Evidence from this iteration

The review runtime could not perform a fresh GitHub clone because outbound DNS resolution for `github.com` was unavailable. A full current-HEAD suite is therefore not claimed as locally passed from this environment.

The new `consult_state.py` was read back from `main`, syntax-compiled, and exercised in a targeted local smoke test:

```text
consult_state.py syntax: passed
5 targeted state assertions: passed
```

Those assertions verified:

- consultation state saves and loads;
- replacing an expired/overfull Web conversation URL does not require lineage machinery;
- `created_at` is preserved across state updates;
- one corrupt consultation file is isolated and reported as a warning;
- two checkouts of the same remote repository receive different project identities;
- invalid non-ChatGPT conversation URLs are rejected.

The security, model-routing, result-verification, preflight, and bundle implementations were not changed by the v1.2 state simplification. They retain the earlier deterministic baseline, but the canonical full-suite commands above must still be run on a connected checkout before declaring the current HEAD fully local-suite validated.

GitHub Actions remains configured to execute the deterministic suite and compile scripts on supported Python versions. Do not claim CI success until a visible successful status exists for the current HEAD.

## Real browser validation

Repository tests cannot prove live ChatGPT Web DOM compatibility. Validate these paths with real Codex + Chrome before calling the release browser-validated:

```text
Codex version:
Chrome plugin version:
macOS version:
ChatGPT locale:
Pro selection and confirmation: pending
High fallback and confirmation: pending
Independent review starts fresh: pending
Independent review withholds local judgment by default: pending
Explicit proposal-attack includes local proposal: pending
Clear follow-up reuses stored conversation: pending
Ambiguous follow-up starts fresh: pending
Context-limited chat -> fresh restore from local snapshot: pending
Corrupt/missing state -> fresh fail-soft path: pending
Text attachment preflight/upload: pending
Binary manual-review path: pending
Exact result verification: pending
Local adoption before state update: pending
```

The browser contract is intentionally thin. A Web UI change may require locator adaptation, but it should not require changes to durable consultation-state semantics.
