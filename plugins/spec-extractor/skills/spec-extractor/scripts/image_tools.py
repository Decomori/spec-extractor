#!/usr/bin/env python3
"""Read received image bytes and create lossless evidence regions. No OCR or AI calls."""
from __future__ import annotations
import argparse
from contextlib import contextmanager
import hashlib
from io import BytesIO
import json
from pathlib import Path
import sys
import warnings

MAX_BYTES = 100_000_000
MAX_PIXELS = 60_000_000

@contextmanager
def opened(path: Path):
    try:
        from PIL import Image, ImageOps
    except ImportError as exc:
        raise ValueError('Image inspection requires Pillow. Use a Python environment with Pillow; do not estimate pixel dimensions.') from exc
    with path.open('rb') as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError('Image exceeds 100 MB.')
    with warnings.catch_warnings():
        warnings.simplefilter('error', Image.DecompressionBombWarning)
        with Image.open(BytesIO(raw)) as im:
            if im.width * im.height > MAX_PIXELS:
                raise ValueError('Image exceeds 60 million pixels; provide separate source images.')
            if getattr(im, 'n_frames', 1) != 1:
                raise ValueError('Multi-frame image: export and inspect each required frame separately.')
            stored = im.size
            orientation = im.getexif().get(274, 1)
            im.load()  # Reject truncated input before reporting success.
            with ImageOps.exif_transpose(im) as upright:
                metadata = {
                    'file': path.name, 'kind': 'image', 'sha256': hashlib.sha256(raw).hexdigest(),
                    'format': im.format, 'stored_width_px': stored[0], 'stored_height_px': stored[1],
                    'exif_orientation': orientation,
                    'width_px': upright.width, 'height_px': upright.height,
                    'coordinate_space': 'exif_transposed_pixels',
                    'measurement': 'decoded_received_file',
                    'original_file_verified': False,
                    'note': 'Measured received bytes, not the screen preview. Original upload identity requires separate verification. No product dimensions or text were inferred.'
                }
                yield upright, metadata

def inspect(path: Path) -> dict:
    with opened(path) as (_, metadata):
        return metadata

def boxes(width: int, height: int, size: int, overlap: int) -> list[list[int]]:
    if not 64 <= size <= 4096 or not 0 <= overlap < size:
        raise ValueError('Tile size must be 64..4096; overlap must be 0..size-1.')
    def starts(length):
        if length <= size:
            return [0]
        result = list(range(0, length-size+1, size-overlap))
        if result[-1] != length-size:
            result.append(length-size)
        return result
    xs, ys = starts(width), starts(height)
    if len(xs) * len(ys) > 500:
        raise ValueError('More than 500 tiles; increase tile size or reduce overlap.')
    return [[x,y,min(x+size,width),min(y+size,height)] for y in ys for x in xs]

def regions(path: Path, out: Path, *, bbox=None, size=1600, overlap=160) -> dict:
    from PIL import Image
    with opened(path) as (im, metadata):
        if bbox is not None:
            if len(bbox) != 4 or any(type(v) is not int for v in bbox):
                raise ValueError('Box requires four integers: left top right bottom.')
            l,t,r,b = bbox
            if not (0 <= l < r <= im.width and 0 <= t < b <= im.height):
                raise ValueError('Box must be inside the EXIF-oriented image, with positive area.')
            areas = [bbox]
        else:
            areas = boxes(im.width, im.height, size, overlap)
        out.mkdir(parents=True, exist_ok=False)
        report = {'source': metadata, 'coverage': 'selected_region' if bbox else 'full_image',
                  'coordinate_space': 'exif_transposed_pixels', 'regions': []}
        for index, area in enumerate(areas, 1):
            filename = f'region-{index:04d}.png'
            with im.crop(area) as crop:
                # Copy pixels into a fresh image; do not export EXIF/GPS metadata.
                mode = 'RGBA' if 'A' in crop.getbands() or 'transparency' in crop.info else 'RGB'
                with crop.convert(mode) as converted:
                    with Image.new(mode, converted.size) as clean:
                        clean.paste(converted)
                        clean.save(out / filename)
            report['regions'].append({'file': filename, 'bbox_px': area,
                                      'width_px': area[2]-area[0], 'height_px': area[3]-area[1],
                                      'review_status': 'not_reviewed'})
        (out/'regions.json').write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
        return report

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['inspect','tiles','crop'])
    parser.add_argument('input', type=Path)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--box', nargs=4, type=int, metavar=('LEFT','TOP','RIGHT','BOTTOM'))
    parser.add_argument('--size', type=int, default=1600)
    parser.add_argument('--overlap', type=int, default=160)
    args=parser.parse_args()
    try:
        if args.action == 'inspect':
            result=inspect(args.input)
        else:
            if args.out is None or (args.action=='crop' and args.box is None):
                raise ValueError('Provide --out; crop also requires --box LEFT TOP RIGHT BOTTOM.')
            result=regions(args.input,args.out,bbox=args.box if args.action=='crop' else None,size=args.size,overlap=args.overlap)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 0
    except (OSError, ValueError, ImportError, Warning) as exc:
        print(f'ERROR: {exc}',file=sys.stderr)
        return 2

if __name__=='__main__':
    raise SystemExit(main())
