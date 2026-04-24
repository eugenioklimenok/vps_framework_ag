# HOST Baseline — Technical Design Document (TDD)

## 1. Purpose

This document defines the **technical architecture** of the HOST module.

It describes:

- how HOST is implemented in Python
- how `audit-vps`, `init-vps`, and `harden-vps` are separated technically
- how shared components are reused
- how the current `init-vps` reconciliation slices fit into the architecture
- how `audit-vps` supports safe gating for host reconciliation
- how the Docker Runtime Baseline is prepared and validated before DEPLOY consumes it

This document is prescriptive and must be used as technical implementation guidance together with the architecture model, engineering rules, HOST FDD, HOST contract, HOST audit specification, and the shared Python baseline.

---

## 2. Role in Documentation Hierarchy

For HOST work, this document defines the **technical source of truth** below the FDD.

It is governed by:

1. `FRAMEWORK_ARCHITECTURE_MODEL.md`
2. `ENGINEERING_RULES.md`
3. `HOST_BASELINE_FDD.md`

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
- documented Docker Runtime Baseline preparation for DEPLOY

Read-only behavior is a property of `audit-vps`, not of the entire HOST module.

---

## 4. Technical Scope of HOST

HOST is implemented as a Python module containing three command families:

- `audit-vps`
- `init-vps`
- `harden-vps`

Technically, HOST must support:

- host audit execution
- host classification
- operator user and SSH-access reconciliation
- Docker runtime reconciliation
- runtime validation
- command-level exit code control
- separate hardening behavior

HOST must not contain responsibilities belonging to PROJECT, DEPLOY, or OPERATE.

### HOST responsibility boundary

HOST prepares the server baseline.

This includes making required host-level runtime capabilities available, including Docker Engine and Docker Compose v2 when the Docker Runtime Baseline slice is in scope.

DEPLOY consumes that runtime.

DEPLOY MUST NOT install, repair, or normalize Docker.

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
- represent reconciliation outcomes
- represent validation outcomes
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
- execute explicit reconciliation slices in order
- execute post-action validation
- produce deterministic phase output

### Validation Layer

Responsibilities:

- verify achieved runtime state after mutation
- expose explicit validation functions
- fail closed when guarantees cannot be confirmed

### Docker Runtime Layer

Responsibilities:

- detect Docker Engine state
- detect Docker Compose v2 availability
- install or normalize Docker runtime only when allowed by the documented slice
- enable and start `docker.service`
- ensure the operator user can access Docker where policy requires it
- validate runtime usability through real commands

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

The audit baseline must provide enough evidence to support safe gating for current `init-vps` slices.

This includes checks for:

- supported OS
- supported architecture
- SSH daemon viability
- effective key-auth capability
- operator-related user state
- operator SSH access filesystem state
- Docker runtime availability and usability where the Docker Runtime Baseline is in scope
- essential safety signals required to avoid ambiguous reconciliation

### Architectural constraints

- no mutation allowed
- no hidden side effects
- no dependence on undocumented external state

The detailed current check behavior is governed by `AUDIT_VPS_SPEC.md`.

---

## 7.2 `init-vps`

`init-vps` is implemented as a gated reconciliation pipeline.

### Technical responsibilities

- reuse or perform internal equivalent of host classification gate
- abort on `BLOCKED` classification
- execute only documented reconciliation slices
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
5. execute operator user and SSH-access reconciliation slice
6. execute Docker Runtime Baseline slice when in scope
7. execute post-action validation for all in-scope slices
8. final decision rendering
9. exit code emission

---

## 9. Current `init-vps` Slice Architecture

The implementation must remain modular and responsibility-separated.

### Recommended module boundaries

- `reconcile_user.py`
  - user existence checks
  - safe create-or-reuse logic
  - user ambiguity detection

- `reconcile_filesystem.py`
  - home path checks
  - `.ssh` creation or reuse
  - `authorized_keys` creation or safe update
  - ownership and permission reconciliation for in-scope SSH paths

- `reconcile_docker.py`
  - Docker package source inspection
  - Docker Engine installation or reuse
  - Docker Compose v2 plugin installation or reuse
  - `docker.service` enable/start behavior
  - operator Docker group membership reconciliation

- `validate.py`
  - post-action validation of user and SSH filesystem state
  - key presence validation
  - permission and ownership verification

- `validate_docker.py`
  - Docker binary validation
  - Docker daemon validation
  - Docker Compose v2 validation
  - operator Docker access validation

- `runner.py`
  - orchestration of gate → reconcile slices → validate flow
  - deterministic output sections
  - exit code decisions

