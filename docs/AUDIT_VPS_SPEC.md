# AUDIT VPS SPECIFICATION

## 1. Purpose

This document defines the current technical specification for the `audit-vps` command.

It translates the HOST contract into:

- explicit Python responsibilities
- concrete runtime evidence commands
- parsing expectations
- severity and classification effects
- output requirements
- deterministic exit behavior
- Docker Runtime Baseline audit behavior

This document is the implementation blueprint for `audit-vps`.

---

## 2. Role in Documentation Hierarchy

This specification is governed by:

1. `FRAMEWORK_ARCHITECTURE_MODEL.md`
2. `ENGINEERING_RULES.md`
3. `HOST_BASELINE_FDD.md`
4. `HOST_BASELINE_TDD.md`
5. `HOST_BASELINE_CONTRACT.md`
6. `PYTHON_IMPLEMENTATION_BASELINE.md`

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
- modify UFW
- modify Docker
- start or stop services
- write system state changes of any kind

---

## 4. Input Model

The audit command may require explicit inputs depending on the checks being run.

### Current minimum relevant input

For the current HOST baseline, the relevant explicit input is:

- operator user identity

### Optional future inputs

Future audit expansion may additionally use inputs such as:

- expected public key
- expected home policy
- future policy toggles approved by contract

### Rule

The audit implementation MUST NOT hardcode a fixed operator identity such as a literal username inside business logic.

---

## 5. Python Implementation Model

### Implementation language

The command MUST be implemented in:

```text
Python 3.12+
```

### CLI layer

The command MUST be exposed through:

```text
Typer
```

### Execution model

System evidence MUST be collected via:

```text
subprocess.run() wrappers in Python
```

Each check MUST use Python as the execution layer, even when evidence comes from native system commands.

### Modeling rule

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

Conceptual shape:

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

### Classification intent

The audit baseline is designed to determine whether the host can safely support documented `init-vps` reconciliation slices.

### Rules

#### BLOCKED

Use when any critical condition makes current reconciliation unsafe or ambiguous.

Typical causes:

- unsupported OS
- unsupported architecture
- invalid SSH syntax
- effective SSH key-auth support cannot be trusted
- ambiguous operator user state
- ambiguous operator home or SSH-access filesystem state
- broken or ambiguous Docker runtime state
- critical safety conditions that prevent trustworthy reconciliation

#### SANEABLE

Use when host state is not yet aligned but can be normalized safely by documented `init-vps` slices.

Typical causes:

- operator user missing
- operator home missing but safely creatable
- `.ssh` missing
- `authorized_keys` missing
- safe permission or ownership repair needed
- Docker Engine missing
- Docker Compose v2 plugin missing
- Docker service stopped or disabled but safely startable/enablable
- operator missing Docker group membership

#### COMPATIBLE

Use when the host already satisfies the current baseline or only has minor acceptable deviations.

#### CLEAN

Use when the host has minimal prior relevant state and no meaningful conflicts for the current baseline.

### Priority rule

If multiple conditions exist, priority MUST be:

```text
BLOCKED > SANEABLE > COMPATIBLE > CLEAN
```

---

## 8. Check Group Definitions

The current executable audit baseline includes the checks needed for safe HOST gating at the current stage.

Check families:

- OS
- USER
- SSH
- FILESYSTEM / SSH ACCESS
- SYSTEM SAFETY
- DOCKER RUNTIME

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
- user appears to map to unsafe or conflicting home state

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
- other non-blocking deviations acceptable before `harden-vps`

**FAIL**

- `pubkeyauthentication no`
- effective config cannot be determined reliably

**Classification impact**

- `WARN` → non-blocking, usually `COMPATIBLE` or `SANEABLE` depending on other evidence
- `FAIL` → `BLOCKED`

### Interpretation rule

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
- path is absent in a way that remains safely creatable by the current slice
- mode is a secure compatible mode, currently `750` or `755`

**WARN**

- path exists but requires safe ownership or permission normalization

**FAIL**

- path exists in conflicting or ambiguous form
- path is not a directory when a directory is required
- ownership or state indicates unsafe reconciliation risk

**Classification impact**

- `WARN` → `SANEABLE`
- `FAIL` → `BLOCKED`

### Home permission note

The operator home may be valid with either:

- `750`
- `755`

This flexibility applies to the operator home only.

