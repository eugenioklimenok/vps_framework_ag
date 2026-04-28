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

# AUDIT VPS SPECIFICATION

## 1. Purpose

This document defines the **current technical specification** of the `audit-vps` command.

It translates the current HOST contract into:

- explicit Python responsibilities
- concrete runtime evidence commands
- parsing expectations
- severity and classification effects
- output requirements
- deterministic exit behavior

This document is the current implementation blueprint for `audit-vps`.

---

## 2. Role in Documentation Hierarchy

This specification is governed by:

- `FRAMEWORK_ARCHITECTURE_MODEL.md`
- `ENGINEERING_RULES.md`
- `HOST_BASELINE_FDD.md`
- `HOST_BASELINE_TDD.md`
- `HOST_BASELINE_CONTRACT.md`
- `PYTHON_IMPLEMENTATION_BASELINE.md`

If this specification conflicts with a higher-level HOST document, this specification MUST be corrected.

---

## 3. Command Definition

### Name

`audit-vps`

### Module

HOST

### Nature

- read-only
- deterministic
- Python-implemented
- runtime-evidence based

### Mandatory Behavior

`audit-vps` MUST:

- inspect the real state of the host
- collect runtime evidence through Python-controlled subprocess execution
- evaluate checks deterministically
- return structured results
- compute host classification
- avoid any system modification

### Forbidden Behavior

`audit-vps` MUST NOT:

- create users
- install packages
- modify SSH configuration
- change UFW state
- modify Docker
- write system state changes of any kind

---

## 4. Input Model

The audit command may require explicit inputs depending on the checks being run.

### Current minimum relevant input

For the current executable HOST baseline, the relevant explicit input is:

- operator user identity

### Optional future input

Future audit expansion may additionally use inputs such as:

- expected public key
- expected home policy
- future policy toggles approved by contract

### Rule

The audit implementation MUST NOT hardcode a fixed operator identity such as a literal username inside business logic.

---

## 5. Python Implementation Model

### 5.1 Implementation Language

The command MUST be implemented in:

→ **Python 3.12+**

### 5.2 CLI Layer

The command MUST be exposed through:

→ **Typer**

### 5.3 Execution Model

System evidence MUST be collected via:

→ `subprocess.run()` wrappers in Python

Each check MUST use Python as the execution layer, even when the evidence comes from native system commands.

### 5.4 Modeling Rule

Each audit check MUST be represented in Python as an explicit object or structure containing at minimum:

- `check_id`
- `title`
- `category`
- `description`
- `evidence_command`
- `expected_behavior`
- `status`
- `evidence`
- `message`
- `classification_impact`

Recommended implementation:

- `Enum` for status and classification
- `dataclass` for check result objects

---

## 6. Result Model

Each check MUST return one of the following statuses:

- `OK`
- `WARN`
- `FAIL`

Each result MUST include:

- `check_id`
- `category`
- `title`
- `status`
- `evidence`
- `message`
- `classification_impact`

Example conceptual shape:

```python
CheckResult(
    check_id="CHECK_OS_01",
    category="OS",
    title="Supported OS",
    status=CheckStatus.OK,
    evidence="Ubuntu 24.04 LTS",
    message="Supported operating system detected",
    classification_impact=ClassificationImpact.NONE,
)
```

---

## 7. Classification Logic

Final host classification MUST be derived after all checks complete.

### Allowed final classifications

- `CLEAN`
- `COMPATIBLE`
- `SANEABLE`
- `BLOCKED`

### Classification intent in current baseline

The current audit baseline is designed to determine whether the host can safely support the current `init-vps` slice.

### Rules

#### BLOCKED

Use when any critical condition makes the current reconciliation slice unsafe or ambiguous.

Typical causes:

- unsupported OS
- unsupported architecture
- invalid SSH syntax
- effective SSH key-auth support cannot be trusted
- ambiguous operator user state
- ambiguous operator home or SSH-access filesystem state
- critical safety conditions that prevent trustworthy reconciliation

#### SANEABLE

Use when host state is not yet aligned but can be normalized safely by the current slice.

Typical causes:

- operator user missing
- operator home missing but safely creatable
- `.ssh` missing
- `authorized_keys` missing
- safe permission or ownership repair needed

#### COMPATIBLE

Use when the host already satisfies the current slice baseline or only has minor acceptable deviations.

#### CLEAN

Use when the host has minimal prior relevant state and no meaningful conflicts for the current slice.

### Classification Priority

If multiple conditions exist, priority MUST be:

`BLOCKED > SANEABLE > COMPATIBLE > CLEAN`

---

## 8. Check Group Definitions

The current executable audit baseline is intentionally limited to the checks needed for safe HOST gating at the current stage.

---