---

## 10. Slice 1 — Operator User and SSH Access

### Purpose

Prepare the operator identity and SSH key-based access needed to operate the VPS safely.

### Allowed mutation

- create or reuse operator user
- ensure operator home exists in expected form
- ensure `.ssh` exists
- ensure `authorized_keys` exists
- ensure target public key is present
- ensure safe ownership and permissions for in-scope paths

### Validation requirements

Validation must confirm:

- operator user exists
- expected operator home exists
- `.ssh` exists
- `authorized_keys` exists
- ownership is correct for in-scope paths
- permissions are correct for in-scope paths
- target public key is present

### Home permission policy

The operator home directory may be considered valid when it is owned by the operator and has a secure compatible permission mode.

The current allowed secure modes are:

- `750`
- `755`

This flexibility applies to the operator home only.

It MUST NOT relax validation for `.ssh` or `authorized_keys`.

### Forbidden mutation in this slice

- Docker install or normalization
- package baseline repair outside documented Docker runtime slice
- timezone mutation
- UFW mutation
- `sshd_config` mutation
- password authentication disablement
- root login restriction
- unrelated filesystem mutation

---

## 11. Slice 2 — Docker Runtime Baseline

### Purpose

Prepare the container runtime required by DEPLOY.

The Docker Runtime Baseline exists because DEPLOY must not install or repair the host runtime. DEPLOY validates and consumes the runtime only.

### Runtime standard

The required runtime baseline is:

- Docker Engine
- Docker Compose v2 plugin exposed as `docker compose`

Legacy `docker-compose` v1 is not the required baseline runtime.

It may be detected for diagnostics, but it MUST NOT satisfy the Docker Compose v2 baseline unless a future contract explicitly allows compatibility fallback.

### Allowed mutation

Within this slice, `init-vps` MAY:

- install required package prerequisites for Docker official repository usage
- configure Docker official APT repository
- install Docker Engine packages
- install Docker Compose v2 plugin
- enable `docker.service`
- start `docker.service`
- add operator user to the `docker` group
- validate Docker runtime usability

### Required package source policy

The Docker Runtime Baseline SHOULD install Docker from the official Docker package source for Ubuntu-compatible systems.

The implementation MUST NOT silently accept an ambiguous or broken mixed Docker installation as valid.

### Required technical checks before mutation

Before attempting Docker reconciliation, the implementation should inspect:

- OS support
- package manager availability
- existing Docker binary state
- existing Compose state
- Docker service state
- operator Docker access state
- signs of conflicting or ambiguous Docker installations

### SANEABLE runtime states

Examples of saneable states:

- Docker is missing
- Docker Compose v2 plugin is missing
- Docker service is installed but disabled or stopped
- operator user is not in `docker` group
- Docker official repository is missing but safely configurable

### BLOCKED runtime states

Examples of blocked states:

- unsupported OS for current Docker installation policy
- package manager unavailable or broken
- Docker binary exists but cannot be identified safely
- Docker service exists but fails repeatedly after reconciliation
- Docker socket ownership or permissions are ambiguous
- incompatible runtime state prevents trustworthy validation
- repository configuration conflicts in a way the framework cannot safely reconcile

### Docker validation requirements

Validation must confirm:

- `docker --version` succeeds
- `docker compose version` succeeds
- `docker.service` is active
- Docker daemon is reachable
- operator user is a member of the `docker` group where policy requires non-root usage
- `docker ps` succeeds for the intended operator context

### Session refresh note

Adding the operator to the `docker` group may require a new login session before non-root Docker access is effective.

The command output SHOULD make this explicit when applicable.

The framework MUST NOT claim operator Docker access is validated in the current shell if group membership has not taken effect.

### Forbidden mutation in this slice

- project deployment
- compose stack startup for application projects
- image build for application projects
- application runtime smoke tests
- reverse proxy configuration
- TLS provisioning
- DNS configuration
- backups
- monitoring stack deployment
- arbitrary runtime cleanup outside Docker baseline preparation

---

## 12. Input and Configuration Model

The current HOST technical design requires explicit inputs.

At minimum, relevant technical inputs are:

- operator user identity
- public key or key source
- future bounded policy flags explicitly approved by contract

For Docker Runtime Baseline work, implementation MAY use documented policy defaults such as:

- required Docker runtime family
- required Compose version family
- official Docker repository target for supported Ubuntu releases

These policy defaults must be documented in config or contract and must not be hidden heuristics.

### Rule

Command-critical values must be obtained through explicit command inputs or structured documented configuration.

