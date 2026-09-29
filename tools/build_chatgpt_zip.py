#!/usr/bin/env python3
"""Build a plugin-root ZIP, never a repository-root ZIP. Does not install or publish."""
from pathlib import Path
import argparse
import json
import zipfile
from publish import public_files
ROOT=Path(__file__).resolve().parents[1]

def build(out: Path):
    allowed=set(public_files(ROOT))
    plugin=Path('plugins/spec-extractor')
    files=[p for p in sorted(allowed) if p.is_relative_to(plugin)]
    manifest=json.loads((ROOT/plugin/'.codex-plugin/plugin.json').read_text())
    if manifest['version'] != (ROOT/'VERSION').read_text().strip():
        raise ValueError('Version mismatch')
    out.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(out,'x',zipfile.ZIP_DEFLATED) as archive:
        for p in files:archive.write(ROOT/p,p.relative_to(plugin))
        for name in ('LICENSE','PRIVACY.md'):archive.write(ROOT/name,name)
    return out

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('out',type=Path)
    print(build(parser.parse_args().out))
