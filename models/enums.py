"""
Shared enumerations for the VPS framework.

Defines bounded values for:
    - CheckStatus: result status of individual audit checks (OK, WARN, FAIL)
    - HostClassification: final host classification after audit (CLEAN → BLOCKED)
    - ClassificationImpact: the classification effect a check result carries
    - ReconcileAction: the action taken during a reconciliation step

These enums prevent scattered string literals across the codebase.
Governed by: AUDIT_VPS_SPEC.md §6, §7 and HOST_BASELINE_TDD.md §11.
"""

from enum import Enum


class CheckStatus(str, Enum):
    """Result status of an individual audit check.

    Values:
        OK:   Check passed successfully.
        WARN: Check detected a non-blocking deviation.
        FAIL: Check detected a blocking failure.
    """

    OK = "OK"
    WARN = "WARN"
    FAIL = "FAIL"


class HostClassification(str, Enum):
    """Final host classification after all audit checks complete.

    Priority (highest to lowest):
        BLOCKED > SANEABLE > COMPATIBLE > CLEAN

    Values:
        CLEAN:      Minimal relevant prior state, no conflicts.
        COMPATIBLE: Existing state is aligned and safe to reuse.
        SANEABLE:   State not yet aligned but safely normalizable.
        BLOCKED:    Unsafe or ambiguous state, manual intervention required.
    """

    CLEAN = "CLEAN"
    COMPATIBLE = "COMPATIBLE"
    SANEABLE = "SANEABLE"
    BLOCKED = "BLOCKED"


class ClassificationImpact(str, Enum):
    """The classification effect that a single check result carries.

    Values:
        NONE:     No impact on classification (check is OK).
        SANEABLE: Check result pushes classification toward SANEABLE.
        BLOCKED:  Check result pushes classification toward BLOCKED.
    """

    NONE = "NONE"
    SANEABLE = "SANEABLE"
    BLOCKED = "BLOCKED"


class ReconcileAction(str, Enum):
    """The action taken during a reconciliation step.

    Used by init-vps to report what happened at each step.
    Governed by: HOST_BASELINE_TDD.md §11.

    Values:
        CREATED:         Resource was created (user, directory, file).
        REUSED:          Existing compatible resource was reused as-is.
        REPAIRED:        Existing resource was repaired (permissions, ownership).
        SKIPPED:         Step was skipped (already in target state).
        FAILED:          Step failed (validation or execution error).
        BLOCKED:         Step aborted due to ambiguous or unsafe state.
    """

    CREATED = "CREATED"
    REUSED = "REUSED"
    REPAIRED = "REPAIRED"
    SKIPPED = "SKIPPED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"


# --- PROJECT Enums ---

class TargetClassification(str, Enum):
    """Classification states for project target paths. (PROJECT)"""

    CLEAN = "CLEAN"
    COMPATIBLE = "COMPATIBLE"
    SANEABLE = "SANEABLE"
    BLOCKED = "BLOCKED"


class ScaffoldAction(str, Enum):
    """Actions taken during project scaffold generation. (PROJECT)"""

    CREATE = "CREATE"
    REUSE = "REUSE"
    SKIP = "SKIP"
    BLOCK = "BLOCK"


# --- DEPLOY Enums ---

class DeploymentClassification(str, Enum):
    """Classification states for project deployment contexts. (DEPLOY)"""

    READY = "READY"
    REDEPLOYABLE = "REDEPLOYABLE"
    BLOCKED = "BLOCKED"


class DeployAction(str, Enum):
    """Actions taken during project deployment. (DEPLOY)"""

    VALIDATE = "VALIDATE"
    BUILD = "BUILD"
    START = "START"
    SMOKE = "SMOKE"
    BLOCK = "BLOCK"


# --- OPERATE Enums ---

class AuditClassification(str, Enum):
    """Classification states for project runtime health audits. (OPERATE)"""

    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    BLOCKED = "BLOCKED"


class BackupResultState(str, Enum):
    """Result states for project backup creation. (OPERATE)"""

    CREATED = "CREATED"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
