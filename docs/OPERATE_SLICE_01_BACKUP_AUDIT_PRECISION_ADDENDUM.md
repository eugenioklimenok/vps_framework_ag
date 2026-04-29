# OPERATE Slice 01 — Backup/Audit Precision Addendum

## 1. Purpose

This document defines a controlled documentation addendum for **OPERATE Slice 01**.

Its purpose is to refine the current OPERATE baseline without replacing, compressing, or weakening any previously approved documentation.

This addendum clarifies precise executable behavior for:

- `backup-project` output directory handling
- backup source scope safety
- backup artifact validation
- checksum handling
- source non-mutation guarantees
- `audit-project` runtime boundary behavior
- OPERATE responsibility boundaries with HOST, PROJECT, and DEPLOY

This document exists because the current OPERATE baseline already defines `audit-project` and `backup-project`, but some execution details need stricter precision before implementation work continues.

---

## 2. Status

**Status:** Merged into canonical OPERATE documents  
**Target domain:** OPERATE  
**Target slice:** Slice 01 — Backup/Audit Precision  
**Document type:** Extension-only addendum  
**Canonical merge status:** Merged into canonical OPERATE documents

This addendum is valid as a planning and integration document until its rules are merged into the canonical OPERATE documents.

After canonical merge, this document SHOULD be retained as a change record and marked as:

```text
Status: Merged into canonical OPERATE documents
```

---

## 3. No-Regression Rule

This addendum MUST follow the project documentation rule:

> Apply a strict no-regression by extension-only rule to all documentation work. Preserve all previously approved valid normative content unless explicitly authorized for removal or replacement. Do not compress, overwrite, simplify, or rewrite an existing baseline document in a way that silently removes scope, guarantees, constraints, inputs, commands, validation logic, safety rules, or documented responsibility boundaries. Any update must be additive, or explicitly marked as a replacement of specific prior content. If prior content is moved, deprecated, narrowed, or removed, state exactly what changed, why it changed, and where the new canonical definition now lives. Default mode is EXTEND, never COMPRESS.

This addendum does not delete or weaken any existing OPERATE rule.

It only adds precision to rules already present in the current OPERATE baseline.

---

## 4. Governing Documents

This addendum is governed by the current project documentation hierarchy.

Primary governing documents:

1. `FRAMEWORK_ARCHITECTURE_MODEL.md`
2. `ENGINEERING_RULES.md`
3. `PYTHON_IMPLEMENTATION_BASELINE.md`
4. `CODEX_DEVELOPMENT_PROTOCOL.md`
5. `OPERATE_BASELINE_FDD.md`
6. `OPERATE_BASELINE_TDD.md`
7. `OPERATE_BASELINE_CONTRACT.md`
8. `AUDIT_PROJECT_SPEC.md`
9. `BACKUP_PROJECT_SPEC.md`

If this addendum conflicts with a higher-precedence canonical OPERATE document before merge, the conflict MUST be resolved explicitly before implementation.

If this addendum is approved and merged, the canonical OPERATE documents MUST be extended so that the final documentation set is internally aligned.

---

## 5. Relationship to Current OPERATE Baseline

The current OPERATE baseline already defines two command families:

- `audit-project`
- `backup-project`

The current baseline already requires:

- explicit input validation
- project identity validation through trusted metadata
- deterministic execution
- runtime or artifact validation
- no cosmetic success reporting
- no hidden backup scope expansion
- no host or deploy repair from OPERATE

This addendum does not introduce a new OPERATE command.

This addendum does not create restore, retention pruning, remote sync, rollback, monitoring, remediation, or alerting behavior.

This addendum only sharpens the current executable meaning of the existing OPERATE Slice 01 behavior.

---

## 6. Scope

### 6.1 In Scope

This addendum covers:

- required `backup-project --path` behavior
- required `backup-project --output-dir` behavior
- safe creation of the output directory
- output directory canonicalization
- rejection of unsafe output directory placement
- rejection of backup recursion risk
- archive artifact placement
- archive artifact validation
- checksum sidecar validation where checksum generation is implemented
- source non-mutation validation
- deterministic result states and exit-code mapping
- `audit-project` runtime boundary precision
- explicit separation from HOST, PROJECT, and DEPLOY responsibilities

