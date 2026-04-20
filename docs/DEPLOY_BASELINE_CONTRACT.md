# DEPLOY BASELINE CONTRACT

## 1. Purpose

This document defines the **current executable contract** of the DEPLOY module baseline.

It establishes:

- what the current DEPLOY baseline guarantees
- how a project is evaluated for deployment
- which actions are currently allowed
- which actions are currently forbidden
- how success is determined

This contract is the executable bridge between DEPLOY design documents and implementation.

---

## 2. Role in Documentation Hierarchy

This contract is governed by:

- `FRAMEWORK_ARCHITECTURE_MODEL.md`
- `ENGINEERING_RULES.md`
- `DEPLOY_BASELINE_FDD.md`
- `DEPLOY_BASELINE_TDD.md`

This contract governs, at the executable level:

- `deploy-project`
- `DEPLOY_PROJECT_SPEC.md`

If this contract conflicts with the DEPLOY FDD or DEPLOY TDD, this contract MUST be corrected.

---

## 3. Core Principle

The DEPLOY module does NOT assume a deployable project by default.

The default case is a:

→ **real project path on a real runtime-capable host**

All behavior must be based on:

- explicit input validation
- real project inspection
- deterministic classification
- runtime prerequisite validation
- configuration validation
- controlled build/start mutation
- smoke testing
- runtime validation

No step is considered successful unless it is validated at runtime.

---

## 4. Engineering Alignment

### 4.1 Implementation Language

All DEPLOY logic MUST be implemented in:

→ **Python**

This includes:

- project inspection
- classification logic
- runtime prerequisite validation
- env-file handling
- subprocess runner control
- smoke logic
- validation logic

### 4.2 Runtime Interaction Model

DEPLOY command execution MUST be performed through:

→ **Python-controlled subprocess execution**

Preferred primitives include:

- centralized subprocess wrapper
- structured command results
- explicit stdout/stderr capture
- explicit return-code evaluation

### 4.3 Shell Policy

Shell is NOT an implementation language for DEPLOY.

Forbidden:

- `.sh` scripts containing deployment decision logic
- delegating classification or validation decisions to shell scripts
- shell glue used as the primary deployment orchestrator instead of Python-controlled logic

### 4.4 Determinism Rule

Given the same inputs and the same project/runtime state:

→ DEPLOY decisions and outcomes MUST be identical

---

## 5. Current Scope of This Contract

This contract describes the **current executable DEPLOY baseline**, not the full future DEPLOY vision.

### Current executable focus

At this stage, the enforceable DEPLOY baseline consists of:

- explicit deploy input validation
- project inspection
- deployment context classification
- runtime prerequisite validation
- env-file validation and loading
- configuration validation
- build/start execution
- smoke testing
- post-deploy runtime validation

### Non-goal of this contract

This contract does NOT claim that rollback, cluster orchestration, migrations, proxying, TLS, or monitoring are already implemented.

Future DEPLOY slices may expand the contract, but only through explicit documentation updates.

---

## 6. Explicit Inputs

The current DEPLOY contract depends on explicit inputs.

These include, where applicable:

- project path
- env file path
- optional smoke endpoint or equivalent bounded smoke input
- future bounded deploy policy flags

### Rule

A hidden deploy target or hidden env source is NOT part of the intended contract baseline.

Implementation MUST NOT silently assume a specific project path, env file, or runtime profile unless a bounded contract explicitly states it.

---

## 7. Deployment Context Classification Model

Every deploy target MUST be classified before any deployment mutation.

### Allowed categories

#### READY
- project scaffold is deployable
- runtime prerequisites are satisfied
- deploy may proceed safely

#### REDEPLOYABLE
- compatible deployment context already exists
- baseline deploy may be safely re-applied for the same project identity

#### BLOCKED
- conflicting or ambiguous state
- safe deploy cannot proceed
- manual intervention is required

### Priority Rule

If multiple conditions exist, priority MUST be:

`BLOCKED > REDEPLOYABLE > READY`

---

## 8. Mandatory Flow

All DEPLOY mutation-capable operations MUST follow:

1. Input Validation
2. Project Inspection
3. Classification
4. Runtime Prerequisite Validation
5. Configuration Validation
6. Execution (if allowed)
7. Smoke Testing
8. Runtime Validation

Skipping required steps is forbidden.

---

## 9. `deploy-project` Contract

### Definition

`deploy-project` performs **deterministic project stack deployment**.

### Guarantees

It MUST:

- validate explicit inputs
- inspect the real project path state
- compute a deterministic deployment classification
- validate runtime prerequisites before build/start
- validate deploy configuration before mutation
- execute build and startup only after successful validation
- run baseline smoke tests
- validate the final runtime state
- produce structured results sufficient for deterministic output