They must not be embedded as unexplained constants in business logic.

---

## 13. Data and State Modeling

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
- state repaired
- state installed
- ambiguity detected
- validation passed or failed
- fatal safety stop required

### Docker-side modeling

Docker runtime state should be represented explicitly.

Recommended modeling categories:

- `DockerRuntimeState`
  - `MISSING`
  - `PARTIAL`
  - `READY`
  - `BROKEN`
  - `AMBIGUOUS`

- `DockerReconcileAction`
  - `INSTALL`
  - `REUSE`
  - `REPAIR_SERVICE`
  - `ADD_GROUP`
  - `VALIDATE`
  - `BLOCK`

The technical design should avoid hidden booleans and implicit state transitions.

---

## 14. Determinism and Idempotency

### Determinism

Given the same inputs and same host state, HOST commands must produce the same decisions, validations, and exit codes.

### Idempotency for `init-vps`

The reconciliation slices must be safe to re-run.

This requires:

- checking state before mutating
- preserving compatible existing data
- not duplicating the same authorized key
- not truncating unrelated keys
- not reinstalling Docker unnecessarily when a compatible runtime is already valid
- not repeatedly rewriting repository configuration without need
- not restarting services unnecessarily unless required for reconciliation or validation

---

## 15. Safety and Abort Model

HOST technical behavior must fail closed.

Execution must stop when:

- host classification is `BLOCKED`
- filesystem state is ambiguous
- user state is ambiguous
- ownership or permissions cannot be safely guaranteed
- Docker runtime state is ambiguous or broken beyond documented reconciliation
- package installation prerequisites cannot be trusted
- post-action validation fails
- runtime execution error prevents contract fulfillment

No fallback heuristics are allowed for ambiguous mutation states.

---

## 16. Cross-Platform Technical Behavior

### Linux

Linux is the authoritative runtime target for real host inspection and reconciliation.

Docker Runtime Baseline reconciliation is Linux-authoritative and expected primarily on supported Ubuntu-compatible VPS environments.

### Windows

Windows is a supported development and test environment only.

Technical implications:

- tests must isolate subprocess interactions through mocking
- reconciliation logic must remain unit-testable without real Linux mutation
- unsupported local execution conditions must abort safely
- Windows success is not authoritative proof of Linux host correctness

---

## 17. Testing Strategy

### Unit Tests

Required for:

- audit parsing and check logic
- classification reducer behavior
- subprocess wrapper behavior
- user reconciliation logic
- filesystem reconciliation logic
- Docker runtime detection logic
- Docker reconciliation planning logic
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
- Docker missing → saneable classification
- Docker broken/ambiguous → blocked classification
- Docker ready → compatible classification
- Compose v1 only → not accepted as Compose v2 baseline unless future contract changes
- operator lacking Docker access → saneable or validation failure according to phase

### Cross-platform Tests

System interactions must be mockable so tests pass in Windows development environments without requiring real Linux mutation.

---

## 18. Known Technical Constraints and Deferred Decisions

The following remain intentionally open or deferred at the current stage:

- structured configuration model for all future host inputs
- final sudo and NOPASSWD automation policy
- full package baseline beyond Docker Runtime Baseline
- Docker runtime support for non-Ubuntu systems
- support for rootless Docker
- support for Podman or other container runtimes
- multi-runtime selection
- reverse proxy automation
- TLS automation
- monitoring agent installation
- automatic reboot/session refresh orchestration after group membership changes
- future audit expansion outside the current gating baseline

These may be extended later, but only through documented, contract-aligned updates.

---

## 19. Technical Freeze Statement

The HOST technical baseline is frozen as:

- a Python-only HOST implementation
- with explicit command separation for audit, init, and harden
- with shared subprocess, classification, and validation foundations
- with `audit-vps` as read-only diagnostic architecture
- with `init-vps` as controlled slice-based reconciliation architecture
- with Slice 1 for operator user and SSH access
- with Slice 2 for Docker Runtime Baseline
- with `harden-vps` reserved for post-initialization security enforcement

The freeze applies to architecture and responsibility boundaries.

It does not imply that every future HOST capability is implemented.

---

## 20. Final Statement

The HOST module technical design must support safe evolution without ambiguity.

Its architecture therefore requires:

- explicit command boundaries
- explicit safety gates
- explicit runtime validation
- deterministic subprocess-driven behavior
- slice-based reconciliation growth
- Docker Runtime Baseline preparation before DEPLOY consumes runtime capabilities
- no hidden repair behavior inside DEPLOY

All HOST implementation must remain aligned with this design.
