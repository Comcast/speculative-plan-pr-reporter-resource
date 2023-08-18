#!/usr/bin/env python

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

import base64
import json
import os
from logging import getLogger
from sys import argv, stdin, stdout

from terraformer import TerraformPlan

from git_utils import GithubUtils
from markdown_reporter import MarkdownReporter

log = getLogger(__name__)


def _out(payload, working_dir="."):
    # Read source and params from payload

    try:
        plan_json_file_path = (
            os.path.join(working_dir, payload["params"]["plan_json_file"])
            if "plan_json_file" in payload["params"]
            else None
        )
        gh_repository = payload["source"]["gh_repository"] if "gh_repository" in payload["source"] else None
        gh_api = payload["source"]["gh_api"] if "gh_api" in payload["source"] else None
        pr_path = os.path.join(working_dir, payload["source"]["pr_path"]) if "pr_path" in payload["source"] else None
        gh_access_token = payload["source"]["gh_access_token"] if "gh_access_token" in payload["source"] else None

    except KeyError as e:
        log.warning(f"Options undefined : {e}")

    state_changes_markdown = MarkdownReporter(
        TerraformPlan(cwd="", plan_path=plan_json_file_path, is_json=True)
    ).generate()

    comment_url = GithubUtils(gh_repository, gh_api, gh_access_token, pr_path).post_pr_comment(state_changes_markdown)

    return {"version": {"ref": base64.b64encode(comment_url.encode("ascii")).decode("ascii")}}


if __name__ == "__main__":
    print(json.dumps(_out(json.loads(stdin.read()), argv[1])), file=stdout)
