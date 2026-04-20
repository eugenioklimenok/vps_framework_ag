# DEPLOY Baseline — Technical Design Document (TDD)

## 1. Purpose

This document defines the **technical architecture** of the DEPLOY module.

It describes:

- how DEPLOY is implemented in Python
- how `deploy-project` is separated technically
- how shared components are reused
- how project inspection, runtime validation, configuration validation, execution, smoke testing, and final validation fit together
- how the current deployment baseline supports future OPERATE work without mixing responsibilities

This document is prescriptive and must be used as technical implementation guidance together with the architecture model, engineering rules, DEPLOY FDD, DEPLOY contract, `deploy-project` specification, and the shared Python baseline.

---

## 2. Role in Documentation Hierarchy

For DEPLOY work, this document defines the **technical source of truth** below the FDD.

It is governed by:

- `FRAMEWORK_ARCHITECTURE_MODEL.md`
- `ENGINEERING_RULES.md`
- `DEPLOY_BASELINE_FDD.md`

It governs, technically, the lower-level DEPLOY documents:

- `DEPLOY_BASELINE_CONTRACT.md`
- `DEPLOY_PROJECT_SPEC.md`

If a lower-level DEPLOY document contradicts this TDD, the lower-level document MUST be corrected.

---

## 3. Technical Design Goals

The DEPLOY module technical design MUST provide:

- deterministic behavior
- Python-only implementation
- modular command boundaries
- explicit project and runtime inspection
- explicit deployment runtime control
- runtime validation
- safe re-run behavior where compatible
- high testability
- Codex-compatible structure
- Linux-authoritative deployment behavior with development-safe abstractions

DEPLOY is runtime deployment logic, not host bootstrap logic and not operational continuity logic.

---

## 4. Technical Scope of DEPLOY

DEPLOY is implemented as a Python module containing one command family:

- `deploy-project`

Technically, DEPLOY must support:

- input normalization and validation
- project scaffold inspection
- deployment context classification
- runtime prerequisite validation
- environment file loading
- deploy configuration validation
- build/start execution
- smoke testing
- runtime validation
- command-level exit code control

DEPLOY must not contain responsibilities belonging to HOST, PROJECT, or OPERATE.

---

## 5. Repository Architecture

The DEPLOY implementation is expected to follow the framework repository model:

```text
framework/
├── cli/
├── modules/
│   └── deploy/
│       ├── project/
│       └── runtime/
├── models/
├── utils/
├── config/
└── tests/
```

### DEPLOY command separation

- `framework/modules/deploy/project/` contains `deploy-project` inspection, classification, execution, smoke, and validation logic
- `framework/modules/deploy/runtime/` contains deployment-runtime wrappers and runtime-specific helpers for the current documented baseline

### Shared technical layers

- `framework/cli/` exposes Typer entrypoints
- `framework/models/` contains shared result and classification models
- `framework/utils/` contains subprocess, logging, and helper abstractions
- `framework/config/` contains explicit deploy input and runtime policy loading helpers where needed
- `tests/` contains isolated unit and integration-oriented tests

### Structure Rule

A generic `framework/core/` layer is not part of the canonical DEPLOY baseline.
Shared functionality should live in explicitly owned technical layers.

---

## 6. Core Technical Components

### CLI Layer

Responsibilities:

- expose `deploy-project`
- parse explicit inputs
- delegate to the DEPLOY runner
- translate runner outcomes into deterministic exit codes

### Shared Models

Responsibilities:

- represent deployment context classification values
- represent deploy actions
- represent smoke outcomes
- represent validation outcomes
- avoid scattered string literals for status or classification

### Subprocess Wrapper

Responsibilities:

- centralize system command execution
- capture stdout, stderr, and return code
- support timeout handling
- normalize execution behavior across commands
- remain the only system interaction path for deployment-runtime commands

### Project Inspector

Responsibilities:

- inspect the requested project root
- validate presence of required scaffold files
- extract project identity metadata from `project.yaml`
- detect ambiguous or blocked project state

### Runtime Prerequisite Validator

Responsibilities:

- validate that the deployment runtime is available
- validate that the current operator can use it
- validate required runtime commands before mutation
- expose evidence-driven results for classification and blocking

