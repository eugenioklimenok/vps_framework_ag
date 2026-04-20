# CODEX DEVELOPMENT PROTOCOL

## 1. Purpose

This document defines the **official protocol for using Codex (GPT) as a development tool**.

Its objective is to ensure that:

- Codex produces deterministic and aligned code
- implementation follows framework documentation correctly
- ambiguity is eliminated from prompts
- outputs are predictable, testable, and compliant

Codex is treated as a **controlled execution engine**, not as a source of improvised architecture.

---

## 2. Core Principle

Codex MUST NOT improvise.

Codex MUST:

- follow explicit instructions
- respect documentation precedence
- operate within strict scope boundaries
- produce deterministic outputs

The quality of output depends on the quality, completeness, and hierarchy-awareness of the prompt.

---

## 3. Documentation Awareness Rule

Every Codex prompt MUST make clear:

- which module is being worked on
- which documents govern that work
- the order of precedence between those documents

### Conflict Handling Rule

If documents conflict:

- Codex MUST follow the higher-precedence document named in the prompt
- the implementation MUST NOT invent a compromise behavior unless the prompt explicitly requests documentation reconciliation work
- the lower-precedence document should then be corrected in documentation work

---

## 4. Prompt Structure (MANDATORY)

Every prompt MUST follow this structure.

---

### 4.1 Context

Define where we are in the system:

- module: `HOST` / `PROJECT` / `DEPLOY` / `OPERATE`
- command or component being implemented
- current phase or slice

Example:

```text
You are implementing the HOST module of the framework.
Specifically, the current `init-vps` reconciliation slice.
```

---

### 4.2 Source of Truth

Explicitly list governing documents in **precedence order**.

#### Example for HOST work

```text
Use the following documents in this precedence order:

1. FRAMEWORK_ARCHITECTURE_MODEL.md
2. ENGINEERING_RULES.md
3. HOST_BASELINE_FDD.md
4. HOST_BASELINE_TDD.md
5. HOST_BASELINE_CONTRACT.md
6. AUDIT_VPS_SPEC.md
7. PYTHON_IMPLEMENTATION_BASELINE.md
8. CODEX_DEVELOPMENT_PROTOCOL.md
```

### Rule

Codex MUST NOT assume behavior outside these documents.

### Rule

Prompts for HOST work MUST NOT omit `HOST_BASELINE_FDD.md` or `HOST_BASELINE_TDD.md`.

Those documents define the current authoritative HOST functional and technical baseline.

---

### 4.3 Scope

Define exactly what to implement.

Examples:

- one command
- one runner
- one slice
- one check family
- one bugfix

Example:

```text
Implement only the current `init-vps` user and SSH-access reconciliation slice.
Do not implement Docker, packages, timezone, UFW, or hardening.
```

---

### 4.4 Constraints

Define hard technical and behavioral limits.

Examples:

- Python only
- read-only behavior
- no system modification
- no hidden assumptions
- do not widen scope
- do not change unrelated files

Example:

```text
Constraints:

- Python only
- no hardcoded operator username
- no mutation outside the current documented slice
- no undocumented behavior
```

---

### 4.5 Expected Output

Define exactly what Codex must produce.

Examples:

- files
- modules
- functions
- tests
- CLI behavior

Example:

```text
Expected output:

- update host init runner
- keep existing audit gate behavior
- add or adjust validation functions
- add tests for ambiguity handling and idempotency
```

---

### 4.6 Definition of Done

Define completion criteria.

Examples:

- behavior
- validation
- testability
- exit code behavior
- scope compliance

Example:

```text
Definition of done:

- only the documented current slice is implemented
- blocked or ambiguous states abort
- post-action validation is required
- tests cover the new behavior
```

---

## 5. Prompt Quality Rules

### Rule 1 — No ambiguity

Prompts MUST NOT contain:

- vague wording
- optional interpretations
- missing constraints
- phrases such as “implement everything”, “make it better”, or “handle all edge cases”

### Rule 2 — No implicit context

Everything Codex needs MUST be stated.

