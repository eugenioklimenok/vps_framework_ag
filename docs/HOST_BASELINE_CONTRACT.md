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

# HOST BASELINE CONTRACT

## 1. Purpose

This document defines the **current executable contract** of the HOST module baseline.

It establishes:

- what the current HOST baseline guarantees
- how a host is evaluated for the current slice
- which actions are currently allowed
- which actions are currently forbidden
- how success is determined

This contract is the executable bridge between HOST design documents and implementation.

---

## 2. Role in Documentation Hierarchy

This contract is governed by:

- `FRAMEWORK_ARCHITECTURE_MODEL.md`
- `ENGINEERING_RULES.md`
- `HOST_BASELINE_FDD.md`
- `HOST_BASELINE_TDD.md`

This contract governs, at the executable level:

- `audit-vps`
- `init-vps`
- `harden-vps` expectations for the current baseline stage
- `AUDIT_VPS_SPEC.md`

If this contract conflicts with the HOST FDD or HOST TDD, this contract MUST be corrected.

---

## 3. Core Principle

The HOST module does NOT assume a clean environment.

The default case is a:

→ **heterogeneous VPS**

All behavior must be based on:

- real system inspection
- explicit classification
- safe reconciliation
- runtime validation

No step is considered successful unless it is validated at runtime.

---

## 4. Engineering Alignment

### 4.1 Implementation Language

All HOST logic MUST be implemented in:

→ **Python**

This includes:

- audit logic
- classification logic
- reconciliation logic
- validation logic

### 4.2 System Interaction Model

System inspection and mutation MUST be performed through:

→ Python-controlled subprocess execution

Shell commands are evidence or execution mechanisms controlled by Python.
They are not an independent implementation layer.

### 4.3 Bash Policy

Bash is NOT allowed as an implementation layer.

Forbidden:

- `.sh` scripts containing framework logic
- delegating decisions to shell scripts

### 4.4 Determinism Rule

Given the same inputs and same host state:

→ HOST decisions and outcomes MUST be identical

---

## 5. Current Scope of This Contract

This contract describes the **current executable HOST baseline**, not the full future HOST vision.

### Current executable focus

At this stage, the enforceable HOST baseline consists of:

- read-only host audit
- host classification sufficient for safe gating
- first controlled `init-vps` reconciliation slice
- runtime validation of that slice
- separate post-initialization hardening responsibility

### Non-goal of this contract

This contract does NOT claim that full host convergence is already implemented.

Future HOST slices may expand the contract, but only through explicit documentation updates.

---

## 6. Explicit Inputs

The current HOST contract depends on explicit inputs.

These include, where applicable:

- operator user identity
- target public key or equivalent key source

### Rule

A fixed hardcoded operator identity is NOT part of the intended contract baseline.

Implementation MUST NOT silently assume a specific operator user unless a temporary bounded contract explicitly states it.

---

## 7. Host Classification Model

Every host MUST be classified before any mutation.

### Allowed categories

#### CLEAN
- minimal relevant prior state
- no conflicting conditions detected

#### COMPATIBLE
- existing state is aligned and safe to reuse

#### SANEABLE
- existing state is not yet aligned but can be normalized safely without destructive behavior

#### BLOCKED
- unsafe or ambiguous state
- safe automation cannot proceed
- manual intervention is required

### Priority Rule

If multiple conditions exist, priority MUST be:

`BLOCKED > SANEABLE > COMPATIBLE > CLEAN`

---

## 8. Mandatory Flow

All HOST mutation-capable operations MUST follow:

1. Inventory
2. Classification
3. Decision
4. Execution (if allowed)
5. Runtime Validation

Skipping required steps is forbidden.

---

## 9. `audit-vps` Contract

### Definition

`audit-vps` performs a **read-only audit** of the host.

### Guarantees

It MUST:

- avoid all mutation
- operate through Python-controlled evidence collection
- collect real runtime evidence
- produce structured results
- compute a deterministic final classification

### Current minimum audit scope

The current executable audit baseline MUST at minimum evaluate evidence for:

