import unittest
import subprocess
from pathlib import Path
from yamlns.testutils import ns
from . import git
from .testutils import sandbox_dir, working_dir

class GitProviders_Test(unittest.TestCase):
	maxDiff = None
	from yamlns.testutils import assertNsEqual

	def clone(self, url):
		self.sandbox = self.enterContext(sandbox_dir())
		output = subprocess.check_output(['git', 'clone', url, 'repo']).decode().strip()
		self.repo = self.enterContext(working_dir('repo'))

	def test_clone(self):
		original_path = Path().resolve()
		original_license = Path('LICENSE').read_text()

		self.clone('https://github.com/vokimon/godot-asset-library-client.git')

		# Path is different
		self.assertNotEqual(Path().resolve(), original_path)

		# LICENSE stil the same content
		cloned_license = Path("LICENSE").read_text()
		self.assertEqual(cloned_license, original_license)

	def config(self, **overrides):
		c = ns(**overrides)
		c.setdefault('repo', git.repo_name())
		c.setdefault('repo_hosting', git.repo_host())
		c.setdefault('branch', git.current_branch())
		c.setdefault('repo_url', git.browse_url_base(c))
		return c

	def assertUrlsEqual(self, c, expected):
		result = ns(
			browse = git.browse_url_base(c),
			issues = git.issues_url(c),
			raw = git.raw_url_base(c),
		)
		self.assertNsEqual(result, expected)

	def inferredParameters(self, remote, **overrides):
		self.clone(remote)
		c = self.config(**overrides)
		return ns(
			remote = git.repo_remote_url(),
			hosting = git.repo_host(),
			repo = git.repo_name(),
			branch = git.current_branch(),
			browse = git.browse_url_base(c),
			issues = git.issues_url(c),
			raw = git.raw_url_base(c),
		)


	def test_github_https(self):
		remote = 'https://github.com/vokimon/godot-asset-library-client.git'
		result = self.inferredParameters(remote)
		self.assertNsEqual(result, ns(
			remote = remote,
			hosting = "GitHub",
			repo = 'vokimon/godot-asset-library-client',
			branch = 'master',
			browse = 'https://github.com/vokimon/godot-asset-library-client',
			issues = 'https://github.com/vokimon/godot-asset-library-client/issues',
			raw = 'https://raw.githubusercontent.com/vokimon/godot-asset-library-client/refs/heads/master',
		))

	def test_github_https__override_repo(self):
		remote = 'https://github.com/vokimon/godot-asset-library-client.git'
		result = self.inferredParameters(remote,
			repo = "otherproject/otherrepo",
		)
		self.assertNsEqual(result, ns(
			remote = remote,
			hosting = "GitHub",
			# Inferred does not change
			repo = 'vokimon/godot-asset-library-client',
			branch = 'master',
			# Those 3 change
			browse = 'https://github.com/otherproject/otherrepo',
			issues = 'https://github.com/otherproject/otherrepo/issues',
			raw = 'https://raw.githubusercontent.com/otherproject/otherrepo/refs/heads/master',
		))

	def test_github_https__override_branch(self):
		remote = 'https://github.com/vokimon/godot-asset-library-client.git'
		result = self.inferredParameters(remote,
			branch="mycustombranch",
		)
		self.assertNsEqual(result, ns(
			remote = remote,
			hosting = "GitHub",
			repo = 'vokimon/godot-asset-library-client',
			# Inferred, does not change
			branch = 'master',
			browse = 'https://github.com/vokimon/godot-asset-library-client',
			issues = 'https://github.com/vokimon/godot-asset-library-client/issues',
			# this one changes
			raw = 'https://raw.githubusercontent.com/vokimon/godot-asset-library-client/refs/heads/mycustombranch',
		))

	def test_bitbucket_https(self):
		remote = 'https://bitbucket.org/guifibaix_coop/dummy_repo.git'
		result = self.inferredParameters(remote)
		self.assertNsEqual(result, ns(
			remote = remote,
			hosting = "BitBucket",
			repo = 'guifibaix_coop/dummy_repo',
			branch = 'main',
			browse = 'https://bitbucket.org/guifibaix_coop/dummy_repo',
			issues = 'https://bitbucket.org/guifibaix_coop/dummy_repo/issues',
			raw = 'https://bitbucket.org/guifibaix_coop/dummy_repo/raw/main',
		))

	def test_gitea_https(self):
		remote = 'https://gitea.com/vokimon/dummy_repo.git'
		result = self.inferredParameters(remote)
		self.assertNsEqual(result, ns(
			remote = remote,
			hosting = "Gitea",
			repo = 'vokimon/dummy_repo',
			branch = 'main',
			browse = 'https://gitea.com/vokimon/dummy_repo',
			issues = 'https://gitea.com/vokimon/dummy_repo/issues',
			raw = 'https://gitea.com/vokimon/dummy_repo/raw/main',
		))






