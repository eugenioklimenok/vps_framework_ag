"""
Tests for the audit classification reducer.
Governed by: AUDIT_VPS_SPEC.md §7.
"""

from models.check_result import CheckResult
from models.enums import CheckStatus, ClassificationImpact, HostClassification
from modules.host.audit.classifier import reduce_classification


def _create_result(impact: ClassificationImpact, status: CheckStatus = CheckStatus.OK) -> CheckResult:
    """Helper to create a minimal CheckResult for testing the classifier."""
    return CheckResult(
        check_id="TEST", title="Test", category="TEST", description="Test",
        evidence_command="test", expected_behavior="test",
        status=status, evidence="", message="", classification_impact=impact,
    )


def test_classifier_empty_results():
    """Empty results list must default to BLOCKED for safety."""
    assert reduce_classification([]) == HostClassification.BLOCKED


def test_classifier_all_clean():
    """All OK checks with NONE impact result in CLEAN."""
    results = [
        _create_result(ClassificationImpact.NONE, CheckStatus.OK),
        _create_result(ClassificationImpact.NONE, CheckStatus.OK),
    ]
    assert reduce_classification(results) == HostClassification.CLEAN


def test_classifier_compatible():
    """WARN check with NONE impact results in COMPATIBLE."""
    results = [
        _create_result(ClassificationImpact.NONE, CheckStatus.OK),
        _create_result(ClassificationImpact.NONE, CheckStatus.WARN),
    ]
    assert reduce_classification(results) == HostClassification.COMPATIBLE


def test_classifier_saneable():
    """WARN check with SANEABLE impact results in SANEABLE."""
    results = [
        _create_result(ClassificationImpact.NONE, CheckStatus.OK),
        _create_result(ClassificationImpact.SANEABLE, CheckStatus.WARN),
    ]
    assert reduce_classification(results) == HostClassification.SANEABLE


def test_classifier_blocked():
    """FAIL check with BLOCKED impact results in BLOCKED."""
    results = [
        _create_result(ClassificationImpact.NONE, CheckStatus.OK),
        _create_result(ClassificationImpact.BLOCKED, CheckStatus.FAIL),
    ]
    assert reduce_classification(results) == HostClassification.BLOCKED


def test_classifier_priority():
    """Priority rule: BLOCKED > SANEABLE > COMPATIBLE > CLEAN."""
    results = [
        _create_result(ClassificationImpact.NONE, CheckStatus.WARN),  # COMPATIBLE
        _create_result(ClassificationImpact.SANEABLE, CheckStatus.WARN), # SANEABLE
        _create_result(ClassificationImpact.BLOCKED, CheckStatus.FAIL),  # BLOCKED
    ]
    # BLOCKED should win
    assert reduce_classification(results) == HostClassification.BLOCKED
