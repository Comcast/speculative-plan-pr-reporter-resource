#!/usr/bin/env python

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
