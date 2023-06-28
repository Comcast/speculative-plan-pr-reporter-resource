# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2023-06-28

### Added

- Read speculative plan JSON parsed through `terraformer` and generate a markdown table of the changes that could be made by the plan
  along with a expandable description of each resource change.
- Post the markdown table as a comment on the PR, the metadata of which is derived using `telia-oss/github-pr-resource`.