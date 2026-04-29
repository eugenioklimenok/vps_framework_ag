# AUDIT PROJECT SPECIFICATION


> **Canonical extension note — OPERATE Slice 01 Backup/Audit Precision**
>
> This document has been extended additively to incorporate `OPERATE_SLICE_01_BACKUP_AUDIT_PRECISION_ADDENDUM.md`.
> No previously approved baseline content is removed, compressed, weakened, or replaced by this merge.
> The extension clarifies executable precision for `backup-project` output directory handling, artifact validation, source non-mutation, and `audit-project` non-mutating runtime boundaries.
> Default documentation mode remains **EXTEND, never COMPRESS**.


## 1. Purpose

This document defines the **current executable technical specification** for the `audit-project` command.

Its purpose is to make the current OPERATE audit baseline precise, deterministic, and Codex-consumable.

It defines:

- command intent
- explicit inputs
- check model
- classification rules
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

`audit-project`

### Domain ownership

OPERATE

### Command purpose

Audit the current project runtime state and classify the result deterministically.

### Command type

Non-mutating diagnostic command under ordinary execution.

---

## 4. Explicit Inputs

The current baseline requires explicit audit inputs.

### Required inputs

- `--path`
  - project root path to audit

### Optional inputs

- `--endpoint-url`
  - optional explicit endpoint to verify as part of the baseline audit

- `--endpoint-timeout`
  - optional bounded timeout for endpoint verification

### Input rule

No hidden audit target sources are allowed for required project identity.

If optional endpoint checks are used, they must come from explicit input or future documented configuration.

---

## 5. Project Identity Requirements

The current baseline requires the project root to contain at minimum:

- `project.yaml`

For runtime-aware audit contexts, the project root is also expected to contain:

- `compose.yaml`

### Identity rule

The implementation MUST resolve project identity from trusted metadata before reporting project health.

If `project.yaml` is missing, malformed, or insufficient:

→ audit MUST classify as `BLOCKED`

---

## 6. Audit Check Model

Each audit check MUST be represented in Python as an explicit object or structure containing at minimum:

- `check_id`
- `description`
- `severity`
- `classification_impact`
- `execution_function`
- `pass_condition`
- `failure_message`

### Required modeling rule

Checks MUST NOT be embedded as scattered ad-hoc conditionals without explicit structure.

### Check impact model

Allowed impact values:

- `NONE`
- `DEGRADED`
- `BLOCKED`

---

## 7. Classification Logic

Final project classification MUST be derived after all checks complete.

### Allowed final classifications

- `HEALTHY`
- `DEGRADED`
- `BLOCKED`

### Classification intent in current baseline

The current audit baseline is designed to determine whether the project runtime is operationally healthy enough to trust as currently running.

### Rules

#### BLOCKED

Use when any critical condition makes the audit unsafe, ambiguous, or untrustworthy.

Typical causes:

- invalid project root
- missing or malformed `project.yaml`
- runtime audit context unavailable
- runtime inspection cannot be trusted
- audit execution error prevents classification

#### DEGRADED

Use when the audit is trustworthy, but one or more health checks fail.

Typical causes:

- required service not running
- service in failed/exited state
- optional explicit endpoint check fails

#### HEALTHY

Use when all required baseline checks pass and no blocked or degraded outcome applies.

### Priority rule

`BLOCKED > DEGRADED > HEALTHY`

---

## 8. Current Baseline Audit Scope

The current executable audit baseline is intentionally limited to the checks needed for trustworthy project runtime health classification at the current stage.

### In-scope check families

- project identity checks
- deploy-context presence checks
- runtime availability checks
- runtime state checks
- optional explicit endpoint verification

### Out-of-scope check families unless later documentation brings them into scope

- performance benchmarking
- log-volume analytics
- deep application introspection
- security scanning
- backup freshness validation
- cross-host fleet audit
- automatic remediation

---

## 9. Current Baseline Checks

### CHECK_PROJECT_01 — Project Root Validity

Confirm that the provided project path exists and is a project root.

**PASS**

- path exists
- path is a directory
- required project identity file exists

**FAIL**

- invalid path
- non-directory path
- missing `project.yaml`

**Impact**

- `BLOCKED`

---

### CHECK_PROJECT_02 — Project Metadata Validity