### 6.2 Out of Scope

This addendum does not add:

- restore command behavior
- backup retention pruning
- remote backup upload or sync
- database dump automation
- automatic Docker volume backup
- object storage integration
- scheduled backups
- monitoring stack provisioning
- alerting
- runtime repair
- project deployment
- compose stack startup
- host bootstrap
- host Docker installation
- project scaffold creation

These may be introduced only through future documented slices.

---

## 7. OPERATE Responsibility Boundary

OPERATE is responsible for operational inspection and bounded artifact creation after a project exists.

OPERATE MUST NOT absorb responsibilities from other framework domains.

### 7.1 HOST Boundary

HOST prepares the host baseline.

HOST owns:

- server bootstrap
- host classification
- operator access preparation
- Docker Engine installation
- Docker Compose v2 installation
- host-level runtime availability
- SSH and hardening behavior

OPERATE MUST NOT:

- install Docker
- repair Docker
- configure host package repositories
- mutate SSH daemon configuration
- repair operator users
- repair host security baseline

If host runtime prerequisites are missing or unusable for an OPERATE audit, `audit-project` MUST classify the result according to documented audit rules, typically as `BLOCKED` when evidence cannot be trusted.

### 7.2 PROJECT Boundary

PROJECT creates and validates project scaffold identity.

PROJECT owns:

- project scaffold creation
- required baseline files
- project identity model
- project metadata structure

OPERATE MUST NOT create a missing project scaffold.

If project identity metadata is missing, malformed, or insufficient, OPERATE MUST block rather than invent identity.

### 7.3 DEPLOY Boundary

DEPLOY performs deployment-time mutation.

DEPLOY owns:

- deployment execution
- application compose lifecycle during deployment
- application runtime startup
- deployment validation
- deployment-specific mutation

OPERATE MUST NOT deploy or redeploy an app as part of `audit-project` or `backup-project`.

OPERATE MAY inspect runtime state where explicitly documented, but it MUST NOT repair runtime state as ordinary audit behavior.

---

## 8. `backup-project` Precision Rules

## 8.1 Required Inputs

`backup-project` requires explicit inputs:

- `--path`
- `--output-dir`

The command MUST NOT infer either value from the current working directory, environment variables, hidden config, shell history, or conventional paths unless a future canonical contract explicitly allows it.

### Required behavior

- `--path` MUST be provided.
- `--output-dir` MUST be provided.
- Both paths MUST be resolved before planning begins.
- Both paths MUST be represented internally as absolute canonical paths.
- Failed path resolution MUST block execution.

---

## 8.2 Project Path Resolution

The project path supplied through `--path` MUST be resolved before backup planning.

The implementation MUST confirm:

- the path exists
- the path is a directory
- the path is readable
- the path contains required project identity metadata
- the path can be represented canonically

If any of these checks fail:

→ `backup-project` MUST block.

The command MUST NOT proceed to archive creation without trusted project identity.

---

## 8.3 Output Directory Resolution

The output directory supplied through `--output-dir` MUST be resolved before artifact planning.

The implementation MUST classify the output directory state as one of:

- `EXISTS_WRITABLE`
- `MISSING_CREATABLE`
- `INVALID`
- `UNSAFE`
- `AMBIGUOUS`

### `EXISTS_WRITABLE`

Use when:

- the output path exists
- it is a directory
- it is writable by the executing context
- it can be represented as an absolute canonical path
- it is outside the project root according to this addendum

### `MISSING_CREATABLE`

Use when:

- the output path does not exist
- its parent exists
- its parent is a directory
- its parent is writable
- creating the output directory does not cross an unsafe boundary
- the resulting output directory would be outside the project root

### `INVALID`

Use when:

- the output path is missing as input
- path parsing fails
- the output path exists as a non-directory
- the parent path does not exist
- the parent path is not a directory
- required permissions are not available

