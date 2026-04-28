# HOST Slice 02 — Docker / Docker Compose Runtime Addendum

## 1. Purpose

This addendum defines the proposed **HOST Slice 02 — Docker / Docker Compose Runtime Baseline**.

It extends the current HOST Phase 1 documentation without replacing, compressing, or weakening any previously approved HOST baseline content.

The purpose of this slice is to make the host runtime ready for later DEPLOY operations by ensuring that Docker Engine and Docker Compose are installed, available, active, and validated through deterministic Python-controlled runtime checks.

This addendum exists to prevent undocumented expansion of HOST responsibilities and to define the exact documentation upgrade path before modifying canonical HOST documents.

---

## 2. Status

**Status:** Proposed Addendum  
**Target module:** HOST  
**Target phase:** Phase 1 HOST  
**Target slice:** Slice 02  
**Canonical merge target:** HOST baseline documentation set

This addendum is not a replacement for the current HOST baseline.

Until merged into the canonical HOST documents, this addendum is a controlled extension proposal.

After approval and merge, the canonical source of truth must remain the main HOST documents:

- `HOST_BASELINE_FDD.md`
- `HOST_BASELINE_TDD.md`
- `HOST_BASELINE_CONTRACT.md`
- `AUDIT_VPS_SPEC.md`

This addendum may remain in the repository as historical change documentation after its contents are merged.

---

## 3. Documentation Non-Regression Rule

This addendum MUST follow the project documentation rule:

> Apply a strict no-regression by extension-only rule to all documentation work. Preserve all previously approved valid normative content unless explicitly authorized for removal or replacement. Do not compress, overwrite, simplify, or rewrite an existing baseline document in a way that silently removes scope, guarantees, constraints, inputs, commands, validation logic, safety rules, or documented responsibility boundaries. Any update must be additive, or explicitly marked as a replacement of specific prior content. If prior content is moved, deprecated, narrowed, or removed, state exactly what changed, why it changed, and where the new canonical definition now lives. Default mode is EXTEND, never COMPRESS.

This rule applies to all future integration of this addendum into canonical HOST documentation.

---

## 4. Relationship to Current HOST Baseline

The current HOST baseline remains valid and unchanged.

Current HOST Slice 01 is focused on:

- host audit
- host classification
- operator user reconciliation
- operator SSH access filesystem preparation
- runtime validation of the current in-scope slice
- separation of hardening into `harden-vps`

This addendum does not alter Slice 01.

This addendum proposes a new Slice 02 that extends `init-vps` and `audit-vps` to support Docker / Docker Compose runtime readiness.

### Current baseline preservation

The following existing HOST guarantees remain intact:

- `audit-vps` remains read-only.
- `init-vps` remains gated by audit/classification.
- `init-vps` remains slice-based.
- HOST does not assume a clean VPS.
- HOST must inspect real runtime state before mutation.
- HOST must fail closed on ambiguous or unsafe state.
- HOST must not claim success without runtime validation.
- HOST must not perform undocumented mutation.
- HOST must not absorb PROJECT, DEPLOY, or OPERATE responsibilities.

---

## 5. Slice Name and Intent

### Slice name

`HOST Slice 02 — Docker / Docker Compose Runtime Baseline`

### Intent

This slice prepares the VPS host with a validated container runtime baseline required by DEPLOY.

The slice ensures that:

- Docker Engine is installed or safely installed when absent.
- Docker daemon is available and active.
- Docker CLI is usable.
- Docker Compose plugin is installed or safely installed when absent.
- Docker Compose command is usable through `docker compose`.
- The runtime state is validated before success is reported.

### Core principle

HOST prepares the runtime.  
DEPLOY consumes the runtime.

HOST must not deploy application workloads as part of this slice.

---

## 6. Scope

The proposed Slice 02 scope includes:

- detecting Docker Engine installation state
- detecting Docker daemon state
- detecting Docker CLI availability
- detecting Docker Compose plugin availability
- installing Docker Engine when missing and safely supported
- installing Docker Compose plugin when missing and safely supported
- enabling and starting Docker service where required and safe
- validating Docker runtime with deterministic commands
- validating Docker Compose availability
- classifying Docker-related host states as `CLEAN`, `COMPATIBLE`, `SANEABLE`, or `BLOCKED`
- integrating Docker checks into `audit-vps`
- integrating Docker reconciliation into `init-vps`
- preserving clear boundary with DEPLOY

