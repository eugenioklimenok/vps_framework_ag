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
