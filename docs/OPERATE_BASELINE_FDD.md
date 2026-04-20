# OPERATE Baseline — Functional Design Document (FDD)

## 1. Purpose

This document defines the **functional behavior of the OPERATE module baseline** within the framework.

The OPERATE module is responsible for operational continuity and runtime control after deployment through:

- project runtime audit
- runtime state verification
- bounded project backup execution
- baseline operational validation

This document defines:

- what OPERATE does functionally
- which commands belong to OPERATE
- how OPERATE relates to the other framework domains
- what the current executable baseline includes
- what remains intentionally deferred

This document is prescriptive and must be treated as executable design input for OPERATE implementation.

---

## 2. Role in Documentation Hierarchy

For OPERATE work, this document defines the **functional source of truth**.

It is governed by:

- `FRAMEWORK_ARCHITECTURE_MODEL.md`
- `ENGINEERING_RULES.md`

It governs, functionally, the lower-level OPERATE documents:

- `OPERATE_BASELINE_TDD.md`
- `OPERATE_BASELINE_CONTRACT.md`
- `AUDIT_PROJECT_SPEC.md`
- `BACKUP_PROJECT_SPEC.md`

If a lower-level OPERATE document contradicts this FDD, the lower-level document MUST be corrected.

---

## 3. Functional Scope

OPERATE is the framework domain responsible for operational continuity and bounded runtime control for an already created and already deployable project.

### In Scope

- audit deployed project health
- verify runtime state
- inspect baseline project identity and deploy context
- execute bounded project backups
- validate backup artifacts
- support baseline operational verification after deployment
- remain safe to re-run where applicable

### Out of Scope

- host bootstrap or host repair
- project scaffold creation
- project deployment
- Docker or runtime installation
- infrastructure provisioning
- recurring automation scheduling inside the command implementation
- restore orchestration unless future documented slices add it
- full disaster-recovery workflows
- monitoring stack provisioning
- log shipping systems
- rollback orchestration

---

## 4. Role in Framework Architecture

OPERATE is the fourth domain in the framework lifecycle:

`HOST → PROJECT → DEPLOY → OPERATE`

OPERATE depends on:

- HOST for a usable host baseline
- PROJECT for a valid project scaffold identity
- DEPLOY for a deployed or deploy-aware project context

OPERATE must not assume responsibility for tasks belonging to:

- HOST (host baseline and security)
- PROJECT (project creation and scaffold design)
- DEPLOY (initial deployment and deployment-time mutation)

---

## 5. Supported Commands

The OPERATE module currently contains two functional commands:

### `audit-project`

Project runtime audit command.

Responsibilities:

- validate explicit audit inputs
- inspect project identity and deploy context
- inspect runtime status
- run baseline health checks
- classify project health status
- produce a deterministic audit result

### `backup-project`

Project backup command.

Responsibilities:

- validate explicit backup inputs
- inspect project identity and backup source scope
- create a bounded project backup artifact
- validate the resulting backup artifact
- remain safe and non-destructive

---

## 6. Functional Model

All OPERATE behavior must follow the same mandatory principles:

1. Input Validation
2. Project Inspection
3. Context Validation
4. Execution (if allowed)
5. Runtime or Artifact Validation
6. Deterministic Final Outcome

No OPERATE command may skip required safety checks for its phase.

---

## 7. Functional Behavior of `audit-project`

### Purpose

`audit-project` audits the current runtime and health state of a project.

### Functional Guarantees

`audit-project` MUST:

- require explicit audit inputs
- validate project identity before runtime conclusions are trusted
- inspect runtime state through documented mechanisms
- execute baseline audit checks deterministically
- classify the resulting audit outcome
- avoid mutating project or host state
- remain safe to run repeatedly

### `audit-project` MUST NOT:

- deploy the project
- repair the host or runtime
- guess missing project identity
- report health without sufficient evidence
- mutate runtime state as part of normal audit behavior

### Audit Classification Model

The current baseline defines the following audit result classifications:

