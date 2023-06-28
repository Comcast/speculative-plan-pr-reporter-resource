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
