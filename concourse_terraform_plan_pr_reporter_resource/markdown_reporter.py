import json
from copy import deepcopy
from logging import getLogger

from markdown_table_generator import generate_markdown, table_from_string_list

log = getLogger(__name__)

log = getLogger(__name__)


class MarkdownReporter:
    def __init__(self, terraform_plan):
        self.terraform_plan = terraform_plan

    def generate(self):
        if (
            self.terraform_plan.creations == 0
            and self.terraform_plan.deletions == 0
            and self.terraform_plan.modifications == 0
        ):
            return "No changes. Infrastructure is up-to-date."
        else:
            table_rows = [["Resource", "Change Type"]]
            change_descriptions = []

            for address, infra_change in self.terraform_plan.changes.items():
                if not "no-op" in infra_change.actions:
                    change_description = MarkdownReporter.generate_resource_description_section(address, infra_change)
                    table_rows.append([address, ",".join(infra_change.actions)])
                    change_descriptions.append(change_description)

            report = MarkdownReporter.generate_summary(self.terraform_plan)

            report += generate_markdown(table_from_string_list(table_rows))

            report += MarkdownReporter.generate_description_section(change_descriptions)

            return report

    def generate_summary(terraform_plan):
        return "Add: {}, Update: {}, Delete: {}\n\n".format(
            terraform_plan.creations, terraform_plan.modifications, terraform_plan.deletions
        )

    def generate_description_section(change_descriptions):
        return "\n\n" + "\n\n".join(change_descriptions)

    def generate_resource_description_section(address, infra_change):
        change_type = ""
        if len(infra_change.actions) == 1 and infra_change.actions[0] == "create":
            change_type = "+"
        elif len(infra_change.actions) == 1 and infra_change.actions[0] == "create":
            change_type = "-"
        else:
            change_type = "!"

        diff = "```diff\n" + change_type + " " + address + "\n```\n"
        diff += "<details><summary>View details</summary>\n\n```\n"

        attributes = (
            list(infra_change.before.keys())
            if infra_change.before
            else [] + list(infra_change.after.keys())
            if infra_change.after
            else []
        )

        for attribute in attributes:
            before_plain = infra_change.before.get(attribute) if infra_change.before else None
            after_plain = infra_change.after.get(attribute) if infra_change.after else None

            before_sanitized = infra_change.before_sanitized.get(attribute) if infra_change.before_sanitized else None
            after_sanitized = infra_change.after_sanitized.get(attribute) if infra_change.after_sanitized else None

            if before_plain != after_plain:
                diff += "\n{} = ".format(attribute)
                diff += json.dumps(before_sanitized) if before_sanitized != None else "null"
                diff += " -> " + "{}\n".format(json.dumps(after_sanitized) if after_sanitized != None else "null")

        diff += "\n```\n</details>"

        return diff