Confirm that `project.yaml` is parseable enough to prove project identity.

**PASS**

- file exists
- metadata is parseable
- required identity fields exist

**FAIL**

- malformed metadata
- insufficient metadata
- ambiguous identity

**Impact**

- `BLOCKED`

---

### CHECK_DEPLOY_01 — Compose Context Presence

Confirm that the project has a baseline deploy context for runtime-oriented audit.

**PASS**

- `compose.yaml` exists

**FAIL**

- `compose.yaml` missing

**Impact**

- `BLOCKED`

---

### CHECK_RUNTIME_01 — Runtime Availability

Confirm that the documented runtime inspection mechanism is available.

**PASS**

- runtime command exists
- runtime wrapper can execute inspection commands

**FAIL**

- runtime command missing
- runtime command unusable

**Impact**

- `BLOCKED`

---

### CHECK_RUNTIME_02 — Runtime State Inspectability

Confirm that runtime state for the project identity can be inspected.

**PASS**

- runtime inspection for the project identity succeeds

**FAIL**

- runtime output unavailable
- runtime state ambiguous
- identity cannot be associated with runtime context

**Impact**

- `BLOCKED`

---

### CHECK_HEALTH_01 — Required Service State

Confirm that baseline runtime services are in an acceptable running state.

**PASS**

- required services are running or otherwise acceptable by the current baseline

**FAIL**

- one or more required services are not running

**Impact**

- `DEGRADED`

---

### CHECK_HEALTH_02 — Failed/Exited State Presence

Confirm that the runtime does not report clearly failed or exited services for the project context.

**PASS**

- no failed/exited service states detected

**FAIL**

- failed or exited state detected

**Impact**

- `DEGRADED`

---

### CHECK_ENDPOINT_01 — Optional Explicit Endpoint Verification

Run only when `--endpoint-url` is provided.

**PASS**

- endpoint responds successfully within the bounded timeout under the documented baseline

**FAIL**

- timeout
- connection error
- non-success response according to the current bounded endpoint policy

**Impact**

- `DEGRADED`

---

## 10. Execution Phases

The current baseline implementation should follow these phases.

### Phase 1 — Input Validation

- validate `--path`
- validate optional endpoint inputs

### Phase 2 — Project Inspection

- inspect project root
- inspect `project.yaml`
- inspect `compose.yaml`
- resolve trusted project identity

### Phase 3 — Check Execution

- execute check families in deterministic order
- collect structured results

### Phase 4 — Classification Reduction

- reduce all check outcomes into one final classification:
  - `HEALTHY`
  - `DEGRADED`
  - `BLOCKED`

### Phase 5 — Final Validation

Confirm that:

- required checks executed
- final classification is consistent with check impacts
- blocked reasons are preserved where applicable

### Phase 6 — Final Result Rendering

Render deterministic human-readable output based on structured state.

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
- executed checks
- classification summary
- degraded findings
- blocked reason if applicable
- final outcome

### Structured result expectations

Recommended result fields include:

- `project_slug`
- `classification`
- `checks`
- `degraded_findings`
- `blocked_reason`
- `validation_passed`

---

## 12. Exit Code Rules

Recommended deterministic exit codes:

- `0` → audit completed and classification is `HEALTHY`
- `1` → audit completed and classification is `DEGRADED`
- `2` → audit completed but classification is `BLOCKED`
- `3` → invalid inputs or runtime execution failure in the audit command itself

This mapping MUST remain deterministic.

---

## 13. Determinism Rules

Given the same project state, runtime state, inputs, and command invocation, `audit-project` MUST produce:

- the same executed checks
- the same classification
- the same blocked reason when applicable
- the same exit code

No hidden fallback behavior or undocumented heuristics are allowed.

---

## 14. Forbidden Implementation Patterns

The following are explicitly forbidden:

- shell scripts as primary audit logic
- blind health conclusions without project identity validation
- mixing CLI parsing with audit reduction logic
- hidden endpoint defaults
- host or deploy repair from the audit command
- success reporting based only on command invocation success without check reduction

---

## 15. Recommended Python Function Mapping Guidance

Recommended naming pattern:

