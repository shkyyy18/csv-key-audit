# CSV key preflight / 联合主键检查

```sh
csv-key-audit input.csv --key region --key id --html report.html --json report.json
```

`--key` repeats for exact composite keys. UTF-8 (optional BOM), comma delimiter, quoted multiline
fields. Duplicate/empty headers, missing key columns and ragged records reject the whole input.
Max 8 MiB / 100,000 records / Python csv default field limit (~128 KiB). No autodetection.

Output: duplicate groups with record numbers; blank/whitespace-only key rows; edge whitespace
locations. Key *values* are never exported, but column names are. Leading zeroes and whitespace
remain significant. `finding_count` = duplicate groups + blank-key rows + edge-whitespace rows;
a row can contribute to more than one category. Header-only CSV yields zero records, not an error.

示例：region,id 两列共同作为主键；重复组只列记录编号，不自动去重。
记录编号从表头之后 1 开始；带换行的单元格不会多算一条记录。
