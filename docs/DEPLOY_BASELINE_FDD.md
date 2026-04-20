# DEPLOY Baseline — Functional Design Document (FDD)

## 1. Purpose

This document defines the **functional behavior of the DEPLOY module baseline** within the framework.

The DEPLOY module is responsible for turning a valid project scaffold into a running project stack through:

- deployability validation
- runtime prerequisite validation
- environment loading
- build and start execution
- smoke testing
- post-deploy validation

This document defines:

- what DEPLOY does functionally
- which command belongs to DEPLOY
- how DEPLOY relates to the other framework domains
- what the current executable baseline includes
- what remains intentionally deferred

This document is prescriptive and must be treated as executable design input for DEPLOY implementation.

---

## 2. Role in Documentation Hierarchy

For DEPLOY work, this document defines the **functional source of truth**.

It is governed by:

- `FRAMEWORK_ARCHITECTURE_MODEL.md`
- `ENGINEERING_RULES.md`

It governs, functionally, the lower-level DEPLOY documents:

- `DEPLOY_BASELINE_TDD.md`
- `DEPLOY_BASELINE_CONTRACT.md`
- `DEPLOY_PROJECT_SPEC.md`

If a lower-level DEPLOY document contradicts this FDD, the lower-level document MUST be corrected.

---

## 3. Functional Scope

DEPLOY is the framework domain responsible for deploying a project stack from a validated scaffold.

### In Scope

- validate that the target project is deployable
- validate runtime prerequisites required for deployment
- load environment variables from explicit inputs
- validate deploy configuration before mutation
- build project services
- start project services
- run baseline smoke tests
- validate the final runtime result
- remain safe to re-run for the same project identity where compatible

### Out of Scope

- host bootstrap or host repair
- SSH hardening
- Docker installation or normalization
- package installation
- project scaffold creation
- application source generation
- backups
- recurring operational checks
- broad runtime health management beyond baseline post-deploy validation
- cloud infrastructure provisioning unless future documented slices add it

---

## 4. Role in Framework Architecture

DEPLOY is the third domain in the framework lifecycle:

`HOST → PROJECT → DEPLOY → OPERATE`

DEPLOY depends on:

- HOST for a usable baseline host environment
- PROJECT for a valid scaffold and deployable project structure

DEPLOY must not assume responsibility for tasks belonging to:

- HOST (host baseline and security)
- PROJECT (project creation and scaffold design)
- OPERATE (runtime continuity and recurring operational checks)

---

## 5. Supported Command

The DEPLOY module currently contains one functional command:

### `deploy-project`

Stack deployment command.

Responsibilities:

- validate explicit deploy inputs
- inspect and classify the target project deployment context
- validate deploy prerequisites
- load environment variables from explicit input
- build and start the project stack
- run baseline smoke tests
- validate the resulting runtime state

---

## 6. Functional Model

All DEPLOY behavior must follow the same mandatory flow:

1. Input Validation
2. Project Inspection
3. Deployment Context Classification
4. Runtime Prerequisite Validation
5. Configuration Validation
6. Execution (if allowed)
7. Smoke Testing
8. Runtime Validation

No DEPLOY command may skip required safety checks for its phase.

---

## 7. Deployment Context Classification Model

Deployment evaluation is based on deterministic classification states.

### READY

The project scaffold and runtime prerequisites are valid and the stack can be deployed safely.

### REDEPLOYABLE

A compatible deployment context already exists and can be safely re-applied or updated through the documented baseline command.

### BLOCKED

Conflicting, ambiguous, or unsafe state prevents trustworthy deployment.

### Classification Priority

If multiple conditions are present, classification priority MUST be:

`BLOCKED > REDEPLOYABLE > READY`

---

## 8. Functional Behavior of `deploy-project`

### Purpose

`deploy-project` deploys or safely re-deploys the documented project stack baseline.

### Functional Guarantees

`deploy-project` MUST:

- require explicit deploy inputs
- validate that the target project structure is deployable
- validate required runtime prerequisites before build/start mutation
- load environment variables only from explicit documented input
- validate deploy configuration before execution
- execute build and start in documented order
- run baseline smoke tests
- validate the final runtime state
- remain safe to re-run for the same project identity where the deployment context is compatible

### `deploy-project` MUST NOT:

- create project scaffolds
- install or normalize the host runtime
- silently guess missing configuration
- skip smoke testing
- report success without post-deploy validation
- mutate unrelated host or project state outside the documented deployment scope

---

## 9. Current `deploy-project` Functional Scope

The current executable DEPLOY baseline is the **first controlled deployment baseline** for `deploy-project`.

### Currently In Scope

- deploy input validation
- project root inspection
- deployability validation against the scaffold baseline
- runtime prerequisite validation
- environment file loading from explicit input
- deploy configuration validation
- stack build
- stack startup
- baseline smoke testing
- runtime validation of the deployment result

### Required Explicit Inputs

The current baseline functionally depends on explicit inputs such as:

- project path
- environment file path
- optional smoke target input
- future bounded policy flags explicitly approved by contract

These inputs must not be silently assumed.

---

## 10. Baseline Deployable Structure Model

The current DEPLOY baseline expects a project scaffold that includes at minimum:

- project root directory
- `project.yaml`
- `compose.yaml`

The scaffold may also contain additional project baseline paths such as:

- `deploy/`
- `config/`
- `docs/`
- `operate/`

### Functional Meaning of Core Deploy Files

- `project.yaml` — canonical scaffold metadata and project identity record
- `compose.yaml` — deployment stack definition used by the current baseline
- explicit env file — runtime configuration source passed by the operator

