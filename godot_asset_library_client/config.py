from pathlib import Path
from dataclasses import dataclass, field
from .godot_project_reader import project_field
from . import git
import yaml

def remove_emojis(description: str) -> str:
    for emoji in "✨🐛🏗🧹🔧📝♻️💄":
        description = description.replace(emoji, '')
    return description

def remove_md_image_lines(description: str) -> str:
    return '\n'.join((
        line for line in description.splitlines()
        if not line.startswith("![")
    ))

@dataclass
class Config:
    asset_id: str
    category: int # = "1" # 2D Tools
    project_license: str
    previews: list[dict] = field(default_factory=list)
    description_files: list[str] = field(default_factory=list)

    repo: str = field(default_factory=git.repo_name)
    branch: str = field(default_factory=git.current_branch)
    git_hash: str = field(default_factory=git.revision_hash)
    repo_hosting: str = field(default_factory=git.repo_host)

    project_name: str = project_field('project_name')
    project_version: str = project_field('project_version')
    config_description: str = project_field('description')
    godot_version: str = project_field('godot_version')
    icon: str = project_field('icon')

    @property
    def repo_url(self):
        return git.browse_url_base(self)

    @property
    def repo_raw(self):
        return git.raw_url_base(self)

    @property
    def issues_url(self):
        return git.issues_url(self)

    @property
    def description(self):
        # TODO: Put some order here
        description = '\n'.join((
            Path(f).read_text() for f in self.description_files
        ))
        description = remove_md_image_lines(description) # markdown is not redered and they look awful
        description = remove_emojis(description)
        if not description:
            description = self.config_description
        return description

    @classmethod
    def from_file(cls, filename):
        config_yaml = yaml.safe_load(Path(filename).read_text())
        return cls(**config_yaml)


