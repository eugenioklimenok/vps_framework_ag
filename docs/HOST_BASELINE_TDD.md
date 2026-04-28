# Approved Additive Integration Notice — HOST Slice 02 Docker / Compose

This document preserves the recovered original HOST baseline content below and extends it under the project **no-regression by extension-only** rule.

Approved change:
- Docker Engine installation and Docker Compose v2 plugin installation are now part of **HOST Phase 1** as **Slice 02 — Docker / Docker Compose Runtime Baseline**.
- Existing Slice 01 operator user and SSH access behavior remains valid and unchanged.
- Any older statement in the recovered baseline saying Docker installation, Docker normalization, or Docker checks are deferred is now narrowed to mean **deferred from Slice 01 only**.
- The canonical definition for Docker / Compose behavior is the Slice 02 extension section added in this document.
- `audit-vps` remains read-only.
- `init-vps` may mutate Docker runtime state only under the documented Slice 02 rules.
- DEPLOY consumes Docker runtime; DEPLOY must not silently install or repair Docker once Slice 02 is canonical.

---

# HOST Baseline — Technical Design Document (TDD)

## 1. Purpose

This document defines the **technical architecture** of the HOST module.

It describes:

- how HOST is implemented in Python
- how its commands are separated technically
- how shared components are reused
- how the current `init-vps` reconciliation slice fits into the architecture
- how the current `audit-vps` baseline supports safe gating for that slice

This document is prescriptive and must be used as technical implementation guidance together with the architecture model, engineering rules, HOST FDD, HOST contract, HOST audit specification, and the shared Python baseline.

---

## 2. Role in Documentation Hierarchy

For HOST work, this document defines the **technical source of truth** below the FDD.

It is governed by:

- `FRAMEWORK_ARCHITECTURE_MODEL.md`
- `ENGINEERING_RULES.md`
- `HOST_BASELINE_FDD.md`

It governs, technically, the lower-level HOST documents:

- `HOST_BASELINE_CONTRACT.md`
- `AUDIT_VPS_SPEC.md`

If a lower-level HOST document contradicts this TDD, the lower-level document MUST be corrected.

---

## 3. Technical Design Goals

The HOST module technical design MUST provide:

- deterministic behavior
- Python-only implementation
- modular command boundaries
- explicit safety gates
- runtime validation
- idempotent reconciliation where applicable
- high testability
- Codex-compatible structure
- safe development on Windows with Linux-targeted host logic

Read-only behavior is a property of `audit-vps`, not of the entire HOST module.

---

## 4. Technical Scope of HOST

HOST is implemented as a Python module containing three command families:

- `audit-vps`
- `init-vps`
- `harden-vps`

Technically, HOST must support:

- audit execution
- host classification
- reconciliation orchestration
- runtime validation
- command-level exit code control

HOST must not contain responsibilities belonging to PROJECT, DEPLOY, or OPERATE.

---

## 5. Repository Architecture

The HOST implementation is expected to follow the framework repository model:

```text
framework/
├── cli/
├── modules/
│   └── host/
│       ├── audit/
│       ├── init/
│       └── harden/
├── models/
├── utils/
├── config/
└── tests/
```

### HOST command separation

- `framework/modules/host/audit/` contains read-only audit logic
- `framework/modules/host/init/` contains controlled reconciliation and validation logic
- `framework/modules/host/harden/` contains security hardening logic

### Shared technical layers

- `framework/cli/` exposes Typer entrypoints
- `framework/models/` contains shared result and classification models
- `framework/utils/` contains subprocess and helper abstractions
- `framework/config/` contains explicit configuration and input-loading helpers where needed
- `tests/` contains isolated unit and integration-oriented tests

### Structure Rule

A generic `framework/core/` layer is not part of the canonical HOST baseline.
Shared functionality should live in explicitly owned technical layers.

---

## 6. Core Technical Components

### CLI Layer

Responsibilities:

- expose `audit-vps`, `init-vps`, and `harden-vps`
- parse explicit inputs
- delegate to command-specific runners
- translate runner outcomes into deterministic exit codes

### Shared Models

Responsibilities:

- represent check results
- represent classification values
- represent reconciliation outcomes where needed
- avoid scattered string literals for status or classification

### Subprocess Wrapper

