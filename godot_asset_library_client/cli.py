import os
from pathlib import Path
from dotenv import load_dotenv
import typer
from typing import Annotated
from .utils import pretty
from .api import Api
from .config import Config
from .previews import previews_edit
from .godot_project_reader import from_project, available_fields

app = typer.Typer()

@app.command()
def project_field(
    field: Annotated[str, typer.Argument()] = None,
):
    """Shows the value of the project parameter"""
    fields = available_fields()

    def print_available_fields():
        print("Available fields:")
        for field in fields:
            print(f"- {field}")

    if not field:
        print_available_fields()
        return

    if field not in fields:
        print(f"Field '{field}' not available")
        print_available_fields()
        return

    print(from_project(field))


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

    resource = f'asset/{config.asset_id}'

    old_previews = api.asset_previews(config.asset_id)
    previews = previews_edit(config.previews, old_previews, config)

    config.edit_id = api.pending_version_edit(
        asset_id = config.asset_id,
        version_string = config.project_version,
    )

    if config.edit_id:
        typer.secho(
            f"Detected pending edit {config.edit_id} for version {config.project_version}.\n"
            "Modifiying it instead of creating a new one.",
            fg=typer.colors.BRIGHT_YELLOW,
        )
        resource = f'asset/edit/{config.edit_id}'
        edited_previews = api.asset_edit_previews(config.edit_id)

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


