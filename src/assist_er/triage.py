from __future__ import annotations

from assist_er.models import Issue, TriageDecision, TriageSeverity

CRITICAL_KEYWORDS = ("outage", "breach", "data loss", "payment failure", "security")
HIGH_KEYWORDS = ("bug", "broken", "error", "fails", "failure")
MEDIUM_KEYWORDS = ("performance", "slow", "flaky", "ux")


class TriageService:
    def classify(self, issue: Issue) -> TriageDecision:
        haystack = f"{issue.title} {issue.body}".lower()
        if any(word in haystack for word in CRITICAL_KEYWORDS):
            return TriageDecision(
                issue_number=issue.number,
                severity=TriageSeverity.critical,
                rationale="Contains critical-risk keywords indicating user or business impact.",
                suggested_labels=["severity:critical", "needs-immediate-attention"],
            )
        if any(word in haystack for word in HIGH_KEYWORDS):
            return TriageDecision(
                issue_number=issue.number,
                severity=TriageSeverity.high,
                rationale="Likely functional defect and should be prioritized in current sprint.",
                suggested_labels=["severity:high", "type:bug"],
            )
        if any(word in haystack for word in MEDIUM_KEYWORDS):
            return TriageDecision(
                issue_number=issue.number,
                severity=TriageSeverity.medium,
                rationale="Potential quality concern that should be addressed soon.",
                suggested_labels=["severity:medium"],
            )
        return TriageDecision(
            issue_number=issue.number,
            severity=TriageSeverity.low,
            rationale="No urgent risk markers found.",
            suggested_labels=["severity:low"],
        )
