# CHANGELOG

## 0.5.0 (2025-01-13)

- 💥 BREAKING CHANGE: former behavior is now the 'upload' subcommand
- ✨ new `project-field` subcommand to obtain godot project fields

## 0.4.0 (2025-01-13)

- ✨ Sending previews

## 0.3.0 (2025-01-03)

- ✨ Support for Gitea hostings
- ♻️ Simpler hosting definitionsa
- 🏗️ Drop Python<3.11 (tests use enterContext, could work but no guaranties)

## 0.2.1 (2024-12-23)

- 🐛 Support github https urls without .git

## 0.2.0 (2024-12-23)

- ✨ Autodetect git branch
- ✨ Autodetect repo hosting for Github repos
- ✨ Autodetect repo name for Github repos
- ✨ BitBucket suport for repo autodetection
- ♻️ Modularized to enable support for other hosting services than GitHub
- 📝 Documented how to use it in Github Actions

## 0.1.1 (2024-12-23)

- 🐛 fixed half renamed option

## 0.1.0 (2024-12-23)

- ✨ First public release
- 💥 Renamed api secrets env vars `ASSET_STORE_*` -> `GODOT_ASSET_LIB_*`
- ✨ Added typer based CLI interface
- ✨ Options for dry run and to force previews edit
- 💄 Show post data with syntax highlight
- ♻️ Extracted original code from godot-dice-roller project

