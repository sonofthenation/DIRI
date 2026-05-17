from diri.constants import METRIC_LABELS
from diri.core.models import DiriReport
from diri.planner.recommendation_engine import build_recommendations


def render_markdown_report(report: DiriReport) -> str:
    lines = [
        "# DIRI Report",
        "",
        "## Summary",
        "",
        f"Raw DIRI Score: {report.raw_score}/100  ",
        f"DIRI Confidence: {report.confidence}/100  ",
        f"Trusted DIRI Score: {report.trusted_score}/100  ",
        f"Level: {report.level}",
        "",
        "## Meaning",
        "",
        _meaning(report),
        "",
        "## Metric Scores",
        "",
        "| Metric | Score | Meaning |",
        "|---|---:|---|",
    ]
    for key, label in METRIC_LABELS.items():
        metric = report.metric_scores[key]
        lines.append(f"| {label} | {metric.score} | {metric.reasoning} |")

    lines.extend(["", "## Main Gaps", ""])
    if report.gaps:
        for index, gap in enumerate(report.gaps, start=1):
            lines.extend(
                [
                    f"### {index}. {gap.title}",
                    "",
                    f"Expected: {gap.expected}  ",
                    f"Actual: {gap.actual}  ",
                    f"Severity: {gap.severity}",
                    "",
                ]
            )
    else:
        lines.append("No major gaps detected by this DIRI version.")

    lines.extend(["", "## TODO Plan", ""])
    for priority in ["high", "medium", "low"]:
        items = [item for item in report.todo if item.priority == priority]
        if not items:
            continue
        lines.extend([f"### {priority.title()} Priority", ""])
        for item in items:
            lines.append(f"- [ ] {item.title}  ")
            lines.append(f"  Expected gain: +{item.expected_gain} DIRI  ")
            lines.append("  Acceptance:")
            for criterion in item.acceptance_criteria:
                lines.append(f"  - {criterion}")
            lines.append("")

    lines.extend(["## Recommendations", ""])
    for index, recommendation in enumerate(build_recommendations(report), start=1):
        lines.append(f"{index}. {recommendation}")
    lines.append("")
    return "\n".join(lines)


def _meaning(report: DiriReport) -> str:
    if report.raw_score <= 30:
        return "The code currently misses the developer intent."
    if report.raw_score <= 50:
        return "The code weakly reproduces the expected result and needs focused correction."
    if report.raw_score <= 70:
        return "The code partially reproduces the expected result, but important gaps remain."
    if report.raw_score <= 85:
        return "The code strongly reproduces the expected result with some remaining refinements."
    return "The code closely reproduces the intended result."
