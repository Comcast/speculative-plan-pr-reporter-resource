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
import os

import requests

from logger import logger

log = logger.getChild(__name__)


class GithubUtils:
    def __init__(self, repository, gh_api, access_token, pr_path) -> None:
        self.repository = repository
        self.gh_api = gh_api
        self.access_token = access_token
        self.pr_path = pr_path

    def get_pr_id(self):
        with open(os.path.join(self.pr_path, ".git", "resource", "version.json"), "r") as version_json:
            pr_id = json.loads(version_json.read())["pr"]
        return pr_id

    def post_pr_comment(self, body):
        headers = {
            "Authorization": "Bearer " + self.access_token,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        data = {"body": body}

        response = requests.post(
            self.gh_api + "/repos/" + self.repository + "/issues/" + self.get_pr_id() + "/comments",
            headers=headers,
            data=json.dumps(data),
        )
        log.info("PR comment posted to github: " + str(response.status_code))
        if response.status_code == 201:
            return response.json()["html_url"]
        else:
            raise GithubEndpointException(
                "An error occurred while posting comment to Github. Status Code: {} Response {}",
                response.status_code,
                response.text,
            )


class GithubEndpointException(Exception):
    pass