## 8.1 OS Checks

### CHECK_OS_01 — Supported Operating System

**Goal**  
Verify that the host runs a supported Ubuntu release.

**Evidence command**

```bash
cat /etc/os-release
```

**Expected parsing**

- `ID`
- `VERSION_ID`
- `PRETTY_NAME`

**OK**

- `ID=ubuntu`
- `VERSION_ID` is supported by framework policy

**FAIL**

- file missing
- non-Ubuntu OS
- unsupported Ubuntu version

**Classification impact**

- `FAIL` → `BLOCKED`

---

### CHECK_OS_02 — CPU Architecture

**Goal**  
Verify supported architecture.

**Evidence command**

```bash
uname -m
```

**OK**

- `x86_64`
- `aarch64`

**FAIL**

- any other value

**Classification impact**

- `FAIL` → `BLOCKED`

---

## 8.2 USER Checks

### CHECK_USER_01 — Operator User Exists

**Goal**  
Verify whether the operator user exists.

**Evidence command**

```bash
id <operator_user>
```

**OK**

- user exists

**WARN**

- user does not exist

**Classification impact**

- `WARN` → `SANEABLE`

---

### CHECK_USER_02 — Operator User Home Mapping

**Goal**  
Verify the current passwd mapping for the operator user.

**Evidence command**

```bash
getent passwd <operator_user>
```

**Expected parsing**

- username
- home directory
- shell

**OK**

- user exists with a valid home path mapping

**WARN**

- user missing
- user exists but home path differs from expected policy while still appearing safe to normalize

**FAIL**

- passwd data is malformed or ambiguous
- user appears to map to an unsafe or clearly conflicting home state

**Classification impact**

- `WARN` → `SANEABLE`
- `FAIL` → `BLOCKED`

---

## 8.3 SSH Checks

### CHECK_SSH_01 — sshd Binary and Syntax Validity

**Goal**  
Verify SSH daemon availability and valid syntax.

**Evidence command**

```bash
sshd -t
```

**OK**

- exit code success
- no syntax errors

**FAIL**

- binary missing
- syntax invalid
- execution error prevents trust

**Classification impact**

- `FAIL` → `BLOCKED`

---

### CHECK_SSH_02 — Effective SSH Runtime Configuration

**Goal**  
Inspect effective SSH configuration rather than raw file contents.

**Evidence command**

```bash
sshd -T
```

**Expected parsing**  
At minimum:

- `pubkeyauthentication`
- `passwordauthentication`
- `permitrootlogin`
- `kbdinteractiveauthentication`

**OK**

- `pubkeyauthentication yes`

**WARN**

- password authentication is enabled
- root-login policy is not yet hardened
- other non-blocking deviations that are acceptable before `harden-vps`

**FAIL**

- `pubkeyauthentication no`
- effective config cannot be determined reliably

**Classification impact**

- `WARN` → non-blocking, usually `COMPATIBLE` or `SANEABLE` depending on other evidence
- `FAIL` → `BLOCKED`

### Interpretation Rule

Because SSH hardening is deferred from the current `init-vps` slice:

- password authentication enabled is not, by itself, a blocking failure
- lack of trusted key-auth capability is blocking

---

## 8.4 FILESYSTEM / SSH ACCESS Checks

### CHECK_FS_01 — Operator Home Path State

**Goal**  
Verify the state of the operator home path relevant to safe reconciliation.

**Evidence command**

```bash
stat -c "%F %U %G %a %n" <expected_operator_home>
```

**OK**

- path exists as a directory with compatible ownership expectations
- or path is absent in a way that remains safely creatable by the current slice

**WARN**

- path exists but requires safe ownership or permission normalization

**FAIL**

- path exists in a clearly conflicting or ambiguous form
- path is not a directory when a directory is required
- ownership or state indicates unsafe reconciliation risk

**Classification impact**

- `WARN` → `SANEABLE`
- `FAIL` → `BLOCKED`

---

### CHECK_FS_02 — Operator SSH Access Paths

**Goal**  
Verify the state of `.ssh` and `authorized_keys` relevant to safe reconciliation.

**Evidence commands**

```bash
stat -c "%F %U %G %a %n" <expected_operator_home>/.ssh
stat -c "%F %U %G %a %n" <expected_operator_home>/.ssh/authorized_keys
```

**OK**

- `.ssh` exists in compatible form
- `authorized_keys` exists in compatible form
- ownership and permissions are safe or already aligned

**WARN**

- one or more paths are missing
- one or more paths require safe ownership or permission normalization

**FAIL**

- one or more paths exist in conflicting or ambiguous form
- a required path is not of the expected file type
- ownership or state makes safe reconciliation untrustworthy

**Classification impact**

