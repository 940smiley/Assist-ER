from __future__ import annotations

from assist_er.pro.models import PRSummary


class PRReviewer:
    def summarize(self, repo: str, number: int, title: str, body: str) -> PRSummary:
        risks: list[str] = []
        lower = f"{title} {body}".lower()
        if "security" in lower:
            risks.append("Contains security-related changes")
        if "migration" in lower:
            risks.append("Potential schema/data migration risk")
        summary = f"PR #{number}: {title}. Estimated impact: {'high' if risks else 'moderate'}"
        return PRSummary(repo=repo, number=number, summary=summary, risks=risks)