- `validate_audit_inputs()`
- `inspect_project_root()`
- `load_project_metadata()`
- `build_audit_checks()`
- `run_audit_checks()`
- `reduce_audit_classification()`
- `validate_audit_result()`

Each function SHOULD:

- have one clear responsibility
- avoid hidden side effects
- return structured results where meaningful
- remain testable in isolation

---

## 16. Final Statement

This specification defines the current executable baseline for `audit-project`.

It exists to ensure that project audit behavior is:

- explicit
- deterministic
- evidence-based
- safe to re-run
- aligned with framework architecture and engineering rules

Deviation is not allowed without documentation-first review.

---

## Appendix — OPERATE Slice 01 Backup/Audit Precision

This appendix integrates `OPERATE_SLICE_01_BACKUP_AUDIT_PRECISION_ADDENDUM.md` into this canonical OPERATE document as an additive extension. It does not remove, replace, compress, or weaken any previously approved baseline content.

### Canonical Precision Rules

The current OPERATE Slice 01 baseline is extended with these executable documentation rules:

1. `backup-project --path` and `backup-project --output-dir` MUST be explicit inputs. Neither path may be inferred from current working directory, environment variables, hidden config, shell history, or conventional paths.
2. `--path` and `--output-dir` MUST be resolved to absolute canonical paths before backup planning begins.
3. For OPERATE Slice 01, the resolved backup output directory MUST NOT be equal to, inside, or symlink-resolved inside the resolved project root. Unsafe or ambiguous placement MUST block.
4. `backup-project` MAY create a missing output directory only when the parent exists, is writable, is safe, the resulting directory is outside the project root, and the created directory is revalidated before archive creation.
5. `backup-project` MUST construct a structured backup plan before archive creation. Archive creation and artifact validation MUST execute against that plan.
6. `backup-project` MUST NOT report `CREATED` merely because archive creation was attempted. It may report `CREATED` only after artifact validation succeeds.
7. Artifact validation MUST confirm existence, regular-file status, non-empty size, placement under resolved output directory, path match with backup plan, archive readability, expected planned content, no output directory self-inclusion, no artifact self-inclusion, and checksum validity where checksum generation is implemented.
8. `backup-project` MUST NOT mutate source project files. Allowed writes are limited to the archive artifact, checksum sidecar where implemented, and safe output directory creation.
9. `audit-project` remains non-mutating. It MUST NOT deploy, redeploy, start services, restart services, run `docker compose up`, run migrations, repair Docker, create missing project files, mutate runtime state, or mutate project files.
10. `audit-project` MUST preserve the distinction between untrustworthy evidence and failed health: insufficient or untrustworthy evidence classifies as `BLOCKED`; trustworthy failed health classifies as `DEGRADED`; all required checks passing may classify as `HEALTHY`.
11. OPERATE MUST NOT absorb HOST, PROJECT, or DEPLOY responsibilities. HOST owns host preparation and Docker runtime availability. PROJECT owns scaffold and identity creation. DEPLOY owns deployment-time mutation and application lifecycle.

### Output Directory Classification

The backup implementation MUST classify output directory state as one of:

- `EXISTS_WRITABLE`
- `MISSING_CREATABLE`
- `INVALID`
- `UNSAFE`
- `AMBIGUOUS`

Only `EXISTS_WRITABLE` and safely revalidated `MISSING_CREATABLE` may proceed. `INVALID`, `UNSAFE`, and `AMBIGUOUS` MUST block.

### Source Scope Rule

The backup source scope remains bounded. The command may include only the project root and one explicit env file when env-file inclusion is explicitly requested and valid under canonical policy. It MUST NOT include arbitrary external paths, implicit database paths, Docker volumes, hidden secret locations, host-level config files, output directory content, generated artifacts, or checksum sidecars from the current run.

### Required Tests

Implementation work for this extension SHOULD include tests proving missing inputs block, unsafe output directory placement blocks, symlink ambiguity blocks, safe output directory creation is revalidated, artifacts are validated before success, checksum mismatch fails where implemented, source project files are not mutated, audit remains non-mutating, and audit distinguishes `BLOCKED` from `DEGRADED`.

### Canonical Addendum Reference

The full design record for this extension is retained in `OPERATE_SLICE_01_BACKUP_AUDIT_PRECISION_ADDENDUM.md`.