---

## 7. Out of Scope

Slice 02 MUST NOT perform application deployment.

The following are explicitly out of scope:

- creating application directories
- generating `project.yaml`
- generating application `compose.yaml`
- building application images
- pulling application images
- starting application containers
- stopping application containers
- restarting application containers
- managing application networks beyond Docker default runtime readiness
- managing application volumes
- managing app `.env` files
- registry authentication
- pushing images
- reverse proxy configuration
- TLS certificate management
- app smoke testing
- N8N/FastAPI/PostgreSQL stack creation
- OPERATE backup/audit behavior
- broad host hardening unrelated to Docker runtime availability

Those responsibilities belong to PROJECT, DEPLOY, OPERATE, or future explicitly documented slices.

---

## 8. Supported Runtime Assumptions

Slice 02 targets Linux VPS environments supported by the HOST baseline.

The initial expected supported OS family is Ubuntu, aligned with the existing HOST audit model.

Supported CPU architectures should remain aligned with the current HOST audit baseline unless explicitly extended.

No Docker behavior may be assumed without runtime evidence.

---

## 9. Docker Installation Policy

Slice 02 may install Docker Engine when all of the following are true:

- Docker is absent.
- The operating system is supported.
- The architecture is supported.
- Required package manager operations are available.
- No conflicting Docker installation is detected.
- Installation can be performed through documented Python-controlled subprocess execution.
- Post-install runtime validation can be performed.

Slice 02 must not blindly overwrite or remove an existing Docker installation.

If Docker exists in a conflicting, ambiguous, partial, or unsupported state, the host must be classified as `BLOCKED` unless a safe documented normalization path exists.

---

## 10. Docker Compose Policy

The preferred Compose interface for this framework is:

```bash
docker compose
```

This means the expected baseline is the Docker Compose plugin, not the legacy standalone `docker-compose` binary.

Slice 02 may install the Docker Compose plugin when all of the following are true:

- Docker Engine is installed or safely installable.
- The Compose plugin is absent.
- The OS and package source support plugin installation.
- No conflicting Compose state prevents safe installation.
- Post-install validation can confirm `docker compose version`.

The legacy `docker-compose` binary may be detected as evidence, but it is not the canonical Compose interface for the baseline unless explicitly approved in a future contract update.

---

## 11. Operator Docker Access Policy

This addendum does not automatically approve broad Docker permission changes unless explicitly merged into the HOST contract.

Docker group membership for the operator user is a sensitive privilege boundary.

The recommended default for Slice 02 is:

- Docker daemon and Compose availability are required.
- Root/sudo-based Docker validation may be used where appropriate.
- Adding the operator user to the `docker` group must be explicitly documented if enabled.

If operator Docker group membership is included in the final slice, the canonical documents must define:

- when the group is created or reused
- when the operator is added
- whether session refresh is required
- how validation is performed
- what is considered `SANEABLE` vs `BLOCKED`
- how privilege implications are documented

Until explicitly merged, Docker group membership remains a policy decision, not an assumed behavior.

---

## 12. Audit Impact

Slice 02 requires extending `audit-vps` with read-only Docker runtime checks.

`audit-vps` must remain read-only.

### Proposed Docker audit check groups

Recommended new group:

- `DOCKER`

Recommended checks:

- `CHECK_DOCKER_01` — Docker CLI availability
- `CHECK_DOCKER_02` — Docker daemon/service state
- `CHECK_DOCKER_03` — Docker runtime usability
- `CHECK_DOCKER_04` — Docker Compose plugin availability
- `CHECK_DOCKER_05` — Conflicting or partial Docker installation state

### Required evidence examples

Potential evidence commands:

```bash
docker --version
systemctl is-active docker
docker info
docker compose version
which docker
```

Implementation may choose equivalent deterministic commands, but they must be documented in `AUDIT_VPS_SPEC.md` before implementation.

### Audit constraints

Docker audit checks MUST NOT:

- install Docker
- start Docker
- enable Docker
- modify package repositories
- modify groups or users
- modify files
- create containers
- pull images
- run long-lived containers

---

## 13. Classification Impact

Docker-related checks must feed the canonical HOST classification model:

- `CLEAN`
- `COMPATIBLE`
- `SANEABLE`
- `BLOCKED`

