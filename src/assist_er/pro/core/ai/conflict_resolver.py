from __future__ import annotations


class ConflictResolver:
    def resolve(self, repo_slug: str, pr_number: int) -> str:
        return (
            f"PR #{pr_number} in {repo_slug} has merge conflicts. "
            "Assist-ER Pro prepared a resolution plan; manual commit update is still required."
        )
