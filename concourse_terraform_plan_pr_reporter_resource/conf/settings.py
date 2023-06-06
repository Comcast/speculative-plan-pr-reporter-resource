from pydantic import BaseSettings


class Settings(BaseSettings):
    project_name: str = "concourse-terraform-plan-pr-reporter-resource"
    debug: bool = False
