import subprocess

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

def repo_name() -> str:
	remote_name = remote_name()
	remote_url = subprocess.check_output(['git', 'remote', 'get-url', remote_name]).decode().strip()
	github = re.match('git@github.com:([^.]+).git', remote_url)
	if github:
		return github.group(1)
	raise Exception(
		f"Repository name detection is only supported for github right now. "
		f"Please explicit the repository name adding the `repo' key to the yaml configuration."
	)

def repo_host() -> str:
	remote_name = remote_name()
	remote_url = subprocess.check_output(['git', 'remote', 'get-url', remote_name]).decode().strip()
	github = re.match('git@github.com:([^.]+).git', remote_url)
	if github:
		return "Github"
	raise Exception(
		f"Repository hosting detection is only supported for github right now. "
		f"Please explicit the repository hosting service adding the `repo_hosting' key to the yaml configuration."
	)

