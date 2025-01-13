import os
from pathlib import Path
from dotenv import load_dotenv
import typer
from typing import Annotated
from .utils import pretty
from .api import Api
from .config import Config
from .previews import previews_edit

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


if __name__ == '__main__':
    app()