- `WARN` → `SANEABLE`
- `FAIL` → `BLOCKED`

---

## 8.5 SYSTEM SAFETY Checks

### CHECK_SYS_01 — Root Filesystem Free Space

**Goal**  
Verify adequate free space for safe baseline operations.

**Evidence command**

```bash
df -Pk /
```

**Expected parsing**

- available space in a deterministic machine-readable form

**OK**

- sufficient free space according to documented threshold

**WARN**

- low but still usable space

**FAIL**

- critically low space such that safe reconciliation cannot be trusted

**Classification impact**

- `WARN` → usually `SANEABLE`
- `FAIL` → `BLOCKED`

### Threshold Rule

Threshold values must be documented in implementation or config and must not be hidden heuristics.

---

## 9. Deferred Check Families

The following check families are intentionally **out of the current executable audit baseline** unless later documentation explicitly brings them back into scope:

- Docker installation and normalization checks
- UFW baseline checks
- package baseline convergence checks
- timezone target checks
- broad operator environment scaffolding checks beyond current SSH access scope

These may return in future documented HOST slices, but must not be silently assumed now.

---

## 10. Python Function Mapping Guidance

Recommended naming pattern:

- `run_check_os_supported()`
- `run_check_os_architecture()`
- `run_check_user_exists()`
- `run_check_user_home_mapping()`
- `run_check_ssh_syntax()`
- `run_check_ssh_effective_config()`
- `run_check_operator_home_state()`
- `run_check_operator_ssh_paths()`
- `run_check_root_free_space()`

Each function SHOULD:

- collect evidence
- parse evidence
- return a `CheckResult`
- avoid side effects
- avoid direct console printing

---

## 11. Subprocess Execution Rules

All subprocess execution MUST follow these rules:

- use explicit argument lists
- avoid `shell=True` unless strictly justified
- capture stdout and stderr
- capture return code
- support timeout
- normalize whitespace before parsing where appropriate

Recommended wrapper responsibilities:

- receive command list
- execute command
- return structured command result object
- centralize timeout and error handling

---

## 12. Output Requirements

### 12.1 Human-readable Output

The command MUST provide a readable summary grouped by category.

Recommended grouping:

- OS
- USER
- SSH
- FILESYSTEM
- SYSTEM

Each line SHOULD contain:

- status
- check id
- short message

### 12.2 Structured Output

The implementation SHOULD be ready for structured export, even if JSON is not enabled in the first iteration.

Suggested internal structure:

- list of check results
- final classification
- summary counters:
  - total
  - ok
  - warn
  - fail

---

## 13. Exit Code Rules

Recommended deterministic exit codes:

- `0` → all checks acceptable, no warnings, no blocking failures
- `1` → warnings present, no blocking failures
- `2` → blocking failures detected
- `3` → execution/runtime error in the audit command itself

This mapping MUST remain deterministic.

---

## 14. Determinism Rules

Given the same host state, same inputs, and same command invocation, `audit-vps` MUST produce:

- the same check results
- the same classification
- the same exit code

No hidden fallback behavior or undocumented heuristics are allowed.

---

## 15. Forbidden Implementation Patterns

The following are explicitly forbidden:

- Bash scripts as primary check logic
- direct mutation of system state
- printing from deep internal check functions
- mixing CLI parsing with check evaluation logic
- hardcoded operator usernames in business logic
- undocumented automatic behavior
- skipping evidence collection and assuming defaults

---

## 16. Implementation Priority

Recommended implementation order:

1. result/status/classification models
2. subprocess wrapper
3. OS checks
4. user checks
5. SSH checks
6. filesystem checks
7. system safety checks
8. classification reducer
9. Typer CLI output layer

---

## 17. Final Statement

`audit-vps` is the diagnostic foundation of the current HOST baseline.

Its reliability determines whether:

- host classification is trustworthy
- `init-vps` can act safely
- the framework can proceed without hidden assumptions

For that reason, `audit-vps` MUST be:

- Python-native
- deterministic
- read-only
- evidence-driven
- contract-aligned
- free of hardcoded operator assumptions

---

# Approved Audit Extension — Docker Runtime Baseline Check Family

## 1. Extension Purpose

This extension adds read-only Docker evidence collection required by HOST Slice 02.

`audit-vps` remains strictly read-only.

## 2. Read-only Constraint

Docker checks MUST NOT:

- install Docker
- install Docker Compose
- start Docker
- stop Docker
- enable Docker
- modify package repositories
- modify users or groups
- modify socket permissions
- create containers
- pull images
- write system state

## 3. CHECK_DOCKER_01 — Docker CLI Availability

### Purpose

Detect whether the Docker CLI is available and executable.

### Evidence command

```bash
docker --version
```

