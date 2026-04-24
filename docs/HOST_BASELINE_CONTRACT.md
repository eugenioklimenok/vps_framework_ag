# HOST Baseline — Contract (HOST_BASELINE_CONTRACT.md)

## 1. Purpose
Defines formal behavior and guarantees of HOST phase.

## 2. Boundary
HOST prepares runtime.
DEPLOY consumes runtime.

## 3. Commands
- audit-vps
- init-vps
- harden-vps

## 4. audit-vps

- MUST be read-only
- MUST classify host using the canonical audit classification model:
  - CLEAN
  - COMPATIBLE
  - SANEABLE
  - BLOCKED

### Classification terminology rule

The canonical HOST audit classifications are only:

- CLEAN
- COMPATIBLE
- SANEABLE
- BLOCKED

The term `OK` MUST NEVER be used as a host classification.

`OK` is allowed only as a per-check status indicator inside audit output.

Examples:

- `[OK] CHECK_DOCKER_01` is valid check output.
- `Classification: OK` is INVALID and FORBIDDEN.
- `Classification: COMPATIBLE` is valid.


## 5. init-vps
- deterministic
- idempotent
- fail closed
- post-validation required

## 6. Slices

### Slice 1 — Operator & SSH
- user exists
- ssh access works

### Slice 2 — Docker Runtime
- docker installed
- docker running
- docker compose v2 available
- operator access valid

## 7. Runtime Requirement
Required:
- docker
- docker compose

Not accepted:
- docker-compose only

## 8. Validation
Must pass:
- docker --version
- docker compose version
- docker ps

## 9. Classification

### CLEAN
Host has minimal relevant prior state and no conflicts for the current HOST baseline.

### COMPATIBLE
Host already satisfies the current HOST baseline.

### SANEABLE
Host is not aligned yet but can be normalized safely by documented `init-vps` slices.

Examples:
- operator user missing
- SSH access filesystem missing but safely creatable
- Docker missing
- Docker Compose v2 missing
- Docker service stopped but safely startable
- operator missing Docker group membership

### BLOCKED
Host state is unsafe, broken, or ambiguous.

Examples:
- unsupported OS
- invalid SSH daemon configuration
- ambiguous operator user or filesystem state
- broken Docker daemon
- ambiguous Docker installation
- conflicting Docker package sources

## 10. Allowed
- install docker
- configure service
- add user to docker group

## 11. Forbidden
- deploy apps
- run compose for apps
- modify project

## 12. Idempotency
- no duplicate install
- no breaking state

## 13. Safety
Stop if:
- BLOCKED
- validation fail

## 14. DEPLOY Interaction
DEPLOY assumes runtime exists.

## 15. Final
HOST guarantees VPS is deploy-ready.
