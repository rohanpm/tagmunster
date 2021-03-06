#!/usr/bin/python3
from typing import List
import sys
import argparse
import os
import logging
import pprint
from subprocess import check_call, check_output, run

import requests

from .context import Context

LOG = logging.getLogger("tagmunster")


def cmd(args, env: dict = None, hide: bool = False):
    cmd_log = "+ %s" % " ".join(args)
    cmd_log = cmd_log.replace(os.environ["GITHUB_TOKEN"], "xxxxxxxxx")

    LOG.info("%s", cmd_log)

    if env != None:
        new_env = os.environ.copy()
        new_env.update(env)
        env = new_env

    check_call(args, env=env)


class NullCommand:
    def __init__(self, _):
        print("Error: must provide a command (try --help)", file=sys.stderr)
        sys.exit(44)


class BranchCommand:
    def __init__(self, ctx):
        self._ctx = ctx

    def run(self):
        os.chdir(self._ctx.workspace)

        self.git_setup()
        self.run_transformers()
        if not self.git_commit():
            return

        self.make_pr()

    def git_setup(self):
        # TODO: would it make sense to skip clone if it's already
        # cloned, e.g. if the actions/checkout was run before us?
        cmd(["git", "init", "-b", "main", "."])
        cmd(["git", "fetch", "--depth", "1", self._ctx.repo_url, self._ctx.src_ref])
        cmd(["git", "reset", "--hard", self._ctx.sha])

    def run_transformers(self):
        for transformer in self._ctx.transformers:
            cmd([transformer])

    def git_commit(self):
        cmd(["git", "add", "--all"])

        have_content = run(["git", "diff", "--staged", "--quiet"]).returncode == 1

        if not have_content:
            LOG.info("No content for commit!")
            return False

        cmd(
            # TODO: configurable message
            ["git", "commit", "--message", "Preparing next tag"],
            env=dict(
                # TODO: configurable
                GIT_AUTHOR_NAME="tagmunster",
                GIT_AUTHOR_EMAIL="tagmunster@users.noreply.github.com",
                GIT_COMMITTER_NAME="tagmunster",
                GIT_COMMITTER_EMAIL="tagmunster@users.noreply.github.com",
            ),
        )

        cmd(["git", "show", "HEAD"])

        cmd(
            [
                "git",
                "push",
                "-v",
                self._ctx.repo_url_writable,
                "+HEAD:refs/heads/%s" % self._ctx.dest,
            ]
        )

        return True

    def make_pr(self):
        s = requests.Session()
        create_response = s.post(
            url=self._ctx.pulls_url,
            headers=dict(
                Accept="application/vnd.github.v3+json",
                Authorization="token %s" % self._ctx.token,
            ),
            json=dict(
                head=self._ctx.dest,
                base=self._ctx.src_branch,
                maintainer_can_modify=True,
                title="Preparing next tag",
            ),
        )

        exists_response = s.get(
            url=self._ctx.pulls_url,
            headers=dict(
                Accept="application/vnd.github.v3+json",
                Authorization="token %s" % self._ctx.token,
            ),
            params=dict(
                head=self._ctx.dest,
                base=self._ctx.src_branch,
                state="open",
            ),
        )
        exists_response.raise_for_status()

        exists_data = exists_response.json()

        if exists_data:
            href = exists_data[0]["_links"]["html"]["href"]
            LOG.info("Created/updated PR: %s", href)
        else:
            # Probably failed
            LOG.warning(
                "Failed to create PR\n%s", pprint.pformat(create_response.json())
            )
            create_response.raise_for_status()
            raise RuntimeError("(PR doesn't exist despite successful response!)")


def main(args: List[str] = None):
    args = args or sys.argv[1:]
    parser = argparse.ArgumentParser(prog="tagmunster")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--dest", type=str, default="tagmunster/release")
    parser.set_defaults(command=NullCommand)

    subparsers = parser.add_subparsers(title="subcommands")

    branch = subparsers.add_parser("branch")
    branch.add_argument("--transformer", type=str, default="true")
    branch.set_defaults(command=BranchCommand)

    p = parser.parse_args(args)

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    if p.debug:
        LOG.setLevel(logging.DEBUG)

    p.command(Context(p)).run()


if __name__ == "__main__":
    main(sys.argv[1:])
