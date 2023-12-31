SHELL := /bin/bash
PACKAGE_SLUG=concourse_terraform_plan_pr_reporter_resource
DOCKER_IMAGE_TAG=<docker-registry>/terraform-plan-pr-reporter-resource:<tag>
ifdef CI
	PYTHON_PYENV :=
	PYTHON_VERSION := $(shell python --version|cut -d" " -f2)
else
	PYTHON_PYENV := pyenv
	PYTHON_VERSION := $(shell cat .python-version)
endif
PYTHON_SHORT_VERSION := $(shell echo $(PYTHON_VERSION) | grep -o '[0-9].[0-9]*')

ifeq ($(USE_SYSTEM_PYTHON), true)
	PYTHON_PACKAGE_PATH:=$(shell python -c "import sys; print(sys.path[-1])")
	PYTHON_ENV :=
	PYTHON := python
	PYTHON_VENV :=
else
	PYTHON_PACKAGE_PATH:=.venv/lib/python$(PYTHON_SHORT_VERSION)/site-packages
	PYTHON_ENV :=  . .venv/bin/activate &&
	PYTHON := . .venv/bin/activate && python
	PYTHON_VENV := .venv
endif

# Used to confirm that pip has run at least once
PACKAGE_CHECK:=$(PYTHON_PACKAGE_PATH)/piptools
PYTHON_DEPS := $(PACKAGE_CHECK)


.PHONY: all
all: $(PACKAGE_CHECK)

.PHONY: install
install: $(PYTHON_PYENV) $(PYTHON_VENV) pip

.venv:
	python -m venv .venv

.PHONY: pyenv
pyenv:
	pyenv install --skip-existing $(PYTHON_VERSION)

pip: $(PYTHON_VENV)
	$(PYTHON) -m pip install -e .[dev]

$(PACKAGE_CHECK): $(PYTHON_VENV)
	$(PYTHON) -m pip install -e .[dev]


#
# Formatting
#

.PHONY: pretty
pretty: black_fixes isort_fixes dapperdata_fixes tomlsort_fixes

.PHONY: black_fixes
black_fixes:
	$(PYTHON) -m black .

.PHONY: isort_fixes
isort_fixes:
	$(PYTHON) -m isort .

.PHONY: dapperdata_fixes
dapperdata_fixes:
	$(PYTHON) -m dapperdata.cli pretty . --no-dry-run

.PHONY: tomlsort_fixes
tomlsort_fixes:
	$(PYTHON_ENV) toml-sort $$(find . -not -path "./.venv/*" -name "*.toml") -i

#
# Testing
#

.PHONY: tests
tests: install pytest isort_check black_check mypy_check dapperdata_check tomlsort_check

.PHONY: pytest
pytest:
	$(PYTHON) -m pytest --cov=./${PACKAGE_SLUG} --cov-report=term-missing tests

.PHONY: pytest_loud
pytest_loud:
	$(PYTHON) -m pytest -s --log-level=INFO --cov=./${PACKAGE_SLUG} --cov-report=term-missing tests

.PHONY: isort_check
isort_check:
	$(PYTHON) -m isort --check-only .

.PHONY: black_check
black_check:
	$(PYTHON) -m black . --check

.PHONY: mypy_check
mypy_check:
	$(PYTHON) -m mypy ${PACKAGE_SLUG}

.PHONY: dapperdata_check
dapperdata_check:
	$(PYTHON) -m dapperdata.cli pretty .

.PHONY: tomlsort_check
tomlsort_check:
	$(PYTHON_ENV) toml-sort $$(find . -not -path "./.venv/*" -name "*.toml") --check
#
# Dependencies
#

.PHONY: rebuild_dependencies
rebuild_dependencies:
	$(PYTHON) -m piptools compile --resolver=backtracking --output-file=requirements.txt pyproject.toml
	$(PYTHON) -m piptools compile --resolver=backtracking --output-file=requirements-dev.txt --extra=dev pyproject.toml

.PHONY: dependencies
dependencies: requirements.txt requirements-dev.txt

requirements.txt: $(PACKAGE_CHECK) pyproject.toml
	$(PYTHON) -m piptools compile --resolver=backtracking --upgrade --output-file=requirements.txt pyproject.toml

requirements-dev.txt: $(PACKAGE_CHECK) pyproject.toml
	$(PYTHON) -m piptools compile --resolver=backtracking --upgrade --output-file=requirements-dev.txt --extra=dev pyproject.toml

#
# Licenses
#
.PHONY: python-licenses
python-licenses:
	$(PYTHON) -m reuse annotate --year 2023 --copyright "Comcast Cable Communications Management, LLC" --recursive --template=python-header --copyright-style string --skip-unrecognised ./**/*.py

.PHONY: licences
licenses: python-licenses

#
# Packaging
#

.PHONY: build
build: $(PACKAGE_CHECK)
	$(PYTHON) -m build


.PHONY: docker-build
docker-build:
	docker build --build-arg="PYTHON_VERSION=${PYTHON_VERSION}" -t ${DOCKER_IMAGE_TAG} .

.PHONY: docker-run-local
docker-local: docker-build
	docker run --rm -i -v "${PWD}:${PWD}" -w "${PWD}" ${DOCKER_IMAGE_TAG} /opt/resource/out . < tests/resources/test-input.json

.PHONY: docker-push
docker-push: docker-build
	docker push ${DOCKER_IMAGE_TAG}
