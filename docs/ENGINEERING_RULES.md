# ENGINEERING RULES

## 1. Purpose

This document defines the **non-negotiable engineering rules** of the framework.

These rules govern:

- implementation language
- development methodology
- use of AI coding tools
- structure and behavior of the codebase
- relationship between documentation and implementation

These rules are mandatory and override any conflicting implementation decision.

---

## 2. Core Philosophy

The framework is:

- deterministic
- reproducible
- explicitly defined
- AI-assisted in development

It is NOT:

- a collection of ad-hoc scripts
- a manually-driven system
- an implicitly defined architecture

All engineering must follow:

→ explicit contracts  
→ explicit inputs and outputs  
→ runtime validation  
→ controlled scope  

---

## 3. Official Implementation Language

### Rule

The framework MUST be implemented in:

→ **Python**

### Implications

- all CLI commands MUST be implemented in Python
- business logic MUST reside in Python
- validation, classification, and reconciliation MUST reside in Python

### Forbidden

- Bash as primary implementation language
- mixing multiple core languages without explicit architectural approval

---

## 4. Bash Usage Policy

### Rule

Bash MAY be used ONLY as:

→ a system command executed from Python

### Allowed

- `subprocess.run()` calls
- system inspection commands
- controlled mutation commands executed by Python

### Forbidden

- Bash scripts as core logic
- delegating decisions to shell scripts
- storing framework behavior in `.sh` files

---

## 5. AI-Assisted Development (Codex)

### Rule

The official AI development tool is:

→ **Codex (GPT)**

### Implications

- implementation tasks SHOULD be executed through structured prompts
- documentation MUST be written for machine consumption
- prompts MUST define context, scope, constraints, and expected output

---

## 6. Documentation Governance and Precedence

Documentation is prescriptive, not descriptive.

Code MUST follow documentation.

### Precedence Rule

When multiple documents apply, precedence is:

1. architecture and engineering governance
2. module functional design
3. module technical design
4. module executable contract
5. command technical specification
6. shared implementation baseline
7. prompt protocol

For HOST specifically, the normal order is:

1. `FRAMEWORK_ARCHITECTURE_MODEL.md`
2. `ENGINEERING_RULES.md`
3. `HOST_BASELINE_FDD.md`
4. `HOST_BASELINE_TDD.md`
5. `HOST_BASELINE_CONTRACT.md`
6. `AUDIT_VPS_SPEC.md`
7. `PYTHON_IMPLEMENTATION_BASELINE.md`
8. `CODEX_DEVELOPMENT_PROTOCOL.md`

### Conflict Rule

If two documents conflict:

- higher-precedence documents win
- lower-precedence documents MUST be updated
- implementation MUST NOT invent a third interpretation

### Prohibition

No “temporary shortcut”, “practical exception”, or undocumented behavior may override documentation precedence.

---

## 7. Prompt-Driven Engineering

All Codex interactions MUST follow structured prompts.

Each prompt MUST include:

### 1. Context
- module (`HOST`, `PROJECT`, `DEPLOY`, `OPERATE`)
- command or component
- phase or slice being worked on

### 2. Source of Truth
- explicit governing documents
- ordered according to documentation precedence

### 3. Scope Boundaries
- what to implement
- what NOT to implement

### 4. Constraints
- Python only
- side-effect policy
- assumptions explicitly allowed

### 5. Expected Output
- files to create or modify
- modules or functions expected
- CLI behavior expected

### 6. Definition of Done
- runtime behavior
- validation requirements
- test expectations

---

## 8. Code Structure Rules

### General Principles

- modular design
- clear separation of concerns
- no hidden side effects
- deterministic behavior

### Mandatory Practices

- functions must be explicit and testable
- no implicit global state
- structured logging required
- clear error handling required
- contracts and specs must map to code structure

---

## 9. Input and Assumption Rules

The framework MUST avoid hidden assumptions.

Therefore:

- operator identity MUST NOT be hardcoded unless explicitly documented as a temporary bounded contract
- target public key or equivalent security inputs MUST be explicit
- system decisions MUST be based on collected evidence, not guesswork

Hardcoded environment assumptions are forbidden unless explicitly approved in architecture or contract documents.

---

## 10. CLI Design Rules

All commands MUST:

- be implemented in Python
- expose clear inputs
- provide deterministic outputs
- return meaningful exit codes

### Output Types

- human-readable output
- optional structured output where relevant

---

## 11. Validation Rules

### Rule

No operation is successful unless validated at runtime.

### Implications

- every critical step must be verified
- success must reflect effective state, not intent
- silent failures are forbidden

---

## 12. Idempotency

### Rule

Operations MUST be safe to re-run when applicable.

### Implications

- no destructive repetition
- state must be checked before modification
- compatible state must be reused
- ambiguous state must abort rather than be guessed through

---

## 13. Abort Policy

Execution MUST stop when:

- state is `BLOCKED`
- ambiguity exists
- contract guarantees cannot be satisfied
- post-action validation fails

No fallback heuristics are allowed for ambiguous states.

---

## 14. Forbidden Practices

The following are strictly forbidden:

- implicit assumptions about system state
- mixing responsibilities across modules
- bypassing validation steps
- partial implementations outside defined scope
- “temporary” hacks without contract update
- silent error handling
- hidden behavior not described in documentation
- prompts that ask Codex to improvise

---

## 15. Testing and Quality

### Required

- code must be testable
- core logic must be isolated
- unit tests must be possible
- command behavior must be reviewable deterministically

### Recommended

- pytest
- ruff
- consistent formatting
- mypy where valuable

---

## 16. Determinism Rule

The framework MUST behave deterministically.

Given the same input and same system state:

→ the output MUST be the same

This applies to:

- command behavior
- validation decisions
- classification outcomes
- prompt interpretation boundaries

---

## 17. Evolution Rule

Any change to:

- architecture
- contracts
- core behavior
- prompt protocol
- implementation baseline

MUST be:

- documented
- reviewed
- aligned with this document

---

## 18. Final Statement

This document defines the **engineering constitution** of the framework.

All:

- code
- prompts
- decisions
- contracts
- future extensions

MUST comply with these rules.

Deviation is not allowed without explicit architectural approval.
