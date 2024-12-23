import subprocess
import re

remote_patterns = [
	('GitHub', r'git@github.com:([^.]+)\.git'),
	('GitHub', r'https://github.com/([^.]+)\.git'),
]

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

def repo_name() -> str:
	remote_url = repo_remote_url()
	for hosting, pattern in remote_patterns:
		match = re.match(pattern, remote_url)
		if match:
			return match.group(1)
	raise Exception(
		f"Repository name detection not supported for remote {remote_url}. "
		f"Please add the key `repo` to the yaml config to make it explicit."
	)

def repo_host() -> str:
	remote_url = repo_remote_url()
	for hosting, pattern in remote_patterns:
		match = re.match(pattern, remote_url)
		if match:
			return hosting
	raise Exception(
		f"Repository hosting detection not supported for remote {remote_url}. "
		f"Please add the key `repo_hosting` to the yaml config to make it explicit."
	)

