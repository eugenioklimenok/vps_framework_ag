# NEW PROJECT SPECIFICATION

## 1. Purpose

This document defines the **current executable technical specification** for the `new-project` command.

Its purpose is to make the current PROJECT baseline implementation precise, deterministic, and Codex-consumable.

It defines:

- command intent
- explicit inputs
- target classification rules
- baseline scaffold requirements
- execution phases
- validation requirements
- output expectations
- exit code behavior
- forbidden implementation patterns

---

## 2. Governing Documents

This specification is governed by:

1. `FRAMEWORK_ARCHITECTURE_MODEL.md`
2. `ENGINEERING_RULES.md`
3. `PROJECT_BASELINE_FDD.md`
4. `PROJECT_BASELINE_TDD.md`
5. `PROJECT_BASELINE_CONTRACT.md`
6. `PYTHON_IMPLEMENTATION_BASELINE.md`
7. `CODEX_DEVELOPMENT_PROTOCOL.md`

If this specification conflicts with a higher-precedence PROJECT document, the higher-precedence document wins and this specification MUST be corrected.

---

## 3. Command Definition

### Command name

`new-project`

### Domain ownership

PROJECT

### Command purpose

Create or safely complete the documented baseline scaffold for a project.

### Command type

Mutation-capable local filesystem scaffold command.

---

## 4. Explicit Inputs

The current baseline requires explicit project creation inputs.

### Required inputs

- `--name`
  - human-readable project name

- `--path`
  - target root path where the scaffold will be created or completed

### Optional inputs

- `--slug`
  - explicit project slug
  - if omitted, deterministic derivation may be used according to the documented slug rule

- `--description`
  - optional short description rendered into project metadata and README template

- `--template`
  - template identifier
  - current baseline may default to `baseline-v1` only if that default is explicitly documented by the CLI behavior

### Input rule

No hidden input sources are allowed for required scaffold identity.

Environment variables may be used only for future explicitly documented optional behavior, not for hidden project identity.

---

## 5. Slug Derivation Rule

When `--slug` is omitted, the implementation MAY derive the slug from `--name` only by the following deterministic rule:

1. trim surrounding whitespace
2. lowercase the value
3. replace spaces and underscores with hyphens
4. collapse repeated separators
5. remove characters outside `a-z`, `0-9`, and `-`
6. reject the result if empty

### Examples

- `My Project` → `my-project`
- `API_Backend` → `api-backend`
- `  Demo  Site  ` → `demo-site`

### Failure rule

If derivation cannot produce a valid non-empty slug, the command MUST abort and require explicit input.

---

## 6. Managed Scaffold Baseline

The current baseline manages the following required scaffold layout:

```text
<project_slug>/
├── app/
├── config/
├── deploy/
├── docs/
├── operate/
├── tests/
├── .env.example
├── .gitignore
├── README.md
├── compose.yaml
└── project.yaml
```

### Managed directories

- `app/`
- `config/`
- `deploy/`
- `docs/`
- `operate/`
- `tests/`

### Managed files

- `.env.example`
- `.gitignore`
- `README.md`
- `compose.yaml`
- `project.yaml`

### Baseline content rules

- managed text files MUST be rendered deterministically from explicit inputs and template metadata
- managed files MUST use UTF-8 encoding
- managed text newline policy SHOULD be normalized consistently across platforms
- `compose.yaml` MAY be a valid placeholder for future DEPLOY work, but it MUST remain syntactically valid text content
- `.env.example` MUST contain placeholders or comments only, never live secrets

---

## 7. `project.yaml` Baseline Schema

The current baseline requires `project.yaml` to contain at minimum:

- `project_name`
- `project_slug`
- `template_id`
- `template_version`
- `generated_by`

### Recommended minimum example

```yaml
project_name: Example Project
project_slug: example-project
template_id: baseline-v1
template_version: 1
generated_by: new-project
```

The exact YAML formatting may vary, but the semantic content must remain deterministic and machine-readable.

---

## 8. Target Classification Rules

The command MUST classify the target path before any scaffold mutation.

### CLEAN

Use when:

- the target path does not exist and is safely creatable
- or the target path exists as an empty directory
- and no conflicting conditions are detected

### COMPATIBLE

Use when:

- `project.yaml` exists and matches the requested project identity
- required managed scaffold state already exists or is fully aligned
- no conflicting managed content is detected

### SANEABLE

Use when:

- `project.yaml` exists and matches the requested project identity
- the target contains a partial but compatible scaffold
- missing managed items can be created safely without overwriting conflicting content

### BLOCKED

Use when any of the following apply:

- target path exists as a non-directory conflicting object
- existing `project.yaml` metadata conflicts with requested identity
- scaffold metadata is malformed or ambiguous
- managed files exist with incompatible content or incompatible ownership/policy assumptions
- the target contains conflicting state such that safe scaffold generation cannot be trusted
- required parent path is not safely writable

### Priority rule

If multiple conditions are present:

`BLOCKED > SANEABLE > COMPATIBLE > CLEAN`

---

## 9. Pre-Execution Checks

At minimum, the current implementation must evaluate the following pre-execution checks.

### CHECK_INPUT_01 — Project Name Validity