It MUST NOT relax `.ssh` or `authorized_keys` checks.

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

- available space in deterministic machine-readable form

**OK**

- sufficient free space according to documented threshold

**WARN**

- low but still usable space

**FAIL**

- critically low space such that safe reconciliation cannot be trusted

**Classification impact**

- `WARN` → usually `SANEABLE`
- `FAIL` → `BLOCKED`

### Threshold rule

Threshold values must be documented in implementation or config and must not be hidden heuristics.

---

## 8.6 DOCKER RUNTIME Checks

This check family supports the Docker Runtime Baseline required by DEPLOY.

The checks are read-only.

They MUST NOT install, start, stop, enable, or modify Docker.

---

### CHECK_DOCKER_01 — Docker CLI Availability

**Goal**

Verify whether Docker CLI is available.

**Evidence command**

```bash
docker --version
```

**OK**

- command exists
- command exits successfully
- output identifies Docker CLI

**WARN**

- Docker CLI is missing

**FAIL**

- Docker CLI exists but execution fails in a way that suggests a broken or ambiguous installation

**Classification impact**

- `WARN` → `SANEABLE`
- `FAIL` → `BLOCKED`

---

### CHECK_DOCKER_02 — Docker Daemon State

**Goal**

Verify whether Docker daemon is active and reachable.

**Evidence commands**

```bash
systemctl is-active docker
docker info
```

**OK**

- `docker.service` is active
- `docker info` succeeds

**WARN**

- Docker is installed but service is stopped or disabled in a state that appears safely startable by `init-vps`

**FAIL**

- Docker service exists but is failed
- Docker daemon cannot be reached due to ambiguous or broken runtime state
- repeated service failures are detected by available evidence
- service manager evidence is unavailable in a way that prevents trust

**Classification impact**

- `WARN` → `SANEABLE`
- `FAIL` → `BLOCKED`

---

### CHECK_DOCKER_03 — Docker Compose v2 Availability

**Goal**

Verify that Docker Compose v2 is available through the Docker CLI plugin model.

**Evidence command**

```bash
docker compose version
```

**OK**

- `docker compose version` succeeds

**WARN**

- Docker exists but Compose v2 plugin is missing

**FAIL**

- `docker compose` exists but fails in a way that suggests a broken or ambiguous installation

**Classification impact**

- `WARN` → `SANEABLE`
- `FAIL` → `BLOCKED`

### Legacy compose rule

The legacy binary:

```bash
docker-compose
```

may be detected for diagnostic messaging.

However, `docker-compose` v1 alone MUST NOT satisfy the Docker Runtime Baseline.

DEPLOY requires `docker compose`.

---

### CHECK_DOCKER_04 — Operator Docker Group Membership

**Goal**

Verify whether the operator user is configured for non-root Docker access.

**Evidence command**

```bash
id -nG <operator_user>
```

**OK**

- operator user is a member of the `docker` group

**WARN**

- operator user exists but is not a member of the `docker` group
- operator user is missing and therefore Docker access cannot yet be assigned

**FAIL**

- group membership evidence is ambiguous or unavailable for an existing operator user
- Docker group state is inconsistent or unsafe to trust

**Classification impact**

- `WARN` → `SANEABLE`
- `FAIL` → `BLOCKED`

---

### CHECK_DOCKER_05 — Operator Docker Socket Access

**Goal**

Verify whether the operator context can access Docker without root privileges.

**Evidence command**

Preferred when executable safely under operator context:

```bash
sudo -u <operator_user> docker ps
```

or equivalent controlled subprocess behavior documented by implementation.

**OK**

- `docker ps` succeeds for operator context

**WARN**

- operator group membership has been configured but current session refresh may be required
- operator cannot yet access Docker due to group membership not taking effect

**FAIL**

- Docker socket permissions are inconsistent
- operator access fails despite expected group membership and daemon readiness
- failure indicates broken or ambiguous Docker socket/runtime state

**Classification impact**

- `WARN` → `SANEABLE`
- `FAIL` → `BLOCKED`

### Session refresh rule

If `init-vps` adds the operator to the Docker group, a new login session may be required.

Audit may report this as `WARN` when evidence indicates the system is otherwise saneable.

---

## 9. Docker Runtime Classification Examples

### Example A — Docker missing

Evidence:

- `docker --version` command not found

Classification:

```text
SANEABLE
```

Reason:

