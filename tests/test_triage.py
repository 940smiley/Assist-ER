from assist_er.models import Issue, TriageSeverity
from assist_er.triage import TriageService


def test_triage_marks_critical_issue() -> None:
    issue = Issue(
        number=1,
        title="Security breach causes outage",
        state="open",
        labels=[],
        body="Production outage with possible data loss.",
        html_url="https://example.com/1",
    )
    decision = TriageService().classify(issue)
    assert decision.severity == TriageSeverity.critical
    assert "severity:critical" in decision.suggested_labels


def test_triage_marks_low_by_default() -> None:
    issue = Issue(
        number=2,
        title="Add docs improvements",
        state="open",
        labels=[],
        body="Requesting more examples in docs",
        html_url="https://example.com/2",
    )
    decision = TriageService().classify(issue)
    assert decision.severity == TriageSeverity.low
