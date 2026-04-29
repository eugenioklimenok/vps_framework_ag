# OPERATE BASELINE CONTRACT


> **Canonical extension note — OPERATE Slice 01 Backup/Audit Precision**
>
> This document has been extended additively to incorporate `OPERATE_SLICE_01_BACKUP_AUDIT_PRECISION_ADDENDUM.md`.
> No previously approved baseline content is removed, compressed, weakened, or replaced by this merge.
> The extension clarifies executable precision for `backup-project` output directory handling, artifact validation, source non-mutation, and `audit-project` non-mutating runtime boundaries.
> Default documentation mode remains **EXTEND, never COMPRESS**.


## 1. Purpose

This document defines the **current executable contract** of the OPERATE module baseline.

It establishes:

- what the current OPERATE baseline guarantees
- how a project is evaluated for operational audit or backup
- which actions are currently allowed
- which actions are currently forbidden
- how success is determined

This contract is the executable bridge between OPERATE design documents and implementation.

---

## 2. Role in Documentation Hierarchy

This contract is governed by:

- `FRAMEWORK_ARCHITECTURE_MODEL.md`
- `ENGINEERING_RULES.md`
- `OPERATE_BASELINE_FDD.md`
- `OPERATE_BASELINE_TDD.md`

This contract governs, at the executable level:

- `audit-project`
- `backup-project`
- `AUDIT_PROJECT_SPEC.md`
- `BACKUP_PROJECT_SPEC.md`

If this contract conflicts with the OPERATE FDD or OPERATE TDD, this contract MUST be corrected.

---

## 3. Core Principle

The OPERATE module does NOT assume a trustworthy project context by default.

The default case is a:

→ **real project path on a real deployed environment**

All behavior must be based on:

- explicit input validation
- real project inspection
- deterministic command-specific evaluation
- bounded execution scope
- runtime or artifact validation
- no cosmetic success reporting

No step is considered successful unless it is validated.

---

## 4. Engineering Alignment

### 4.1 Implementation Language

All OPERATE logic MUST be implemented in:

→ **Python**

This includes:

- project inspection
- audit logic
- classification logic
- backup scope planning
- archive creation
- checksum handling
- validation logic

### 4.2 Runtime and Filesystem Interaction Model

OPERATE interaction MUST be performed through:

→ **Python-controlled subprocess execution for runtime checks**  
→ **Python-native filesystem operations for backup work**

Preferred primitives include:

- centralized subprocess wrapper
- structured command results
- `pathlib`
- controlled archive creation
- controlled hashing helpers

### 4.3 Shell Policy

Shell is NOT an implementation language for OPERATE.

Forbidden:

- `.sh` scripts containing audit or backup decision logic
- shell glue used as the primary operational orchestrator instead of Python-controlled logic

### 4.4 Determinism Rule

Given the same inputs and the same project/runtime state:

→ OPERATE decisions and outcomes MUST be identical

---

## 5. Current Scope of This Contract

This contract describes the **current executable OPERATE baseline**, not the full future operational vision.

### Current executable focus

At this stage, the enforceable OPERATE baseline consists of:

- explicit audit input validation
- explicit backup input validation
- project identity validation
- runtime audit classification
- bounded backup artifact creation
- artifact and result validation

### Non-goal of this contract

This contract does NOT claim that restore, retention pruning, remote sync, remediation, or alerting are already implemented.

Future OPERATE slices may expand the contract, but only through explicit documentation updates.

---

## 6. Explicit Inputs

The current OPERATE contract depends on explicit inputs.

### For `audit-project`

- project path
- optional explicit endpoint or bounded audit target input

### For `backup-project`

- project path
- output directory
- optional explicit inclusion flags documented by the current baseline

### Rule

A hidden audit target or hidden backup scope is NOT part of the intended contract baseline.

Implementation MUST NOT silently assume a specific project path, output location, endpoint, or inclusion scope unless a bounded contract explicitly states it.

---

## 7. Project Identity Policy

Both OPERATE commands depend on trustworthy project identity.

### Minimum identity requirement

`project.yaml` MUST be treated as authoritative project metadata for the current baseline.

### The commands MUST block when:

- `project.yaml` is missing
- metadata is malformed
- metadata is insufficient to prove project identity
- the path appears project-like but identity cannot be trusted

No audit or backup result may be trusted without project identity validation.

---

## 8. `audit-project` Contract

### Definition

`audit-project` performs **deterministic project runtime audit**.

### Allowed classifications

- `HEALTHY`
- `DEGRADED`
- `BLOCKED`

### Guarantees

It MUST:

- validate explicit inputs
- inspect the real project path state
- validate project identity
- execute baseline audit checks
- classify results deterministically
- avoid source or runtime mutation in the normal audit path
- produce structured results sufficient for deterministic output