- documented Docker Runtime Baseline slice can install Docker.

---

### Example B — Docker installed, Compose v1 only

Evidence:

- `docker --version` succeeds
- `docker-compose --version` succeeds
- `docker compose version` fails

Classification:

```text
SANEABLE
```

Reason:

- Docker exists, but Compose v2 plugin is missing.
- `init-vps` can install or normalize Compose v2 if state is not ambiguous.

---

### Example C — Docker service failed

Evidence:

- `docker --version` succeeds
- `systemctl is-active docker` returns `failed`
- `docker info` cannot connect to daemon

Classification:

```text
BLOCKED` or `SANEABLE` depending on failure evidence
```

Rule:

- If daemon is merely stopped and safely startable → `SANEABLE`
- If daemon is failed, repeatedly crashing, or ambiguous → `BLOCKED`

---

### Example D — Docker ready but operator lacks group access

Evidence:

- Docker CLI OK
- Docker daemon OK
- Compose v2 OK
- operator not in `docker` group

Classification:

```text
SANEABLE
```

Reason:

- Docker group membership can be reconciled by `init-vps`.

---

### Example E — Docker fully ready

Evidence:

- `docker --version` OK
- `docker compose version` OK
- Docker daemon active
- `docker ps` works for operator context

Classification:

```text
COMPATIBLE
```

unless other host checks produce higher-priority results.

---

## 10. Deferred Check Families

The following check families are intentionally out of the current executable audit baseline unless later documentation explicitly brings them into scope:

- UFW baseline checks
- timezone target checks
- broad package baseline convergence checks beyond Docker Runtime Baseline
- reverse proxy checks
- TLS checks
- monitoring checks
- application runtime checks
- backup freshness checks
- cross-host fleet audit
- automatic remediation

These may return in future documented HOST slices, but must not be silently assumed now.

---

## 11. Python Function Mapping Guidance

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
- `run_check_docker_cli_available()`
- `run_check_docker_daemon_state()`
- `run_check_docker_compose_v2_available()`
- `run_check_operator_docker_group()`
- `run_check_operator_docker_access()`

Each function SHOULD:

- collect evidence
- parse evidence
- return a `CheckResult`
- avoid side effects
- avoid direct console printing

---

## 12. Subprocess Execution Rules

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

## 13. Output Requirements

### Human-readable output

The command MUST provide a readable summary grouped by category.

Recommended grouping:

- OS
- USER
- SSH
- FILESYSTEM
- SYSTEM
- DOCKER

Each line SHOULD contain:

- status
- check id
- short message

### Structured output

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

## 14. Exit Code Rules

Recommended deterministic exit codes:

- `0` → all checks acceptable, no warnings, no blocking failures
- `1` → warnings present, no blocking failures
- `2` → blocking failures detected
- `3` → execution/runtime error in the audit command itself

This mapping MUST remain deterministic.

---

## 15. Determinism Rules

Given the same host state, same inputs, and same command invocation, `audit-vps` MUST produce:

- the same check results
- the same classification
- the same exit code

No hidden fallback behavior or undocumented heuristics are allowed.

---

## 16. Forbidden Implementation Patterns

The following are explicitly forbidden:

- Bash scripts as primary check logic
- direct mutation of system state
- printing from deep internal check functions
- mixing CLI parsing with check evaluation logic
- hardcoded operator usernames in business logic
- undocumented automatic behavior
- skipping evidence collection and assuming defaults
- treating `docker-compose` v1 as equivalent to Docker Compose v2 without contract approval
- installing or starting Docker from `audit-vps`

---

## 17. Implementation Priority

Recommended implementation order:

1. result/status/classification models
2. subprocess wrapper
3. OS checks
4. user checks
5. SSH checks
6. filesystem checks
7. system safety checks
8. Docker runtime checks
9. classification reducer
10. Typer CLI output layer

---

## 18. Final Statement

`audit-vps` is the diagnostic foundation of the HOST baseline.

Its reliability determines whether:

- host classification is trustworthy
- `init-vps` can act safely
- Docker Runtime Baseline reconciliation can proceed
- DEPLOY can later consume a validated runtime without installing host dependencies

For that reason, `audit-vps` MUST be:

- Python-native
- deterministic
- read-only
- evidence-driven
- contract-aligned
- free of hardcoded operator assumptions
- explicit about Docker Runtime Baseline readiness
