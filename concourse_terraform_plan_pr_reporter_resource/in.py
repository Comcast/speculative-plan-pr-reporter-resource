#!/usr/bin/env python

import base64
import json
import os
import sys
from logging import getLogger

log = getLogger(__name__)


def _in(instream, dest="."):
    payload = json.load(instream)

    log.info(payload)

    decoded_plan_string = base64.b64decode(payload["version"]["ref"].encode("ascii")).decode("ascii")

    # Write the decoded plan to a markdown file.
    with open(os.path.join(dest, "state_changes.md"), "w") as state_changes_file:
        state_changes_file.write(decoded_plan_string)
        print('{"version": {"ref": "1.0.0"}}', file=sys.stdout)


if __name__ == "__main__":
    _in(sys.stdin, sys.argv[1])