### `UNSAFE`

Use when:

- the output directory is inside the project root
- the output directory equals the project root
- the output directory would cause backup recursion risk
- the path points through an unsafe or ambiguous symlink
- the path would cause artifacts to be written into source scope

### `AMBIGUOUS`

Use when:

- canonicalization cannot prove whether output is inside or outside project root
- ownership or permissions cannot be trusted
- symlink resolution is unclear
- filesystem state changes during planning

### Required behavior

- `EXISTS_WRITABLE` → backup may proceed.
- `MISSING_CREATABLE` → implementation may create the output directory, then revalidate it.
- `INVALID` → backup MUST block.
- `UNSAFE` → backup MUST block.
- `AMBIGUOUS` → backup MUST block.

---

## 8.4 Output Directory Creation Rule

The implementation MAY create `--output-dir` only when all conditions are true:

1. the requested output directory does not already exist;
2. the parent directory exists;
3. the parent directory is writable by the executing context;
4. the parent directory is not inside an unsafe path boundary;
5. the resulting output directory will be outside the project root;
6. the path does not resolve through ambiguous symlinks;
7. the implementation can revalidate the created directory after creation.

After creation, the command MUST revalidate:

- directory exists
- path is directory
- path is writable
- canonical path is outside project root
- path matches the planned output directory

If post-creation validation fails:

→ backup MUST block or fail according to whether archive creation began.

---

## 8.5 Output Directory Must Not Be Inside Project Root

For OPERATE Slice 01, the backup output directory MUST NOT be inside the project root.

This rule is intentional.

It prevents:

- recursive backup inclusion
- backup artifact being included in its own source scope
- unbounded artifact growth
- accidental source mutation by generated artifacts
- misleading validation where output files become project files

### Examples

Given:

```text
--path /srv/my-app
```

Allowed:

```text
--output-dir /var/backups/vps-framework/my-app
--output-dir /tmp/vps-framework-backups/my-app
--output-dir ../backups/my-app    # only if canonical path resolves outside /srv/my-app
```

Blocked:

```text
--output-dir /srv/my-app/backups
--output-dir /srv/my-app/.backups
--output-dir /srv/my-app
--output-dir ./backups            # when current working directory resolves to /srv/my-app
```

A future slice may allow project-local backup directories only if explicit exclusion logic is documented, implemented, and validated.

Until then:

> Output directory inside project root is forbidden.

---

## 8.6 Symlink Policy

The implementation MUST resolve canonical paths before comparing project root and output directory placement.

The command MUST NOT rely only on raw string prefix checks.

### Required behavior

- resolve `--path` to a canonical project root path
- resolve `--output-dir` to a canonical output directory path where possible
- compare canonical paths, not raw user input strings
- block if symlink resolution creates ambiguity

### Blocked cases

The command MUST block when:

- output path points into the project root through a symlink
- output path appears outside the project root but resolves inside it
- output path cannot be resolved safely enough to prove it is outside the project root
- project root itself is ambiguous due to symlink resolution

---

## 8.7 Backup Source Scope Precision

The current backup source scope is bounded.

The baseline source scope includes:

- the project root directory

Optional source scope may include:

- one explicit env file only when `--include-env-file` is set and `--env-file` is provided

The implementation MUST NOT include:

- arbitrary external paths
- implicit database paths
- Docker volumes
- hidden secret locations
- host-level config files
- output directory content
- generated backup artifacts
- checksum sidecars from the current run

Every included path MUST be explainable by one of:

- fixed current baseline scope
- explicit documented input

---

## 8.8 Env File Inclusion Precision

If env-file inclusion is supported in the current implementation, it MUST remain explicit and bounded.

The implementation may include an env file only when:

1. `--include-env-file` is set;
2. `--env-file` is provided;
3. the env file path resolves safely;
4. the env file exists;
5. the env file is a regular file;
6. the env file is readable;
7. the env file is allowed by current policy;
8. the inclusion is recorded in the backup plan and output summary.

