import requests
from pathlib import Path
import os
from dotenv import load_dotenv
import yaml
from dataclasses import dataclass, field
from typing import Annotated
import typer
from . import git
from .godot_project_reader import project_field

app = typer.Typer()

@app.command()
def upload(
    yaml_metadata: Annotated[Path, typer.Argument(
        exists=True,
        readable=True,
    )],
    do: Annotated[bool, typer.Option(
        help="Do the actual upload",
    )] = False,
    send_previews: Annotated[bool, typer.Option(
        help="Send previews (this will be disabled by default until it works)",
    )] = False,
):
    """Uploads the project to Godot Asset Library"""

    # Load secrets from environment or .env file
    load_dotenv('.env')
    username = os.environ.get('GODOT_ASSET_LIB_USER')
    password = os.environ.get('GODOT_ASSET_LIB_PASSWORD')

    config = Config.from_file(yaml_metadata)

    api = Api()
    api.login(username, password)

    edit_id = api.pending_version_edit(
        asset_id = config.asset_id,
        version_string = config.project_version,
    )

    config.edit_id = edit_id
    if edit_id:
        typer.secho(
            f"Detected pending edit {config.edit_id} for version {config.project_version}.\n"
            "Modifiying it instead of creating a new one.",
            fg=typer.colors.BRIGHT_YELLOW,
        )

    resource = (
        f'asset/edit/{config.edit_id}'
        if config.edit_id else
        f'asset/{config.asset_id}'
    )

    old_data = api.get(f'asset/{config.asset_id}')
    old_previews = old_data.get('previews', [])
    previews = previews_edit(config.previews, old_previews, config)

    json = {
        "title": config.project_name,
        "description": config.description,
        "category_id": config.category,
        "godot_version": config.godot_version,
        "version_string": config.project_version,
        "cost": config.project_license,
        "download_provider": config.repo_hosting,
        "download_commit": config.git_hash,
        "download_hash": "", # deprecated
        "browse_url": config.repo_url,
        "issues_url": config.issues_url,
        "icon_url": f"{config.repo_raw}/icon.svg",
        "previews": previews,
    }

    # TODO: previews not working yet
    if not send_previews:
        json['previews'] = []

    print(f"POST DATA to {api.base}{resource}:\n{pretty(json)}")

    if not do:
        typer.secho("NOTHING DONE, DRY RUN", fg=typer.colors.BRIGHT_RED)
        print("Check the output and use --do option to actually upload")
        return

    result = api.post(resource, json=json)
    print("RESULT:", 
        pretty(result))
    print(f"Check at {api.base}/{result['url']}")


class Api:
    """Access to the Godot Asset Library API"""

    def __init__(self, base=None):
        self.base = base or f"https://godotengine.org/asset-library/api/"

    def login(self, username, password):
        r = self.post('/login', json=dict(
            username=username,
            password=password,
        ))
        self.token = r['token']

    def _process_response(self, response):
        #print(response.text)
        response.raise_for_status()
        try:
            return response.json()
        except:
            print(response.text)
            raise

    def post(self, url, json={}, *args, **kwds):
        if hasattr(self, 'token'):
            json = dict(json, token=self.token)

        response = requests.post(
            self.base+url,
            json=json,
            headers = {'Content-Type': 'application/json; charset=utf-8'},
            *args, **kwds)
        return self._process_response(response)

    def get(self, url, *args, **kwds):
        response = requests.get(
            self.base+url,
            *args, **kwds)
        return self._process_response(response)

    def pending_version_edit(self, asset_id, version_string):
        """
        Returns the last pending edit for the current version or None.
        """
        result = self.get('asset/edit', params=dict(
            asset=asset_id,
            status='new',
            version_string=version_string,
        ))

        edit_ids = [
            p['edit_id']
            for p in result.get('result')
            if p['version_string'] == version_string
        ]
        if edit_ids:
            return max(edit_ids)

def pretty(data):
    from pygments import highlight
    from pygments.lexers import YamlLexer
    from pygments.formatters import TerminalFormatter

    code = yaml.dump(data)
    return highlight(code, YamlLexer(), TerminalFormatter())

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

def remove_emojis(description: str) -> str:
    for emoji in "✨🐛🏗🧹🔧📝♻️💄":
        description = description.replace(emoji, '')
    return description

def remove_md_image_lines(description: str) -> str:
    return '\n'.join((
        line for line in description.splitlines()
        if not line.startswith("![")
    ))

def previews_edit(previews, old_previews, config):
    previews = [
        enhance_preview(p, config)
        for p in previews
    ]
    previews = [
        preview_action(p, old_previews)
        for p in previews
    ] 
    previews += to_remove_previews(previews, old_previews)
    return previews

def enhance_preview(preview, context):
    """
    Enables certain shortcuts for specifying previews.

    >>> class context:
    ...     repo_raw = "https://reporaw.com/path"
    ...
    >>> enhance_preview({'youtube': 'AD8awHLpFxs'}, context)
    {'type': 'video', 'link': 'https://www.youtube.com/watch?v=AD8awHLpFxs', 'thumbnail': 'https://img.youtube.com/vi/AD8awHLpFxs/maxresdefault.jpg'}
    >>> enhance_preview({'repoimage': 'images/myimage.png'}, context)
    {'type': 'image', 'link': 'https://reporaw.com/path/images/myimage.png'}
    >>> enhance_preview({'repothumb': 'thumbs/myimage.jpg'}, context)
    {'thumbnail': 'https://reporaw.com/path/thumbs/myimage.jpg'}
    """
    if 'youtube' in preview:
        youtube_id = preview.pop('youtube')
        preview.update(
            type = "video",
            link = f"https://www.youtube.com/watch?v={youtube_id}",
            thumbnail = f"https://img.youtube.com/vi/{youtube_id}/maxresdefault.jpg",
        )
    if 'repoimage' in preview:
        repoimage = preview.pop('repoimage')
        preview.update(
            type = 'image',
            link = f'{context.repo_raw}/{repoimage}',
        )
    if 'repothumb' in preview:
        repothumb = preview.pop('repothumb')
        preview.update(
            thumbnail = f'{context.repo_raw}/{repothumb}',
        )
    return preview

def preview_action(preview, old_previews):
    """
    Turns a preview in metadata into an action to perform
    (insert, update) with existing previews in the library
    based on matching link field.
    """
    if 'operation' in preview:
        return preview # alredy an op

    for old in old_previews:
        if old['link'] != preview['link']:
            continue
        return dict(
            preview,
            edit_preview_id=old['preview_id'],
            operation='update',
            enabled=True,
        )

    return dict(
        preview,
        operation='insert',
        enabled=True,
    )

def to_remove_previews(previews, old_previews):
    """
    Generates delete edition action to those existing
    previews not defined in the new metadata.
    """
    return [
        dict(
            edit_preview_id=old['preview_id'],
            operation='delete',
            enabled=True,
        )
        for old in old_previews
        if all(
            old['link']!=preview['link']
            for preview in previews
        )
    ]


if __name__ == '__main__':
    app()


