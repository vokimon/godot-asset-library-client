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
in the project to upload a Godot asset into the Godot asset library.

## Features

- Smart metadata gathering: do not duplicate metadata again
- Reuses existing pending edits of the same release in the library to enable corrections.
- Smart behaviour with existing previews (still not working)
- Shortcuts for previews hosted youtube or the repository (still not working)
- Easy integration in Github actions or any other CI/CD platform.

## Install

```bash
pip install godot-asset-library-client
```

## Usage

- Define `GODOT_ASSET_LIB_USER` and `GODOT_ASSET_LIB_PASSWORD` environment variables.
  You may use a .env file with them but consider security concerns.

- Write a yaml metadata file with content similar to this:

```yaml
# asset-metadata.yaml

asset_id: '6666666' # You will obtain this id after the first publication by hand
category: "1" # 2D Tools. See available values in https://godotengine.org/asset-library/api/configure
project_license: AGPLv3
previews:

# Shortcut for youtube previews
- youtube: AD8awHLpFxs

# Shortcut for media commited in the repository
- repoimage: /screenshots/screenshot1.png
  repothumb: /screenshots/screenshot1-thumb.jpg

# If not shortcutted the preview entry should look like this
- type: image
  link: https://raw.githubusercontent.com/vokimon/godot-dice-roller/refs/heads/main/screenshots/screenshot2.png
  thumbnail: https://raw.githubusercontent.com/vokimon/godot-dice-roller/refs/heads/main/screenshots/screenshot2-thumb.jpg

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
- Current branch
- Repository hosting (currently only for github)
- Repository name (currently only for github)

## Integration with Github Actions

Provided that you already have a working `asset-metadata.yaml` in your repository,
add the environment variables for your secrets in Github in
`Your Project / Settings / Secrets and Variables / Actions / Repository secrets`.


Add this file to your repo:

```yaml
# .github/workflows/publish.yml
name: Upload Plugin to Godot Asset Library

on:
  release:
    types: [published]
  workflow_dispatch:

jobs:
  publish:
    runs-on: ubuntu-latest
    name: Publish new version to asset lib
    steps:

    - name: Checkout
      uses: actions/checkout@v2

    - uses: actions/setup-python@v2
      with:
        python-version: 3

    - name: Godot Asset Lib
      shell: bash
      run: |
        echo "GODOT_ASSET_LIB_USER=${{ secrets.GODOT_ASSET_LIB_USER }}" >> .env
        echo "GODOT_ASSET_LIB_PASSWORD=${{ secrets.GODOT_ASSET_LIB_PASSWORD }}" >> .env
        pip install godot-asset-library-client
        godot-asset-library-client asset-metadata.yaml --do
```

You may want to remove the `--do` option until you are sure
you are not uploading garbage to the asset library.


## TODO

Sure you can help with those:

- BUG: Previews are generated as json but the api returns a warning and ignores them
- Solve the emoji problem by not removing them. The blacklist is quite limited and fragile.
- Support first upload of a project
- Auto-identify license available in repository
- Auto-identify repo name from git remote for non github hostings
- Auto-identify repo hosting for non github hostings