- supported operating system
- supported CPU architecture
- SSH daemon syntax viability
- effective SSH key-auth capability
- operator user state
- operator SSH access filesystem state
- additional essential safety signals needed to avoid ambiguous reconciliation

### Allowed expansion

Additional audit checks MAY exist only when:

- they remain read-only
- they are documented
- they do not silently redefine the gating behavior of the current baseline

### Output model

Each audit check MUST include at minimum:

- identifier
- category
- status (`OK`, `WARN`, `FAIL`)
- message
- evidence
- classification impact

---

## 10. `init-vps` Contract

### Definition

`init-vps` initializes or normalizes the host baseline through a controlled reconciliation pipeline.

### Precondition

- prior `audit-vps` execution OR equivalent internal gate logic
- explicit inputs available for the current slice
- no `BLOCKED` host classification

### Current executable slice

The current contract for `init-vps` is limited to the first controlled reconciliation slice.

### MUST

Within the current slice, `init-vps` MUST:

- create or reuse the operator user safely
- ensure the expected operator home exists in compatible form
- ensure `.ssh` exists for the operator
- ensure `authorized_keys` exists
- ensure the target public key is present
- preserve unrelated existing keys
- ensure safe ownership and permissions for in-scope paths
- validate all in-scope outcomes at runtime

### MUST NOT

Within the current slice, `init-vps` MUST NOT:

- assume a clean system
- overwrite unknown state blindly
- destroy unrelated data
- continue if classification is `BLOCKED`
- continue through ambiguous user or filesystem state
- claim success without post-action validation

### Explicitly out of scope for the current slice

The following are NOT part of the current executable `init-vps` contract:

- Docker installation
- Docker normalization
- package installation or repair
- timezone mutation
- UFW configuration
- `sshd_config` hardening changes
- password authentication disablement
- root login restriction
- broad operator directory scaffolding beyond SSH access preparation
- automated sudo policy enforcement
- automated NOPASSWD policy enforcement

These remain deferred to later slices or to `harden-vps`.

---

## 11. Runtime Validation Contract

Every critical in-scope step MUST be validated via Python.

### Required current validation checks

For the current `init-vps` slice, validation MUST confirm:

- operator user exists
- expected operator home exists
- `.ssh` exists
- `authorized_keys` exists
- ownership is correct for in-scope paths
- permissions are correct for in-scope paths
- target public key is present

### Failure Rule

If any required in-scope validation fails:

→ the current operation is **FAILED**

Success reporting without effective state validation is forbidden.

---

## 12. SSH Policy Contract

### During `init-vps`

`init-vps` prepares SSH key-based access but does NOT fully harden SSH.

It MUST:

- preserve or establish key-based access prerequisites for the operator
- validate SSH daemon syntax or effective viability where required by the current slice
- ensure safe ownership and permissions for in-scope SSH access paths

It MUST NOT:

- disable password authentication as part of the current slice
- restrict root login as part of the current slice
- introduce lockout-prone hardening behavior in initialization

### During `harden-vps`

Hardening-sensitive SSH policy belongs to `harden-vps`.

---

## 13. `harden-vps` Contract

### Definition

`harden-vps` applies post-initialization security hardening.

### Responsibilities

Where documented and implemented, this includes:

- password authentication disablement
- root login restriction
- stricter SSH policy enforcement

### Precondition

- host is not blocked
- initialization prerequisites are satisfied
- pre-hardening validation confirms safe state

---

## 14. Idempotency

Where applicable:

- operations MUST be safe to re-run
- compatible state MUST be reused
- destructive repetition is forbidden
- only safely saneable state may be normalized

---

## 15. Abort Rules

Execution MUST stop if:

- classification is `BLOCKED`
- ambiguity is detected
- contract guarantees cannot be satisfied
- post-action validation fails
- runtime execution failure prevents trustworthy completion

---

## 16. Success Criteria

The current HOST baseline is valid only if:

- classification is resolved deterministically
- in-scope current-slice actions complete safely
- required runtime validation passes
- no out-of-scope mutation was required or silently introduced

