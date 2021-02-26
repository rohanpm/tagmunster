import os


class Context:
    def __init__(self, parsed, env=None):
        self._parsed = parsed
        self._env = env or os.environ.copy()

    @property
    def dest(self):
        return self._parsed.dest

    @property
    def transformer(self):
        return self._parsed.transformer

    @property
    def repo_url(self):
        return os.path.join(
            self._env["GITHUB_SERVER_URL"], self._env["GITHUB_REPOSITORY"]
        )

    @property
    def pulls_url(self):
        return os.path.join(
            self.api_url, "repos", self._env["GITHUB_REPOSITORY"], "pulls"
        )

    @property
    def repo_url_writable(self):
        server = self._env["GITHUB_SERVER_URL"]
        server = server.replace("//", "//tagmunster:%s@" % self.token, 1)
        return os.path.join(server, self._env["GITHUB_REPOSITORY"])

    @property
    def token(self):
        return self._env["GITHUB_TOKEN"]

    @property
    def src_ref(self):
        return self._env["GITHUB_REF"]

    @property
    def src_branch(self):
        ref = self.src_ref
        if not ref.startswith("refs/heads/"):
            raise ValueError("Triggered from non-branch ref %s" % ref)
        return ref[len("refs/heads/") :]

    @property
    def sha(self):
        return self._env["GITHUB_SHA"]

    @property
    def workspace(self):
        out = self._env["GITHUB_WORKSPACE"]
        os.makedirs(out, exist_ok=True)
        return out

    @property
    def api_url(self):
        return self._env["GITHUB_API_URL"]

    @property
    def transformers(self):
        cmds = self._parsed.transformer.split(",")
        cmds = [cmd.strip() for cmd in cmds]
        cmds = [os.path.expandvars(cmd) for cmd in cmds]
        return cmds
