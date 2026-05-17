from diri.core.models import DiriReport, InternalDiriReport


def render_console_report(report: DiriReport) -> str:
    gaps = "\n".join(f"- {gap.title} ({gap.affected_metric}, {gap.severity})" for gap in report.gaps[:5])
    if not gaps:
        gaps = "- No major gaps detected"
    next_actions = "\n".join(
        f"- [{item.priority}] {item.title} (+{item.expected_gain})" for item in report.todo[:5]
    )
    if not next_actions:
        next_actions = "- Keep validating new changes against developer intent"
    return (
        f"Project DIRI Score: {report.raw_score}/100\n"
        f"DIRI Confidence: {report.confidence}/100\n"
        f"Trusted DIRI Score: {report.trusted_score}/100\n"
        f"Level: {report.level}\n\n"
        f"Main gaps:\n{gaps}\n\n"
        f"Next actions:\n{next_actions}"
    )


def render_internal_report(report: InternalDiriReport) -> str:
    weak = ", ".join(report.weak_at) if report.weak_at else "none"
    return (
        f"DIRI v{report.diri_version} Internal DIRI: {report.confidence_index}/100\n"
        f"Trust level: {report.trust_level}\n"
        f"Weak at: {weak}"
    )
