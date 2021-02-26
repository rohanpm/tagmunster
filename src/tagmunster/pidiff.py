#!/usr/bin/python3
from typing import List
import sys
import argparse
import os
import logging
import pprint
from subprocess import check_call, check_output, run
import re

from .context import Context

LOG = logging.getLogger("pidiff-bump")


class PyInfo:
    def __init__(self):
        if not os.path.exists("setup.py"):
            LOG.error("Repository must have a top-level 'setup.py' to use pidiff-bump")
            sys.exit(37)

        python = sys.executable or "python"
        self.egg_name = check_output([python, "setup.py", "--name"], text=True).strip()
        self.egg_old_version = check_output(
            [python, "setup.py", "--version"], text=True
        ).strip()

        pidiff_cmd = ["pidiff", "--gen-version", self.egg_name, "."]
        LOG.info("+ %s", " ".join(pidiff_cmd))
        self.egg_new_version = check_output(pidiff_cmd, text=True).strip()


class BumpCommand:
    # TODO: add more, make configurable, etc.
    BUMP_FILES = [
        "setup.py",
        "docs/conf.py",
    ]

    def __init__(self, ctx):
        self._ctx = ctx

    def run(self):
        pyinfo = PyInfo()
        self.bump_versions(pyinfo)

    def bump_versions(self, pyinfo):
        for file in self.BUMP_FILES:
            if os.path.exists(file):
                check_call(
                    [
                        "sed",
                        "-E",
                        "-e",
                        "s|%s|%s|g"
                        % (re.escape(pyinfo.egg_old_version), pyinfo.egg_new_version),
                        "-i",
                        file,
                    ]
                )
                LOG.info("Bumped version in %s", file)


def main(args: List[str] = None):
    args = args or sys.argv[1:]
    parser = argparse.ArgumentParser(prog="pidiff-bump")
    parser.add_argument("--debug", action="store_true")
    p = parser.parse_args(args)

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    if p.debug:
        LOG.setLevel(logging.DEBUG)

    BumpCommand(Context(p)).run()


if __name__ == "__main__":
    main(sys.argv[1:])
