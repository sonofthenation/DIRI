from diri.core.models import ProjectSummary


def find_evidence_for_terms(project: ProjectSummary, terms: list[str]) -> list[str]:
    evidence = []
    lower_files = {path.lower(): path for path in project.files}
    lower_summaries = {path: summary.lower() for path, summary in project.file_summaries.items()}
    for term in terms:
        normalized = term.lower().replace(" ", "_")
        for lower_path, original in lower_files.items():
            if normalized in lower_path or term.lower() in lower_path:
                evidence.append(original)
        for original, summary in lower_summaries.items():
            if term.lower() in summary:
                evidence.append(original)
    return sorted(set(evidence))
