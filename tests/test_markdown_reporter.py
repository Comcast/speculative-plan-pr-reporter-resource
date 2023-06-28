import os
from unittest import mock

from terraformer import TerraformPlan

from concourse_terraform_plan_pr_reporter_resource.markdown_reporter import (
    MarkdownReporter,
)


def test_markdown_output():
    state_changes_markdown = MarkdownReporter(
        TerraformPlan(cwd="", plan_path="tests/resources/terraform-plans/plan.json", is_json=True)
    ).generate()
    with open("tests/resources/markdown-outputs/simple-plan.md") as expected_markdown:
        assert expected_markdown.read() == state_changes_markdown
