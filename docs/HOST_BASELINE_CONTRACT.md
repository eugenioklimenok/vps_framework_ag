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
- read-only
- classifies: OK / SANEABLE / BLOCKED

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
SANEABLE:
- docker missing

BLOCKED:
- broken docker
- ambiguous state

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
