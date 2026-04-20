# PROJECT BASELINE CONTRACT

## 1. Purpose

This document defines the **current executable contract** of the PROJECT module baseline.

It establishes:

- what the current PROJECT baseline guarantees
- how a target path is evaluated for scaffold creation
- which actions are currently allowed
- which actions are currently forbidden
- how success is determined

This contract is the executable bridge between PROJECT design documents and implementation.

---

## 2. Role in Documentation Hierarchy

This contract is governed by:

- `FRAMEWORK_ARCHITECTURE_MODEL.md`
- `ENGINEERING_RULES.md`
- `PROJECT_BASELINE_FDD.md`
- `PROJECT_BASELINE_TDD.md`

This contract governs, at the executable level:

- `new-project`
- `NEW_PROJECT_SPEC.md`

If this contract conflicts with the PROJECT FDD or PROJECT TDD, this contract MUST be corrected.

---

## 3. Core Principle

The PROJECT module does NOT assume an empty target path.

The default case is a:

→ **real local filesystem workspace**

All behavior must be based on:

- explicit input validation
- real target path inspection
- deterministic classification
- safe scaffold generation
- runtime validation

No step is considered successful unless it is validated at runtime.

---

## 4. Engineering Alignment

### 4.1 Implementation Language

All PROJECT logic MUST be implemented in:

→ **Python**

This includes:

- input normalization
- target inspection
- classification logic
- scaffold planning
- scaffold rendering
- validation logic

### 4.2 Filesystem Interaction Model

PROJECT inspection and scaffold generation MUST be performed through:

→ **Python-native filesystem operations**

Preferred primitives include:

- `pathlib`
- `os`
- controlled file I/O
- limited standard-library helpers where explicitly justified

### 4.3 Shell Policy

Shell is NOT part of the baseline implementation model for PROJECT.

Forbidden:

- `.sh` scripts containing scaffold logic
- delegating scaffold decisions to shell scripts
- depending on shell path expansion for correctness

### 4.4 Determinism Rule

Given the same inputs and the same target filesystem state:

→ PROJECT decisions and outcomes MUST be identical

---

## 5. Current Scope of This Contract

This contract describes the **current executable PROJECT baseline**, not the full future PROJECT vision.

### Current executable focus

At this stage, the enforceable PROJECT baseline consists of:

- explicit project identity input validation
- target path inspection
- target classification sufficient for safe scaffold generation
- first scaffold baseline for `new-project`
- runtime validation of that scaffold baseline

### Non-goal of this contract

This contract does NOT claim that every future stack profile, template, or generated asset is already implemented.

Future PROJECT slices may expand the contract, but only through explicit documentation updates.

---

## 6. Explicit Inputs

The current PROJECT contract depends on explicit inputs.

These include, where applicable:

- project name
- target path
- optional project slug
- optional project description
- template identifier when multiple templates exist

### Rule

A fixed hardcoded project identity is NOT part of the intended contract baseline.

Implementation MUST NOT silently assume a specific project name or path unless a temporary bounded contract explicitly states it.

### Deterministic Slug Rule

If slug input is omitted, slug derivation is allowed only by a documented deterministic rule.
Undocumented slug generation is forbidden.

---

## 7. Target Classification Model

Every target path MUST be classified before any scaffold mutation.

### Allowed categories

#### CLEAN
- target path is absent or empty
- no conflicting conditions detected

#### COMPATIBLE
- existing scaffold state is aligned and safe to reuse

#### SANEABLE
- existing scaffold state is partial but can be completed safely without destructive behavior

#### BLOCKED
- conflicting or ambiguous state
- safe scaffold generation cannot proceed
- manual intervention is required

### Priority Rule

If multiple conditions exist, priority MUST be:

`BLOCKED > SANEABLE > COMPATIBLE > CLEAN`

---

## 8. Mandatory Flow

All PROJECT mutation-capable operations MUST follow:

1. Input Validation
2. Target Inspection
3. Classification
4. Plan
5. Execution (if allowed)
6. Runtime Validation

Skipping required steps is forbidden.

---

## 9. `new-project` Contract

### Definition

`new-project` performs **deterministic project scaffold creation**.

### Guarantees

It MUST:

- validate explicit inputs
- inspect real target path state
- compute a deterministic target classification
- create or reuse only the managed scaffold items allowed by the current baseline
- avoid destructive overwrite
- produce structured results sufficient for deterministic output
- validate the final scaffold at runtime

