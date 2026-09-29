#!/usr/bin/env python3
"""Validate source-linked specifications and export reviewable JSON/CSV/Markdown.
This utility validates structure; the host agent reads documents and verifies evidence.
"""
from __future__ import annotations
import argparse
import csv
from html import escape
import json
import math
from pathlib import Path
import sys
from typing import Any

STATUSES = {'sourced', 'derived', 'missing', 'illegible', 'conflict', 'not_applicable'}


def validate(data: Any) -> list[str]:
    errors: list[str] = []
    def check(ok: bool, message: str) -> None:
        if not ok:
            errors.append(message)
    if not isinstance(data, dict):
        return ['Root must be an object.']
    check(data.get('schema_version') == '1.0', 'schema_version must be 1.0.')
    sources = data.get('sources')
    products = data.get('products')
    if not isinstance(sources, list) or not isinstance(products, list) or not products:
        return errors + ['sources must be a list; products must be a nonempty list.']
    known: set[str] = set()
    for index, source in enumerate(sources):
        label = f'sources[{index}]'
        if not isinstance(source, dict):
            errors.append(label + ': must be an object.')
            continue
        sid = source.get('id')
        check(isinstance(sid, str) and bool(sid.strip()), label + ': nonempty id required.')
        if isinstance(sid, str):
            check(sid not in known, label + ': duplicate source id.')
            known.add(sid)
        check(isinstance(source.get('file'), str) and bool(source.get('file', '').strip()), label + ': file/URL label required.')
        check(source.get('kind') in {'pdf', 'image', 'text', 'html', 'spreadsheet', 'other'}, label + ': invalid kind.')
    def evidence(items: Any, label: str, required: bool = False) -> None:
        if not isinstance(items, list):
            errors.append(label + ': evidence must be a list.')
            return
        check(not required or len(items) > 0, label + ': source evidence required.')
        for j, item in enumerate(items):
            where = f'{label}.evidence[{j}]'
            if not isinstance(item, dict):
                errors.append(where + ': must be an object.')
                continue
            check(isinstance(item.get('source_id'), str) and item.get('source_id') in known,
                  where + ': unknown source_id.')
            check(isinstance(item.get('locator'), str) and bool(item.get('locator', '').strip()), where + ': locator required (page, row, line, or image region).')
            check(isinstance(item.get('quote'), str) and bool(item.get('quote', '').strip()), where + ': short verbatim evidence required.')
            if 'page' in item:
                check(type(item['page']) is int and item['page'] >= 1, where + ': page must be a positive one-based integer.')
    product_keys: set[tuple[str, str]] = set()
    for pi, product in enumerate(products):
        label = f'products[{pi}]'
        if not isinstance(product, dict):
            errors.append(label + ': must be an object.')
            continue
        pid, variant = product.get('product_id'), product.get('variant_id')
        check(isinstance(pid, str) and bool(pid.strip()), label + ': product_id required.')
        check(isinstance(variant, str) and bool(variant.strip()), label + ': variant_id required; use default if not applicable.')
        if isinstance(pid, str) and isinstance(variant, str):
            key = (pid, variant)
            check(key not in product_keys, label + ': duplicate product/variant identity.')
            product_keys.add(key)
        fields = product.get('fields')
        if not isinstance(fields, list) or not fields:
            errors.append(label + ': fields must be nonempty.')
            continue
        seen: set[str] = set()
        for fi, field in enumerate(fields):
            where = f'{label}.fields[{fi}]'
            if not isinstance(field, dict):
                errors.append(where + ': must be an object.')
                continue
            name = field.get('key')
            check(isinstance(name, str) and bool(name.strip()), where + ': key required.')
            if isinstance(name, str):
                check(name not in seen, where + ': duplicate field key in variant.')
                seen.add(name)
            status = field.get('status')
            check(isinstance(status, str) and status in STATUSES, where + ': invalid status.')
            if not isinstance(status, str):
                status = None
            for required in ['raw_value', 'value', 'unit', 'evidence']:
                check(required in field, where + ': missing ' + required)
            value, raw = field.get('value'), field.get('raw_value')
            check(field.get('unit') is None or isinstance(field.get('unit'), str), where + ': unit must be string or null.')
            check(raw is None or isinstance(raw, str), where + ': raw_value must be source text or null.')
            if isinstance(value, float):
                check(math.isfinite(value), where + ': non-finite numbers are forbidden.')
            evidence(field.get('evidence'), where, status in {'sourced', 'derived'})
            if status in {'sourced', 'derived'}:
                check(value is not None, where + ': sourced/derived value cannot be null.')
                check(isinstance(raw, str) and bool(raw.strip()), where + ': source spelling must be preserved.')
            if status in {'missing', 'illegible', 'conflict', 'not_applicable'}:
                check(value is None, where + ': unresolved value must be null, not guessed.')
            if status == 'missing':
                check(raw is None, where + ': missing raw_value must be null.')
            if status == 'derived':
                check(isinstance(field.get('derivation'), str) and bool(field.get('derivation', '').strip()), where + ': derivation/formula required.')
            if status in {'illegible', 'not_applicable'}:
                check(isinstance(field.get('notes'), str) and bool(field.get('notes', '').strip()), where + ': explanation required.')
            if status == 'conflict':
                candidates = field.get('candidates')
                if not isinstance(candidates, list) or len(candidates) < 2:
                    errors.append(where + ': conflict requires at least two candidates.')
                else:
                    for ci, candidate in enumerate(candidates):
                        cwhere = f'{where}.candidates[{ci}]'
                        if not isinstance(candidate, dict):
                            errors.append(cwhere + ': must be an object.')
                            continue
                        check(candidate.get('value') is not None, cwhere + ': candidate value required.')
                        check(isinstance(candidate.get('raw_value'), str) and bool(candidate.get('raw_value', '').strip()), cwhere + ': raw_value required.')
                        evidence(candidate.get('evidence'), cwhere, True)
    return errors


