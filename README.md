# VPS Framework

Modular Python-based CLI framework for VPS preparation, validation and management.

## Architecture

The framework is organized into four functional domains:

```
HOST → PROJECT → DEPLOY → OPERATE
```

### Current Implementation: HOST Module (Slice 1)

- **`audit-vps`** — Read-only diagnostic audit and host classification
- **`init-vps`** — Controlled reconciliation (user + SSH access)
- **`harden-vps`** — Post-initialization security hardening (deferred)

## Requirements

- Python 3.12+
- Linux VPS (Ubuntu) for runtime execution
- Windows supported for development and testing

## Quick Start

```bash
# Install dependencies
pip install -e ".[dev]"

# Show available commands
python main.py --help

# HOST module commands
python main.py host --help
python main.py host audit-vps --help
python main.py host init-vps --help

# Run tests
pytest
```

## Documentation

All design and specification documents are in the `docs/` directory.
See `docs/FRAMEWORK_ARCHITECTURE_MODEL.md` for the architectural overview.
