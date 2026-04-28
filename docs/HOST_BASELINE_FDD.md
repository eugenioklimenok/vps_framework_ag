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

# HOST Baseline — Functional Design Document (FDD)

## 1. Purpose

This document defines the **functional behavior of the HOST module baseline** within the framework.

The HOST module is responsible for transforming a heterogeneous VPS into a standardized, validated, and operational host baseline through:

- host inspection
- deterministic classification
- controlled reconciliation
- runtime validation
- post-initialization hardening

This document defines:

- what HOST does functionally
- which commands belong to HOST
- how those commands relate to each other
- what the current executable slice includes
- what remains intentionally deferred

This document is prescriptive and must be treated as executable design input for HOST implementation.

---

## 2. Role in Documentation Hierarchy

For HOST work, this document defines the **functional source of truth**.

It is governed by:

- `FRAMEWORK_ARCHITECTURE_MODEL.md`
- `ENGINEERING_RULES.md`

It governs, functionally, the lower-level HOST documents:

- `HOST_BASELINE_TDD.md`
- `HOST_BASELINE_CONTRACT.md`
- `AUDIT_VPS_SPEC.md`

If a lower-level HOST document contradicts this FDD, the lower-level document MUST be corrected.

---

## 3. Functional Scope

HOST is the framework domain responsible for preparing and securing the server baseline.

### In Scope

- inspect real VPS state
- classify host condition deterministically
- determine whether automation may proceed safely
- perform controlled host reconciliation through `init-vps`
- validate runtime results after reconciliation
- apply hardening through `harden-vps`

### Out of Scope

- project scaffolding
- application deployment
- project runtime operations
- application-specific service orchestration
- any behavior belonging to PROJECT, DEPLOY, or OPERATE

---

## 4. Supported Commands

The HOST module contains three functional commands:

### `audit-vps`

Read-only diagnostic command.

Responsibilities:

- inspect real host state
- collect runtime evidence
- classify the host as `CLEAN`, `COMPATIBLE`, `SANEABLE`, or `BLOCKED`
- provide structured and human-readable output
- avoid any mutation

### `init-vps`

Controlled reconciliation command.

Responsibilities:

- initialize or normalize the host baseline
- operate only after audit-based gating or equivalent internal gate logic
- reconcile only the states allowed by the current implementation slice
- validate all in-scope mutations at runtime
- abort on unsafe or ambiguous conditions

### `harden-vps`

Security hardening command.

Responsibilities:

- apply post-initialization hardening
- enforce stricter SSH security policies
- run only after initialization prerequisites are satisfied

---

## 5. Functional Model

All HOST behavior must follow the same mandatory flow:

1. Inventory
2. Classification
3. Decision
4. Execution (if allowed)
5. Runtime Validation

No HOST command may skip required safety checks for its phase.

---

## 6. Host Classification Model

All host evaluation is based on the following deterministic classification states:

### CLEAN
The host has minimal prior state and no relevant conflicts.

### COMPATIBLE
The host contains existing components that are already aligned and safe to reuse.

### SANEABLE
The host contains state that is not yet aligned but can be normalized safely without destructive behavior.

### BLOCKED
The host contains unsafe, ambiguous, or conflicting state that prevents safe automation and requires manual intervention.

### Classification Priority

If multiple conditions are present, classification priority MUST be:

`BLOCKED > SANEABLE > COMPATIBLE > CLEAN`

---

## 7. Functional Behavior of `audit-vps`

### Purpose

`audit-vps` is the diagnostic foundation of HOST.

### Functional Guarantees

`audit-vps` MUST:

- be read-only
- collect real runtime evidence
- produce deterministic results
- classify the host before mutation phases
- degrade gracefully when evidence commands are unavailable
- never modify system state

### Current Functional Scope

The current executable audit baseline focuses on the checks required to classify the host safely for the current HOST slice.

At minimum, this includes evidence sufficient to evaluate:

- operating system support
- CPU architecture support
- SSH daemon viability and effective key-auth capability
- operator-related user state
- operator SSH access filesystem state
- essential safety signals needed to avoid unsafe reconciliation

### Functional Output

`audit-vps` MUST provide:

- grouped human-readable output
- per-check result data
- final classification
- deterministic exit code behavior

### Expansion Rule

Audit coverage MAY expand in later documented slices.
Additional checks MUST NOT silently redefine the gating behavior of the current documented slice.

---

## 8. Functional Behavior of `init-vps`

### Purpose

`init-vps` initializes or normalizes the host baseline through controlled reconciliation.

### Functional Rules

`init-vps` MUST:

- rely on prior host classification or equivalent internal gate logic
- abort if classification is `BLOCKED`
- avoid blind overwrite of unknown state
- preserve existing compatible data when safe
- validate all in-scope changes at runtime
- remain safe to re-run

`init-vps` MUST NOT:

