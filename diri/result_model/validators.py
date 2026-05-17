from diri.core.models import ExpectedResultModel


def validate_expected_result(model: ExpectedResultModel) -> ExpectedResultModel:
    if not model.result_summary:
        model.result_summary = "Expected result is not yet clearly defined."
    if not model.acceptance_criteria:
        model.acceptance_criteria.append("Developer can recognize the intended result in the running project.")
    return model