### Current minimum scaffold scope

The current executable scaffold baseline MUST at minimum manage:

- root target directory
- baseline directories: `app/`, `config/`, `deploy/`, `docs/`, `operate/`, `tests/`
- baseline files: `.env.example`, `.gitignore`, `README.md`, `compose.yaml`, `project.yaml`

### `project.yaml` contract

`project.yaml` MUST exist after successful scaffold generation and MUST contain at minimum:

- project name
- project slug
- template identifier
- template version
- generator command identity

### Allowed expansion

Additional generated assets MAY exist only when:

- they are documented
- they do not silently redefine the current scaffold baseline
- they preserve safe overwrite and validation guarantees

### Output model

The command result MUST make clear at minimum:

- target classification
- whether the scaffold was created, completed, reused, or blocked
- which managed paths were created or reused
- whether runtime validation passed

---

## 10. Mutation Policy

### Managed mutation rule

Within the current baseline, `new-project` MAY mutate only:

- the target root directory when safely creatable
- required baseline managed directories
- required baseline managed files
- missing compatible managed paths in saneable or compatible scaffold states

### Preserve rule

It MUST preserve:

- unrelated existing files
- already-correct managed content
- compatible scaffold state that does not require change

### Overwrite rule

It MUST NOT:

- overwrite conflicting existing managed files blindly
- rewrite unmanaged user content
- proceed through ambiguous metadata mismatch
- claim a safe scaffold when compatibility cannot be proven

---

## 11. Runtime Validation Contract

Every critical in-scope step MUST be validated via Python.

### Required current validation checks

For the current `new-project` baseline, validation MUST confirm:

- target root exists
- required baseline directories exist
- required baseline files exist
- `project.yaml` exists
- `project.yaml` metadata matches intended project identity
- no required managed path is missing

### Failure Rule

If any required in-scope validation fails:

→ the current operation is **FAILED**

Success reporting without effective state validation is forbidden.

---

## 12. Identity and Metadata Policy

### Project identity rule

The requested project identity MUST be explicit and stable for the lifecycle of a scaffold.

### Metadata compatibility rule

If `project.yaml` already exists, it MUST be treated as authoritative scaffold metadata for compatibility checks.

The command MUST block when:

- requested slug conflicts with existing metadata
- requested template conflicts with existing metadata
- metadata is malformed or ambiguous
- the target appears scaffolded but lacks enough trustworthy metadata to prove compatibility

---

## 13. Environment and Platform Contract

PROJECT is a local scaffold domain.

It is expected to work across supported local development platforms, including:

- Windows
- Linux
- macOS

### Platform rule

The contract is satisfied by deterministic Python-native filesystem behavior, not by shell-specific behavior.

---

## 14. Idempotency

Where applicable:

- operations MUST be safe to re-run
- compatible state MUST be reused
- saneable partial scaffold MAY be completed
- destructive repetition is forbidden
- conflicting scaffold state MUST block rather than be guessed through

---

## 15. Abort Rules

Execution MUST stop if:

- required inputs are invalid
- classification is `BLOCKED`
- scaffold metadata is ambiguous
- conflicting existing managed content is detected
- required parent path is not safely writable
- post-action validation fails
- runtime execution failure prevents trustworthy completion

---

## 16. Success Criteria

The current PROJECT baseline is valid only if:

- target classification is resolved deterministically
- in-scope baseline scaffold actions complete safely
- required runtime validation passes
- no out-of-scope mutation was required or silently introduced

---

## 17. Forbidden Behavior

Forbidden:

- implicit project identity assumptions
- blind overwrite
- undocumented mutation
- skipping validation
- reporting success without runtime verification
- shell-driven scaffold logic
- non-deterministic scaffold generation

---

## 18. Evolution Rule

This contract MAY expand in future documented PROJECT slices.

However:

- new obligations must be documented first
- future-slice requirements MUST NOT be retroactively treated as already implemented
- lower-level specs must remain aligned with this contract

---

## 19. Final Statement

The current PROJECT contract defines a:

- Python-based
- deterministic
- filesystem-driven
- baseline-bounded
- runtime-validated

foundation for PROJECT execution.

It is mandatory for the current stage and must remain aligned with the PROJECT FDD and PROJECT TDD.
