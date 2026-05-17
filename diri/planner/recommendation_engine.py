from diri.core.models import DiriReport


def build_recommendations(report: DiriReport) -> list[str]:
    recommendations = []
    for gap in report.gaps[:3]:
        recommendations.append(f"Address {gap.affected_metric}: {gap.title}.")
    if not recommendations:
        recommendations.append("Keep validating new changes against developer intent.")
    return recommendations