### PASS

- command exists
- return code is zero
- output identifies Docker CLI

### WARN

- Docker CLI is missing on a supported host where installation is safe

### FAIL

- Docker CLI exists but execution fails in a way that suggests broken or ambiguous installation

### Classification impact

- `WARN` → `SANEABLE`
- `FAIL` → `BLOCKED`

## 4. CHECK_DOCKER_02 — Docker Daemon / Service State

### Purpose

Detect whether Docker daemon is active and reachable.

### Evidence commands

```bash
systemctl is-active docker
docker info
```

### PASS

- `docker.service` is active or daemon reachability is otherwise confirmed by documented platform policy
- `docker info` succeeds

### WARN

- Docker is installed but service is stopped/disabled and appears safely startable by `init-vps`

### FAIL

- Docker service is failed
- daemon cannot be reached due to broken or ambiguous runtime state
- Docker socket permissions are unsafe or cannot be trusted

### Classification impact

- `WARN` → `SANEABLE`
- `FAIL` → `BLOCKED`

## 5. CHECK_DOCKER_03 — Docker Compose v2 Availability

### Purpose

Detect whether Docker Compose v2 plugin is available through the canonical command.

### Evidence command

```bash
docker compose version
```

### PASS

- command succeeds
- output identifies Docker Compose v2 or plugin-compatible Compose

### WARN

- Docker exists but Compose v2 plugin is missing on a supported host where installation is safe

### FAIL

- `docker compose` exists but fails in a way that suggests broken or ambiguous installation

### Classification impact

- `WARN` → `SANEABLE`
- `FAIL` → `BLOCKED`

## 6. CHECK_DOCKER_04 — Legacy Compose Diagnostic

### Purpose

Detect legacy standalone `docker-compose` only as diagnostic evidence.

### Evidence command

```bash
docker-compose --version
```

Legacy `docker-compose` alone MUST NOT satisfy the Docker Compose v2 baseline.

DEPLOY requires `docker compose` unless a future contract explicitly allows fallback.

## 7. CHECK_DOCKER_05 — Operator Docker Group Membership

### Purpose

Detect whether the configured operator user is a member of the `docker` group when DEPLOY is expected to run Docker as that operator.

### Evidence commands

```bash
id <operator_user>
getent group docker
```

### PASS

- operator user exists
- `docker` group exists
- operator user is a member of `docker`

### WARN

- operator exists but is not a member of `docker`
- `docker` group is missing but can be safely created/reused by Docker package installation

### FAIL

- operator identity is ambiguous
- `docker` group state is inconsistent or unsafe to trust

### Classification impact

- `WARN` → `SANEABLE`
- `FAIL` → `BLOCKED`

## 8. CHECK_DOCKER_06 — Operator Docker Access

### Purpose

Detect whether the intended operator execution context can use Docker.

### Evidence command

```bash
sudo -u <operator_user> docker ps
```

Alternative equivalent evidence may be used if documented and deterministic.

### PASS

- command succeeds for intended operator context

### WARN

- operator group membership may require a new login session before access becomes effective

### FAIL

- permission error cannot be explained by known session-refresh behavior
- socket permission state is inconsistent
- failure indicates broken Docker runtime

### Classification impact

- `WARN` → `SANEABLE`
- `FAIL` → `BLOCKED`

## 9. Docker Classification Examples

### Docker missing

- `docker --version` command not found
- host OS/architecture supported
- package manager appears usable

Classification: `SANEABLE`

### Docker installed, Compose v1 only

- `docker --version` succeeds
- `docker-compose --version` succeeds
- `docker compose version` fails

Classification: `SANEABLE` if Compose v2 plugin can be safely installed; otherwise `BLOCKED`.

### Docker service failed

- Docker CLI exists
- `systemctl is-active docker` returns `failed`
- `docker info` fails

Classification: `BLOCKED` unless a safe documented recovery path exists.

### Docker fully ready

- Docker CLI OK
- Docker daemon reachable
- Compose v2 OK
- operator access valid when required

Classification: `COMPATIBLE`

## 10. Output Grouping Update

Human-readable audit output SHOULD include a `DOCKER` group.

Recommended Docker check ids:

- `CHECK_DOCKER_01`
- `CHECK_DOCKER_02`
- `CHECK_DOCKER_03`
- `CHECK_DOCKER_04`
- `CHECK_DOCKER_05`
- `CHECK_DOCKER_06`

## 11. Documentation Change Record

This extension preserves the recovered `AUDIT_VPS_SPEC.md`.

Prior statements that Docker checks were deferred are narrowed to mean Docker checks were deferred before Slice 02. Docker evidence collection is now in scope, but Docker mutation remains forbidden for `audit-vps`.
