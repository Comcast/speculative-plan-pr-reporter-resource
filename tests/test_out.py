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

import json
import sys
from unittest import mock

import pytest

from concourse_terraform_plan_pr_reporter_resource import out

# There isn't a need to test the complex/sensitive markdowns because those are already handled in tedivm/terraformer.


@mock.patch.object(out.GithubUtils, "post_pr_comment")
def test_out_simple(post_pr_comment):
    post_pr_comment.return_value = "https://github.com/test-org/test-repo/issues/1"
    with open("tests/resources/test-input.json", "r") as test_input_file:
        # Computed value compared against actual value.
        assert "{'version': {'ref': 'aHR0cHM6Ly9naXRodWIuY29tL3Rlc3Qtb3JnL3Rlc3QtcmVwby9pc3N1ZXMvMQ=='}}" == str(
            out._out(json.load(test_input_file))
        )
