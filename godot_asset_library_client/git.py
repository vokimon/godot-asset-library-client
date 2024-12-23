import subprocess
import re

class GitHub:
	remote_patterns = [
		r'^git@github.com:([^.]+)\.git$',
		r'^https://github.com/([^.]+)\.git$',
	]
	@classmethod
	def raw_url(cls, config):
		return f'https://raw.githubusercontent.com/{config.repo}/refs/heads/{config.branch}'

	@classmethod
	def browse_url(cls, config):
		return f'https://github.com/{config.repo}'

	@classmethod
	def issues_url(cls, config):
		return f'{config.repo_url}/issues'


class BitBucket:
	remote_patterns = [
		r'^git@bitbucket.org:([^.]+)\.git$',
		r'^https://bitbucket.org/([^.]+)\.git$',
	]

	@classmethod
	def raw_url(cls, config):
		return f'https://bitbucket.org/{config.repo}/raw/{config.branch}'

	@classmethod
	def browse_url(cls, config):
		return f'https://bitbucket.org/{config.repo}'

	@classmethod
	def issues_url(cls, config):
		return f'{config.repo_url}/issues' # Could be also /jira but...


providers = {
	p.__name__: p
	for p in (
		GitHub,
		BitBucket,
	)
}

def provider(config):
	return providers.get(config.repo_hosting)

def raw_url_base(config):
	return provider(config).raw_url(config)

def browse_url_base(config):
	return provider(config).browse_url(config)

def issues_url(config):
	return provider(config).issues_url(config)

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
			"and host (github, bitbucket...) in the yaml config."
		)
	if not remotes:
		raise Exception(
			f"No remote repository detected. "
			f"Unable to retrieve repository information. "
			f"Please explicit repository name (user/repo) "
			"and host (github, bitbucket...) in the yaml config."
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