Responsibilities:

- centralize system command execution
- capture stdout, stderr, and return code
- support timeout handling
- normalize execution behavior across commands
- remain the only system interaction path

### Audit Runner

Responsibilities:

- execute audit checks
- aggregate results
- reduce classification
- produce evidence-driven output

### Init Runner

Responsibilities:

- perform preflight and gate logic
- stop on blocked conditions
- execute explicit reconciliation steps in order
- execute post-action validation
- produce deterministic phase output

### Validation Layer

Responsibilities:

- verify achieved runtime state after mutation
- expose explicit validation functions
- fail closed when guarantees cannot be confirmed

---

## 7. Command Architecture

## 7.1 `audit-vps`

`audit-vps` is implemented as a read-only diagnostic pipeline.

### Technical responsibilities

- run grouped checks
- collect evidence through subprocess wrappers
- produce structured result objects
- compute final classification
- emit deterministic output and exit codes

### Current technical scope

The current audit baseline must provide enough evidence to support safe gating for the current `init-vps` slice.

This includes checks for:

- supported OS
- supported architecture
- SSH daemon viability
- effective key-auth capability
- operator-related user state
- operator SSH access filesystem state
- essential safety signals required to avoid ambiguous reconciliation

### Architectural constraints

- no mutation allowed
- no hidden side effects
- no dependence on undocumented external state

The detailed current check behavior is governed by the audit specification.

---

## 7.2 `init-vps`

`init-vps` is implemented as a gated reconciliation pipeline.

### Technical responsibilities

- reuse or perform internal equivalent of host classification gate
- abort on `BLOCKED` classification
- execute only the currently allowed reconciliation slice
- validate in-scope changes after execution
- emit deterministic human-readable phase output

### Architectural constraints

- no blind overwrite
- no undocumented mutation
- no progression after ambiguous state detection
- no success reporting without post-validation

`init-vps` is intentionally slice-based and may expand over time, but each slice must remain explicit and documented.

---

## 7.3 `harden-vps`

`harden-vps` is implemented as a separate hardening pipeline.

### Technical responsibilities

- apply security policies intentionally deferred from initialization
- validate security-sensitive outcomes
- preserve responsibility separation from `init-vps`

---

## 8. Technical Execution Flows

## 8.1 `audit-vps` Flow

1. CLI invocation
2. input validation
3. audit runner initialization
4. execution of configured checks
5. result aggregation
6. classification reduction
7. output rendering
8. exit code emission

---

## 8.2 Current `init-vps` Flow

1. CLI invocation
2. explicit input validation
3. preflight / audit gate evaluation
4. abort if host classification is `BLOCKED`
5. operator user reconciliation
6. operator filesystem reconciliation (`home`, `.ssh`, `authorized_keys` in current slice)
7. post-action validation
8. final decision rendering
9. exit code emission

This flow is currently limited to the first controlled reconciliation slice.

---

## 9. Current `init-vps` Slice Architecture

The current implementation slice should remain modular and responsibility-separated.

### Recommended module boundaries

- `reconcile_user.py`
  - user existence checks
  - safe create-or-reuse logic
  - user ambiguity detection

- `reconcile_filesystem.py`
  - home path checks
  - `.ssh` creation or reuse
  - `authorized_keys` creation or safe update
  - ownership and permission reconciliation for in-scope paths

- `validate.py`
  - post-action validation of user and SSH filesystem state
  - key presence validation
  - permission and ownership verification

- `runner.py`
  - orchestration of gate → reconcile → validate flow
  - deterministic output sections
  - exit code decisions

### Current slice technical boundaries

Allowed mutation in the current slice:

- create or reuse operator user
- ensure operator home exists in expected form
- ensure `.ssh` exists
- ensure `authorized_keys` exists
- ensure target key is present
- ensure safe ownership and permissions for in-scope paths

Forbidden mutation in the current slice:

- Docker install or normalization
- package install or repair
- timezone mutation
- UFW mutation
- `sshd_config` mutation
- password authentication disablement
- root login restriction
- automated sudo or NOPASSWD policy enforcement
- unrelated filesystem mutation

---

## 10. Input and Configuration Model

The current HOST technical design requires explicit inputs.

At minimum, the relevant technical inputs for the current slice are:

