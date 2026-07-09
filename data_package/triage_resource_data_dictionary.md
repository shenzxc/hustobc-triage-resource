# Triage Resource Data Dictionary

This dictionary describes `triage_resource.csv` and `triage_resource.json`.
The table is a mechanical triage resource for the 9,408 HUST-OBC
undeciphered classes. It records the top-1 official Yinqi Wenyuan match,
the official `JTZ` status for that match, whether the live API exposed a
Jitilin child entry, and whether the HUST-OBC class is part of the 279
verified metadata corrections.

The table does not make or imply palaeographic reading conclusions.

## Files

- `triage_resource.csv`: 9,408 rows plus header, for spreadsheet use.
- `triage_resource.json`: same 9,408 records as a JSON array.
- `triage_resource_api_cache.json`: per-official-code cache for
  `getzxbybm` API responses and retry failures.
- `triage_resource_summary.json`: construction metadata and aggregate
  counts.
- `build_triage_resource.py`: deterministic builder for the package.

## Field Definitions

| Field | CSV type | JSON type | Description |
|---|---|---|---|
| `hustobc_class` | string | string | HUST-OBC class path, for example `L/1`, `X/12`, or `Y+H/60007`. |
| `source_group` | string enum | string enum | Mechanical source group derived from `hustobc_class`: `X`, `L`, or `Y+H`. |
| `top1_official_code` | string | string | Top-1 official Yinqi Wenyuan glyph code from `分析/官方映射_HUSTOBC.json`. |
| `top1_similarity` | decimal string | number | Top-1 glyph retrieval similarity score from `分析/官方映射_HUSTOBC.json`. |
| `top1_official_reading_jtz` | string | string | Official `JTZ` reading copied from `分析/yqwy_all_glyphs.json`; blank means no official reading in that source table. |
| `top1_official_status` | string enum | string enum | `deciphered` when `top1_official_reading_jtz` is nonempty, otherwise `undeciphered`. |
| `top1_has_jitilin_entry` | string enum | string enum | `true` if the cached `getzxbybm` response exposed a child entry with `GLLX=1`; `false` if the request succeeded and no such child was found; `unknown-if-fetch-failed` if all retry attempts failed for that official code. |
| `identity_official_code` | string | string | **(Y+H rows only.)** Construction-guaranteed official code whose last five hex digits equal the `Y+H` directory name (`Y+H/60007` → `U60007`). Blank for `X`/`L`. Authoritative code for `Y+H` and basis of the 279 audit. |
| `identity_official_reading_jtz` | string | string | **(Y+H rows only.)** Official `JTZ` reading of `identity_official_code`. Blank for `X`/`L`. |
| `identity_official_status` | string enum | string enum | **(Y+H rows only.)** `deciphered`/`undeciphered` for `identity_official_code`. Blank for `X`/`L`. |
| `is_verified_correction` | boolean string | boolean | Whether `hustobc_class` appears in `yh279_corrections.json`. CSV uses `true`/`false`; JSON native booleans. For every such row the `identity_*` columns give the authoritative reading. |

## Two independent code signals — do not conflate

The table carries **two distinct official-code signals**:

1. **`top1_*` (shape-retrieval signal, all 9,408 rows)** — the official code whose glyph *looks*
   most similar, from ResNet-18 retrieval; the paper's method output.
2. **`identity_*` (constructive-identity signal, 2,676 `Y+H` rows)** — the official code the class
   *is*, by directory-name construction; ground truth for `Y+H` and the basis of the 279 audit.

For `Y+H` rows these agree only **19.7 %** of the time — shape retrieval and construction diverge
because of the domain gap between rendered official fonts and handwritten/rubbing images. This
divergence is a documented property of the resource, not an error. Prefer `identity_*` as the
authoritative reading for `Y+H`; use `top1_*` only as the independent shape signal. `X`/`L` rows
have no identity mapping and rely on `top1_*` alone.

## Value Domains

| Field | Values |
|---|---|
| `source_group` | `X`, `L`, `Y+H` |
| `top1_official_status` | `deciphered`, `undeciphered` |
| `top1_has_jitilin_entry` | `true`, `false`, `unknown-if-fetch-failed` |
| `is_verified_correction` | CSV: `true`, `false`; JSON: `true`, `false` |

## Construction Notes

1. Load all 9,408 HUST-OBC classes from `分析/官方映射_HUSTOBC.json`.
2. Take the first match in each class record as `top1_official_code` and
   `top1_similarity`.
3. Load official `JTZ` readings from `分析/yqwy_all_glyphs.json` and assign
   `top1_official_status` mechanically from whether the reading is blank.
4. Build the verified-correction set from
   `论文/data_package/yh279_corrections.json`.
5. Query each unique top-1 official code through
   `http://jgw.aynu.edu.cn/home/zx/method/jgwzx.ashx?type=getzxbybm&bm=...`
   with three attempts and a local JSON cache.
6. Mark `top1_has_jitilin_entry` from cached API children where `GLLX=1`.

## Aggregate Counts

| Metric | Count |
|---|---:|
| Rows | 9,408 |
| Unique top-1 official codes | 2,751 |
| API success, unique codes | 2,731 |
| API failure, unique codes | 20 |
| Rows with top-1 official status `deciphered` | 4,409 |
| Rows with top-1 official status `undeciphered` | 4,999 |
| Rows with `top1_has_jitilin_entry=true` | 6,229 |
| Rows with `top1_has_jitilin_entry=false` | 3,107 |
| Rows with `top1_has_jitilin_entry=unknown-if-fetch-failed` | 72 |
| Rows with `is_verified_correction=true` | 279 |

For rows with a successful API result, the Jitilin-entry rate is
6,229 / (6,229 + 3,107) = 66.72%.
