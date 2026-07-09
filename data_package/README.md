# Oracle Bone Decipherment Data Package

This directory packages tabular data products used by the oracle-bone
decipherment project. It currently contains the 279 HUST-OBC metadata
corrections and a 9,408-row triage resource for HUST-OBC undeciphered
classes.

These are metadata and retrieval packages, not new decipherment claims. The
packages copy official readings verbatim, add stable identifiers and
normalized field names, and record mechanical API checks.

## Contents

- `yh279_corrections.csv`: canonical tabular package, 279 data rows plus header.
- `yh279_corrections.json`: same records as a JSON array for programmatic use.
- `data_dictionary.md`: field definitions, value domains, type mapping, and integrity checks.
- `triage_resource.csv`: 9,408-row triage table for HUST-OBC undeciphered classes.
- `triage_resource.json`: same triage records as a JSON array.
- `triage_resource_api_cache.json`: cached `getzxbybm` API results for the 2,751 unique top-1 official codes.
- `triage_resource_summary.json`: construction metadata and aggregate counts for the triage table.
- `triage_resource_data_dictionary.md`: field definitions and count summary for the triage table.
- `build_triage_resource.py`: deterministic builder for the triage table and cache.

## YH279 Construction Method

The source file is `分析/勘误_YH279.csv`. Each source row contains a HUST-OBC class directory such as `Y+H/60007` and an official code such as `U60007`.

The construction is deterministic:

1. Copy the source row order and assign stable IDs `YH279-001` through `YH279-279`.
2. Split `hustobc_class` to obtain `yh_dirname`.
3. Check that `official_code == "U" + yh_dirname`.
4. Copy `official_reading_jtz` and `repro_url` verbatim from the source CSV.
5. Set `hustobc_label` to `undeciphered`.
6. Map the source reading types mechanically:
   - `纯` -> `plain`
   - `通假` -> `loan_or_variant`
   - `存疑` -> `tentative`
7. Copy parenthetical annotations into `note` for `loan_or_variant` rows and record the official `*` marker in `tentative` rows.

## Reproducing Individual Checks

The `repro_url` field can be queried directly. Examples:

```bash
curl 'http://jgw.aynu.edu.cn/home/zx/method/jgwzx.ashx?bm=U60007&type=getzxbybm'
curl 'http://jgw.aynu.edu.cn/home/zx/method/jgwzx.ashx?bm=U60040&type=getzxbybm'
curl 'http://jgw.aynu.edu.cn/home/zx/method/jgwzx.ashx?bm=U60770&type=getzxbybm'
```

Expected checks:

- `U60007` returns the official reading copied into the package as `望`.
- `U60040` returns the official reading copied into the package as `匕(妣)`.
- `U60770` returns the official reading copied into the package as `早*`.

The source errata note records a live cross-check on 2026-07-06: 279/279 package codes returned the expected official reading.

## YH279 Summary Counts

| `reading_type` | Count |
|---|---:|
| `plain` | 266 |
| `loan_or_variant` | 11 |
| `tentative` | 2 |
| **Total** | **279** |

## Triage Resource Construction Method

The triage resource is built by `build_triage_resource.py` from three local
inputs:

- `分析/官方映射_HUSTOBC.json`: 9,408 HUST-OBC undeciphered classes and their official glyph retrieval matches.
- `分析/yqwy_all_glyphs.json`: official Yinqi Wenyuan glyph rows and `JTZ` readings.
- `论文/data_package/yh279_corrections.json`: the 279 verified metadata-correction records.

The construction is deterministic apart from the live API cache:

1. For each HUST-OBC class, take the top-1 official match from `分析/官方映射_HUSTOBC.json`.
2. Deduplicate top-1 official codes and query each unique code through `getzxbybm`.
3. Cache the API result in `triage_resource_api_cache.json`.
4. Copy the official `JTZ` reading from `分析/yqwy_all_glyphs.json`.
5. Set `top1_official_status` mechanically from whether the official reading is blank.
6. Set `top1_has_jitilin_entry` from cached API children where `GLLX=1`; failed API codes are recorded as `unknown-if-fetch-failed`.
7. Mark `is_verified_correction` by membership in `yh279_corrections.json`.

Rebuild from the live API:

```bash
python3 论文/data_package/build_triage_resource.py
```

Rebuild outputs from the existing cache without network access:

```bash
python3 论文/data_package/build_triage_resource.py --offline
```

## Triage Resource Summary Counts

| Metric | Count |
|---|---:|
| Rows | 9,408 |
| Unique top-1 official codes | 2,751 |
| API success, unique codes | 2,731 |
| API failure, unique codes | 20 |
| Top-1 official status `deciphered` rows | 4,409 |
| Top-1 official status `undeciphered` rows | 4,999 |
| `top1_has_jitilin_entry=true` rows | 6,229 |
| `top1_has_jitilin_entry=false` rows | 3,107 |
| `top1_has_jitilin_entry=unknown-if-fetch-failed` rows | 72 |
| `is_verified_correction=true` rows | 279 |

The Jitilin-entry rate among rows with a successful API result is
6,229 / 9,336 = 66.72%.

## License

TODO: confirm redistribution terms for Yinqi Wenyuan official reading data before public archival release.

## Citation

TODO: add DOI and final citation text after Zenodo or another archive publishes the data package.