If `--include-env-file` is set without `--env-file`:

→ backup MUST block.

If `--env-file` is provided without `--include-env-file`:

→ implementation SHOULD block or ignore only if the canonical spec explicitly defines ignore behavior.

Recommended Slice 01 behavior:

→ block to avoid ambiguous user intent.

---

## 8.9 Backup Plan Requirements

Before archive creation, the command MUST construct a structured backup plan.

The backup plan SHOULD contain at minimum:

- resolved project root
- resolved output directory
- project identity summary
- artifact filename
- artifact absolute path
- checksum filename when implemented
- checksum absolute path when implemented
- included source paths
- excluded generated artifact paths
- env-file inclusion decision
- validation requirements

Archive creation MUST use the backup plan.

Artifact validation MUST validate against the backup plan.

The command MUST NOT create an archive from ad-hoc paths that were not part of the plan.

---

## 8.10 Artifact Naming Precision

The archive artifact name SHOULD be derived from trusted project identity plus a documented uniqueness suffix.

Recommended pattern:

```text
<project_slug>__backup__<UTC timestamp>.tar.gz
```

### Required naming properties

The generated artifact name MUST:

- be deterministic in structure
- avoid path traversal
- avoid raw untrusted metadata injection
- use a safe project slug derived from trusted identity
- be unique enough to avoid overwriting previous successful backups
- be represented in the structured output

The implementation MUST NOT silently overwrite an existing artifact unless a future documented overwrite policy explicitly permits it.

If the planned artifact path already exists:

→ backup MUST choose a documented collision-safe alternative or block.

Recommended Slice 01 behavior:

→ block or generate a deterministic additional uniqueness suffix; do not overwrite.

---

## 8.11 Archive Creation Precision

Archive creation MUST be performed through Python-controlled archive logic.

The implementation MUST:

- create the archive in the resolved output directory
- include only planned source paths
- avoid source mutation
- avoid hidden host path inclusion
- avoid shell-driven archive orchestration as primary logic
- fail closed on archive creation errors

The archive SHOULD be created in a way that avoids treating the output artifact as source content.

Because Slice 01 forbids output directory inside project root, self-inclusion risk is blocked at planning time.

---

## 8.12 Artifact Validation Precision

`backup-project` MUST NOT report success merely because archive creation was attempted.

`backup-project` may report `CREATED` only after artifact validation succeeds.

Artifact validation MUST confirm:

1. artifact path exists;
2. artifact path is a regular file;
3. artifact path is inside the resolved output directory;
4. artifact path matches the backup plan;
5. artifact file size is greater than zero;
6. artifact can be opened/read as the expected archive type;
7. archive contains expected planned source content;
8. archive does not contain the output directory;
9. archive does not contain the artifact itself;
10. archive does not contain checksum sidecar from the current run;
11. checksum validation passes where checksum generation is implemented.

If any required validation fails:

→ backup MUST NOT report `CREATED`.

---

## 8.13 Checksum Precision

Where checksum generation is implemented, the checksum sidecar MUST map directly to the archive artifact.

Recommended algorithm:

```text
SHA-256
```

The checksum sidecar SHOULD use a predictable name derived from the archive path, such as:

```text
<artifact>.sha256
```

### Required checksum behavior when implemented

The implementation MUST:

- compute checksum after archive creation
- write checksum sidecar in the resolved output directory
- validate checksum sidecar exists
- validate checksum sidecar is non-empty
- validate checksum sidecar references the expected artifact
- recompute or verify checksum match before reporting success

If checksum generation is implemented but checksum validation fails:

→ backup MUST fail validation.

If checksum generation is not implemented in the current code slice, artifact validation MUST provide equivalent minimum validation through existence, size, path, readability, and archive structure checks.

---

## 8.14 Source Non-Mutation Rule

`backup-project` MUST NOT mutate source project files.

Allowed writes:

- archive artifact in resolved output directory
- checksum sidecar in resolved output directory where implemented
- output directory creation when safely creatable under this addendum

Forbidden writes:

