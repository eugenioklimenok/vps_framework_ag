# BACKUP PROJECT SPECIFICATION

## 1. Purpose

This document defines the **current executable technical specification** for the `backup-project` command.

Its purpose is to make the current OPERATE backup baseline precise, deterministic, and Codex-consumable.

It defines:

- command intent
- explicit inputs
- backup scope rules
- archive and validation requirements
- execution phases
- output expectations
- exit code behavior
- forbidden implementation patterns

---

## 2. Governing Documents

This specification is governed by:

1. `FRAMEWORK_ARCHITECTURE_MODEL.md`
2. `ENGINEERING_RULES.md`
3. `OPERATE_BASELINE_FDD.md`
4. `OPERATE_BASELINE_TDD.md`
5. `OPERATE_BASELINE_CONTRACT.md`
6. `PYTHON_IMPLEMENTATION_BASELINE.md`
7. `CODEX_DEVELOPMENT_PROTOCOL.md`

If this specification conflicts with a higher-precedence OPERATE document, the higher-precedence document wins and this specification MUST be corrected.

---

## 3. Command Definition

### Command name

`backup-project`

### Domain ownership

OPERATE

### Command purpose

Create a bounded backup artifact for a validated project.

### Command type

Mutation-capable artifact creation command.

---

## 4. Explicit Inputs

The current baseline requires explicit backup inputs.

### Required inputs

- `--path`
  - project root path to back up

- `--output-dir`
  - directory where backup artifacts will be created

### Optional inputs

- `--include-env-file`
  - bounded flag allowing explicit inclusion of an env file when documented by the current baseline

- `--env-file`
  - explicit env file path used only when `--include-env-file` is set

### Input rule

No hidden backup scope sources are allowed.

The command MUST NOT silently discover arbitrary additional host paths.

---

## 5. Project Identity Requirements

The current baseline requires the project root to contain at minimum:

- `project.yaml`

### Identity rule

The implementation MUST resolve project identity from trusted metadata before creating the backup artifact.

If `project.yaml` is missing, malformed, or insufficient:

→ backup MUST block

---

## 6. Backup Scope Rules

The current backup baseline is intentionally bounded.

### Required source scope

- project root directory

### Optional explicit source scope

- env file only when:
  - `--include-env-file` is set
  - `--env-file` is provided
  - the path is trusted by current policy

### Forbidden source scope

- arbitrary external host paths
- implicit database paths
- automatic runtime volume discovery
- hidden inclusion of secret files

### Scope rule

Every included source must be explainable by explicit input or fixed baseline scope.

---

## 7. Output Artifact Model

The current baseline SHOULD produce:

- one archive artifact
- one checksum sidecar file where implemented

### Archive format

The baseline SHOULD use a deterministic archive format suitable for the authoritative runtime environment, such as:

- `.tar.gz`

### Naming rule

The archive name SHOULD be derived from trusted project identity plus a documented uniqueness suffix.

Recommended pattern:

`<project_slug>__backup__<UTC timestamp>.tar.gz`

### Checksum rule

When implemented, the checksum sidecar SHOULD use a stable algorithm such as SHA-256 and map directly to the artifact created.

---

## 8. Pre-Execution Checks

At minimum, the current implementation must evaluate the following pre-execution checks.

### CHECK_INPUT_01 — Project Path Validity

Confirm that the provided project path is non-empty and resolves safely.

**FAIL**

- missing project path
- invalid path resolution
- inaccessible project root

**Impact**

- invalid input or `BLOCKED`

---

### CHECK_INPUT_02 — Output Directory Validity

Confirm that the output directory exists or is safely creatable.

**FAIL**

- missing output directory input
- output location invalid
- output directory cannot be created or written safely

**Impact**

- invalid input or `BLOCKED`

---

### CHECK_PROJECT_01 — Project Identity Validity

Confirm that the project root contains trustworthy identity metadata.

