# FRAMEWORK ARCHITECTURE MODEL

## 1. Purpose

This document defines the **official architecture model** of the VPS framework.

The framework is organized into four functional domains:

- HOST
- PROJECT
- DEPLOY
- OPERATE

This model defines the stable architectural separation of concerns for v1.

Its purpose is to:

- enforce domain boundaries
- avoid responsibility overlap
- support incremental delivery without redesign
- preserve consistency between documentation, implementation, and operation
- reduce long-term technical debt

---

## 2. Core Principle

Each module is a **functional domain**, not merely a directory or a script collection.

This implies:

- each module has a clearly defined responsibility
- each command belongs to exactly one domain
- domains must not overlap responsibilities
- implementation order follows real dependency order between domains

---

## 3. Engineering Governance (Hard Rules)

The framework is governed by the following non-negotiable rules:

### 3.1 Implementation Language

The framework MUST be implemented in:

→ **Python**

Implications:

- all CLI commands are implemented in Python
- business logic resides in Python
- classification, reconciliation, and validation logic reside in Python

### 3.2 Bash Usage Policy

Bash is NOT an implementation language.

Bash MAY only be used as:

→ a system command executed from Python

Forbidden:

- Bash scripts containing framework logic
- delegating decision-making to shell scripts

### 3.3 AI-Assisted Development

The official AI development tool is:

→ **Codex (GPT)**

Implications:

- implementation work is prompt-driven
- documentation MUST be machine-consumable
- prompts MUST define context, scope, constraints, and expected output

### 3.4 Prompt-Driven Engineering

Implementation MUST follow:

→ **explicit prompt contracts**

This ensures:

- deterministic outputs
- no hidden assumptions
- traceability between design and code

### 3.5 Documentation as Source of Truth

Documentation is:

→ **prescriptive and executable**

This means:

- code MUST follow documentation
- undocumented behavior is not allowed
- documents MUST be consumable by both humans and Codex

---

## 4. Documentation Hierarchy

This document governs the **macro architecture** of the framework.

More specific behavior is governed by lower-level documents.

For HOST work, the intended hierarchy is:

1. `FRAMEWORK_ARCHITECTURE_MODEL.md`
2. `ENGINEERING_RULES.md`
3. `HOST_BASELINE_FDD.md`
4. `HOST_BASELINE_TDD.md`
5. `HOST_BASELINE_CONTRACT.md`
6. `AUDIT_VPS_SPEC.md`
7. `PYTHON_IMPLEMENTATION_BASELINE.md`
8. `CODEX_DEVELOPMENT_PROTOCOL.md`

Rules:

- higher-level documents define stable intent and boundaries
- lower-level documents derive executable details
- lower-level documents MUST NOT contradict higher-level documents
- if conflict exists, the higher-level document prevails until the lower-level document is corrected

---

## 5. Architecture Overview

The framework is structured as:

HOST → PROJECT → DEPLOY → OPERATE

### Dependency Flow

- PROJECT depends on HOST
- DEPLOY depends on PROJECT
- OPERATE depends on DEPLOY

This dependency flow is mandatory.

---

## 6. Module Definitions

## MODULE 1 — HOST

### Definition

Responsible for preparing, evaluating, normalizing, validating, and securing the server baseline.

### Scope

Transforms a heterogeneous VPS into a predictable and reliable host baseline.

### Responsibilities

- inspect current host state
- classify host condition (`CLEAN`, `COMPATIBLE`, `SANEABLE`, `BLOCKED`)
- reconcile host state when safe and in scope
- validate achieved runtime state
- apply post-initialization hardening

### Commands

- `audit-vps`
- `init-vps`
- `harden-vps`

### Delivery Rule

HOST capabilities MAY be delivered incrementally through documented slices.

This architecture document defines HOST ownership and boundaries.
It does NOT define the exact implementation scope of the current HOST slice.
That detail belongs to HOST FDD, HOST TDD, HOST contract, and HOST specs.

### Boundary Rule

HOST:

- does NOT create projects
- does NOT deploy application stacks
- does NOT perform runtime project operations belonging to OPERATE

---

## MODULE 2 — PROJECT

### Definition

Responsible for creating a standardized project scaffold.

### Responsibilities

- create project structure
- apply naming conventions
- generate base files
- prepare templates

### Command

- `new-project`

### Boundary Rule

PROJECT does not:

- modify host baseline
- deploy services

---

## MODULE 3 — DEPLOY

### Definition

Responsible for deploying the project stack.

### Responsibilities

- validate deployable structure
- load environment variables
- build and start services
- run smoke tests

### Command

- `deploy-project`

---

## MODULE 4 — OPERATE

### Definition

Responsible for operational continuity and runtime control.

### Responsibilities

- audit project health
- verify runtime state
- execute backups
- support recurring operational checks

### Commands

- `audit-project`
- `backup-project`

---

## 7. Command Ownership

Each command belongs to exactly one module:

- `audit-vps` → HOST
- `init-vps` → HOST
- `harden-vps` → HOST
- `new-project` → PROJECT
- `deploy-project` → DEPLOY
- `audit-project` → OPERATE
- `backup-project` → OPERATE

---

## 8. Design Constraints

The full framework MUST preserve:

- runtime validation
- no cosmetic success
- idempotency where applicable
- deterministic behavior
- explicit abort on ambiguity
- no cross-module responsibility leakage

---

## 9. Implementation Model

The framework is implemented as:

- a Python-based CLI application
- a modular internal architecture
- a set of explicit contracts and specs

System interaction is performed via:

- controlled subprocess execution
- explicit parsing and validation

---

## 10. Evolution Rule

Any change to:

- architecture
- command ownership
- cross-module boundaries
- implementation model

MUST be:

- documented
- reviewed
- aligned with engineering rules

Architectural changes MUST NOT be smuggled in through lower-level documents.

---

## 11. Final Statement

This document defines the **official macro architecture** of the framework.

The framework is a:

→ **modular, Python-based, AI-assisted platform**

with stable domain order:

HOST → PROJECT → DEPLOY → OPERATE

This structure is frozen for v1 unless an explicit architectural review approves change.
