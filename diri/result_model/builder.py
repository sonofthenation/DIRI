from diri.core.models import DeveloperIntent, ExpectedResultModel
from diri.result_model.acceptance_criteria import build_acceptance_criteria
from diri.result_model.validators import validate_expected_result


def build_expected_result(intent: DeveloperIntent) -> ExpectedResultModel:
    model = ExpectedResultModel(
        result_summary=intent.true_goal or intent.surface_goal,
        success_conditions=[
            "The implementation visibly and functionally matches the developer intent.",
            "Important must-have expectations are present in the project.",
        ],
        failure_conditions=[
            "The project is technically present but does not reproduce the intended result.",
            "The output matches a negative example from the developer notes.",
        ],
        feature_expectations=intent.functional_target,
        ux_expectations=intent.visual_target + intent.emotional_target,
        architecture_expectations=[
            "Architecture supports the expected result without becoming the evaluation goal itself."
        ],
        runtime_expectations=[
            "CLI commands complete and produce inspectable JSON/Markdown artifacts."
        ],
        acceptance_criteria=build_acceptance_criteria(intent),
    )
    return validate_expected_result(model)
