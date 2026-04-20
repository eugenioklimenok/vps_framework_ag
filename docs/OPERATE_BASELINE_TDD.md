# OPERATE Baseline — Technical Design Document (TDD)

## 1. Purpose

This document defines the **technical architecture** of the OPERATE module.

It describes:

- how OPERATE is implemented in Python
- how `audit-project` and `backup-project` are separated technically
- how shared components are reused
- how project inspection, runtime audit, backup planning, archive creation, and validation fit together
- how the current operate baseline supports future automation without mixing responsibilities

This document is prescriptive and must be used as technical implementation guidance together with the architecture model, engineering rules, OPERATE FDD, OPERATE contract, the command specs, and the shared Python baseline.

---

## 2. Role in Documentation Hierarchy

For OPERATE work, this document defines the **technical source of truth** below the FDD.

It is governed by:

- `FRAMEWORK_ARCHITECTURE_MODEL.md`
- `ENGINEERING_RULES.md`
- `OPERATE_BASELINE_FDD.md`

It governs, technically, the lower-level OPERATE documents:

- `OPERATE_BASELINE_CONTRACT.md`
- `AUDIT_PROJECT_SPEC.md`
- `BACKUP_PROJECT_SPEC.md`

If a lower-level OPERATE document contradicts this TDD, the lower-level document MUST be corrected.

---

## 3. Technical Design Goals

The OPERATE module technical design MUST provide:

- deterministic behavior
- Python-only implementation
- modular command boundaries
- explicit project identity inspection
- explicit runtime audit modeling
- explicit backup scope planning
- artifact validation
- high testability
- Codex-compatible structure
- Linux-authoritative real-runtime behavior with development-safe abstractions

OPERATE is ongoing project runtime inspection and bounded backup logic, not host bootstrap and not deployment logic.

---

## 4. Technical Scope of OPERATE

OPERATE is implemented as a Python module containing two command families:

- `audit-project`
- `backup-project`

Technically, OPERATE must support:

- input normalization and validation
- project root inspection
- project metadata loading
- audit check execution
- audit classification reduction
- backup plan construction
- archive creation
- artifact validation
- command-level exit code control

OPERATE must not contain responsibilities belonging to HOST, PROJECT, or DEPLOY.

---

## 5. Repository Architecture

The OPERATE implementation is expected to follow the framework repository model:

```text
framework/
├── cli/
├── modules/
│   └── operate/
│       ├── audit/
│       ├── backup/
│       └── runtime/
├── models/
├── utils/
├── config/
└── tests/
```

### OPERATE command separation

- `framework/modules/operate/audit/` contains `audit-project` inspection, check execution, classification, and validation logic
- `framework/modules/operate/backup/` contains `backup-project` scope planning, archive creation, and artifact validation logic
- `framework/modules/operate/runtime/` contains runtime wrappers and shared operational inspection helpers for the current documented baseline

### Shared technical layers

- `framework/cli/` exposes Typer entrypoints
- `framework/models/` contains shared result and classification models
- `framework/utils/` contains subprocess, filesystem, hashing, and helper abstractions
- `framework/config/` contains explicit operate input and policy loading helpers where needed
- `tests/` contains isolated unit and integration-oriented tests

### Structure Rule

A generic `framework/core/` layer is not part of the canonical OPERATE baseline.
Shared functionality should live in explicitly owned technical layers.

---

## 6. Core Technical Components

### CLI Layer

Responsibilities:

- expose `audit-project`
- expose `backup-project`
- parse explicit inputs
- delegate to the OPERATE runners
- translate runner outcomes into deterministic exit codes

### Shared Models

Responsibilities:

- represent audit classifications
- represent backup results
- represent check outcomes
- represent artifact validation outcomes
- avoid scattered string literals for status or classification

### Project Inspector

Responsibilities:

- inspect the requested project root
- validate presence of required scaffold files
- extract trusted project identity metadata from `project.yaml`
- detect ambiguous or blocked project state

### Runtime Wrapper

Responsibilities:

- centralize runtime inspection commands
- capture stdout, stderr, and return code
- support timeout handling
- remain the only system interaction path for runtime-aware audit checks

### Audit Check Engine

Responsibilities:

