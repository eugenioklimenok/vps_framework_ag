"""
Deploy execution result models.
"""

from dataclasses import dataclass, field

from models.enums import DeployAction, DeploymentClassification


@dataclass(frozen=True)
class DeployResult:
    """Result of a deploy-project execution.
    
    Attributes:
        classification:   Final deployment context classification.
        actions_taken:    List of actions performed.
        project_slug:     The resolved project identity.
        config_validated: True if pre-mutation config validation passed.
        build_succeeded:  True if the build phase succeeded or was skipped.
        startup_succeeded: True if the startup phase succeeded.
        smoke_passed:     True if baseline smoke tests passed.
        validation_passed: True if final runtime state validation passed.
        blocked_reason:   Reason for aborting, if applicable.
    """

    classification: DeploymentClassification
    actions_taken: list[DeployAction] = field(default_factory=list)
    project_slug: str = ""
    config_validated: bool = False
    build_succeeded: bool = False
    startup_succeeded: bool = False
    smoke_passed: bool = False
    validation_passed: bool = False
    blocked_reason: str = ""
