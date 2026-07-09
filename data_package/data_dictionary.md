# YH279 Corrections Data Dictionary

This data package expands `分析/勘误_YH279.csv` into a citable, machine-readable errata table for 279 HUST-OBC `Y+H` classes. It only reorganizes previously verified metadata. It does not add or revise any palaeographic reading.

## Files

- `yh279_corrections.csv`: UTF-8 CSV with one row per correction.
- `yh279_corrections.json`: JSON array containing the same records and field names as the CSV.

## Fields

| Field | Type | Required | Meaning / Source | Values |
|---|---:|---:|---|---|
| `id` | string | yes | Stable package-local row identifier assigned in source CSV order. | `YH279-001` through `YH279-279` |
| `hustobc_class` | string | yes | HUST-OBC class directory copied from `分析/勘误_YH279.csv`. | `Y+H/<five-hex-code>` |
| `hustobc_label` | string | yes | HUST-OBC split label for these classes. | fixed `undeciphered` |
| `yh_dirname` | string | yes | The five-character directory name after `Y+H/`. | five hex characters, e.g. `60007` |
| `official_code` | string | yes | Yinqi Wenyuan official glyph code. Constructed identity: `U` + `yh_dirname`. | `U<five-hex-code>` |
| `official_reading_jtz` | string | yes | Official `JTZ` reading copied verbatim from the source errata CSV, which copied it from the public `getzxbybm` response. | Chinese reading string; may include parenthetical annotation or `*` |
| `reading_type` | string | yes | Normalized type derived mechanically from the source `释读类型` column. | `plain`, `loan_or_variant`, `tentative` |
| `evidence_source` | string | yes | Source endpoint used for verification. | fixed `Yinqi Wenyuan getzxbybm API` |
| `repro_url` | string | yes | Per-record reproduction URL copied from source CSV. | `http://jgw.aynu.edu.cn/home/zx/method/jgwzx.ashx?bm=<official_code>&type=getzxbybm` |
| `fetched_date` | date string | yes | Date of the live API cross-check recorded by the source errata note. | fixed `2026-07-06` |
| `verifier` | string | yes | Verification statement from the errata note. | fixed `automated API cross-check, 279/279` |
| `note` | string | no | Mechanical extraction of source annotations. Blank for `plain`; parenthetical content for `loan_or_variant`; star marker note for `tentative`. | empty, `loan_or_variant: <annotation>`, or `official tentative marker: *` |

## Type Mapping

| Source `释读类型` | `reading_type` | Row Count | Transformation |
|---|---|---:|---|
| `纯` | `plain` | 266 | Official reading copied as-is; `note` empty. |
| `通假` | `loan_or_variant` | 11 | Official reading copied as-is; parenthetical annotation copied to `note`. |
| `存疑` | `tentative` | 2 | Official reading copied as-is; `note` records the official `*` marker. |

The source column does not mechanically distinguish `loan` from `variant`; the package therefore uses `loan_or_variant` instead of assigning a narrower category.

## Integrity Checks

- Row count: 279 records.
- Identifier range: `YH279-001` to `YH279-279`.
- Identity check: every `official_code` equals `U` + `yh_dirname`.
- Label check: every `hustobc_label` is `undeciphered`.
- Required-field check: no required field is blank.