### CLEAN

Use when Docker-relevant state is minimal or absent and no conflict is detected, assuming the slice can safely install Docker.

Example:

- Docker not installed.
- No conflicting packages detected.
- Host is supported.
- Package manager state appears usable.

### COMPATIBLE

Use when Docker runtime already satisfies the expected baseline.

Example:

- Docker CLI exists.
- Docker daemon is active.
- `docker info` succeeds.
- `docker compose version` succeeds.

### SANEABLE

Use when Docker state is incomplete but can be safely normalized by Slice 02.

Examples:

- Docker absent but safely installable.
- Compose plugin absent but safely installable.
- Docker service installed but inactive and safe to start.
- Docker installed but minor service enablement is needed.

### BLOCKED

Use when Docker state is unsafe, ambiguous, unsupported, or cannot be normalized deterministically.

Examples:

- unsupported OS for Docker installation
- unsupported architecture
- broken package manager state
- conflicting Docker packages or repositories
- Docker CLI exists but daemon state cannot be trusted
- Docker daemon fails to start
- `docker info` fails in a way that cannot be safely resolved
- Compose installation path is ambiguous
- permission model cannot be safely validated

### Priority rule

Classification priority remains:

```text
BLOCKED > SANEABLE > COMPATIBLE > CLEAN
```

---

## 14. `init-vps` Impact

Slice 02 extends `init-vps` as a controlled reconciliation pipeline after the current Slice 01 prerequisites are satisfied.

### Proposed execution position

Recommended order:

1. explicit input validation
2. audit/classification gate
3. Slice 01 — operator user and SSH access filesystem reconciliation
4. Slice 01 post-action validation
5. Slice 02 — Docker / Compose runtime reconciliation
6. Slice 02 post-action validation
7. final decision rendering
8. deterministic exit code emission

### Precondition

Slice 02 may execute only when:

- host classification is not `BLOCKED`
- Slice 01 prerequisites are satisfied or already compatible
- OS and architecture are supported
- Docker-related state is `CLEAN`, `COMPATIBLE`, or `SANEABLE`
- required package manager operations are available where installation is needed

### Allowed mutation

Slice 02 may perform only documented Docker runtime baseline mutations, such as:

- install Docker Engine when absent and safely supported
- install Docker Compose plugin when absent and safely supported
- enable Docker service when required and safe
- start Docker service when required and safe
- apply explicitly documented minimal package repository setup if required by the chosen install method

### Forbidden mutation

Slice 02 MUST NOT:

- remove unknown Docker installations blindly
- overwrite custom Docker daemon configuration blindly
- delete containers
- delete images
- delete volumes
- delete networks
- deploy apps
- create app-specific Compose projects
- mutate unrelated host services
- perform undocumented package repair
- silently change operator privilege model
- claim success without runtime validation

---

## 15. Validation Requirements

Slice 02 success requires runtime validation.

At minimum, post-action validation must confirm:

- Docker CLI is available.
- Docker daemon/service is active or otherwise usable according to documented policy.
- Docker runtime responds successfully.
- Docker Compose plugin is available through `docker compose`.
- Docker Compose version can be read.

Recommended validation commands:

```bash
docker --version
docker info
docker compose version
```

If systemd is part of the supported runtime model, validation may also include:

```bash
systemctl is-active docker
systemctl is-enabled docker
```

Validation must be performed via Python-controlled subprocess execution.

If any required validation fails, Slice 02 fails.

Success reporting without effective runtime validation is forbidden.

---

## 16. Error and Abort Rules

Slice 02 must fail closed.

Execution must stop if:

- host classification is `BLOCKED`
- Docker state is ambiguous
- install method cannot be selected deterministically
- package manager operation fails
- Docker daemon cannot be started or trusted
- Docker CLI validation fails
- Docker Compose validation fails
- runtime validation cannot be completed
- the operation would require undocumented mutation

No fallback heuristics are allowed for ambiguous Docker states.

---

## 17. DEPLOY Boundary

This slice exists because DEPLOY requires a working container runtime.

HOST responsibilities:

- prepare Docker runtime availability
- prepare Docker Compose availability
- validate runtime readiness
- report deterministic success/failure

DEPLOY responsibilities:

- read project configuration
- locate deployment artifacts
- use Docker/Compose runtime
- build or pull application images where documented
- start application services
- perform deployment smoke checks
- report deployment status