def text(value: Any) -> str:
    if value is None:
        return ''
    if isinstance(value, (dict, list, bool)):
        return json.dumps(value, ensure_ascii=False, allow_nan=False)
    return str(value)


def csv_safe(value: Any) -> str:
    result = text(value)
    # Prefix a literal apostrophe; quoting alone does not prevent spreadsheet formulas.
    if result.lstrip().startswith(('=', '+', '-', '@')) or result.startswith(('\t', '\r', '\n')):
        return "'" + result
    return result


def flatten(data: dict) -> list[dict]:
    rows: list[dict] = []
    for product in data['products']:
        for field in product['fields']:
            rows.append({'product_id': product['product_id'], 'variant_id': product['variant_id'],
                         'field': field['key'], 'status': field['status'], 'raw_value': field['raw_value'],
                         'value': field['value'], 'unit': field['unit'], 'evidence': field['evidence'],
                         'candidates': field.get('candidates', []), 'derivation': field.get('derivation', ''),
                         'notes': field.get('notes', '')})
    return rows


def export(data: dict, out: Path) -> None:
    errors = validate(data)
    if errors:
        raise ValueError('\n'.join(errors))
    # A new folder prevents accidental replacement of earlier evidence/results.
    out.mkdir(parents=True, exist_ok=False)
    (out / 'specifications.json').write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n', 'utf-8')
    rows = flatten(data)
    with (out / 'specifications.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        for row in rows:
            writer.writerow({key: csv_safe(value) for key, value in row.items()})
    def md(value: Any) -> str:
        return escape(text(value), quote=False).replace('\\', '\\\\').replace('|', '\\|').replace('\r', '').replace('\n', '<br>')
    lines = ['# Specification review', '', '**Structure validated; source truth still requires human/agent review.**', '',
             '| Product / variant | Field | Status | Raw | Value | Unit | Evidence |',
             '|---|---|---|---|---|---|---|']
    for row in rows:
        values = [f"{row['product_id']} / {row['variant_id']}", row['field'], row['status'], row['raw_value'], row['value'], row['unit'], row['evidence']]
        lines.append('| ' + ' | '.join(md(v) for v in values) + ' |')
    unresolved = [r for r in rows if r['status'] in {'missing', 'illegible', 'conflict'}]
    lines += ['', '## Needs review', '']
    for row in unresolved:
        lines.append(f"- {md(row['product_id'])} / {md(row['variant_id'])} / {md(row['field'])}: {md(row['status'])}; {md(row['notes'])}")
        if row['candidates']:
            lines.append('  Candidates: ' + md(row['candidates']))
    if not unresolved:
        lines.append('No unresolved fields reported by the input. This does not independently verify source accuracy.')
    lines += ['', '## Source inventory', '']
    for source in data['sources']:
        lines.append(f"- {md(source['id'])}: {md(source['file'])} ({md(source['kind'])})")
    (out / 'review.md').write_text('\n'.join(lines) + '\n', 'utf-8')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['validate', 'export'])
    parser.add_argument('input', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    try:
        if args.input.stat().st_size > 20_000_000:
            raise ValueError('Input exceeds 20 MB; split the extraction by document or product.')
        data = json.loads(args.input.read_text('utf-8-sig'), parse_constant=lambda x: (_ for _ in ()).throw(ValueError('Non-finite JSON number: ' + x)))
        errors = validate(data)
        if errors:
            print('\n'.join(errors), file=sys.stderr)
            return 1
        if args.action == 'export':
            if args.out is None:
                raise ValueError('--out is required for export.')
            export(data, args.out)
            print(f'Exported JSON, UTF-8-BOM CSV and review.md to {args.out}')
        else:
            print('PASS: structure and evidence references. Source accuracy was NOT independently checked.')
        return 0
    except (OSError, ValueError, TypeError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
