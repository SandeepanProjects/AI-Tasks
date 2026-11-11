"""Version-diff and historical artifact impact candidate generation."""
from dataclasses import dataclass
from difflib import unified_diff

@dataclass(frozen=True)
class PolicyChange:
    policy_code: str
    old_version: str
    new_version: str
    added_lines: tuple[str, ...]
    removed_lines: tuple[str, ...]

class PolicyImpactAnalyzer:
    @staticmethod
    def compare(policy_code: str, old_version: str, old_text: str, new_version: str, new_text: str) -> PolicyChange:
        diff = list(unified_diff(old_text.splitlines(), new_text.splitlines(), lineterm=""))
        return PolicyChange(policy_code, old_version, new_version,
                            tuple(x[1:] for x in diff if x.startswith("+") and not x.startswith("+++")),
                            tuple(x[1:] for x in diff if x.startswith("-") and not x.startswith("---")))
    @staticmethod
    def candidates(change: PolicyChange, historical_artifacts: list[dict]) -> list[dict]:
        terms = {w.casefold() for line in change.added_lines + change.removed_lines for w in line.split() if len(w) > 4}
        candidates = []
        for artifact in historical_artifacts:
            content = str(artifact.get("content", "")).casefold()
            hits = sorted(term for term in terms if term in content)
            if hits:
                candidates.append({"artifact_id": artifact["artifact_id"], "matched_terms": hits,
                                   "status": "reassessment_candidate", "requires_human_review": True})
        return candidates
