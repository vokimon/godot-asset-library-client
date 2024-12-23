# godot-asset-library-client

[![CI](https://github.com/vokimon/godot-asset-library-client/actions/workflows/main.yml/badge.svg)](https://github.com/vokimon/godot-asset-library-client/actions/workflows/main.yml)
[![Coverage](https://img.shields.io/coveralls/vokimon/godot-asset-library-client/master.svg?style=flat-square&label=Coverage)](https://coveralls.io/r/vokimon/godot-asset-library-client)
[![PyPi](https://img.shields.io/pypi/v/godot-asset-library-client.svg?style=flat-square&label=PyPI)](https://pypi.org/project/godot-asset-library-client/)
[![license: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![downloads](https://img.shields.io/pypi/dm/godot-asset-library-client.svg?style=flat-square&label=PyPI%20Downloads)](https://pypi.org/project/godot-asset-library-client/)
<!--
[![image](https://img.shields.io/pypi/pyversions/godot-asset-library-client.svg?style=flat-square&label=Python%20Versions)](https://pypi.org/project/godot-asset-library-client/)
[![image](https://img.shields.io/pypi/implementation/godot-asset-library-client.svg?style=flat-square&label=Python%20Implementations)](https://pypi.org/project/godot-asset-library-client/)
-->

Interact with the Godot Asset Library

This script retrieves all the information already available
in the project to upload an Godot asset into the Godot asset library.

## Features

- Smart metadata gathering: avoid duplicating information already there
- Smart behaviour with existing pending edits
- Smart behaviour with existing previews (still not working)
- Shortcuts for previews hosted youtube or the repository (still not working)

## Install

```bash
pip install godot-asset-library-client
```

## Usage

- Define `ASSET_STORE_USER` and `ASSET_STORE_PASSWORD` environment variables.
  You may use a .env file with them but consider security concerns.

- Write a yaml metadata file with content like this:

```yaml
# asset-metadata.yaml

asset_id: '6666666' # You will obtain this id after the first publish by hand
repo_hosting: GitHub
repo: vokimon/godot-dice-roller
branch: main
category: "1" # 2D Tools
project_license: AGPLv3
previews:

# Shortcut for youtube previews
- youtube: AD8awHLpFxs

# Shortcut for media commited in the repository
- repoimage: /screenshots/example-landscape.png
  repothumb: /screenshots/example-landscape-thumb.jpg

# If not shortcutted the preview entry should look like this
- type: image
  link: https://raw.githubusercontent.com/vokimon/godot-dice-roller/refs/heads/main/screenshots/example-portrait.png
  thumbnail: https://raw.githubusercontent.com/vokimon/godot-dice-roller/refs/heads/main/screenshots/example-portrait-thumb.jpg

# These will be concatenated and processed as description
description_files:
- README.md
- CHANGES.md
```

Then, from the root of your project (where `project.godot` resides):

```bash
godot-asset-library-client asset-metadata.yaml
```

Check that the metadata is correct, and then add the option `--do`:

```bash
godot-asset-library-client asset-metadata.yaml --do
```

### Smart metadata guessing

If not explicitly provided,
it takes most metadata from existing files in your repository
so you don't have to duplicate that.

From `project.godot`:

- Project name
- Project version
- Project description
- Project icon
- Godot version

From local git:

- Commit hash

## TODO

- BUG: Previews are generated as json but the api returns a warning and ignores them
- Solve the emoji problem by not removing them
- Solution to the first upload
- Auto-identify license available in repository
- Auto-identify branch from current branch
- Auto-identify repo name from git remote