**PASS**

- `project.yaml` exists
- metadata is parseable
- required identity fields exist

**FAIL**

- missing metadata
- malformed metadata
- ambiguous identity

**Impact**

- `BLOCKED`

---

### CHECK_SCOPE_01 — Backup Scope Validity

Confirm that all requested source paths are allowed by the current baseline.

**PASS**

- project root is valid
- optional explicit env-file inclusion is valid if requested

**FAIL**

- env-file inclusion requested without explicit env-file path
- optional scope path invalid by current policy
- hidden or arbitrary path inclusion attempted

**Impact**

- `BLOCKED`

---

## 9. Execution Phases

The current baseline implementation should follow these phases.

### Phase 1 — Input Validation

- validate `--path`
- validate `--output-dir`
- validate optional env-file inclusion inputs

### Phase 2 — Project Inspection

- inspect project root
- inspect `project.yaml`
- resolve trusted project identity

### Phase 3 — Backup Scope Planning

- build the bounded source list
- build the artifact naming plan
- build the checksum plan where implemented

### Phase 4 — Archive Creation

- create the archive artifact in the output directory
- preserve source data

### Phase 5 — Artifact Validation

Confirm that:

- artifact exists
- artifact is non-empty
- artifact path matches the backup plan
- checksum exists and matches when implemented

### Phase 6 — Final Result Rendering

Render deterministic human-readable output based on structured state.

---

## 10. Result States

Recommended result states include:

- `CREATED`
- `BLOCKED`
- `FAILED`

### CREATED

Artifact creation and validation succeeded.

### BLOCKED

Safe backup could not proceed because inputs, identity, or scope were ambiguous or invalid.

### FAILED

Backup execution began but artifact creation or validation did not complete successfully.

---

## 11. Output Expectations

The command SHOULD expose:

1. human-readable output
2. structured internal result data
3. future-ready export capability where relevant

### Minimum human-readable output sections

Recommended sections include:

- input summary
- project identity summary
- backup scope summary
- artifact path
- checksum path when produced
- artifact validation result
- final outcome

### Structured result expectations

Recommended result fields include:

- `project_slug`
- `result_state`
- `artifact_path`
- `checksum_path`
- `artifact_validated`
- `blocked_reason`

---

## 12. Exit Code Rules

Recommended deterministic exit codes:

- `0` → backup artifact created successfully and validation passed
- `2` → blocked/unsafe/ambiguous state or failed artifact validation
- `3` → invalid inputs or command runtime execution failure

This mapping MUST remain deterministic.

---

## 13. Determinism Rules

Given the same project state, input scope, naming policy, and command invocation time semantics, `backup-project` MUST produce:

- the same validated source scope
- the same artifact naming pattern
- the same validation rules
- the same exit code class for the same success or failure condition

The artifact name itself may differ across successful runs due to the documented uniqueness suffix.

---

## 14. Forbidden Implementation Patterns

The following are explicitly forbidden:

- shell scripts as primary backup logic
- hidden source discovery
- arbitrary host-path inclusion
- source mutation during backup
- restore behavior inside backup execution
- success reporting based only on archive command completion without artifact validation

---

## 15. Recommended Python Function Mapping Guidance

Recommended naming pattern:

- `validate_backup_inputs()`
- `inspect_project_root()`
- `load_project_metadata()`
- `build_backup_plan()`
- `create_backup_archive()`
- `create_backup_checksum()`
- `validate_backup_artifact()`

Each function SHOULD:

- have one clear responsibility
- avoid hidden side effects
- return structured results where meaningful
- remain testable in isolation

---

## 16. Final Statement

This specification defines the current executable baseline for `backup-project`.

It exists to ensure that project backup behavior is:

- explicit
- deterministic in scope
- bounded
- non-destructive
- artifact-validating
- aligned with framework architecture and engineering rules

Deviation is not allowed without documentation-first review.