- assume a clean machine
- destroy unrelated data
- continue when contract guarantees cannot be met
- claim success without post-action validation

### Incremental Reconciliation Model

`init-vps` is allowed to evolve through controlled implementation slices.

This means:

- not all HOST baseline responsibilities must be implemented in the first slice
- each slice must define explicit scope boundaries
- each slice must define explicit out-of-scope behavior
- each slice must define required runtime validation
- no slice may introduce undocumented side effects

---

## 9. Current `init-vps` Functional Scope

The current implemented reconciliation slice is the **first controlled reconciliation slice** of `init-vps`.

### Currently In Scope

- operator user reconciliation
- operator home validation
- operator `.ssh` directory reconciliation
- operator `authorized_keys` reconciliation
- safe post-action validation for these items only

### Required Explicit Inputs

The current slice functionally depends on explicit inputs such as:

- operator user identity
- target public key or equivalent key source

These inputs must not be silently assumed.

### Current Functional Guarantees

For the current slice, `init-vps` MUST:

- create the operator user if missing and safe to create
- reuse the existing operator user if compatible
- ensure the operator home exists and is valid for expected ownership
- ensure `.ssh` exists with safe permissions and ownership
- ensure `authorized_keys` exists with safe permissions and ownership
- ensure the target public key is present
- preserve unrelated existing keys
- avoid duplicate insertion of the same key
- abort on clearly unsafe or ambiguous filesystem or user state
- validate all in-scope outcomes after reconciliation

### Explicitly Out of Scope in the Current Slice

The current slice of `init-vps` does **not** implement:

- Docker installation
- Docker normalization
- package installation
- timezone configuration
- UFW configuration
- SSH daemon hardening
- disabling password authentication
- root login restriction
- broad filesystem scaffolding beyond operator SSH access preparation
- automated sudo policy enforcement
- automated NOPASSWD policy enforcement

These items remain deferred to later `init-vps` slices or to `harden-vps`, depending on responsibility.

---

## 10. Functional Behavior of `harden-vps`

### Purpose

`harden-vps` applies post-initialization security hardening.

### Functional Responsibilities

`harden-vps` is responsible for policies intentionally deferred from initialization, including where documented:

- disabling password authentication
- restricting root login
- enforcing stricter SSH runtime policy

### Preconditions

`harden-vps` may run only when:

- the host is not blocked
- initialization prerequisites have already been completed
- runtime validation confirms the host is in a safe pre-hardening state

---

## 11. Runtime Validation Guarantees

No HOST phase is successful unless validated at runtime.

### Validation Rule

Every command that performs mutation MUST verify that the intended state was actually achieved.

### For the current `init-vps` slice, required validation includes:

- operator user exists
- expected operator home exists
- `.ssh` exists
- `authorized_keys` exists
- ownership is correct
- permissions are correct
- target public key is present

If post-action validation fails, the command is considered failed.

---

## 12. Environment Behavior

### Target Environment

- Linux VPS
- primarily Ubuntu-based systems

### Development Environment

- Windows may be used for local development and testing
- local Windows execution is non-authoritative for real host mutation
- testability must be preserved through mocking and isolation
- unsupported local runtime conditions must fail safely rather than crash unpredictably

---

## 13. Configuration and Inputs

HOST behavior must not rely on hidden assumptions.

### Functional Requirement

Inputs required for reconciliation must be explicit.

This includes, where applicable:

- operator user identity
- expected public key
- other host normalization targets required by future slices

A fixed hardcoded operator identity is not part of the intended long-term functional design.

---

## 14. Functional Acceptance Criteria

The HOST baseline is functionally valid when:

### For `audit-vps`

- host inspection executes successfully
- required check groups produce deterministic output
- classification is consistent with evidence
- no mutation occurs

### For the current `init-vps` slice

- preflight and audit gate still function
- reconciliation does not run on `BLOCKED` state
- in-scope user and SSH filesystem reconciliation complete safely
- post-action validation passes for in-scope items
- repeated execution remains idempotent
- no out-of-scope mutations are introduced

### For `harden-vps`

- hardening remains separate from initialization
- security enforcement occurs only in its proper phase

---

## 15. Limitations and Deferred Decisions

The following are intentionally deferred or not yet frozen at the current baseline stage:

- full `init-vps` host baseline convergence in a single run
- detailed sudo policy automation
- NOPASSWD policy decision
- broad operator environment scaffolding
- Docker normalization implementation in later slices
- timezone target policy
- package baseline convergence beyond current slice
- expanded audit coverage unrelated to current safe gating

Deferred items must be documented before they are implemented.

---

## 16. Functional Freeze Statement

The HOST baseline is functionally frozen as:

- a multi-command HOST domain
- with `audit-vps` as read-only diagnostic foundation
- with `init-vps` as controlled incremental reconciliation
- with `harden-vps` as post-initialization hardening
- with mandatory classification, abort rules, and runtime validation