---

## 17. Forbidden Behavior

Forbidden:

- implicit assumptions
- blind overwrites
- undocumented mutation
- skipping validation
- reporting success without runtime verification
- hardcoded operator assumptions outside explicit contract
- non-deterministic behavior

---

## 18. Evolution Rule

This contract MAY expand in future documented HOST slices.

However:

- new obligations must be documented first
- future-slice requirements MUST NOT be retroactively treated as already implemented
- lower-level specs must remain aligned with this contract

---

## 19. Final Statement

The current HOST contract defines a:

- Python-based
- deterministic
- evidence-driven
- slice-bounded
- runtime-validated

baseline for HOST execution.

It is mandatory for the current stage and must remain aligned with the HOST FDD and HOST TDD.

---

# Approved Contract Extension — HOST Slice 02 Docker / Docker Compose Runtime Baseline

## 1. Contract Status

This section extends the current HOST executable contract.

It does not remove or weaken Slice 01.

## 2. Definition

Slice 02 prepares and validates Docker Engine and Docker Compose v2 as HOST runtime prerequisites for DEPLOY.

## 3. Preconditions

Slice 02 may execute only when:

- prior audit execution or equivalent internal gate logic has completed
- host classification is not `BLOCKED`
- Slice 01 prerequisites are satisfied or already compatible
- OS and architecture are supported for the Docker install policy
- Docker state is `CLEAN`, `COMPATIBLE`, or `SANEABLE`
- required package manager operations are available where installation is needed

## 4. MUST

Within Slice 02, `init-vps` MUST:

- install Docker Engine when absent and safely supported
- install Docker Compose v2 plugin when absent and safely supported
- reuse an existing compatible Docker runtime when already valid
- enable and start `docker.service` when required and safe
- reconcile operator Docker access when DEPLOY is expected to execute Docker as the operator user
- validate Docker CLI availability
- validate Docker daemon availability
- validate Docker Compose v2 availability through `docker compose`
- fail closed on ambiguous, conflicting, unsupported, or broken Docker state
- preserve DEPLOY as the owner of application workload execution

## 5. MUST NOT

Within Slice 02, `init-vps` MUST NOT:

- remove unknown Docker installations blindly
- overwrite custom Docker daemon configuration blindly
- delete containers, images, volumes, or networks
- create application Compose projects
- build or pull application images
- start application containers
- perform registry authentication
- configure reverse proxy or TLS
- perform application smoke testing
- perform unrelated package repair
- silently alter privilege model outside the documented operator Docker access rule

## 6. Required Runtime Validation

Slice 02 success requires runtime validation confirming:

```bash
docker --version
docker info
docker compose version
```

When systemd is part of the supported runtime model:

```bash
systemctl is-active docker
```

When DEPLOY is expected to run Docker as the operator user, validation MUST confirm operator Docker access in the intended execution context.

## 7. Classification Contract

Docker-related classification MUST follow:

- Docker absent but safely installable → `SANEABLE`
- Compose v2 absent but safely installable → `SANEABLE`
- Docker service stopped but safely startable → `SANEABLE`
- operator missing Docker group membership when required → `SANEABLE`
- Docker ready, daemon reachable, Compose v2 available, operator access valid → `COMPATIBLE`
- broken Docker daemon, conflicting Docker packages, ambiguous install source, unsupported OS/architecture, or untrusted socket permissions → `BLOCKED`

## 8. DEPLOY Boundary Contract

HOST owns Docker runtime preparation.

DEPLOY owns workload deployment.

DEPLOY MUST NOT silently install or repair Docker once this contract is active.

If Docker runtime prerequisites are missing during DEPLOY, DEPLOY must fail clearly and point back to HOST.

## 9. Documentation Change Record

This extension preserves the recovered HOST Contract.

Prior statements that Docker installation and Docker normalization were out of current scope are narrowed to mean out of Slice 01. Docker Engine and Docker Compose v2 are now part of the current executable HOST baseline through Slice 02.
