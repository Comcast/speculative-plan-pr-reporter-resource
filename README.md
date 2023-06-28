# concourse-terraform-plan-reporter

A Concourse resource to generate a report from a speculative terraform plan.

Written in Python, it currently supports publishing the report of changes as a table to a Github Pull Request
by taking advantage of the [telia-oss/github-pr-resource](https://github.com/telia-oss/github-pr-resource)
to fetch metadata for the PR.

## Source Configuration

| Parameter | Required | Default | Description |
|-|-|-|-|
| gh_api_endpoint | No | `https://api.github.com` | The API endpoint for the Github instance to which the resource should publish the speculative plan report. |
| gh_access_token | Yes |  | The Github Personal Access Token to be used for accessing the Github API endpoint. This is usually fetched from a secret store like Vault and defined in the pipeline configuration as ((github.access_token)) |
| gh_repository | Yes | | The Github repository for which the pipeline is being executed. The path should be in the format `org_name/repo_name`. |
| pr_path | Yes | | The directory path to the pull request where `get` on `github-pr-resource` fetches the repository and the pull request metadata. |

## Behavior

### `check`

N/A. The check itself doesn't do anything in this resource currently to trigger
any action.

### `put`

| Parameter | Required | Default | Description |
|-|-|-|-|
| plan_json_file | Yes | | The path to the terraform plan in the JSON format, generated using `terraform show --json <plan_file>`. This can be the result of a task or the use of `ljfranklin/terraform-resource` |

The version emitted from out is a `base64` representation of the terraform changeset
in the markdown table format, comprising of the resources that are being created, modified or removed.

### `get`

The base64 representation of the terraform changeset is decoded and written to a file called `state_changes.md`
under the resource directory.

## Example

```yml
resource_types:
- name: terraform
  type: registry-image
  source:
    repository: ljfranklin/terraform-resource

- name: terraform-plan-gh-pr-resource
  type: docker-image
  source:
    repository: <docker-registry-namespace>/terraform-plan-pr-reporter-resource # Registry URL and namespace where the resource image is pushed to. The image can be generated using the `Dockerfile`.

- name: pull-request
  type: registry-image
  source:
    repository: teliaoss/github-pr-resource

resources:
- name: examples
  type: git
  source:
    uri: https://github.com/concourse/examples.git # This has a terraform example
    branch: master

- name: appcode-pull-request
  type: pull-request
  check_every: 12h
  source:
    repository: <gh_org>/<gh_repository>
    access_token: ((github.access_token))
    v3_endpoint: https://api.github.com
    v4_endpoint: https://api.github.com/graphql
    base_branch: main
    states: ["OPEN"]
    disable_forks: false

- name: deve-env-terraform
  type: terraform
  source:
    env_name: main
    backend_type: s3
    backend_config:
      bucket     : ((terraform.backend.bucket))
      region     : us-east-1
      key        : ((terraform.backend.key))
      access_key : ((aws.access_key_id))
      secret_key : ((aws.secret_access_key))
      token      : ((aws.session_token))

- name: terraform-gh-pr
  type: terraform-plan-gh-pr-resource
  source:
    gh_access_token: ((github.access_token))
    gh_api: https://api.github.com
    pr_path: appcode-pull-request
    gh_repository: <gh_org>/gh_repository>
jobs:

- name: terraform-plan-aws
  serial: true
  plan:
  
  - get: examples
  - put: deve-env-terraform
    get_params:
      output_planfile: true
      output_statefile: true
    params:
      plan_only: true
      env_name      : deve
      terraform_source: examples/terraform/staging
  - get: appcode-pull-request
  - put: terraform-gh-pr
    params:
      plan_json_file: "deve-env-terraform/plan.json"
```