The current freeze does **not** mean full host convergence is already implemented.
It means the functional model and responsibility boundaries are fixed, while HOST may continue to grow through explicitly documented slices.

---

## 17. Final Statement

The HOST module is the framework layer responsible for turning a heterogeneous VPS into a predictable and validated server baseline.

Its functional model is:

- inspect first
- classify explicitly
- reconcile only when safe
- validate every critical result
- harden afterward

All HOST implementation must remain aligned with this model.

---

# Approved Extension — HOST Slice 02 Docker / Docker Compose Runtime Baseline

## 1. Extension Purpose

This extension adds Docker Engine and Docker Compose v2 runtime preparation to HOST Phase 1 without removing or weakening the existing HOST Slice 01 baseline.

Slice 01 remains responsible for operator user and SSH access preparation.

Slice 02 is responsible for preparing the container runtime baseline required by DEPLOY.

## 2. Functional Ownership

HOST prepares runtime.

DEPLOY consumes runtime.

Therefore:

- HOST MUST prepare Docker Engine when absent and safely supported.
- HOST MUST prepare Docker Compose v2 plugin when absent and safely supported.
- HOST MUST validate Docker runtime readiness before reporting success.
- DEPLOY MUST NOT silently install, repair, or normalize Docker as a hidden deployment side effect.

## 3. Slice 02 In Scope

Slice 02 includes:

- detecting Docker Engine installation state
- detecting Docker daemon/service state
- detecting Docker CLI usability
- detecting Docker Compose v2 plugin availability through `docker compose`
- installing Docker Engine when absent and safely supported
- installing Docker Compose v2 plugin when absent and safely supported
- enabling `docker.service` when required and safe
- starting `docker.service` when required and safe
- creating or reusing the `docker` group when required by the platform package model
- adding the configured operator user to the `docker` group when required for DEPLOY operator execution
- validating Docker Engine and Docker Compose availability before success is reported

## 4. Slice 02 Out of Scope

Slice 02 MUST NOT:

- deploy application workloads
- generate application `compose.yaml` files
- create application directories
- build application images
- pull application images
- start application containers
- stop application containers
- delete containers, images, volumes, or networks
- manage registry authentication
- configure reverse proxies
- configure TLS certificates
- perform application smoke tests
- perform broad package repair unrelated to Docker runtime installation
- perform unrelated host hardening

## 5. Functional Guarantees

For Slice 02, `init-vps` MUST:

- install Docker Engine if Docker is absent and the host is supported
- install Docker Compose v2 plugin if Compose is absent and the host is supported
- reuse an existing compatible Docker runtime when already valid
- avoid unnecessary reinstall when Docker is already compatible
- refuse to overwrite, remove, or blindly normalize unknown Docker installations
- classify broken, ambiguous, conflicting, unsupported, or untrusted Docker states as `BLOCKED` unless a safe documented normalization path exists
- validate Docker CLI availability through runtime evidence
- validate Docker daemon reachability through runtime evidence
- validate Docker Compose v2 availability through runtime evidence
- validate operator Docker access when DEPLOY is expected to execute Docker as the operator user
- preserve the separation between HOST runtime preparation and DEPLOY workload execution

## 6. Validation Requirements

Slice 02 success requires runtime validation.

At minimum, validation MUST confirm:

```bash
docker --version
docker info
docker compose version
```

When systemd is the supported service manager, validation SHOULD also confirm:

```bash
systemctl is-active docker
```

When DEPLOY is expected to run as the operator user, validation MUST confirm Docker access in the intended operator execution context.

Success reporting without effective Docker runtime validation is forbidden.

## 7. Classification Rules

Docker-related state contributes to the canonical HOST classification model.

### SANEABLE

Examples:

- Docker absent on a supported host with a safe installation path
- Docker Compose v2 plugin absent on a supported host with a safe installation path
- Docker service installed but stopped/disabled and safely startable
- operator missing Docker group membership when that access is required and safely reconcilable

### COMPATIBLE

Examples:

- Docker CLI exists
- Docker daemon is reachable
- Docker Compose v2 is available through `docker compose`
- operator Docker access is valid when required

### BLOCKED

Examples:

- unsupported OS or architecture for the approved Docker installation policy
- broken package manager state
- conflicting Docker package sources
- ambiguous Docker installation
- Docker daemon fails after documented reconciliation
- Docker socket permissions are unsafe or untrusted
- Compose path is ambiguous or broken

The classification priority remains unchanged:

```text
BLOCKED > SANEABLE > COMPATIBLE > CLEAN
```

## 8. Documentation Change Record

This extension does not remove any recovered HOST Slice 01 content.

The only semantic change is that Docker installation and Docker normalization are no longer globally deferred. They are now:

- out of scope for Slice 01
- in scope for Slice 02
- governed by this extension and the aligned HOST TDD, HOST Contract, and AUDIT VPS Spec updates
