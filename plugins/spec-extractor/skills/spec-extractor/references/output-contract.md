# Extraction contract 1.0

Root: `schema_version: "1.0"`, `sources: []`, `products: []`.
Each source has unique `id`, `file` (portable display name or exact URL), `kind`
(pdf/image/text/html/spreadsheet/other), optionally verified `revision`, `date`, `sha256`.
Do not put personal absolute paths or access tokens in a result intended for sharing.

Each product has `product_id`, `variant_id` (`default` only if no variant distinction),
and a nonempty `fields` array. Each field has unique `key` inside its variant:

- `raw_value`: source spelling, or null when missing.
- `value`: normalized JSON value, or null if unresolved/not applicable.
- `unit`: source unit or null; never guess.
- `status`: sourced / derived / missing / illegible / conflict / not_applicable.
- `evidence`: array of `{source_id, locator, quote, page?}`. Page is 1-based.
- `notes`: optional explanation; required for illegible and not_applicable.
- `derivation`: mandatory formula/procedure only when status is derived.
- `candidates`: at least two `{raw_value,value,unit?,evidence}` objects for conflict.

Keep a dimensional string or object when axis meaning is not explicitly stated.
Do not invent length/width/height order. Preserve literal `±`, `>`, ranges and conditions.
Evidence quotes should be the shortest useful supporting fragment, not full documents.
`missing` means not found within the inspected scope, not proof that the fact doesn't exist.
The validator detects malformed results and broken reference IDs; it cannot prove that
quoted evidence exists or is interpreted correctly. Review the actual source to do that.
