# Image review and pixel measurements

Distinguish **file pixels** from **printed product dimensions**. A 1200 × 30000 px
image does not establish any physical dimension of its pictured product.

## Capability gate
- Exact pixels require a tool reading the received file bytes. Do not infer dimensions
  from the chat preview, model image representation, filename, or apparent aspect ratio.
- Use `scripts/image_tools.py inspect SOURCE` (Python + Pillow). Record its measured
  dimensions, SHA-256, and coordinate space in the source entry. These measure the
  received file; do not call them the original upload dimensions unless identity is verified.
- If code/files are unavailable, state: "원본 파일의 픽셀 크기를 도구로 확인할 수 없음".
  Leave dimensions absent/unknown. Continue only the parts supported by visible evidence.
- The plugin does not grant code execution or access to attachments. Do not claim the
  script ran merely because it is installed. No automatic fallback to invented numbers.

## Read long images without shrinking away the text
1. Inspect pixels and EXIF orientation first. `width_px`/`height_px` and every region
   coordinate refer to the EXIF-oriented image; stored dimensions are reported separately.
2. Create readable regions covering the whole image:
   `python3 scripts/image_tools.py tiles SOURCE --out NEW_REGION_FOLDER`
   Default tiles are at most 1600 × 1600 px, overlap 160 px, with no resizing.
3. Open and actually inspect region images, including the final bottom/right regions.
   Generating regions is not evidence that they were read. Track reviewed region filenames;
   report unreviewed regions and restrict missing-value claims to the reviewed scope.
4. If a digit, unit, axis label, or option boundary is unclear, inspect a narrower crop:
   `python3 scripts/image_tools.py crop SOURCE --box LEFT TOP RIGHT BOTTOM --out NEW_FOLDER`
   Bounds are half-open `[left, top, right, bottom]`. No AI enhancement or invented pixels.
5. For product dimensions, preserve the printed string and match labels/arrows to the
   applicable product/variant. Keep axis order ambiguous when the source is ambiguous.
   Never convert screen pixels or DPI to physical product dimensions.
6. Recheck critical numbers against the region (dimensions, ratings, model IDs). Use
   `illegible`, null, and a reason when unresolved. OCR output is only a transcription
   candidate; it still needs visual review. Conflicting actual sources use `conflict`.

## Evidence
Keep `source_id`, `quote`, and `locator`. When a region was inspected, also record
`bbox_px: [left, top, right, bottom]` and `coordinate_space: "exif_transposed_pixels"`.
Coordinates must be from the tool or a checked mapping, never guessed from a resized
preview. Without trustworthy coordinates, use a descriptive locator and omit bbox.
Do not mark a model interpretation as programmatically verified: the image tool only
measures files and creates regions; it does not read or certify the printed numbers.

## Delivery
Report received-file dimensions only if measured, reviewed scope, unresolved fields,
and which tool checks actually ran. Export `viewer.html` with JSON/CSV so filtering,
comparison and evidence browsing do not require another model response. The viewer
shows supplied evidence; it is not an independent OCR engine or a hosted ChatGPT widget.
