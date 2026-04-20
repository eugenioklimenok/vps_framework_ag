# PYTHON IMPLEMENTATION BASELINE

## 1. Purpose

This document defines the **shared Python implementation baseline** for the framework.

It standardizes:

- repository structure
- Python version
- CLI architecture
- system interaction model
- modeling approach
- testing expectations
- implementation conventions

This baseline exists to ensure:

- consistency across modules
- compatibility with Codex-driven development
- maintainability
- controlled future growth

---

## 2. Python Version

### Rule

The framework MUST use:

→ **Python 3.12+**

### Rationale

- modern typing support
- cleaner dataclass and enum usage
- long-term maintainability

---

## 3. Canonical Repository Structure

The canonical repository layout for v1 is:

```text
framework/
├── cli/                # CLI entrypoints and command registration
├── modules/
│   ├── host/
│   │   ├── audit/
│   │   ├── init/
│   │   └── harden/
│   ├── project/
│   ├── deploy/
│   └── operate/
├── models/             # shared models, enums, and typed result objects
├── utils/              # subprocess, parsing, logging, and utility helpers
├── config/             # explicit configuration definitions and loaders
├── tests/              # test suite
├── main.py             # CLI root
├── pyproject.toml      # dependencies and tool configuration
└── README.md
```

### Repository Rule

This structure is the default baseline.

Additional top-level directories require explicit architectural justification.

### Clarification

A generic `framework/core/` directory is **not** part of the canonical baseline for v1.
Shared behavior should live in clearly named locations such as:

- `models/`
- `utils/`
- `config/`
- or explicit domain modules

This avoids “miscellaneous core dumping” and keeps ownership clear.

---

## 4. CLI Framework

### Rule

CLI MUST be implemented using:

→ **Typer**

### Requirements

- one root CLI (`main.py`)
- explicit command registration
- subcommands per domain and command family
- deterministic exit codes

### Principle

CLI code is a thin entry layer.
It MUST NOT absorb business logic.

---

## 5. System Command Execution

### Rule

All system interaction MUST go through Python.

### Required Pattern

- use `subprocess.run()` or a thin framework wrapper over it
- capture stdout
- capture stderr
- capture return code
- support timeout handling

### Requirements

- no direct shell scripts as implementation
- no silent subprocess failures
- commands must use explicit argument lists unless strongly justified otherwise

### Preferred Design

System command execution SHOULD be centralized in shared helpers so:

- command behavior is normalized
- timeout handling is consistent
- parsing receives stable inputs
- tests can mock execution cleanly

---

## 6. Data Modeling

### Rule

Structured behavior MUST use explicit Python models.

### Required Shared Modeling

Use explicit objects for at least:

- check results
- command outcomes
- classifications
- statuses
- reconciliation outcomes where applicable

### Preferred Tools

- `dataclasses` for structured return objects
- `Enum` for bounded values
- `TypedDict` or pydantic only where genuinely needed

### Prohibition

Do not scatter raw string literals for status or classification across the codebase.

---

## 7. Configuration Handling

### Rule

Configuration MUST be explicit.

### Requirements

- no hidden defaults that alter behavior invisibly
- module inputs must be named and documented
- command-relevant configuration must be typed where feasible

### Examples

For HOST, this includes values such as:

- operator user identity
- expected public key or key source
- policy toggles approved by contract

### Prohibition

Do not hardcode operator identity, host assumptions, or environment-sensitive behavior unless a controlling document explicitly permits it.

---

## 8. Logging

### Rule

Logging MUST be structured.

### Requirements

- use Python `logging`
- no print-based debugging inside business logic
- keep CLI rendering separate from internal logs
- use consistent formats across modules

---

## 9. Error Handling

### Rule

Errors MUST be explicit and controlled.

### Requirements

- no silent failures
- meaningful exceptions or typed outcome objects
- deterministic exit points
- distinguish between:
  - contract failure
  - blocked/unsafe state
  - runtime execution error

---

## 10. Output Design

### Required Outputs

Framework commands SHOULD support:

1. human-readable output
2. structured internal result data
3. future-ready export capability where relevant

### Rule

User-facing output MUST be driven from structured internal state rather than ad-hoc prints.

---

## 11. Idempotency Support

### Rule

Code MUST support safe re-execution where applicable.

### Implementation Expectations

- inspect state before modifying it
- reuse compatible state
- avoid destructive repetition
- keep mutation scope bounded to documented contract

---

## 12. Testing

### Rule

All core logic MUST be testable.

### Framework

→ **pytest**

### Minimum Expectations

Tests SHOULD cover:

- parsing logic
- classification logic
- runner decisions
- subprocess wrappers
- validation logic
- idempotent re-run behavior where applicable

### Cross-Platform Rule

When the runtime target is Linux but development may occur on Windows:

- system interactions MUST be mockable
- tests MUST NOT depend on real Linux mutation
- unit tests MUST remain authoritative for isolated logic

---

## 13. Code Quality

### Required

- ruff for linting and formatting

### Recommended

- mypy where valuable
- strict typing on shared models and public interfaces

---

## 14. Dependency Management

### Rule

Dependencies MUST be declared via:

→ `pyproject.toml`

### Requirements

- no ad-hoc dependency installation as implementation policy
- all runtime and development dependencies must be declared explicitly

---

## 15. Determinism

### Rule

Given the same inputs and same observed system state:

→ output MUST be identical

No hidden randomness or undocumented fallback behavior is allowed.

---

## 16. Forbidden Practices

The following are not allowed:

- Bash scripts as core logic
- hardcoded system assumptions
- global mutable state for command decisions
- mixing CLI logic with business logic
- duplicating shared check or parsing logic
- generic dumping grounds for unclear code ownership

---

## 17. Extension Rule

New modules or features MUST:

- follow the canonical structure
- integrate into the CLI cleanly
- respect module boundaries
- use explicit contracts and specs when behavior becomes non-trivial

---

## 18. Final Statement

This document defines the **shared Python implementation baseline** of the framework.

All Python code MUST:

- follow this structure
- respect these constraints
- align with architecture, engineering rules, and module-level design documents

Deviation is not allowed without architectural review.