- `HEALTHY`
- `DEGRADED`
- `BLOCKED`

#### HEALTHY

The project identity is trustworthy, the runtime is inspectable, and all required baseline health checks pass.

#### DEGRADED

The project identity is trustworthy and the audit completed, but one or more health checks failed without making the audit itself untrustworthy.

#### BLOCKED

The project identity, runtime context, or audit evidence is too ambiguous or unsafe to support a trustworthy audit result.

### Classification Priority

If multiple conditions are present, classification priority MUST be:

`BLOCKED > DEGRADED > HEALTHY`

---

## 8. Functional Behavior of `backup-project`

### Purpose

`backup-project` creates a bounded backup artifact for a project.

### Functional Guarantees

`backup-project` MUST:

- require explicit backup inputs
- validate project identity before creating the backup
- create a bounded backup from documented sources only
- avoid hidden scope expansion
- validate the resulting backup artifact
- remain non-destructive to source project data

### `backup-project` MUST NOT:

- guess backup scope
- include arbitrary filesystem paths by default
- modify project source content
- claim success without validating the produced backup artifact
- perform restore behavior

### Backup Scope Rule

The current baseline backup scope is intentionally bounded.

It includes:

- project root content
- optional explicitly allowed additional inputs documented by contract

It does not automatically include arbitrary external host paths.

---

## 9. Current OPERATE Baseline Scope

The current executable OPERATE baseline is the **first controlled operate baseline** for `audit-project` and `backup-project`.

### Currently In Scope

- audit input validation
- project root inspection
- project identity validation
- runtime audit baseline checks
- audit classification
- backup input validation
- bounded project-root backup creation
- optional explicit env-file inclusion only when documented and requested
- backup artifact validation
- checksum-capable verification where implemented

### Required Explicit Inputs

The current baseline functionally depends on explicit inputs such as:

#### For `audit-project`

- project path
- optional explicit smoke/endpoint audit input

#### For `backup-project`

- project path
- backup output directory
- optional explicit inclusion flags documented by contract

These inputs must not be silently assumed.

---

## 10. Baseline Project Context Model

The current OPERATE baseline expects a project context that includes at minimum:

- project root directory
- `project.yaml`
- `compose.yaml` for runtime-oriented audit cases

### Functional Meaning of Core Files

- `project.yaml` — canonical project identity metadata
- `compose.yaml` — baseline runtime context reference for project-level runtime inspection
- project root — bounded source scope for backup

### Context Rule

A project is not operationally auditable or backupable in the current baseline unless:

- `project.yaml` exists and is parseable enough to confirm project identity
- the project root is valid
- command-specific prerequisites pass

---

## 11. Current Functional Guarantees

For the current baseline:

### `audit-project` MUST:

- validate that the target path is a project root
- validate that `project.yaml` exists
- inspect runtime state through the documented baseline mechanisms
- produce a deterministic classification
- never report `HEALTHY` without sufficient runtime evidence

### `backup-project` MUST:

- validate that the target path is a project root
- validate that the output directory is usable
- create a bounded backup artifact
- validate that the artifact was actually created
- avoid source mutation

### Blocking Behavior

OPERATE commands MUST block when:

- project identity is ambiguous
- the project path is invalid
- command-specific prerequisites are missing
- audit or backup evidence is insufficient for trustworthy completion
- artifact or runtime validation fails

---

## 12. Baseline Audit Model

The current baseline audit model includes:

### Required project identity checks

- project root validity
- `project.yaml` presence
- parseable project metadata sufficient for identity

### Required runtime checks

- runtime audit context is available
- runtime state is inspectable
- baseline runtime-state checks can be executed

### Optional explicit endpoint checks

When an explicit bounded endpoint input is supplied, the audit MAY include endpoint verification as an additional health check.

### Rule

A `HEALTHY` audit result requires all required baseline checks to pass.

---

## 13. Baseline Backup Model

The current baseline backup model includes:

### Required backup source

- project root

### Optional explicit additions