### Environment Loader

Responsibilities:

- validate env file input
- load or pass explicit env configuration to the deployment runtime
- avoid hidden environment assumptions
- expose structured information to the runner

### Deploy Runtime Runner

Responsibilities:

- run configuration validation
- run build
- run startup
- query runtime status
- expose structured execution results

### Smoke Layer

Responsibilities:

- execute baseline smoke checks
- support runtime-state smoke
- support optional explicit endpoint smoke when provided
- expose explicit pass/fail results

### Validator

Responsibilities:

- verify the final deployment state after mutation
- confirm runtime baseline success conditions
- fail closed when guarantees cannot be confirmed

### DEPLOY Runner

Responsibilities:

- orchestrate validate → inspect → classify → validate runtime → build/start → smoke → validate flow
- stop on blocked conditions
- produce deterministic phase output
- emit result state and exit code decisions

---

## 7. Command Architecture

## 7.1 `deploy-project`

`deploy-project` is implemented as a deterministic deployment pipeline.

### Technical responsibilities

- validate and normalize inputs
- inspect the target project
- compute deployment context classification
- validate runtime prerequisites
- validate deploy configuration
- execute build and startup
- run smoke tests
- validate the final runtime state
- emit deterministic output and exit codes

### Architectural constraints

- no host bootstrap
- no undocumented mutation
- no hidden configuration sources for required identity inputs
- no progression after ambiguous project or runtime state detection
- no success reporting without smoke and post-validation

`deploy-project` is baseline-based and may expand over time, but each expansion must remain explicit and documented.

---

## 8. Technical Execution Flow

## 8.1 Current `deploy-project` Flow

1. CLI invocation
2. explicit input validation
3. input normalization
4. project root inspection
5. deployment context classification
6. runtime prerequisite validation
7. deploy configuration validation
8. build execution
9. startup execution
10. smoke testing
11. post-deploy validation
12. final decision rendering
13. exit code emission

---

## 9. Current `deploy-project` Baseline Architecture

The current implementation baseline should remain modular and responsibility-separated.

### Recommended module boundaries

- `inspect_project.py`
  - project path checks
  - scaffold file checks
  - metadata extraction from `project.yaml`
  - project identity ambiguity detection
  - deployment context classification support

- `validate_runtime.py`
  - deployment runtime existence checks
  - runtime usability checks
  - compose command availability checks
  - pre-mutation blocking decisions

- `load_env.py`
  - env file path validation
  - explicit env-file policy handling
  - runtime handoff preparation

- `run_config.py`
  - deploy configuration validation
  - stack syntax/config checks through the runtime wrapper

- `run_build.py`
  - build orchestration through the runtime wrapper

- `run_up.py`
  - startup orchestration through the runtime wrapper

- `smoke.py`
  - runtime-state smoke
  - optional explicit endpoint smoke
  - result reduction

- `validate.py`
  - post-deploy validation of runtime state
  - service status verification
  - final decision support

- `runner.py`
  - orchestration of inspect → validate runtime → config → build → up → smoke → validate flow
  - deterministic output sections
  - exit code decisions

### Current baseline technical boundaries

Allowed mutation in the current baseline:

- build the documented project stack through the deployment runtime
- start the documented project stack
- re-run documented build/start behavior for the same project identity when compatible

Forbidden mutation in the current baseline:

- host package install or repair
- runtime installation or normalization
- project scaffold creation
- secrets generation
- DNS/TLS mutation
- reverse proxy provisioning
- rollback orchestration
- backup execution
- recurring operational control
- undocumented runtime cleanup affecting unrelated workloads

---

## 10. Input and Configuration Model

The current DEPLOY technical design requires explicit inputs.

At minimum, the relevant technical inputs for the current baseline are:

- project path
- env file path
- optional explicit smoke endpoint or equivalent bounded smoke input
- future bounded deploy flags explicitly approved by contract

### Rule

These values must be obtained through explicit command inputs or structured configuration.
They must not be embedded as hidden constants in business logic.

### Runtime Baseline Rule

The current baseline may assume a documented compose-compatible deployment runtime accessible through the subprocess wrapper.