- writing artifacts inside project root
- writing marker files inside project root
- changing project files
- deleting project files
- changing project permissions
- changing runtime state
- modifying compose files
- modifying env files

The command SHOULD be designed so that source non-mutation can be tested.

---

## 8.15 Backup Result States

Recommended result states remain:

- `CREATED`
- `BLOCKED`
- `FAILED`

### `CREATED`

Use only when:

- inputs are valid
- project identity is trusted
- output directory is safe
- backup plan is valid
- archive was created
- artifact validation passed
- checksum validation passed where implemented
- source project was not mutated by the command

### `BLOCKED`

Use when execution does not safely proceed because of:

- invalid input
- missing project identity
- malformed project identity
- ambiguous source scope
- unsafe output directory
- output directory inside project root
- output directory cannot be created safely
- backup plan cannot be trusted

### `FAILED`

Use when execution begins but cannot complete successfully because of:

- archive creation failure
- filesystem write failure after planning
- artifact validation failure
- checksum validation failure
- unexpected runtime exception after safe execution began

---

## 8.16 Backup Exit Code Mapping

The current deterministic exit code policy SHOULD remain:

- `0` → backup artifact created and validation passed
- `2` → blocked, unsafe, ambiguous, or validation failed
- `3` → invalid command invocation or runtime execution failure

This addendum sharpens the interpretation:

- output directory inside project root SHOULD map to `2`
- output directory unsafe or ambiguous SHOULD map to `2`
- missing required CLI input MAY map to `3` if treated as CLI invocation error
- failed artifact validation SHOULD map to `2`
- unexpected implementation/runtime exception SHOULD map to `3`

The final mapping MUST remain deterministic.

---

## 9. `audit-project` Precision Rules

## 9.1 Audit Is Non-Mutating

`audit-project` is a non-mutating diagnostic command under ordinary execution.

It may inspect:

- project files
- project metadata
- compose configuration where required by audit context
- runtime status through bounded read-only commands
- explicit endpoint health where requested

It MUST NOT:

- deploy the project
- restart services
- start stopped services
- run `docker compose up`
- run application migrations
- repair Docker
- create missing project files
- mutate runtime state
- mutate project files

---

## 9.2 Runtime Boundary Precision

`audit-project` may inspect runtime state only as a consumer of already established HOST and DEPLOY state.

If Docker, Compose, or runtime services are unavailable, `audit-project` MUST classify based on evidence.

It MUST NOT repair the host runtime.

It MUST NOT perform deployment actions to make the audit pass.

### Required interpretation

- missing runtime evidence may produce `BLOCKED`
- failed but trustworthy service checks may produce `DEGRADED`
- all required checks passing may produce `HEALTHY`

The command MUST preserve the documented distinction between:

- cannot trust audit evidence → `BLOCKED`
- can trust audit evidence, but health check fails → `DEGRADED`

---

## 9.3 Compose Context Precision

For runtime-aware audit contexts, the project root is expected to contain `compose.yaml`.

If the current audit mode requires runtime-aware checks and `compose.yaml` is missing:

→ `audit-project` MUST classify as `BLOCKED`.

If a future audit mode supports metadata-only audit without compose context, that mode must be explicitly documented.

Until then, runtime-aware audit MUST NOT silently degrade into a weaker audit mode without reporting that limitation.

---

## 9.4 Endpoint Check Precision

Endpoint checks are optional and must be bounded.

If endpoint checks are used, they MUST come from:

- explicit `--endpoint-url`, or
- future documented configuration

Endpoint checks MUST use:

- bounded timeout
- deterministic failure handling
- no hidden retry storms
- no mutation

Endpoint failure SHOULD produce `DEGRADED` when the audit context is otherwise trustworthy.

Endpoint ambiguity or execution failure MAY produce `BLOCKED` when the check prevents trustworthy classification.

---

## 9.5 Audit Result Output Precision

`audit-project` output MUST make clear:

- project identity summary
- runtime context inspected
- checks executed
- checks skipped only if skipping is documented
- final classification
- degraded reasons where applicable
- blocked reason where applicable