- explicitly requested env file inclusion only when documented and bounded by the current contract

### Required artifact outputs

At minimum, a successful backup must produce:

- a backup archive artifact
- sufficient artifact validation evidence to prove creation succeeded

### Backup Naming Rule

The current baseline SHOULD use deterministic naming derived from trusted project identity plus a timestamp or equivalent documented artifact-uniqueness suffix.

---

## 14. Explicitly Out of Scope in the Current Baseline

The current OPERATE baseline does **not** implement:

- automatic repair actions from audit
- host remediation
- deployment retries from audit
- restore workflows
- external storage sync
- database-consistent application-aware snapshot orchestration
- recurring scheduler logic embedded inside the commands
- advanced retention policies
- full incident management automation
- monitoring/alerting platform provisioning

These items remain deferred to later OPERATE slices or to the appropriate downstream automation layer.

---

## 15. Runtime and Artifact Validation Guarantees

No OPERATE phase is successful unless validated.

### Validation Rule

Every audit or backup command that produces a result MUST verify that the result is trustworthy.

### For the current baseline, required validation includes:

#### For `audit-project`

- required project identity checks passed
- runtime inspection completed
- classification was derived from real check outcomes

#### For `backup-project`

- archive artifact exists
- archive artifact is non-empty
- artifact validation passed
- optional checksum or equivalent verification passed where implemented

If required validation fails, the command is considered failed or blocked according to the contract.

---

## 16. Environment Behavior

### Target Environment

- authoritative runtime target is the deployed project environment on a usable host
- project backup and audit operate on a real project path and runtime context

### Functional Implications

OPERATE is not responsible for making the host or deployment ready.
It is responsible for inspecting and protecting an already established project context safely.

### Development Environment

- Windows, Linux, and macOS are acceptable development and test environments for isolated code work
- authoritative audit and backup validation remains the real target project context
- unsupported or unsafe conditions must fail safely rather than be guessed through

---

## 17. Configuration and Inputs

OPERATE behavior must not rely on hidden assumptions.

### Functional Requirement

Inputs required for audit and backup must be explicit.

This includes, where applicable:

- project path
- output directory
- optional explicit endpoint audit input
- optional explicit bounded inclusion flags
- future bounded operate policy flags approved by contract

A hidden backup scope or hidden audit target is not part of the intended functional design.

---

## 18. Functional Acceptance Criteria

The OPERATE baseline is functionally valid when:

### For `audit-project`

- input validation is deterministic
- project identity is trustworthy
- audit checks run deterministically
- classification is evidence-based
- repeated execution remains safe

### For `backup-project`

- input validation is deterministic
- source scope is bounded and explicit
- backup artifact is created successfully
- artifact validation passes
- source project data is not modified

---

## 19. Limitations and Deferred Decisions

The following are intentionally deferred or not yet frozen at the current OPERATE baseline stage:

- restore workflow
- external object storage integration
- advanced retention and pruning
- application-aware backup plugins
- richer audit policy registries
- scheduled recurring checks inside the framework
- automated remediation
- advanced incident response hooks
- multi-project fleet operations

Deferred items must be documented before they are implemented.

---

## 20. Functional Freeze Statement

The OPERATE baseline is functionally frozen as:

- a two-command OPERATE domain
- with `audit-project` as deterministic project audit
- with `backup-project` as bounded project backup
- with mandatory input validation, project identity validation, result validation, and explicit blocking on ambiguous state
- with strong separation from PROJECT and DEPLOY responsibilities

The current freeze does **not** mean the full future operational lifecycle is already implemented.
It means the functional model and responsibility boundaries are fixed, while OPERATE may continue to grow through explicitly documented slices.

---

## 21. Final Statement

The OPERATE module is the framework layer responsible for ongoing project inspection and bounded project protection after deployment.

Its functional model is:

- validate inputs first
- verify project identity
- inspect or back up only within documented scope
- validate every resulting audit or artifact
- never claim success cosmetically

All OPERATE implementation must remain aligned with this model.