- define explicit audit checks as data-driven units
- execute check families in deterministic order
- record PASS / FAIL / WARN style outcomes where documented
- attach classification impact to each check
- reduce checks into a final audit classification

### Backup Planner

Responsibilities:

- validate and normalize backup scope
- construct a bounded backup plan
- prevent hidden scope expansion
- identify artifact output paths

### Archive Builder

Responsibilities:

- create the backup archive
- apply deterministic inclusion rules
- preserve source data
- optionally create checksum outputs

### Validator

Responsibilities:

- validate final audit outcomes
- validate backup artifact existence, size, and readability
- confirm checksum generation where implemented
- fail closed when guarantees cannot be confirmed

### OPERATE Runners

Responsibilities:

- orchestrate inspect → execute → validate flow for each command
- stop on blocked conditions
- produce deterministic phase output
- emit result state and exit code decisions

---

## 7. Command Architecture

## 7.1 `audit-project`

`audit-project` is implemented as a deterministic project runtime audit pipeline.

### Technical responsibilities

- validate and normalize inputs
- inspect project identity
- execute audit checks
- classify audit outcomes
- emit deterministic output and exit codes

### Architectural constraints

- no runtime mutation in the normal audit path
- no project or host repair
- no health conclusion without sufficient evidence
- no hidden audit target assumptions

---

## 7.2 `backup-project`

`backup-project` is implemented as a deterministic bounded backup pipeline.

### Technical responsibilities

- validate and normalize inputs
- inspect project identity
- build a backup scope plan
- create archive artifacts
- validate artifacts
- emit deterministic output and exit codes

### Architectural constraints

- no hidden source expansion
- no source mutation
- no restore logic
- no success reporting without artifact validation

---

## 8. Technical Execution Flow

## 8.1 Current `audit-project` Flow

1. CLI invocation
2. explicit input validation
3. input normalization
4. project root inspection
5. audit prerequisite validation
6. audit check execution
7. classification reduction
8. final validation
9. final decision rendering
10. exit code emission

## 8.2 Current `backup-project` Flow

1. CLI invocation
2. explicit input validation
3. input normalization
4. project root inspection
5. backup scope validation
6. backup plan generation
7. archive creation
8. artifact validation
9. final decision rendering
10. exit code emission

---

## 9. Current `audit-project` Baseline Architecture

### Recommended module boundaries

- `inspect_project.py`
  - project path checks
  - scaffold file checks
  - metadata extraction from `project.yaml`
  - ambiguity detection

- `checks.py`
  - audit check definitions
  - classification impact definitions
  - ordered check registry

- `runtime_checks.py`
  - runtime availability checks
  - runtime status checks
  - optional endpoint audit checks

- `reduce.py`
  - final classification reduction
  - output summary building

- `validate.py`
  - final audit validation
  - check consistency validation

- `runner.py`
  - orchestration of inspect → checks → reduce → validate flow
  - deterministic output sections
  - exit code decisions

### Current baseline technical boundaries

Allowed behavior in the current baseline:

- inspect project metadata
- inspect runtime state
- run endpoint checks when explicitly requested
- classify health

Forbidden behavior in the current baseline:

- deploy or restart services
- repair runtime failures
- modify host settings
- mutate project files
- mutate runtime state as part of ordinary audit execution

---

## 10. Current `backup-project` Baseline Architecture

### Recommended module boundaries

- `inspect_project.py`
  - project identity checks
  - project root validation

- `plan.py`
  - bounded scope generation
  - archive target resolution
  - output naming

- `archive.py`
  - archive creation
  - explicit inclusion handling
  - source-preserving behavior

- `checksum.py`
  - checksum generation where implemented
  - artifact verification helpers

- `validate.py`
  - artifact existence validation
  - non-empty artifact validation
  - checksum validation where implemented

- `runner.py`
  - orchestration of inspect → plan → archive → validate flow
  - deterministic output sections
  - exit code decisions

### Current baseline technical boundaries

Allowed behavior in the current baseline:

- archive project root
- include explicitly allowed inputs
- create backup artifacts in the output directory
- create checksum sidecar files where implemented

Forbidden behavior in the current baseline:

- source deletion
- source mutation
- hidden host-path inclusion
- restore execution
- external sync mutation
- retention pruning outside documented scope

---

## 11. Input and Configuration Model

The current OPERATE technical design requires explicit inputs.

