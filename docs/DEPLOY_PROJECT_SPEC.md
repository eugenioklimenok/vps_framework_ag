# DEPLOY PROJECT SPECIFICATION

## 1. Purpose

This document defines the **current executable technical specification** for the `deploy-project` command.

Its purpose is to make the current DEPLOY baseline implementation precise, deterministic, and Codex-consumable.

It defines:

- command intent
- explicit inputs
- deployment classification rules
- required project/runtime checks
- execution phases
- smoke and validation requirements
- output expectations
- exit code behavior
- forbidden implementation patterns

---

## 2. Governing Documents

This specification is governed by:

1. `FRAMEWORK_ARCHITECTURE_MODEL.md`
2. `ENGINEERING_RULES.md`
3. `DEPLOY_BASELINE_FDD.md`
4. `DEPLOY_BASELINE_TDD.md`
5. `DEPLOY_BASELINE_CONTRACT.md`
6. `PYTHON_IMPLEMENTATION_BASELINE.md`
7. `CODEX_DEVELOPMENT_PROTOCOL.md`

If this specification conflicts with a higher-precedence DEPLOY document, the higher-precedence document wins and this specification MUST be corrected.

---

## 3. Command Definition

### Command name

`deploy-project`

### Domain ownership

DEPLOY

### Command purpose

Deploy or safely re-deploy the documented project stack for a valid project scaffold.

### Command type

Mutation-capable runtime deployment command.

---

## 4. Explicit Inputs

The current baseline requires explicit deployment inputs.

### Required inputs

- `--path`
  - project root path to deploy

- `--env-file`
  - explicit environment file path to be used by the deployment runtime

### Optional inputs

- `--smoke-url`
  - optional explicit endpoint used for additional smoke validation

- `--smoke-timeout`
  - optional bounded timeout for explicit smoke checks

- `--project-name`
  - optional explicit runtime project name override only if the baseline formally documents this behavior
  - if omitted, the implementation SHOULD derive stable runtime identity from trusted project metadata

### Input rule

No hidden input sources are allowed for required deployment identity or env loading.

Hidden `.env` fallback is forbidden in the current baseline unless explicitly documented by CLI contract.

---

## 5. Required Deployable Baseline

The current baseline requires the project root to contain at minimum:

- `project.yaml`
- `compose.yaml`

The command also requires:

- explicit env file
- usable deployment runtime exposed to the command environment

### Core file meanings

- `project.yaml` — authoritative project identity metadata
- `compose.yaml` — stack definition for the current baseline
- explicit env file — runtime configuration input for deployment

---

## 6. Project Identity Resolution

The implementation MUST resolve project identity from trusted metadata before runtime mutation.

### Preferred identity source

`project.yaml`

### Minimum metadata expected

- `project_name`
- `project_slug`
- `template_id`
- `template_version`

### Identity rule

If `project.yaml` is missing, malformed, or insufficient to prove project identity:

→ deployment MUST block

### Runtime project name rule

If the deployment runtime requires a stable project name, the implementation SHOULD use the trusted project slug unless an explicitly documented override is supplied.

---

## 7. Deployment Classification Rules

The command MUST classify the deploy target before any runtime mutation.

### READY

Use when:

- project root is valid
- `project.yaml` exists and is compatible
- `compose.yaml` exists
- env file exists
- deployment runtime prerequisites are satisfied
- configuration validation may proceed safely

### REDEPLOYABLE

Use when:

- the deployment context already contains a compatible runtime state for the same project identity
- build/start may be safely re-applied within the documented baseline
- no conflicting runtime ambiguity is detected

### BLOCKED

Use when any of the following apply:

- project root is missing or invalid
- `project.yaml` is missing, malformed, or incompatible
- `compose.yaml` is missing
- env file is missing
- deployment runtime is missing or unusable
- configuration validation fails
- runtime state is ambiguous or conflicts with the intended project identity
- safe deployment cannot be trusted

### Priority rule

If multiple conditions are present:

`BLOCKED > REDEPLOYABLE > READY`

---

## 8. Pre-Execution Checks

At minimum, the current implementation must evaluate the following pre-execution checks.

### CHECK_INPUT_01 — Project Path Validity

Confirm that the provided project path is non-empty and resolves safely.

**FAIL**

- missing project path
- invalid path resolution
- inaccessible project root

**Impact**

- invalid input or `BLOCKED`

---

### CHECK_INPUT_02 — Env File Validity

Confirm that the explicit env file path exists and is usable.

**FAIL**

- missing env file input
- env file does not exist
- env file is unreadable by documented policy

**Impact**

- invalid input or `BLOCKED`

---

### CHECK_PROJECT_01 — Project Root Structure

Confirm that the project root contains the minimum required deployable scaffold.

**PASS requires**

- `project.yaml` exists
- `compose.yaml` exists

**FAIL**

- missing `project.yaml`
- missing `compose.yaml`
- path is not a valid project root

**Impact**

- `BLOCKED`

---

### CHECK_PROJECT_02 — Project Metadata Compatibility

Evaluate `project.yaml`.

**PASS**

- metadata exists
- metadata is parseable enough to confirm project identity

**FAIL**

- metadata malformed
- metadata insufficient
- metadata conflicts with explicit deploy identity assumptions

**Impact**

- `BLOCKED`

---

### CHECK_RUNTIME_01 — Runtime Availability

Confirm that the documented deployment runtime is available.

**FAIL**

- runtime binary missing
- runtime command unavailable
- runtime invocation fails before deploy begins

**Impact**

- `BLOCKED`

---

### CHECK_RUNTIME_02 — Runtime Usability

