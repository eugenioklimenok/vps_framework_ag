# PROJECT Baseline — Technical Design Document (TDD)

## 1. Purpose

This document defines the **technical architecture** of the PROJECT module.

It describes:

- how PROJECT is implemented in Python
- how `new-project` is separated technically
- how shared components are reused
- how target inspection, scaffold planning, rendering, and validation fit together
- how the current scaffold baseline supports future DEPLOY and OPERATE phases without mixing responsibilities

This document is prescriptive and must be used as technical implementation guidance together with the architecture model, engineering rules, PROJECT FDD, PROJECT contract, `new-project` specification, and the shared Python baseline.

---

## 2. Role in Documentation Hierarchy

For PROJECT work, this document defines the **technical source of truth** below the FDD.

It is governed by:

- `FRAMEWORK_ARCHITECTURE_MODEL.md`
- `ENGINEERING_RULES.md`
- `PROJECT_BASELINE_FDD.md`

It governs, technically, the lower-level PROJECT documents:

- `PROJECT_BASELINE_CONTRACT.md`
- `NEW_PROJECT_SPEC.md`

If a lower-level PROJECT document contradicts this TDD, the lower-level document MUST be corrected.

---

## 3. Technical Design Goals

The PROJECT module technical design MUST provide:

- deterministic behavior
- Python-only implementation
- modular command boundaries
- explicit target inspection
- safe scaffold planning
- runtime validation
- idempotent scaffold completion where applicable
- high testability
- Codex-compatible structure
- cross-platform filesystem-safe behavior

PROJECT is local filesystem scaffold logic, not host mutation logic.

---

## 4. Technical Scope of PROJECT

PROJECT is implemented as a Python module containing one command family:

- `new-project`

Technically, PROJECT must support:

- input normalization and validation
- target path inspection
- target classification
- scaffold plan generation
- template rendering
- filesystem materialization
- runtime validation
- command-level exit code control

PROJECT must not contain responsibilities belonging to HOST, DEPLOY, or OPERATE runtime execution.

---

## 5. Repository Architecture

The PROJECT implementation is expected to follow the framework repository model:

```text
framework/
├── cli/
├── modules/
│   └── project/
│       ├── new/
│       └── templates/
├── models/
├── utils/
├── config/
└── tests/
```

### PROJECT command separation

- `framework/modules/project/new/` contains `new-project` inspection, planning, rendering, and validation logic
- `framework/modules/project/templates/` contains scaffold templates and metadata used by the current baseline

### Shared technical layers

- `framework/cli/` exposes Typer entrypoints
- `framework/models/` contains shared result and classification models
- `framework/utils/` contains shared filesystem, logging, and helper abstractions
- `framework/config/` contains explicit template and scaffold policy loading helpers where needed
- `tests/` contains isolated unit and integration-oriented tests

### Structure Rule

A generic `framework/core/` layer is not part of the canonical PROJECT baseline.
Shared functionality should live in explicitly owned technical layers.

---

## 6. Core Technical Components

### CLI Layer

Responsibilities:

- expose `new-project`
- parse explicit inputs
- delegate to the PROJECT runner
- translate runner outcomes into deterministic exit codes

### Shared Models

Responsibilities:

- represent target classification values
- represent scaffold actions
- represent validation outcomes
- avoid scattered string literals for status or classification

### Filesystem Helper Layer

Responsibilities:

- centralize path inspection and safe file creation helpers
- normalize text writing conventions
- provide reusable existence, emptiness, and compatibility checks
- remain deterministic across supported platforms

### Target Inspector

Responsibilities:

- inspect the requested target path
- classify the target state
- detect ambiguous or blocked scaffold situations
- expose evidence-driven results for planning

### Scaffold Planner

Responsibilities:

- convert validated inputs and target classification into a deterministic scaffold plan
- identify which managed directories and files must be created
- identify which compatible items may be safely reused
- refuse undocumented or unsafe mutation plans

### Template Renderer

Responsibilities:

- render managed text files from explicit inputs and template metadata
- ensure deterministic content generation
- avoid hidden values and undocumented placeholders

### Validator

Responsibilities:

- verify the final scaffold state after mutation
- confirm required managed paths exist
- confirm metadata matches intended project identity
- fail closed when guarantees cannot be confirmed

### PROJECT Runner

Responsibilities:

- orchestrate validate → inspect → classify → plan → render/materialize → validate flow
- stop on blocked conditions
- produce deterministic phase output
- emit result state and exit code decisions

---

## 7. Command Architecture

## 7.1 `new-project`

`new-project` is implemented as a deterministic scaffold pipeline.

### Technical responsibilities

- validate and normalize inputs
- inspect the target path
- compute target classification
- generate a scaffold plan
- create or reuse managed scaffold items as allowed
- validate the final scaffold state
- emit deterministic output and exit codes

### Architectural constraints

- no hidden defaults beyond documented rules
- no blind overwrite
- no undocumented mutation
- no host mutation
- no deployment behavior
- no success reporting without post-validation

`new-project` is baseline-based and may expand over time, but each expansion must remain explicit and documented.

---

## 8. Technical Execution Flow

## 8.1 Current `new-project` Flow

1. CLI invocation
2. explicit input validation
3. input normalization
4. target inspection
5. target classification
6. scaffold plan generation
7. filesystem materialization of allowed managed items
8. post-action validation
9. final decision rendering
10. exit code emission

---

## 9. Current `new-project` Baseline Architecture

The current implementation baseline should remain modular and responsibility-separated.

### Recommended module boundaries