At minimum, the relevant technical inputs for the current baseline are:

### For `audit-project`

- project path
- optional explicit endpoint or smoke-style audit input

### For `backup-project`

- project path
- output directory
- optional explicit include flags documented by contract

### Rule

These values must be obtained through explicit command inputs or structured configuration.
They must not be embedded as hidden constants in business logic.

---

## 12. Data and State Modeling

Audit and backup flows should use explicit result objects.

### Recommended modeling categories

#### `AuditClassification`
- `HEALTHY`
- `DEGRADED`
- `BLOCKED`

#### `CheckImpact`
- `NONE`
- `DEGRADED`
- `BLOCKED`

#### `BackupResult`
- `CREATED`
- `BLOCKED`
- `FAILED`

#### `OperateResult`
- actions taken
- classification or result state
- artifact paths
- validation outcome
- fatal block reason where applicable

### Modeling Rule

The technical design should avoid hidden booleans and implicit state transitions.

---

## 13. Determinism and Re-Run Behavior

### Determinism

Given the same inputs and same project/runtime state, OPERATE commands must produce the same decisions, validations, and exit codes.

### Re-Run Behavior for `audit-project`

`audit-project` must be safe to re-run without mutating the project.

### Re-Run Behavior for `backup-project`

`backup-project` is not idempotent in artifact count because each successful run may create a new backup artifact.

However, it MUST remain deterministic in:

- validated source scope
- output naming policy
- artifact validation rules
- non-destructive behavior

---

## 14. Safety and Abort Model

OPERATE technical behavior must fail closed.

Execution must stop when:

- project identity is ambiguous
- project root is invalid
- command-specific prerequisites are missing
- audit evidence is insufficient for trustworthy classification
- backup scope cannot be validated safely
- artifact validation fails
- runtime execution error prevents contract fulfillment

No fallback heuristics are allowed for ambiguous project states.

---

## 15. Cross-Platform Technical Behavior

### Linux

Linux is the authoritative runtime target for real audit and backup execution on deployed projects.

### Windows and macOS

Windows and macOS are supported development and test environments only for isolated code and mocked runner logic.

Technical implications:

- runtime command execution must be abstracted through the runtime wrapper
- filesystem/archive logic must remain unit-testable without requiring a real target host
- local green tests do not replace authoritative runtime and artifact validation on the target environment

---

## 16. Testing Strategy

### Unit Tests

Required for:

- project inspection logic
- audit check evaluation
- classification reduction
- backup scope planning
- archive naming
- checksum generation
- artifact validation
- runner decision logic

### CLI Tests

Required for:

- command entrypoint behavior
- deterministic output sections
- exit code mapping

### Safety Tests

Required for:

- blocked project abort behavior
- malformed metadata blocking
- audit degraded vs blocked classification separation
- hidden-path backup rejection
- artifact validation failure handling
- non-destructive backup behavior

### Cross-platform Tests

Runtime interactions must be mockable so tests pass in Windows and macOS development environments without requiring real Linux mutation.

---

## 17. Known Technical Constraints and Deferred Decisions

The following remain intentionally open or deferred at the current stage:

- restore workflows
- retention policy automation
- external storage upload
- application-aware backup adapters
- fleet-wide audits
- richer policy-driven audit registries
- automated remediation hooks
- recurring scheduler integration
- alert delivery integrations

These may be extended later, but only through documented, contract-aligned updates.

---

## 18. Technical Freeze Statement

The OPERATE technical baseline is frozen as:

- a Python-only OPERATE implementation
- with explicit command separation for `audit-project` and `backup-project`
- with shared runtime inspection, backup planning, archive, checksum, and validation foundations
- with Linux-authoritative real-runtime behavior
- with strong blocking on ambiguous or unsafe state

The freeze applies to architecture and responsibility boundaries.
It does not imply that all future OPERATE slices are already implemented.

---

## 19. Final Statement

The OPERATE module technical design must support safe evolution without ambiguity.

Its architecture therefore requires:

- explicit command boundaries
- explicit project identity inspection
- explicit audit check modeling
- explicit backup scope planning
- explicit artifact validation
- deterministic Python-controlled behavior
- baseline-based growth of operate logic without breaking contracts

All OPERATE implementation must remain aligned with this design.