- operator user identity
- public key or key source
- any bounded policy flags explicitly approved by contract

### Rule

These values must be obtained through explicit command inputs or structured configuration.
They must not be embedded as hidden constants in business logic.

---

## 11. Data and State Modeling

### Audit-side modeling

Audit results should use explicit result objects containing at minimum:

- check identifier
- status
- evidence
- message
- classification impact

### Init-side modeling

Reconciliation and validation should use explicit return values or dataclasses that make these outcomes clear:

- action taken
- state reused
- ambiguity detected
- validation passed or failed
- fatal safety stop required

The technical design should avoid hidden booleans and implicit state transitions.

---

## 12. Determinism and Idempotency

### Determinism

Given the same inputs and same host state, HOST commands must produce the same decisions, same validations, and same exit codes.

### Idempotency for `init-vps`

The current reconciliation slice must be safe to re-run.

This requires:

- checking state before mutating
- preserving compatible existing data
- not duplicating the same authorized key
- not truncating unrelated keys
- not recreating already-correct compatible state

---

## 13. Safety and Abort Model

HOST technical behavior must fail closed.

Execution must stop when:

- host classification is `BLOCKED`
- filesystem state is ambiguous
- user state is ambiguous
- ownership or permissions cannot be safely guaranteed
- post-action validation fails
- runtime execution error prevents contract fulfillment

No fallback heuristics are allowed for ambiguous mutation states.

---

## 14. Cross-Platform Technical Behavior

### Linux

Linux is the authoritative runtime target for real host inspection and reconciliation.

### Windows

Windows is a supported development and test environment only.

Technical implications:

- tests must isolate subprocess interactions through mocking
- reconciliation logic must remain unit-testable without real Linux mutation
- unsupported local execution conditions must abort safely
- Windows success is not authoritative proof of Linux host correctness

---

## 15. Testing Strategy

### Unit Tests

Required for:

- audit parsing and check logic
- classification reducer behavior
- subprocess wrapper behavior
- user reconciliation logic
- filesystem reconciliation logic
- post-action validation logic
- runner decision logic

### CLI Tests

Required for:

- command entrypoint behavior
- deterministic output sections
- exit code mapping

### Safety Tests

Required for:

- blocked host abort behavior
- ambiguous state abort behavior
- idempotent rerun behavior
- preservation of unrelated authorized keys
- duplicate key prevention

### Cross-platform Tests

System interactions must be mocked so tests pass in Windows development environments without requiring real Linux mutation.

---

## 16. Known Technical Constraints and Deferred Decisions

The following remain intentionally open or deferred at the current stage:

- structured configuration model for all future host inputs
- final operator user parameterization model across all commands
- detailed sudo and NOPASSWD automation policy
- full multi-slice `init-vps` orchestration beyond current scope
- future Docker normalization implementation details
- broad operator environment scaffolding beyond current SSH access slice
- future audit expansion outside the current gating baseline

These may be extended later, but only through documented, contract-aligned updates.

---

## 17. Technical Freeze Statement

The HOST technical baseline is frozen as:

- a Python-only HOST implementation
- with explicit command separation for audit, init, and harden
- with shared subprocess, classification, and validation foundations
- with `audit-vps` as read-only diagnostic architecture
- with `init-vps` as controlled slice-based reconciliation architecture
- with `harden-vps` reserved for post-initialization security enforcement

The freeze applies to architecture and responsibility boundaries.
It does not imply that all future HOST slices are already implemented.

---

## 18. Final Statement

The HOST module technical design must support safe evolution without ambiguity.

Its architecture therefore requires:

- explicit command boundaries
- explicit safety gates
- explicit runtime validation
- deterministic subprocess-driven behavior
- slice-based growth of reconciliation logic without breaking contracts

All HOST implementation must remain aligned with this design.

---

# Approved Technical Extension — HOST Slice 02 Docker / Docker Compose Runtime Baseline

## 1. Technical Intent

This extension adds a second controlled `init-vps` reconciliation slice.

Slice 02 prepares Docker Engine and Docker Compose v2 as host-level runtime prerequisites for DEPLOY.

The existing Slice 01 architecture remains unchanged.

## 2. Execution Flow Update

The extended `init-vps` flow is:

