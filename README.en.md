# Spec Extractor

Independent agent skill and single-skill plugin, version 0.1.1. No dependency on any
sibling plugin, company data, fixed domain, saved account context or personal paths.
[한국어](README.md)

## Install
Ask a supported local agent to read this repository's README and `docs/INSTALL.md`,
review the scripts, and install **one** of the following modes. Do not install both.

```bash
python3 tools/manage.py install --mode plugin
# OR, for a local skills-capable host:
python3 tools/manage.py install --mode skill
```

Plugin mode registers files in the personal marketplace; it does not click the app's
Install/Enable button. Restart the desktop app, select the plugin in Plugins, install or
enable it, and start a new chat. Skill mode copies only the skill to `~/.agents/skills/`.
The required plugin manifest lives at `plugins/spec-extractor/.codex-plugin/plugin.json`.

Required capabilities: Host document/text/image reading; optional Python 3.10+ for validation/export.

This is an agent workflow with deterministic helpers, not a bundled image/LLM service.
Python 3.10+ is required for helpers. Product Visual's helpers additionally require Pillow.
Use `docs/TESTING.md` for actual automated coverage and untested host/runtime boundaries.

## Share
Publish this repository separately from unrelated skills. `tools/publish.py --plan`
lists exactly the files to upload without network access. Explicit `--confirm` is required
to create a repository. It defaults to private, uses your own `gh` authentication, and
never modifies an existing remote repository. See `docs/SHARING.md`.
A GitHub repository is not automatic publication in the universal ChatGPT directory.
Web/mobile distribution and directory review remain separate.

## Use, update, remove
Keep client assets, project preferences and credentials outside this repository.
`tools/manage.py install --mode plugin --replace` updates only this managed plugin with a
backup. `tools/manage.py uninstall --mode plugin --confirm` removes only this registration
and installed directory. Use `--mode skill` for the standalone copy instead.

No background hooks, telemetry, shared API keys or automatic production writes are bundled.
See SECURITY.md and PRIVACY.md for processing boundaries. MIT licensed.

## Image evidence and offline viewer (0.2.0)
`image_tools.py` measures received-file pixels, reports EXIF-oriented and stored sizes,
and creates overlapping lossless regions with coordinates. It requires Python 3.10+
and Pillow (`pip install -r requirements.txt`). JSON helpers still use only the standard library.
The host must expose file access and code execution; installation does not grant either.
No OCR or source-truth guarantee is provided. Text interpretation still needs model/human review.
Exports include an offline viewer.html for search, option comparison and evidence browsing.
Build the personal ChatGPT ZIP with `python3 tools/build_chatgpt_zip.py NEW_ZIP_PATH`;
the manifest and skills must be at the ZIP root. Repository archives are not upload bundles.
