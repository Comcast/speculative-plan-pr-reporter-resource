# Copyright 2023 Comcast Cable Communications Management, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