### Current minimum deploy scope

The current executable deployment baseline MUST at minimum require:

- project root
- `project.yaml`
- `compose.yaml`
- explicit env file
- documented deployment runtime availability

### Allowed execution scope

Within the current baseline, `deploy-project` MAY:

- validate deploy configuration through the runtime wrapper
- build services
- start services
- re-apply build/start behavior for the same project identity when compatible
- inspect runtime state for smoke and validation purposes

### Output model

The command result MUST make clear at minimum:

- deployment classification
- whether deployment was executed, re-applied, or blocked
- whether configuration validation passed
- whether build/start succeeded
- whether smoke tests passed
- whether runtime validation passed

---

## 10. Mutation Policy

### Managed mutation rule

Within the current baseline, `deploy-project` MAY mutate only:

- the documented project stack through the deployment runtime
- compatible runtime resources associated with the current project identity as part of the documented baseline build/start behavior

### Preserve rule

It MUST preserve:

- unrelated project files
- unrelated host state
- unrelated runtime workloads not owned by the current project identity

### Overreach rule

It MUST NOT:

- install or repair the host runtime
- mutate firewall or SSH state
- rewrite project scaffold design
- create backups
- perform recurring operations
- extend runtime cleanup beyond the documented project stack scope
- claim a safe deploy when compatibility cannot be proven

---

## 11. Runtime Validation Contract

Every critical in-scope step MUST be validated via Python-controlled runtime inspection.

### Required current validation checks

For the current `deploy-project` baseline, validation MUST confirm:

- project root remains valid
- `project.yaml` exists
- `compose.yaml` exists
- env file exists
- configuration validation succeeded
- build/start completed successfully
- baseline smoke checks passed
- runtime inspection confirms successful stack state according to the documented baseline

### Failure Rule

If any required in-scope validation fails:

→ the current operation is **FAILED**

Success reporting without effective state validation is forbidden.

---

## 12. Project Identity and Deployment Compatibility Policy

### Project identity rule

The requested deploy target MUST resolve to one stable project identity.

### Metadata compatibility rule

`project.yaml` MUST be treated as authoritative scaffold metadata for project identity checks.

The command MUST block when:

- project metadata is malformed or ambiguous
- project identity conflicts with the deployment context
- the path appears partially project-like but lacks enough trustworthy metadata to prove compatibility
- the runtime state cannot be safely associated with the intended project identity

### Compose project identity rule

The deployment identity SHOULD remain stable across re-runs for the same project slug.
Undocumented project-name drift is forbidden.

---

## 13. Environment and Platform Contract

DEPLOY is a runtime deployment domain.

The authoritative target environment is:

- a host capable of executing the documented deployment runtime

### Platform rule

The contract is satisfied by deterministic Python-controlled deployment execution, not by shell-specific orchestration.

### Host responsibility boundary

If the deployment runtime is absent or unusable:

→ DEPLOY MUST block

It MUST NOT repair HOST responsibilities within the current baseline.

---

## 14. Re-Run Behavior

Where applicable:

- deployment MUST be safe to re-run for the same project identity
- compatible deployment state MAY be reused or re-applied
- conflicting deployment state MUST block rather than be guessed through
- destructive cleanup beyond documented deployment scope is forbidden

---

## 15. Abort Rules

Execution MUST stop if:

- required inputs are invalid
- classification is `BLOCKED`
- project scaffold identity is ambiguous
- runtime prerequisites are missing or unusable
- configuration validation fails
- build fails
- startup fails
- smoke tests fail
- post-deploy validation fails
- runtime execution failure prevents trustworthy completion

---

## 16. Success Criteria

The current DEPLOY baseline is valid only if:

- deployment classification is resolved deterministically
- in-scope deploy actions complete safely
- baseline smoke checks pass
- required runtime validation passes
- no out-of-scope mutation was required or silently introduced

---

## 17. Forbidden Behavior

Forbidden:

- implicit project path or env-file assumptions
- blind deployment into ambiguous state
- undocumented mutation
- host repair from DEPLOY
- skipping smoke tests
- reporting success without runtime verification
- shell-driven deployment logic
- non-deterministic project identity handling

---

## 18. Evolution Rule

This contract MAY expand in future documented DEPLOY slices.

However:

- new obligations must be documented first
- future-slice requirements MUST NOT be retroactively treated as already implemented
- lower-level specs must remain aligned with this contract

---

## 19. Final Statement

The current DEPLOY contract defines a:

- Python-based
- deterministic
- subprocess-controlled
- runtime-validated
- baseline-bounded

foundation for DEPLOY execution.

It is mandatory for the current stage and must remain aligned with the DEPLOY FDD and DEPLOY TDD.