1. CLI invocation
2. explicit input validation
3. preflight / audit gate evaluation
4. abort if host classification is `BLOCKED`
5. Slice 01 operator user reconciliation
6. Slice 01 operator filesystem reconciliation
7. Slice 01 post-action validation
8. Slice 02 Docker / Docker Compose runtime reconciliation
9. Slice 02 post-action validation
10. final decision rendering
11. exit code emission

## 3. Recommended Module Boundaries

Recommended new or extended modules:

```text
framework/modules/host/audit/checks/docker.py
framework/modules/host/init/reconcile_docker.py
framework/modules/host/init/validate_docker.py
```

### `audit/checks/docker.py`

Responsibilities:

- Docker CLI evidence collection
- Docker daemon/service evidence collection
- Docker Compose v2 evidence collection
- legacy `docker-compose` diagnostic detection
- operator Docker group membership evidence
- operator Docker access evidence where required
- conflict and ambiguity signal detection

### `init/reconcile_docker.py`

Responsibilities:

- Docker installation planning
- Docker official package source setup where required and supported
- Docker Engine installation or compatible reuse
- Docker Compose v2 plugin installation or compatible reuse
- `docker.service` enable/start behavior
- operator `docker` group membership reconciliation when required

### `init/validate_docker.py`

Responsibilities:

- Docker binary validation
- Docker daemon validation
- Docker Compose v2 validation
- operator Docker access validation when required for DEPLOY operator execution

## 4. Docker Installation Policy

For supported Ubuntu-compatible systems, the preferred installation policy is:

- Docker Engine from the official Docker package source
- Docker Compose v2 plugin exposed as `docker compose`

Legacy standalone `docker-compose` may be detected for diagnostics, but it MUST NOT satisfy the Docker Compose v2 baseline unless a future contract explicitly allows compatibility fallback.

## 5. Allowed Mutation in Slice 02

Slice 02 may:

- install Docker Engine when absent and safely supported
- install Docker Compose v2 plugin when absent and safely supported
- configure the documented Docker package source when required by the approved install method
- enable `docker.service` when required and safe
- start `docker.service` when required and safe
- create or reuse the `docker` group according to platform behavior
- add the configured operator user to the `docker` group when required for DEPLOY operator execution

## 6. Forbidden Mutation in Slice 02

Slice 02 MUST NOT:

- remove unknown Docker installations blindly
- overwrite custom Docker daemon configuration blindly
- delete containers, images, volumes, or networks
- create application Compose projects
- start application workloads
- mutate registry credentials
- perform unrelated package repair
- mutate SSH hardening state
- mutate UFW state
- silently change privilege policy outside the documented operator Docker access rule

## 7. Validation Requirements

Slice 02 post-action validation MUST confirm:

- `docker --version` succeeds
- `docker info` succeeds
- `docker compose version` succeeds
- `docker.service` is active or the daemon is otherwise reachable according to documented platform policy
- operator Docker access succeeds when DEPLOY is expected to execute Docker as the operator user

Adding the operator to the `docker` group may require a new login session before non-root Docker access is effective.

The implementation MUST NOT claim operator Docker access is valid until the intended execution context is validated.

## 8. Blocked States

The implementation MUST classify the host as `BLOCKED` when Docker state is unsafe or ambiguous, including:

- unsupported OS or architecture for the current Docker install policy
- broken package manager state
- conflicting Docker packages or repositories
- Docker binary exists but cannot be identified safely
- Docker daemon fails after documented reconciliation
- Compose path is ambiguous or broken
- Docker socket ownership or permission state cannot be trusted

## 9. Test Expectations

At minimum, tests SHOULD cover:

- Docker absent → saneable classification and install plan
- Docker ready → compatible classification and no reinstall
- Docker Compose v2 missing → saneable classification and plugin install plan
- legacy `docker-compose` only → not compatible with Compose v2 baseline
- Docker daemon failed → blocked classification unless documented safe recovery exists
- operator missing Docker group membership → saneable or validation failure according to execution phase
- idempotent rerun after successful Docker baseline preparation

## 10. Documentation Change Record

This extension preserves the recovered HOST TDD.

Prior statements that Docker normalization details were future/deferred are narrowed to mean Docker was deferred from Slice 01. Docker Engine and Docker Compose v2 are now governed by Slice 02.
