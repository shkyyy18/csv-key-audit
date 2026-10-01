"""Exact composite-key diagnostics. Values are deliberately absent from reports."""

import csv
import io
from .common import text


def audit(source, keys):
    if not keys or len(set(keys)) != len(keys):
        raise ValueError("Provide distinct key names")
    try:
        reader = csv.reader(io.StringIO(source, newline=""), strict=True)
        header = next(reader)
        if not header or any(not h for h in header) or len(header) != len(set(header)):
            raise ValueError("Headers must be nonempty and unique")
        if any(k not in header for k in keys):
            raise ValueError("Key column missing")
        indices = [header.index(k) for k in keys]
        seen = {}
        empty, whitespace = [], []
        records = 0
        for records, row in enumerate(reader, 1):
            if records > 100000:
                raise ValueError("At most 100000 records")
            if len(row) != len(header):
                raise ValueError("Ragged CSV record")
            values = tuple(row[i] for i in indices)
            seen.setdefault(values, []).append(records)
            if any(not value.strip() for value in values):
                empty.append({"record": records})
            columns = [
                keys[i] for i, value in enumerate(values) if value != value.strip()
            ]
            if columns:
                whitespace.append({"record": records, "columns": columns})
    except (csv.Error, StopIteration) as exc:
        raise ValueError("Invalid CSV") from exc
    duplicates = [
        {"group": i, "records": rows, "count": len(rows)}
        for i, rows in enumerate((r for r in seen.values() if len(r) > 1), 1)
    ]
    return {
        "keys": keys,
        "records": records,
        "distinct_keys": len(seen),
        "duplicate_groups": duplicates,
        "empty_key_records": empty,
        "edge_whitespace": whitespace,
        "finding_count": len(duplicates) + len(empty) + len(whitespace),
        "boundary": "Exact strings, no normalization. Findings count groups + empty rows + whitespace rows; categories may overlap. Key values never exported.",
    }


def configure(parser):
    parser.add_argument("csv", nargs="?")
    parser.add_argument("--key", action="append", help="Repeat for a composite key")


def run(args):
    if not args.csv:
        raise ValueError("CSV path required")
    return audit(text(args.csv), args.key)


def demo():
    return audit(
        "region,id,label\nwest,01,Example A\nwest,01,Example B\neast,01,Example C\nwest,,Example D\neast, 01 ,Example E\n",
        ["region", "id"],
    )
