ARG PYTHON_VERSION=3.11.1

FROM python:${PYTHON_VERSION}-slim

COPY requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

COPY concourse_terraform_plan_pr_reporter_resource /opt/resource