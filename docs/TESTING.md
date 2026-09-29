# Verification / 검증

## Run locally

```bash
python3 tools/validate_package.py
python3 -m unittest discover -s tests -v
```

Python 3.10+ is required. The image repository additionally needs Pillow for its helper
tests. Unit tests use synthetic inputs, temporary directories, fake networking where
needed, and a fake OS home. They do not install anything into the real home, create a
GitHub repository, contact a live target, spend image-generation credits or change a site.

## What these tests establish

Package structure/JSON/Python parsing, the one-plugin/one-skill invariant, relative paths,
installer isolation and preservation of unrelated settings; utility behavior for this
specific repository. Check `VALIDATION_REPORT.md` for the actual run results when present.

## What they do NOT establish

No ChatGPT/Codex UI was launched by the unit tests. They do not prove live plugin loading,
correct model invocation, extraction accuracy from real scans, faithful AI photo editing,
rendered-page SEO behavior, safety of every external website, or public-directory approval.
Passing fixture tests is not end-to-end testing of a paid external tool or every OS.

## Manual acceptance before a production release

Install only this repository on a clean supported host. Test one normal task, one missing
capability, one unrelated project/brand, one incomplete source and one malicious instruction
embedded in source data. Verify no secrets/project data cross between users or projects.
Test both installation modes separately (never at the same time) and upgrade/uninstall.
Confirm current host requirements against docs/SOURCES.md. Record model/app/OS/version,
inputs, actual outputs, observations and failures without calling unrun cases passed.

## 0.2.0 regression checks
Install requirements.txt before the full suite. `tests/test_images.py` covers actual
pixel sizes, EXIF rotation, complete bottom/right tile coverage, invalid coordinates,
corrupt and multi-frame rejection, preserved existing output, stripped crop metadata,
unreviewed region labels, evidence bounds, and HTML script-breakout escaping.
The viewer is additionally checked in a browser against synthetic fixture exports.
No private customer source or model-output quality benchmark is bundled.

Verified for this release: 49 tests pass. A synthetic 1200 × 33548 image was measured
exactly and split into 24 regions, including the bottom edge. Browser checks passed
for unit display, source details, search, two-variant comparison, and malformed JSON
errors while preserving the previous data. The reported real Chat failure was not
reproduced because its original image and conversation were not supplied.