DEPLOY MUST NOT install or repair Docker as a hidden side effect once Slice 02 becomes part of the HOST baseline.

If Docker runtime is missing or invalid during DEPLOY, DEPLOY should fail with a clear message pointing back to HOST prerequisites.

---

## 18. Proposed Repository Impact

Recommended new or extended modules:

```text
framework/modules/host/audit/checks/docker.py
framework/modules/host/init/reconcile_docker.py
framework/modules/host/init/validate_docker.py
```

Recommended tests:

```text
tests/test_audit_docker_checks.py
tests/test_init_reconcile_docker.py
tests/test_init_validate_docker.py
tests/test_init_runner_docker_slice.py
```

These names are guidance only. Final implementation structure must remain aligned with the canonical TDD after merge.

---

## 19. Documentation Merge Plan

This addendum must be integrated in canonical documentation order.

### 19.1 `HOST_BASELINE_FDD.md`

Add an explicit functional section for:

- Slice 02 — Docker / Docker Compose Runtime Baseline
- updated HOST Phase 1 scope
- Docker as runtime preparation responsibility
- clear boundary with DEPLOY
- preserved Slice 01 behavior

Do not delete or compress existing Slice 01 content.

### 19.2 `HOST_BASELINE_TDD.md`

Add technical design sections for:

- Docker audit checks
- Docker reconciliation modules
- Docker validation modules
- Slice 02 execution flow
- subprocess and validation behavior
- safety and abort model for Docker states

Do not replace existing user/SSH slice architecture.

### 19.3 `HOST_BASELINE_CONTRACT.md`

Extend the executable contract with:

- Docker/Compose runtime guarantees
- allowed Docker mutations
- forbidden Docker mutations
- Docker validation contract
- Docker-specific abort rules
- DEPLOY boundary rule

Do not weaken current explicit input, classification, idempotency, or validation rules.

### 19.4 `AUDIT_VPS_SPEC.md`

Extend audit specification with:

- Docker check group
- specific Docker check ids
- evidence commands
- parsing expectations
- classification impacts
- output requirements

Remove Docker from deferred check families only after the canonical documents approve Slice 02 as current executable scope.

### 19.5 `DEPLOY_BASELINE_CONTRACT.md` and `DEPLOY_PROJECT_SPEC.md`

If Slice 02 becomes canonical, DEPLOY docs should be updated only to clarify that Docker/Compose runtime is a HOST prerequisite and DEPLOY must not silently install Docker.

No DEPLOY behavior should be moved into HOST.

---

## 20. Acceptance Criteria for the Addendum

This addendum is ready for canonical merge only when all of the following are true:

- Scope is approved.
- Out-of-scope boundaries are approved.
- Docker install policy is approved.
- Compose plugin policy is approved.
- Operator Docker access policy is explicitly decided.
- Audit classification rules are approved.
- `init-vps` mutation rules are approved.
- Runtime validation requirements are approved.
- DEPLOY boundary is approved.
- No current HOST Slice 01 guarantees are removed or weakened.

---

## 21. Open Decisions Before Merge

The following decisions must be resolved before this addendum is merged into canonical docs:

1. Should HOST install Docker Engine from the official Docker repository, Ubuntu packages, or a documented framework-approved method?
2. Should HOST install the Compose plugin only, or also tolerate legacy `docker-compose` as compatible evidence?
3. Should HOST add the operator user to the `docker` group?
4. If operator group membership is enabled, how should session refresh and validation be handled?
5. Should Docker service enablement be mandatory or only daemon runtime availability?
6. What exact Ubuntu versions are supported for Docker Slice 02?
7. What package manager failure states are `BLOCKED` vs retryable runtime errors?
8. Should Docker daemon configuration files be considered out of scope unless absent/default?

Until these are resolved, this addendum should not be merged as current executable baseline.

---

## 22. Final Statement

HOST Slice 02 must evolve the HOST baseline without damaging the current approved documentation.

The correct model is:

- preserve Slice 01
- add Docker / Compose as Slice 02
- keep `audit-vps` read-only
- keep `init-vps` gated and validated
- keep DEPLOY separate
- validate runtime state before success
- merge documentation from higher-level documents downward

This addendum defines the controlled path for adding Docker and Docker Compose to HOST Phase 1 while preserving the existing baseline and preventing documentation regression.