### Deployability Rule

A project is not deployable in the current baseline unless:

- `project.yaml` exists and is parseable enough to confirm project identity
- `compose.yaml` exists
- the explicit env file exists
- the deployment runtime prerequisites are satisfied
- deploy configuration validation passes

---

## 11. Current Functional Guarantees

For the current baseline, `deploy-project` MUST:

- validate that the target path is a project root
- validate that `project.yaml` and `compose.yaml` exist
- validate that the env file exists
- validate that the deployment runtime is available and usable
- validate the deploy configuration before attempting mutation
- execute build and startup only after successful validation
- run baseline smoke tests after startup
- validate that the deployment achieved the expected baseline runtime result

### Redeploy Behavior

When the project is already deployed in a compatible way, `deploy-project` MAY:

- rebuild the project stack
- re-apply startup safely
- reuse compatible existing runtime resources where the underlying deployment runtime handles them deterministically
- remain safe to re-run with the same project identity and explicit inputs

### Blocking Behavior

`deploy-project` MUST block when:

- project scaffold identity is ambiguous
- `compose.yaml` is missing or invalid for the documented baseline
- env file is missing
- runtime prerequisites are missing or unusable
- deploy configuration validation fails
- project identity conflicts with the existing deployment context
- smoke tests fail
- post-deploy validation fails

---

## 12. Baseline Smoke Test Model

DEPLOY must include baseline smoke validation.

The current baseline smoke model includes:

### Required runtime smoke

Confirm that the project stack reached a running state compatible with the deployment runtime's service status inspection.

### Optional explicit endpoint smoke

When an explicit smoke endpoint or equivalent bounded smoke input is provided, the deployment baseline MAY include an additional explicit endpoint check.

### Rule

A deployment is not considered successful unless baseline smoke validation passes.

---

## 13. Explicitly Out of Scope in the Current Baseline

The current baseline of `deploy-project` does **not** implement:

- Docker installation
- compose runtime installation
- host package repair
- reverse proxy provisioning
- DNS setup
- TLS issuance
- zero-downtime orchestration strategies
- database migrations unless a future documented slice adds them explicitly
- rollback automation
- recurring health checks
- backup execution
- monitoring stack provisioning
- cloud resource creation

These items remain deferred to later DEPLOY slices or to the appropriate downstream module.

---

## 14. Runtime Validation Guarantees

No DEPLOY phase is successful unless validated at runtime.

### Validation Rule

Every deployment command that performs build/start mutation MUST verify that the intended deploy result was actually achieved.

### For the current `deploy-project` baseline, required validation includes:

- the project root still resolves correctly
- `project.yaml` and `compose.yaml` remain present
- the deployment runtime reports the stack in a successful running state according to the documented baseline
- baseline smoke checks pass
- no required in-scope deploy step failed

If post-deploy validation fails, the command is considered failed.

---

## 15. Environment Behavior

### Target Environment

- authoritative runtime target is a host capable of running the documented deployment stack
- the current baseline assumes a container-compose style deployment runtime exposed to the command environment

### Functional Implications

DEPLOY is not responsible for making the host ready.
It is responsible for using an already-usable host and project scaffold safely.

### Development Environment

- Windows, Linux, and macOS are acceptable development and test environments for isolated code work
- successful local tests do not replace authoritative validation on the real deployment target
- unsupported or unsafe runtime conditions must fail safely rather than be guessed through

---

## 16. Configuration and Inputs

DEPLOY behavior must not rely on hidden assumptions.

### Functional Requirement

Inputs required for deployment must be explicit.

This includes, where applicable:

- project path
- env file path
- optional smoke target input
- future bounded deploy policy flags approved by contract

A hidden default runtime configuration source is not part of the intended functional design.

---

## 17. Functional Acceptance Criteria

The DEPLOY baseline is functionally valid when:

### For `deploy-project`

- input validation is deterministic
- deployment context classification is consistent with real state
- deploy configuration validation runs before mutation
- build/start runs only when safe
- baseline smoke tests pass
- post-deploy validation passes
- repeated execution with the same intended project identity remains safe where compatible
- no out-of-scope mutation is introduced

---

## 18. Limitations and Deferred Decisions

The following are intentionally deferred or not yet frozen at the current DEPLOY baseline stage:

- multiple deployment runtimes
- richer service orchestration profiles
- rollback policy
- advanced service dependency waiting strategies
- database migration model
- proxy and TLS automation
- multi-host or clustered deployment
- canary or blue/green deployment models
- external secret managers
- richer smoke test registry model
- generated deployment artifact versioning

Deferred items must be documented before they are implemented.

---

## 19. Functional Freeze Statement

The DEPLOY baseline is functionally frozen as:

- a single-command DEPLOY domain
- with `deploy-project` as deterministic stack deployment
- with mandatory input validation, project inspection, runtime prerequisite validation, configuration validation, smoke testing, and post-action validation
- with explicit blocking on ambiguous or unsafe state
- with strong separation from HOST and OPERATE responsibilities

The current freeze does **not** mean the full future deployment lifecycle is already implemented.
It means the functional model and responsibility boundaries are fixed, while DEPLOY may continue to grow through explicitly documented slices.

---

## 20. Final Statement

The DEPLOY module is the framework layer responsible for turning a valid project scaffold into a running, baseline-validated project stack.

Its functional model is:

- validate inputs first
- inspect the project
- classify explicitly
- validate prerequisites
- build and start only when safe
- smoke test and validate every resulting runtime state

All DEPLOY implementation must remain aligned with this model.