Confirm that the provided project name is non-empty and acceptable for the documented baseline.

**FAIL**

- missing project name
- empty or whitespace-only name
- other documented name-invalid conditions

**Impact**

- invalid input
- command abort

---

### CHECK_INPUT_02 — Project Slug Validity

Confirm that the explicit or derived slug is valid for the documented baseline.

**FAIL**

- empty slug
- invalid characters remain
- slug derivation failed

**Impact**

- invalid input
- command abort

---

### CHECK_TARGET_01 — Parent Path Viability

Confirm that the parent path can safely host scaffold creation.

**FAIL**

- parent path does not exist and cannot be created by documented policy
- parent path is not writable or otherwise unsafe
- path resolution is ambiguous

**Impact**

- `BLOCKED`

---

### CHECK_TARGET_02 — Target Path State

Confirm whether the target path is absent, empty, scaffold-compatible, scaffold-partial, or conflicting.

**Possible outcomes**

- `CLEAN`
- `COMPATIBLE`
- `SANEABLE`
- `BLOCKED`

---

### CHECK_TARGET_03 — Scaffold Metadata Compatibility

Evaluate `project.yaml` when present.

**PASS**

- metadata exists
- metadata is parseable
- metadata matches requested project identity

**FAIL**

- metadata missing in a state that requires it for safe reuse
- metadata malformed
- metadata conflicts with requested slug or template

**Impact**

- typically `BLOCKED`
- or contributes to `SANEABLE` only when compatibility remains provable by documented policy

---

## 10. Execution Phases

The current baseline implementation should follow these phases.

### Phase 1 — Input Validation

- validate `--name`
- validate or derive `--slug`
- validate `--path`
- validate template selection if applicable

### Phase 2 — Target Inspection

- inspect parent and target path state
- inspect existing marker metadata where present
- determine managed/unmanaged path conflicts

### Phase 3 — Classification

- reduce findings into one classification:
  - `CLEAN`
  - `COMPATIBLE`
  - `SANEABLE`
  - `BLOCKED`

### Phase 4 — Scaffold Planning

Build a deterministic plan containing at minimum:

- managed directories to create
- managed files to create
- managed items safe to reuse
- block reason when execution must not proceed

### Phase 5 — Materialization

When classification is allowed:

- create target root if needed
- create missing managed directories
- render and create missing managed files
- create deterministic `project.yaml`

### Phase 6 — Post-Action Validation

Confirm that:

- all required managed paths exist
- `project.yaml` exists
- `project.yaml` metadata matches intended identity
- no required managed path is missing after execution

### Phase 7 — Final Result Rendering

Render deterministic human-readable output based on structured state.

---

## 11. Re-Run Behavior

The command MUST remain safe to re-run for the same intended project identity.

### Allowed re-run behavior

- no-op success on already-correct compatible scaffold
- create missing managed items in saneable compatible scaffold
- reuse already-correct managed content

### Forbidden re-run behavior

- overwrite conflicting existing content
- mutate unrelated user files
- silently repair ambiguous metadata
- reinterpret a different project identity as compatible

---

## 12. Output Expectations

The command SHOULD expose:

1. human-readable output
2. structured internal result data
3. future-ready export capability where relevant

### Minimum human-readable output sections

Recommended sections include:

- input summary
- target classification
- action summary
- validation result
- final outcome

### Structured result expectations

Recommended result fields include:

- `classification`
- `result_state`
- `created_paths`
- `reused_paths`
- `blocked_reason`
- `validation_passed`

---

## 13. Exit Code Rules

Recommended deterministic exit codes:

- `0` → scaffold created, completed, or reused successfully and validation passed
- `2` → blocked/unsafe/ambiguous state or failed post-validation
- `3` → invalid inputs or command runtime execution failure

This mapping MUST remain deterministic.

---

## 14. Determinism Rules

Given the same target state, same inputs, and same command invocation, `new-project` MUST produce:

- the same classification
- the same scaffold plan
- the same validation result
- the same exit code

No hidden fallback behavior or undocumented heuristics are allowed.

---

## 15. Forbidden Implementation Patterns

The following are explicitly forbidden:

- shell scripts as primary scaffold logic
- blind overwrite of existing files
- printing from deep internal functions instead of structured return objects
- mixing CLI parsing with scaffold planning logic
- hardcoded project identities in business logic
- undocumented automatic content generation
- hidden template selection rules
- live secret generation inside `.env.example`

---

## 16. Recommended Python Function Mapping Guidance

Recommended naming pattern:

- `normalize_project_slug()`
- `validate_project_inputs()`
- `inspect_target_state()`
- `classify_target_state()`
- `build_scaffold_plan()`
- `render_project_metadata()`
- `render_readme()`
- `render_env_example()`
- `materialize_scaffold()`
- `validate_scaffold()`

Each function SHOULD:

- have one clear responsibility
- avoid hidden side effects
- return structured results where meaningful
- remain testable in isolation

---

## 17. Final Statement

This specification defines the current executable baseline for `new-project`.

It exists to ensure that PROJECT scaffold behavior is:

- explicit
- deterministic
- safe to re-run
- validation-driven
- aligned with framework architecture and engineering rules

Deviation is not allowed without documentation-first review.