Codex MUST NOT guess:

- architecture
- naming
- scope
- behavior
- precedence between documents

### Rule 3 — One coherent responsibility per prompt

Each prompt MUST implement:

→ one coherent unit of work

Examples:

- good: “implement audit filesystem checks”
- bad: “implement audit + init + harden + deploy”

### Rule 4 — Incremental delivery

Complex implementation SHOULD be broken into steps such as:

1. CLI
2. models
3. checks
4. runner
5. validation
6. tests

### Rule 5 — Explicit exclusions

Prompts SHOULD explicitly name what is **not** in scope.

This is especially important for slice-based work.

---

## 6. Output Requirements

Codex outputs MUST:

- be valid Python code
- follow documented repository structure
- be readable and modular
- avoid duplication
- include clear function boundaries
- stay inside the documented slice or bugfix scope

---

## 7. Forbidden Codex Behavior

Prompts MUST prevent Codex from:

- inventing undocumented features
- widening documented scope
- hardcoding operator identity without contract authorization
- modifying system state in read-only phases
- mixing module responsibilities
- skipping validation logic
- introducing hidden assumptions
- silently reconciling document conflicts through guessed behavior

---

## 8. Validation of Codex Output

Every Codex result MUST be reviewed against the governing documents in precedence order.

For HOST work, review MUST include at least:

1. architecture compliance  
   - matches `FRAMEWORK_ARCHITECTURE_MODEL.md`

2. engineering compliance  
   - matches `ENGINEERING_RULES.md`

3. functional compliance  
   - matches `HOST_BASELINE_FDD.md`

4. technical compliance  
   - matches `HOST_BASELINE_TDD.md`

5. executable contract compliance  
   - matches `HOST_BASELINE_CONTRACT.md`

6. command specification compliance  
   - matches `AUDIT_VPS_SPEC.md` when the work touches `audit-vps`

7. shared implementation baseline compliance  
   - matches `PYTHON_IMPLEMENTATION_BASELINE.md`

---

## 9. Iteration Protocol

If Codex output is incorrect:

1. do NOT rewrite everything by default
2. create a corrective prompt
3. target the exact issue
4. restate the governing documents and scope boundary

Example:

```text
Fix only the operator-home ambiguity detection in the current init slice.
Do not modify CLI registration, unrelated checks, or hardening behavior.
```

---

## 10. Version Control Rule

Each Codex output SHOULD be:

- committed in small increments
- traceable to a specific prompt
- reversible if incorrect

Large, mixed-scope commits reduce auditability and increase ambiguity.

---

## 11. Prompt Templates

### Template — Implementation Task

```text
Context:
[describe module, command, and current slice]

Source of truth (highest to lowest precedence):
[list documents in order]

Scope:
[exactly what to implement]

Out of scope:
[what must not be touched]

Constraints:
[hard technical and behavioral rules]

Expected output:
[files/modules/functions/tests]

Definition of done:
[criteria]
```

---

### Template — Fix Task

```text
Context:
[existing implementation and slice]

Source of truth (highest to lowest precedence):
[list documents in order]

Issue:
[what is wrong]

Scope:
[what to fix]

Out of scope:
[what must remain unchanged]

Constraints:
[do not widen behavior]

Expected result:
[desired corrected behavior]
```

---

## 12. Anti-Patterns

Avoid prompts such as:

- “implement everything”
- “make it production-ready” without scope
- “optimize this” without a metric
- “handle edge cases” without defining them
- “use your best judgment” when contracts exist

These create non-deterministic output.

---

## 13. Determinism Rule

Given the same prompt and same documentation context:

→ Codex output should be consistent

If not, the prompt is incomplete, ambiguous, or improperly governed.

---

## 14. Final Statement

Codex is a **controlled development engine**, not a creative architecture source.

The system works only if:

- prompts are precise
- documentation precedence is explicit
- scope is tightly bounded
- constraints are enforced
- outputs are reviewed against the right documents in the right order

This protocol is mandatory for all AI-assisted development within the framework.