### Classification rule

- `HEALTHY` requires all required baseline checks to pass
- `DEGRADED` requires a trustworthy audit with one or more degraded health outcomes
- `BLOCKED` requires ambiguous, unsafe, or insufficient audit evidence

### Output model

The command result MUST make clear at minimum:

- project identity summary
- audit classification
- executed check outcomes
- degraded findings if any
- blocked reason when applicable

---

## 9. `backup-project` Contract

### Definition

`backup-project` performs **bounded project backup creation**.

### Guarantees

It MUST:

- validate explicit inputs
- inspect the real project path state
- validate project identity
- create a bounded backup artifact from documented sources only
- validate the artifact after creation
- avoid source mutation
- produce structured results sufficient for deterministic output

### Current minimum backup scope

The current executable backup baseline MUST at minimum support:

- project root backup into an output directory

### Optional explicit additions

The current baseline MAY support explicitly requested env-file inclusion only when:

- it is documented
- it is explicitly requested
- scope remains bounded and trusted

### Output model

The command result MUST make clear at minimum:

- project identity summary
- artifact path
- artifact validation result
- checksum path when produced
- blocked or failure reason when applicable

---

## 10. Mutation Policy

### `audit-project`

Allowed behavior:

- inspect project files
- inspect runtime state
- execute bounded endpoint checks when explicitly requested

Forbidden behavior:

- deploy or restart services
- repair runtime failures
- mutate project files
- mutate runtime state as ordinary audit behavior

### `backup-project`

Allowed behavior:

- read project files
- create archive artifacts in the output directory
- create checksum sidecar files where implemented

Forbidden behavior:

- source deletion
- source mutation
- arbitrary host-path inclusion
- restore execution
- retention pruning outside documented scope

---

## 11. Validation Contract

Every critical in-scope step MUST be validated.

### For `audit-project`, validation MUST confirm:

- project identity is trustworthy
- audit checks executed successfully
- final classification matches documented reduction rules

### For `backup-project`, validation MUST confirm:

- artifact exists
- artifact is non-empty
- artifact path matches the bounded plan
- checksum generation or equivalent validation passed where implemented

### Failure Rule

If any required in-scope validation fails:

→ the current operation is **FAILED** or **BLOCKED** according to command rules

Success reporting without effective validation is forbidden.

---

## 12. Environment and Platform Contract

OPERATE is a runtime inspection and project protection domain.

The authoritative target environment is:

- a real deployed project context on a usable host

### Platform rule

The contract is satisfied by deterministic Python-controlled audit and backup execution, not by shell-specific orchestration.

### Host responsibility boundary

If runtime prerequisites required for audit are absent or unusable:

→ `audit-project` MUST classify accordingly, typically as `BLOCKED`

It MUST NOT repair HOST or DEPLOY responsibilities within the current baseline.

---

## 13. Re-Run Behavior

### `audit-project`

Must be safe to re-run and non-destructive.

### `backup-project`

Is not idempotent in artifact count because each successful run may create a new artifact.

However, it MUST remain deterministic in:

- source validation
- inclusion scope
- output naming policy
- artifact validation rules
- non-destructive behavior

---

## 14. Abort Rules

Execution MUST stop if:

- required inputs are invalid
- project identity is ambiguous
- command-specific prerequisites are missing
- audit evidence is insufficient for trustworthy classification
- backup scope cannot be validated safely
- archive creation fails
- artifact validation fails
- runtime execution failure prevents trustworthy completion

---

## 15. Success Criteria

The current OPERATE baseline is valid only if:

### For `audit-project`

- classification is resolved deterministically
- classification is evidence-based
- no hidden mutation occurred

### For `backup-project`

- bounded source scope was honored
- artifact was created successfully
- artifact validation passed
- source project data was not modified

---

## 16. Forbidden Behavior

Forbidden:

- implicit project path assumptions
- hidden audit targets
- hidden backup scope expansion
- undocumented mutation
- host or deploy repair from OPERATE
- reporting success without runtime or artifact verification
- shell-driven operational logic
- non-deterministic artifact handling

---

## 17. Evolution Rule

This contract MAY expand in future documented OPERATE slices.

However:

- new obligations must be documented first
- future-slice requirements MUST NOT be retroactively treated as already implemented
- lower-level specs must remain aligned with this contract

---

## 18. Final Statement

The current OPERATE contract defines a:

- Python-based
- deterministic
- runtime-aware
- artifact-validating
- baseline-bounded

foundation for OPERATE execution.

It is mandatory for the current stage and must remain aligned with the OPERATE FDD and OPERATE TDD.

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

