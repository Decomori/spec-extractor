# Changelog

## 0.1.1 — 2026-09-29

- Validate finite JSON values throughout the entire document, including conflict candidates, nested values and optional metadata.
- Reject overflow before creating an export folder, keeping validate and export consistent.
- Add API and CLI regression tests plus a valid nested-value export test.

## 0.1.0 — 2026-09-29

- Initial independent Spec Extractor skill and single-skill plugin.
- Relative-path references, project-local optional configuration, Korean/English guide.
- Explicit capability checks; no proprietary/company defaults, credentials or hooks.
- Local helper scripts and automated tests; safe local installer and create-only GitHub publisher.
- Packaging uses .codex-plugin/plugin.json with a one-entry .agents/plugins/marketplace.json.
- Host UI installation, model-quality evaluation and public-directory approval are not certified.