The command MUST NOT report `HEALTHY` if required runtime evidence was unavailable, ambiguous, or skipped without documented allowance.

---

## 10. Implementation Guidance

## 10.1 Recommended Backup Module Boundaries

The backup implementation SHOULD remain modular.

Recommended module responsibilities:

```text
framework/modules/operate/backup/
├── inputs.py
├── inspect_project.py
├── paths.py
├── plan.py
├── archive.py
├── checksum.py
├── validate.py
└── runner.py
```

### `inputs.py`

- parse and normalize CLI input values
- reject missing required inputs
- preserve raw input for output summary where useful

### `paths.py`

- resolve canonical project root
- resolve canonical output directory
- detect output-inside-project-root
- detect symlink ambiguity
- classify output directory state

### `inspect_project.py`

- validate `project.yaml`
- extract trusted project identity
- return structured identity object

### `plan.py`

- construct backup plan
- compute artifact path
- compute checksum path where implemented
- define included source paths
- define excluded generated paths

### `archive.py`

- create archive from plan
- avoid hidden scope expansion
- avoid shell orchestration

### `checksum.py`

- create checksum sidecar where implemented
- validate checksum sidecar

### `validate.py`

- validate artifact exists
- validate artifact non-empty
- validate artifact path under output directory
- validate archive readability
- validate archive expected content
- validate checksum where implemented

### `runner.py`

- orchestrate validate inputs → inspect project → plan → create → validate → render result
- stop on blocked conditions
- produce deterministic output and exit codes

---

## 10.2 Recommended Audit Module Boundaries

The audit implementation SHOULD preserve the current architecture.

Recommended responsibilities:

```text
framework/modules/operate/audit/
├── inputs.py
├── inspect_project.py
├── checks.py
├── classify.py
├── runtime.py
└── runner.py
```

### Key rule

Runtime inspection helpers may execute read-only commands, but they MUST NOT mutate runtime state.

---

## 11. Test Requirements

The implementation of this addendum SHOULD include tests that prove the precision rules.

### 11.1 Backup Input and Path Tests

Required test cases:

- backup blocks when `--path` is missing
- backup blocks when `--output-dir` is missing
- backup blocks when project path does not exist
- backup blocks when project path is not a directory
- backup blocks when `project.yaml` is missing
- backup blocks when `project.yaml` is malformed
- backup resolves relative paths before planning
- backup compares canonical paths, not raw strings

### 11.2 Output Directory Tests

Required test cases:

- backup proceeds when output directory exists and is writable
- backup creates output directory when parent exists and is safe
- backup blocks when output parent does not exist
- backup blocks when output path exists as a file
- backup blocks when output directory is not writable
- backup blocks when output directory equals project root
- backup blocks when output directory is inside project root
- backup blocks when symlinked output path resolves inside project root
- backup blocks when output path ambiguity cannot be resolved

### 11.3 Backup Scope Tests

Required test cases:

- backup includes project root only by default
- backup does not include arbitrary external host paths
- backup blocks env-file inclusion when flag is set but path is missing
- backup blocks ambiguous env-file input
- backup records explicit env-file inclusion when allowed
- backup does not include output directory content
- backup does not include generated archive
- backup does not include checksum sidecar

### 11.4 Artifact Validation Tests

Required test cases:

- backup validates artifact exists
- backup validates artifact is non-empty
- backup validates artifact path is under resolved output directory
- backup validates artifact path matches backup plan
- backup validates archive can be opened
- backup validates archive contains expected planned source content
- backup fails if artifact is missing after creation
- backup fails if artifact is empty
- backup fails if checksum mismatch occurs where checksum is implemented
- backup does not report `CREATED` when validation fails

### 11.5 Source Non-Mutation Tests

Required test cases:

- backup does not modify source project files
- backup does not write marker files into project root
- backup does not change source permissions
- backup writes only to resolved output directory

### 11.6 Audit Boundary Tests

Required test cases:

- audit blocks when project identity is missing
- audit blocks when runtime-aware audit requires `compose.yaml` and it is missing
- audit does not mutate project files
- audit does not start services
- audit does not restart services
- audit does not run deployment commands
- audit does not repair Docker
- audit classifies failed trustworthy health checks as `DEGRADED`
- audit classifies untrustworthy or insufficient evidence as `BLOCKED`

---

## 12. Documentation Merge Plan

If this addendum is approved, canonical documents SHOULD be extended in this order.

### 12.1 `OPERATE_BASELINE_FDD.md`

Add a section such as:

```text
## Appendix — OPERATE Slice 01 Backup/Audit Precision
```

This section should summarize:

- output directory must be explicit
- output directory must not be inside project root
- backup success requires artifact validation
- audit remains non-mutating
- OPERATE does not repair HOST or DEPLOY responsibilities

### 12.2 `OPERATE_BASELINE_TDD.md`

Add technical details for:

- canonical path resolution
- output directory classification
- backup plan structure
- artifact validation responsibilities
- recommended module boundaries
- tests required for output-dir and artifact safety

### 12.3 `OPERATE_BASELINE_CONTRACT.md`

Add executable guarantees for:

- explicit output directory
- no output directory inside project root
- safe output directory creation
- no source mutation
- artifact validation before success
- audit non-mutation boundary

### 12.4 `BACKUP_PROJECT_SPEC.md`

Add detailed checks:

- output directory canonicalization
- output-inside-project-root rejection
- symlink ambiguity rejection
- artifact validation details
- checksum validation details
- result state mapping

### 12.5 `AUDIT_PROJECT_SPEC.md`

Add precision for:

- non-mutating runtime inspection
- compose context requirement
- endpoint boundedness
- blocked vs degraded distinction
- no runtime repair from audit

---

## 13. Codex Implementation Prompt Guardrails

When sending this slice to an implementation agent, use a prompt with these constraints:

```text
Implement OPERATE Slice 01 Backup/Audit Precision according to OPERATE_SLICE_01_BACKUP_AUDIT_PRECISION_ADDENDUM.md.

Do not rewrite existing OPERATE behavior except where this addendum explicitly extends it.
Do not modify HOST, PROJECT, or DEPLOY behavior.
Do not add restore, retention, remote sync, database dump, deployment, or runtime repair features.
Preserve current command names and documented result states.
Implement path canonicalization, output-dir safety checks, artifact validation, and audit non-mutation boundaries.
Add tests proving the new precision rules.
Fail closed on ambiguity.
```

---

## 14. Acceptance Criteria

This addendum is considered ready for canonical merge when all are true:

1. It is approved as an extension to the current OPERATE baseline.
2. No current baseline section is deleted or compressed.
3. `backup-project` output directory behavior is unambiguous.
4. Output directory inside project root is explicitly blocked.
5. Safe output directory creation rules are explicit.
6. Artifact validation requirements are explicit.
7. Checksum behavior is explicit where implemented.
8. Source non-mutation is explicit.
9. `audit-project` non-mutation boundaries are explicit.
10. HOST/PROJECT/DEPLOY boundaries are preserved.
11. Canonical merge changes are applied additively.
12. Tests are defined for all new precision rules.

---

## 15. Final Statement

OPERATE Slice 01 does not expand the framework into restore, monitoring, remediation, or deployment behavior.

It makes the existing OPERATE baseline safer and more deterministic by clarifying exactly how audit and backup must behave.

The most important executable rule introduced by this addendum is:

> `backup-project --output-dir` MUST be explicit, canonicalized, safe, writable or safely creatable, and outside the project root.

The second most important executable rule is:

> `backup-project` MUST NOT report success until the backup artifact is validated.

The third most important executable rule is:

> `audit-project` MUST remain non-mutating and MUST NOT repair HOST or DEPLOY responsibilities.

This addendum is extension-only and must be merged into canonical OPERATE documents without removing previously approved normative content.


---

## Merge Completion Note

This addendum has been merged additively into the canonical OPERATE documents listed in its documentation merge plan. It is retained as a change record.