Confirm that the current operator can use the deployment runtime for the current baseline.

**FAIL**

- permission denied
- runtime environment unusable
- required runtime subcommand unavailable

**Impact**

- `BLOCKED`

---

### CHECK_CONFIG_01 — Deploy Configuration Validity

Validate the project deployment configuration through the documented runtime wrapper before build/start mutation.

**FAIL**

- invalid compose configuration
- invalid env interpolation behavior
- runtime config evaluation failure

**Impact**

- `BLOCKED`

---

## 9. Execution Phases

The current baseline implementation should follow these phases.

### Phase 1 — Input Validation

- validate `--path`
- validate `--env-file`
- validate optional smoke inputs

### Phase 2 — Project Inspection

- inspect project root
- inspect `project.yaml`
- inspect `compose.yaml`
- resolve trusted project identity

### Phase 3 — Classification

- reduce findings into one classification:
  - `READY`
  - `REDEPLOYABLE`
  - `BLOCKED`

### Phase 4 — Runtime Prerequisite Validation

- validate deployment runtime availability
- validate deployment runtime usability

### Phase 5 — Configuration Validation

- validate deployment configuration through the runtime wrapper
- block on any config validation failure

### Phase 6 — Build

- execute stack build using the documented runtime wrapper

### Phase 7 — Startup

- execute stack startup using the documented runtime wrapper

### Phase 8 — Smoke

- execute required runtime-state smoke
- execute optional explicit endpoint smoke when configured

### Phase 9 — Post-Deploy Validation

Confirm that:

- project identity remains valid
- build/start completed successfully
- baseline smoke passed
- runtime inspection confirms successful stack state for the current baseline

### Phase 10 — Final Result Rendering

Render deterministic human-readable output based on structured state.

---

## 10. Runtime Wrapper Expectations

The current baseline assumes a compose-compatible runtime wrapper.

### Wrapper responsibilities

- run config validation
- run build
- run startup
- inspect stack status

### Wrapper rule

The wrapper MUST return structured results containing at minimum:

- command identity
- stdout
- stderr
- return code
- timeout state where relevant

### Baseline runtime commands

The exact subprocess invocation may vary by implementation details, but the baseline must support command equivalents for:

- configuration validation
- build
- startup
- runtime status inspection

Undocumented runtime fallbacks are forbidden.

---

## 11. Smoke Model

The current baseline requires smoke validation after startup.

### Required smoke

Runtime-state smoke:

- confirm that the deployment runtime reports the stack in an acceptable running state for the current baseline
- reject clearly failed or exited service states

### Optional explicit smoke

When `--smoke-url` is provided:

- perform a bounded explicit endpoint check
- treat failure as deployment failure for the current command run

### Timeout rule

Smoke behavior must use explicit bounded timeouts.
Infinite waiting is forbidden.

---

## 12. Re-Run Behavior

The command MUST remain safe to re-run for the same intended project identity when the deployment context is compatible.

### Allowed re-run behavior

- configuration re-validation
- rebuild
- startup re-application
- compatible runtime-state reuse

### Forbidden re-run behavior

- host repair
- blind cleanup of unrelated runtime workloads
- identity drift across re-runs
- silent fallback to different project metadata
- claiming compatibility when runtime ownership is ambiguous

---

## 13. Output Expectations

The command SHOULD expose:

1. human-readable output
2. structured internal result data
3. future-ready export capability where relevant

### Minimum human-readable output sections

Recommended sections include:

- input summary
- project identity summary
- deployment classification
- config validation summary
- build summary
- startup summary
- smoke summary
- final validation result
- final outcome

### Structured result expectations

Recommended result fields include:

- `classification`
- `result_state`
- `project_slug`
- `config_validated`
- `build_succeeded`
- `startup_succeeded`
- `smoke_passed`
- `validation_passed`
- `blocked_reason`

---

## 14. Exit Code Rules

Recommended deterministic exit codes:

- `0` → deployment executed or safely re-applied and validation passed
- `2` → blocked/unsafe/ambiguous state, failed config validation, failed smoke, or failed post-validation
- `3` → invalid inputs or command runtime execution failure

This mapping MUST remain deterministic.

---

## 15. Determinism Rules

Given the same project state, runtime state, inputs, and command invocation, `deploy-project` MUST produce:

- the same classification
- the same blocking decision
- the same validation result
- the same exit code

No hidden fallback behavior or undocumented heuristics are allowed.

---

## 16. Forbidden Implementation Patterns

The following are explicitly forbidden:

- shell scripts as primary deployment logic
- blind runtime mutation
- mixing CLI parsing with deployment orchestration logic
- hidden `.env` discovery rules
- hardcoded project paths in business logic
- host repair from DEPLOY
- skipping smoke checks
- reporting success from startup alone without validation

---

## 17. Recommended Python Function Mapping Guidance

Recommended naming pattern:

- `validate_deploy_inputs()`
- `inspect_project_root()`
- `load_project_metadata()`
- `classify_deploy_context()`
- `validate_runtime_prereqs()`
- `validate_deploy_config()`
- `run_build()`
- `run_startup()`
- `run_runtime_smoke()`
- `run_endpoint_smoke()`
- `validate_deploy_result()`

Each function SHOULD:

- have one clear responsibility
- avoid hidden side effects
- return structured results where meaningful
- remain testable in isolation

---

## 18. Final Statement

This specification defines the current executable baseline for `deploy-project`.

It exists to ensure that DEPLOY behavior is:

- explicit
- deterministic
- safe to re-run
- validation-driven
- aligned with framework architecture and engineering rules

Deviation is not allowed without documentation-first review.
