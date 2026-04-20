# PROJECT Baseline — Functional Design Document (FDD)

## 1. Purpose

This document defines the **functional behavior of the PROJECT module baseline** within the framework.

The PROJECT module is responsible for creating a standardized, deterministic, and validated project scaffold through:

- explicit input validation
- target path inspection
- deterministic target classification
- controlled scaffold generation
- post-generation validation

This document defines:

- what PROJECT does functionally
- which command belongs to PROJECT
- how PROJECT relates to the other framework domains
- what the current executable baseline includes
- what remains intentionally deferred

This document is prescriptive and must be treated as executable design input for PROJECT implementation.

---

## 2. Role in Documentation Hierarchy

For PROJECT work, this document defines the **functional source of truth**.

It is governed by:

- `FRAMEWORK_ARCHITECTURE_MODEL.md`
- `ENGINEERING_RULES.md`

It governs, functionally, the lower-level PROJECT documents:

- `PROJECT_BASELINE_TDD.md`
- `PROJECT_BASELINE_CONTRACT.md`
- `NEW_PROJECT_SPEC.md`

If a lower-level PROJECT document contradicts this FDD, the lower-level document MUST be corrected.

---

## 3. Functional Scope

PROJECT is the framework domain responsible for creating a standardized project scaffold.

### In Scope

- validate explicit project creation inputs
- inspect the requested target path
- classify the target state deterministically
- create a documented baseline scaffold when safe
- complete missing managed scaffold items when the target is compatible and saneable
- validate the generated scaffold after execution
- remain safe to re-run

### Out of Scope

- host inspection or host mutation
- package installation
- dependency installation
- container build or startup
- remote deployment
- DNS, TLS, or infrastructure provisioning
- runtime application audit
- backups and operational tasks
- secrets generation beyond placeholder/example files
- CI/CD platform integration unless a future documented slice adds it

---

## 4. Role in Framework Architecture

PROJECT is the second domain in the framework lifecycle:

`HOST → PROJECT → DEPLOY → OPERATE`

PROJECT depends on HOST being available as the baseline host domain, but PROJECT itself does **not** mutate host baseline state.

PROJECT prepares a project structure that later phases may consume:

- DEPLOY uses the scaffold as the deployable project basis
- OPERATE uses the scaffold outputs and conventions as the operational basis

---

## 5. Supported Command

The PROJECT module currently contains one functional command:

### `new-project`

Scaffold creation command.

Responsibilities:

- validate explicit project creation inputs
- inspect and classify the requested target location
- create the documented baseline scaffold when safe
- refuse unsafe or ambiguous overwrite situations
- validate that the scaffold was actually created successfully

---

## 6. Functional Model

All PROJECT behavior must follow the same mandatory flow:

1. Input Validation
2. Target Inspection
3. Target Classification
4. Scaffold Planning
5. Execution (if allowed)
6. Runtime Validation

No PROJECT command may skip required safety checks for its phase.

---

## 7. Target Classification Model

Project target evaluation is based on deterministic classification states.

### CLEAN

The target path is absent or empty and safe for scaffold creation.

### COMPATIBLE

The target path already contains a framework-compatible scaffold aligned with the requested project identity and safe to reuse.

### SANEABLE

The target path contains a partial but framework-compatible scaffold that can be completed safely without destructive overwrite.

### BLOCKED

The target path contains conflicting, ambiguous, or unsafe state that prevents safe scaffold creation or completion.

### Classification Priority

If multiple conditions are present, classification priority MUST be:

`BLOCKED > SANEABLE > COMPATIBLE > CLEAN`

---

## 8. Functional Behavior of `new-project`

### Purpose

`new-project` creates or completes a standardized project scaffold.

### Functional Guarantees

`new-project` MUST:

- require explicit project creation inputs
- inspect the real target path before writing files
- produce deterministic scaffold results from documented inputs
- avoid blind overwrite of conflicting user content
- create only the managed scaffold items in the current baseline
- validate the final scaffold after execution
- remain safe to re-run with the same intended project identity

### `new-project` MUST NOT:

- assume the target path is empty
- silently overwrite conflicting existing files
- mutate unrelated host or runtime state
- perform deployment behavior
- report success without post-generation validation

---

## 9. Current `new-project` Functional Scope

The current executable PROJECT baseline is the **first scaffold baseline** for `new-project`.

### Currently In Scope

- project identity input validation
- target path inspection and classification
- baseline scaffold planning
- creation of documented baseline directories
- creation of documented baseline files
- creation of scaffold metadata
- safe completion of missing managed items in compatible/saneable targets
- post-action scaffold validation

### Required Explicit Inputs

The current baseline functionally depends on explicit inputs such as:

- project name
- target path
- optional explicit project slug
- optional project description
- template identifier when multiple templates exist

These inputs must not be silently assumed.

### Deterministic Slug Rule

If the user does not provide an explicit slug, the slug may be derived from the project name only by a documented deterministic rule.

At minimum, the derivation rule must:

- lowercase the value
- trim surrounding whitespace
- replace spaces and underscores with hyphens
- collapse repeated separators
- allow only `a-z`, `0-9`, and `-`

If deterministic derivation does not produce a valid slug, the command MUST abort and require explicit input.

---

## 10. Baseline Scaffold Model

The current PROJECT baseline defines one standard scaffold model.

At minimum, the managed scaffold includes:

```text
<project_slug>/
├── app/
├── config/
├── deploy/
├── docs/
├── operate/
├── tests/
├── .env.example
├── .gitignore
├── README.md
├── compose.yaml
└── project.yaml
```

### Functional Meaning of Managed Paths

- `app/` — application source location
- `config/` — explicit project configuration artifacts
- `deploy/` — deployment-related project assets and templates
- `docs/` — project-local documentation
- `operate/` — operational project assets and templates
- `tests/` — project test location
- `.env.example` — placeholder example environment file
- `.gitignore` — baseline ignore policy for the scaffold
- `README.md` — project-local overview and usage stub
- `compose.yaml` — future-facing deploy template placeholder
- `project.yaml` — canonical project scaffold metadata record

### `project.yaml` Purpose

`project.yaml` is the canonical scaffold marker and metadata file.

It MUST record at minimum:

- project name
- project slug
- template identifier
- template version
- generator command identity

This metadata is required to support compatible re-runs and future scaffold-aware commands.

---

## 11. Current Functional Guarantees

For the current baseline, `new-project` MUST:

- create the target directory when it is safely creatable
- create the required baseline directories when missing
- create the required baseline files when missing
- create `project.yaml` with deterministic scaffold metadata
- preserve unrelated existing files when they do not conflict with managed paths
- avoid duplicate or conflicting scaffold generation
- refuse unsafe overwrite situations
- validate that all required managed paths exist after execution

### Completion Behavior for Existing Compatible Targets

When the target already contains a compatible scaffold, `new-project` MAY:

- reuse already-correct managed paths
- create only missing managed items
- preserve existing managed content when already aligned
- complete a saneable partial scaffold without destructive overwrite

### Blocking Behavior

`new-project` MUST block when:

- the target path is a non-directory conflicting object
- the target contains conflicting managed files with incompatible identity
- the target contains ambiguous scaffold metadata
- the command cannot determine safe ownership of managed outputs
- required managed files cannot be created safely
- post-action validation fails

---

## 12. Explicitly Out of Scope in the Current Baseline

The current baseline of `new-project` does **not** implement:

- Git repository initialization
- dependency installation
- Python environment creation
- Docker image build
- service startup
- database provisioning
- secrets generation
- CI/CD setup
- cloud resource provisioning
- runtime health checks
- backup configuration execution
- any behavior belonging to DEPLOY or OPERATE beyond placeholder scaffold preparation

These items remain deferred to later PROJECT slices or to the appropriate downstream module.

---

## 13. Runtime Validation Guarantees

No PROJECT phase is successful unless validated at runtime.

### Validation Rule

Every scaffold generation command that performs filesystem mutation MUST verify that the intended managed scaffold state was actually achieved.

### For the current `new-project` baseline, required validation includes:

- target root exists
- all required baseline directories exist
- all required baseline files exist
- `project.yaml` exists
- `project.yaml` metadata matches the intended project identity
- managed text files were rendered successfully
- no required managed path is missing after completion

If post-action validation fails, the command is considered failed.

---

## 14. Environment Behavior

### Target Environment

- local project workspace
- supported on Windows, Linux, and macOS where Python filesystem operations are available

### Functional Implications

PROJECT is not Linux-host mutation logic.

The authoritative behavior for PROJECT is successful deterministic scaffold generation through Python-managed local filesystem operations.

### Development Environment

- Windows, Linux, and macOS are acceptable development environments
- behavior must remain deterministic across supported platforms
- path handling must be cross-platform safe
- unsupported or unsafe path states must fail safely rather than mutate unpredictably

---

## 15. Configuration and Inputs

PROJECT behavior must not rely on hidden assumptions.

### Functional Requirement

Inputs required for scaffold generation must be explicit.

This includes, where applicable:

- project name
- project slug
- target path
- project description
- template identifier
- future bounded scaffold policy flags approved by contract

A hardcoded project identity is not part of the intended functional design.

---

## 16. Functional Acceptance Criteria

The PROJECT baseline is functionally valid when:

### For `new-project`

- input validation is deterministic
- target classification is consistent with real path state
- scaffold generation runs only when safe
- required managed scaffold items are created or safely reused
- post-action validation passes
- repeated execution with the same intended project identity remains idempotent
- no out-of-scope mutation is introduced

---

## 17. Limitations and Deferred Decisions

The following are intentionally deferred or not yet frozen at the current PROJECT baseline stage:

- multiple official scaffold templates
- advanced language or stack profiles
- Git initialization policy
- dependency manager selection
- generated CI/CD artifacts
- generated secrets handling model
- generated application code beyond placeholders
- richer project metadata schema
- automated integration with DEPLOY and OPERATE templates beyond the baseline placeholders

Deferred items must be documented before they are implemented.

---

## 18. Functional Freeze Statement

The PROJECT baseline is functionally frozen as:

- a single-command PROJECT domain
- with `new-project` as deterministic scaffold creation
- with mandatory input validation, target classification, safe execution, and post-action validation
- with a documented baseline scaffold model
- with explicit non-overwrite behavior for conflicting state

The current freeze does **not** mean the full future project lifecycle is already implemented.
It means the functional model and responsibility boundaries are fixed, while PROJECT may continue to grow through explicitly documented slices.

---

## 19. Final Statement

The PROJECT module is the framework layer responsible for turning explicit project inputs into a predictable and validated scaffold.

Its functional model is:

- validate inputs first
- inspect the target
- classify explicitly
- generate only when safe
- validate every managed output

All PROJECT implementation must remain aligned with this model.
