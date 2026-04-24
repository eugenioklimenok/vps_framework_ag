# HOST_BASELINE_FDD.md

## Purpose
Define the functional behavior of the HOST phase in the VPS Framework.

## Scope
The HOST phase is responsible for preparing a VPS into a deterministic, secure, and deploy-ready state.

## Functional Slices

### Slice 1: Operator User & SSH Hardening
- Ensure operator user exists
- Validate home directory
- Configure SSH key-based access
- Disable password authentication
- Disable root login
- Validate effective SSH runtime config

### Slice 2: Docker Runtime Baseline

#### Objective
Ensure a consistent and usable container runtime for DEPLOY phase.

#### Responsibilities
- Install Docker Engine (official package source)
- Install Docker Compose v2 plugin
- Enable docker.service
- Start docker.service
- Add operator user to docker group
- Validate Docker CLI usability
- Validate Docker daemon availability
- Validate Docker Compose v2 availability

#### Validation Rules
- docker --version must succeed
- docker ps must execute without permission errors
- docker compose version must be available
- Docker daemon must be active (systemctl)

#### Classification
- Missing Docker → SANEABLE
- Broken Docker → BLOCKED
- Fully working → OK

## Non-Responsibilities
- No application deployment
- No project-level configuration
- No runtime usage (handled by DEPLOY)

## Contract Boundary
HOST prepares runtime. DEPLOY consumes runtime.
