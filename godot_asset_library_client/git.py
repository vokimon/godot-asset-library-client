import subprocess
import re

class StandardGitHost:
	"""
	Most hostings use this pattern based on the domain.
	If a hosting differs, just override the property method.
	"""

	def __init__(self, config=None):
		self.config = config

	@property
	def browse_url(self) -> str:
		return f'https://{self.domain}/{self.config.repo}'

	@property
	def issues_url(self) -> str:
		return f'{self.config.repo_url}/issues'

	@property
	def raw_url(self) -> str:
		return f'https://{self.domain}/{self.config.repo}/raw/{self.config.branch}'


class GitHub(StandardGitHost):
	domain = 'github.com'
	remote_patterns = [
		r'^git@github\.com:([^.]+)\.git$',
		r'^https://github\.com/([^.]+)\.git$',
		r'^https://github\.com/([^.]+)$',
	]

	@property
	def raw_url(self):
		return f'https://raw.githubusercontent.com/{self.config.repo}/refs/heads/{self.config.branch}'

class BitBucket(StandardGitHost):
	domain = 'bitbucket.org'
	remote_patterns = [
		r'^[^@]+@bitbucket\.org:([^.]+)\.git$',
		r'^https://bitbucket\.org/([^.]+)\.git$',
		r'^https://[^@]+@bitbucket.org/([^.]+)\.git$',
	]

class Gitea(StandardGitHost):
	domain = 'gitea.com'
	remote_patterns = [
		r'^git@gitea.com:([^.]+)\.git$',
		r'^https://gitea.com/([^.]+)\.git$',
	]


providers = {
	p.__name__: p
	for p in (
		GitHub,
		BitBucket,
		Gitea,
	)
}

def provider(config):
	return providers.get(config.repo_hosting)(config)

def raw_url_base(config):
	return provider(config).raw_url

def browse_url_base(config):
	return provider(config).browse_url

def issues_url(config):
	return provider(config).issues_url

def revision_hash() -> str:
    return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip()

def current_branch() -> str:
	branch = subprocess.check_output(['git', 'branch', '--show-current']).decode().strip()
	if branch not in ['master', 'main']:
		raise Exception(
			f"Current detected branch '{branch}' is neither 'master' nor 'main'. "
			f"Stopping to preventing accidentally publication from a feature branch. "
			f"If you still want to release from '{branch}', "
			f"make that explicit adding a 'branch' key in the yaml config."
		)
	return branch

def remote_name() -> str:
	remotes = subprocess.check_output(['git', 'remote']).decode().strip().split()
	if len(remotes) > 1:
		raise Exception(
			f"More than one remote found ({', '.join(remotes)}) "
			f"while detecting repository information. "
			f"Please explicit repository name (user/repo) "
			"and host (github, bitbucket, gitea...) in the yaml config."
		)
	if not remotes:
		raise Exception(
			f"No remote repository detected. "
			f"Unable to retrieve repository information. "
			f"Please explicit repository name (user/repo) "
			"and host (github, bitbucket, gitea...) in the yaml config."
		)
	return remotes[0]

def repo_remote_url() -> str:
	name = remote_name()
	return subprocess.check_output(['git', 'remote', 'get-url', name]).decode().strip()

def _match_remote_hosting():
	remote_url = repo_remote_url()
	for provider_name, provider in providers.items():
		for pattern in provider.remote_patterns:
			found = re.match(pattern, remote_url)
			if not found: continue
			repo_name = found.group(1)
			return provider_name, repo_name

	raise Exception(
		f"Repository name/provider detection not supported for remote {remote_url}. "
		f"Please add the keys `repo` and `repo_hosting` to the yaml config to make them explicit."
	)

def repo_name() -> str:
	hosting, repo = _match_remote_hosting()
	return repo

def repo_host() -> str:
	hosting, repo = _match_remote_hosting()
	return hosting