- `inspect_target.py`
  - path existence checks
  - empty/non-empty checks
  - managed marker discovery
  - compatibility and ambiguity detection
  - target classification production

- `plan.py`
  - deterministic scaffold plan generation
  - create/reuse/block decisions
  - managed path inventory generation

- `render.py`
  - template loading
  - text rendering for managed files
  - metadata rendering for `project.yaml`

- `materialize.py`
  - safe directory creation
  - safe file creation
  - guarded update of missing compatible managed files only

- `validate.py`
  - post-action validation of required paths
  - metadata consistency validation
  - managed file presence validation

- `runner.py`
  - orchestration of validate → inspect → plan → materialize → validate flow
  - deterministic output sections
  - exit code decisions

### Current baseline technical boundaries

Allowed mutation in the current baseline:

- create the target directory when safely creatable
- create required baseline directories
- create required baseline files
- write deterministic metadata to `project.yaml`
- create missing managed items in saneable compatible scaffolds

Forbidden mutation in the current baseline:

- overwrite conflicting existing managed files
- rewrite unmanaged user content
- initialize Git
- install dependencies
- start services
- provision infrastructure
- inject secrets
- execute deployment or operational commands
- create undocumented files or directories

---

## 10. Input and Configuration Model

The current PROJECT technical design requires explicit inputs.

At minimum, the relevant technical inputs for the current baseline are:

- project name
- target path
- optional explicit slug
- optional project description
- template identifier when multiple templates exist

### Rule

These values must be obtained through explicit command inputs or structured configuration.
They must not be embedded as hidden constants in business logic.

### Template Baseline Rule

The current baseline may support a single official scaffold template (`baseline-v1`).

If this template is defaulted by the CLI, the default must be explicitly documented and remain deterministic.

---

## 11. Data and State Modeling

Target inspection, scaffold planning, and validation should use explicit result objects.

### Recommended modeling categories

- `TargetClassification`
  - `CLEAN`
  - `COMPATIBLE`
  - `SANEABLE`
  - `BLOCKED`

- `ScaffoldAction`
  - `CREATE`
  - `REUSE`
  - `SKIP`
  - `BLOCK`

- `ScaffoldResult`
  - actions taken
  - paths created
  - paths reused
  - warnings or block reasons
  - validation outcome

### Modeling Rule

The technical design should avoid hidden booleans and implicit state transitions.

---

## 12. Determinism and Idempotency

### Determinism

Given the same inputs and same filesystem state, PROJECT commands must produce the same plan, the same validations, and the same exit codes.

### Idempotency for `new-project`

The current scaffold baseline must be safe to re-run with the same intended project identity.

This requires:

- checking state before mutating
- preserving compatible existing scaffold items
- creating only missing managed paths in saneable compatible state
- refusing conflicting overwrite
- not regenerating already-correct metadata or content unnecessarily

---

## 13. Safety and Abort Model

PROJECT technical behavior must fail closed.

Execution must stop when:

- input normalization fails
- the target classification is `BLOCKED`
- scaffold metadata is ambiguous
- the target contains conflicting managed content
- required parent paths are not safely writable
- post-action validation fails
- runtime execution error prevents contract fulfillment

No fallback heuristics are allowed for ambiguous scaffold states.

---

## 14. Cross-Platform Technical Behavior

### Windows, Linux, and macOS

PROJECT is a local scaffold command and must behave deterministically across supported platforms.

Technical implications:

- use Python-native filesystem operations (`pathlib`, `os`, `shutil` only where necessary)
- avoid shell-dependent behavior
- normalize text encoding and newline policy for managed files
- preserve testability without depending on platform-specific shell tools

### Path Rule

Path joins, existence checks, and file creation must use Python-native path handling.
No path behavior may depend on shell expansion.

---

## 15. Testing Strategy

### Unit Tests

Required for:

- slug normalization and validation
- target classification behavior
- scaffold plan generation
- metadata rendering
- validation logic
- runner decision logic

### CLI Tests

Required for:

- command entrypoint behavior
- deterministic output sections
- exit code mapping

### Safety Tests

Required for:

- blocked target abort behavior
- conflicting file abort behavior
- saneable partial scaffold completion
- idempotent re-run behavior
- metadata mismatch blocking behavior

### Cross-platform Tests

Filesystem interactions should be testable using temporary directories and mocks where appropriate so tests pass across Windows, Linux, and macOS development environments.

---

## 16. Known Technical Constraints and Deferred Decisions

The following remain intentionally open or deferred at the current stage:

- multiple official scaffold templates
- richer template inheritance model
- advanced content generation per application stack
- generated Git policy
- generated dependency manager files
- generated CI/CD files
- generated secret bootstrap files
- richer metadata schema beyond baseline scaffold identity
- future scaffold migrations across template versions

These may be extended later, but only through documented, contract-aligned updates.

---

## 17. Technical Freeze Statement

The PROJECT technical baseline is frozen as:

- a Python-only PROJECT implementation
- with explicit command separation for `new-project`
- with shared validation, inspection, planning, rendering, and filesystem foundations
- with `new-project` as deterministic scaffold architecture
- with cross-platform local filesystem behavior
- with explicit non-overwrite and post-validation rules

The freeze applies to architecture and responsibility boundaries.
It does not imply that all future PROJECT slices are already implemented.

---

## 18. Final Statement

The PROJECT module technical design must support safe evolution without ambiguity.

Its architecture therefore requires:

- explicit command boundaries
- explicit target inspection
- explicit scaffold planning
- explicit runtime validation
- deterministic Python-native filesystem behavior
- baseline-based growth of scaffold logic without breaking contracts

All PROJECT implementation must remain aligned with this design.