If the runtime is absent or unusable, the command must block rather than repair the host.

---

## 11. Data and State Modeling

Deployment inspection, runtime validation, execution, and smoke handling should use explicit result objects.

### Recommended modeling categories

- `DeploymentClassification`
  - `READY`
  - `REDEPLOYABLE`
  - `BLOCKED`

- `DeployAction`
  - `VALIDATE`
  - `BUILD`
  - `START`
  - `SMOKE`
  - `BLOCK`

- `DeployResult`
  - actions taken
  - build outcome
  - startup outcome
  - smoke outcome
  - validation outcome
  - fatal block reason where applicable

### Modeling Rule

The technical design should avoid hidden booleans and implicit state transitions.

---

## 12. Determinism and Re-Run Behavior

### Determinism

Given the same inputs and same project/runtime state, DEPLOY commands must produce the same decisions, same validations, and same exit codes.

### Safe Re-Run for `deploy-project`

The current deployment baseline should be safe to re-run for the same intended project identity where the underlying deployment context remains compatible.

This requires:

- checking project state before mutating
- validating runtime prerequisites before mutating
- using explicit project identity and inputs
- refusing conflicting or ambiguous deployment state
- not extending mutation beyond the documented project stack scope

---

## 13. Safety and Abort Model

DEPLOY technical behavior must fail closed.

Execution must stop when:

- project state is ambiguous
- deployment context classification is `BLOCKED`
- runtime prerequisites are missing or unusable
- configuration validation fails
- build or startup fails
- smoke tests fail
- post-deploy validation fails
- runtime execution error prevents contract fulfillment

No fallback heuristics are allowed for ambiguous deployment states.

---

## 14. Cross-Platform Technical Behavior

### Linux

Linux is the authoritative runtime target for real stack deployment.

### Windows and macOS

Windows and macOS are supported development and test environments only for isolated code and mocked runner logic.

Technical implications:

- runtime command execution must be abstracted through the subprocess wrapper
- deployment logic must remain unit-testable without requiring a real target host
- unsupported local execution conditions must abort safely
- local green tests do not replace authoritative runtime validation on the target environment

---

## 15. Testing Strategy

### Unit Tests

Required for:

- project inspection logic
- deployment classification behavior
- runtime prerequisite validation logic
- env-file handling
- runtime wrapper behavior
- smoke reduction logic
- post-deploy validation logic
- runner decision logic

### CLI Tests

Required for:

- command entrypoint behavior
- deterministic output sections
- exit code mapping

### Safety Tests

Required for:

- blocked project abort behavior
- missing runtime abort behavior
- invalid env-file abort behavior
- configuration validation failure abort behavior
- smoke failure abort behavior
- safe redeploy behavior

### Cross-platform Tests

System interactions must be mockable so tests pass in Windows and macOS development environments without requiring real Linux mutation.

---

## 16. Known Technical Constraints and Deferred Decisions

The following remain intentionally open or deferred at the current stage:

- support for multiple deployment runtimes
- richer service status interpretation
- database migration orchestration
- proxy/TLS automation
- rollback workflow
- clustered deployment
- advanced health-check registries
- release/version tagging policy
- deploy history persistence
- richer structured output export model

These may be extended later, but only through documented, contract-aligned updates.

---

## 17. Technical Freeze Statement

The DEPLOY technical baseline is frozen as:

- a Python-only DEPLOY implementation
- with explicit command separation for `deploy-project`
- with shared subprocess, validation, runtime, and smoke foundations
- with `deploy-project` as controlled deployment architecture
- with Linux-authoritative real-runtime behavior
- with strong blocking on ambiguous or unsafe state

The freeze applies to architecture and responsibility boundaries.
It does not imply that all future DEPLOY slices are already implemented.

---

## 18. Final Statement

The DEPLOY module technical design must support safe evolution without ambiguity.

Its architecture therefore requires:

- explicit command boundaries
- explicit project and runtime inspection
- explicit configuration validation
- explicit smoke testing
- explicit runtime validation
- deterministic subprocess-driven behavior
- baseline-based growth of deploy logic without breaking contracts

All DEPLOY implementation must remain aligned with this design.
