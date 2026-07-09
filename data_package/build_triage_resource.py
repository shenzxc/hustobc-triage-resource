#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the 9408-row HUST-OBC triage resource table.

Pure data construction. No palaeographic reading judgment is made.
"""

import argparse
import csv
import json
import time
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ANALYSIS = ROOT / "分析"
PACKAGE = ROOT / "论文/data_package"

MAPPING_JSON = ANALYSIS / "官方映射_HUSTOBC.json"
YQWY_JSON = ANALYSIS / "yqwy_all_glyphs.json"
YH279_JSON = PACKAGE / "yh279_corrections.json"

CACHE_JSON = PACKAGE / "triage_resource_api_cache.json"
OUT_CSV = PACKAGE / "triage_resource.csv"
OUT_JSON = PACKAGE / "triage_resource.json"
SUMMARY_JSON = PACKAGE / "triage_resource_summary.json"

URL_TEMPLATE = "http://jgw.aynu.edu.cn/home/zx/method/jgwzx.ashx?bm={code}&type=getzxbybm"
MAX_ATTEMPTS = 3
TIMEOUT_SECONDS = 12
REQUEST_GAP_SECONDS = 0.35
SAVE_EVERY = 25

FIELDS = [
    "hustobc_class",
    "source_group",
    "top1_official_code",
    "top1_similarity",
    "top1_official_reading_jtz",
    "top1_official_status",
    "top1_has_jitilin_entry",
    "is_verified_correction",
]


def log(message):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}", flush=True)


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def source_group(hust_class):
    if hust_class.startswith("Y+H/"):
        return "Y+H"
    return hust_class.split("/", 1)[0]


def build_yqwy_reading_map(rows):
    by_code = {}
    for row in rows:
        code = row.get("code")
        if not code:
            continue
        by_code.setdefault(code, [])
        reading = str(row.get("jt") or "").strip()
        if reading and reading not in by_code[code]:
            by_code[code].append(reading)
    result = {}
    for code, readings in by_code.items():
        result[code] = {
            "official_reading_jtz": " / ".join(readings),
            "top1_official_status": "deciphered" if readings else "undeciphered",
        }
    return result


def load_cache():
    if CACHE_JSON.exists():
        return load_json(CACHE_JSON)
    return {}


def fetch_code(code):
    url = URL_TEMPLATE.format(code=urllib.parse.quote(code))
    errors = []
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0",
                "Connection": "close",
            })
            with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
                raw = resp.read().decode("utf-8")
            data = json.loads(raw)
            child = data.get("child") or []
            gl_pages = [str(c.get("GLZ")) for c in child if str(c.get("GLLX")) == "1" and c.get("GLZ") not in (None, "")]
            return {
                "ok": True,
                "attempts": attempt,
                "fetched_at": datetime.now().isoformat(timespec="seconds"),
                "url": url,
                "official_reading_jtz_api": data.get("JTZ") or "",
                "has_jitilin_entry": bool(gl_pages),
                "jitilin_pages": gl_pages,
                "child_count": len(child),
            }
        except Exception as exc:
            errors.append(f"{type(exc).__name__}: {exc}")
            time.sleep(REQUEST_GAP_SECONDS * attempt)
    return {
        "ok": False,
        "attempts": MAX_ATTEMPTS,
        "fetched_at": datetime.now().isoformat(timespec="seconds"),
        "url": url,
        "error": "; ".join(errors),
        "has_jitilin_entry": None,
        "jitilin_pages": [],
    }


def ensure_cache(unique_codes, offline=False, limit=None):
    cache = load_cache()
    pending = [code for code in unique_codes if code not in cache]
    if limit is not None:
        pending = pending[:limit]
    log(f"unique_top1_codes={len(unique_codes)} cached={len(cache)} pending={len(pending)} offline={offline}")
    if offline:
        return cache

    for idx, code in enumerate(pending, 1):
        cache[code] = fetch_code(code)
        status = "ok" if cache[code].get("ok") else "fail"
        log(f"[{idx}/{len(pending)}] {code} {status} gl={cache[code].get('has_jitilin_entry')}")
        if idx % SAVE_EVERY == 0:
            save_json(CACHE_JSON, cache)
        time.sleep(REQUEST_GAP_SECONDS)
    save_json(CACHE_JSON, cache)
    return cache


def build_rows(mapping, yqwy_map, verified_classes, cache):
    rows = []
    for hust_class in sorted(mapping):
        hits = mapping[hust_class]
        top1 = hits[0] if hits else {}
        code = top1.get("code") or ""
        yqwy = yqwy_map.get(code, {"official_reading_jtz": "", "top1_official_status": "undeciphered"})
        api = cache.get(code, {})
        if api.get("ok") and api.get("official_reading_jtz_api") and api.get("official_reading_jtz_api") != yqwy["official_reading_jtz"]:
            # Prefer the complete local all-glyphs table for the package field, but retain API response in cache.
            pass
        has_gl = api.get("has_jitilin_entry")
        if has_gl is True:
            has_gl_value = "true"
        elif has_gl is False:
            has_gl_value = "false"
        else:
            has_gl_value = "unknown-if-fetch-failed"
        rows.append({
            "hustobc_class": hust_class,
            "source_group": source_group(hust_class),
            "top1_official_code": code,
            "top1_similarity": top1.get("sim", ""),
            "top1_official_reading_jtz": yqwy["official_reading_jtz"],
            "top1_official_status": yqwy["top1_official_status"],
            "top1_has_jitilin_entry": has_gl_value,
            "is_verified_correction": hust_class in verified_classes,
        })
    return rows


def write_csv(rows):
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            csv_row = dict(row)
            csv_row["is_verified_correction"] = (
                "true" if row["is_verified_correction"] else "false"
            )
            writer.writerow(csv_row)


def summarize(rows, cache, unique_codes):
    status_counts = {}
    gl_counts = {}
    group_counts = {}
    for row in rows:
        status_counts[row["top1_official_status"]] = status_counts.get(row["top1_official_status"], 0) + 1
        gl_counts[row["top1_has_jitilin_entry"]] = gl_counts.get(row["top1_has_jitilin_entry"], 0) + 1
        group_counts[row["source_group"]] = group_counts.get(row["source_group"], 0) + 1
    success_codes = [code for code in unique_codes if cache.get(code, {}).get("ok")]
    failure_codes = [code for code in unique_codes if code not in cache or not cache.get(code, {}).get("ok")]
    has_gl_success_codes = [code for code in success_codes if cache.get(code, {}).get("has_jitilin_entry") is True]
    summary = {
        "task": "HUST-OBC triage resource",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "inputs": {
            "mapping": str(MAPPING_JSON.relative_to(ROOT)),
            "yqwy_all_glyphs": str(YQWY_JSON.relative_to(ROOT)),
            "yh279_corrections": str(YH279_JSON.relative_to(ROOT)),
        },
        "outputs": {
            "csv": str(OUT_CSV.relative_to(ROOT)),
            "json": str(OUT_JSON.relative_to(ROOT)),
            "cache": str(CACHE_JSON.relative_to(ROOT)),
        },
        "row_count": len(rows),
        "unique_top1_official_codes": len(unique_codes),
        "api_success_unique_codes": len(success_codes),
        "api_failure_unique_codes": len(failure_codes),
        "api_failure_codes": failure_codes,
        "unique_success_codes_with_jitilin_entry": len(has_gl_success_codes),
        "row_counts_by_official_status": status_counts,
        "row_counts_by_jitilin_entry": gl_counts,
        "row_counts_by_source_group": group_counts,
        "verified_correction_rows": sum(1 for row in rows if row["is_verified_correction"]),
    }
    save_json(SUMMARY_JSON, summary)
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true", help="Do not call API; use existing cache only.")
    parser.add_argument("--limit", type=int, default=None, help="Fetch at most N missing unique codes.")
    args = parser.parse_args()

    mapping = load_json(MAPPING_JSON)
    yqwy_map = build_yqwy_reading_map(load_json(YQWY_JSON))
    verified_classes = {row["hustobc_class"] for row in load_json(YH279_JSON)}

    unique_codes = []
    seen = set()
    for hust_class in sorted(mapping):
        hits = mapping[hust_class]
        if not hits:
            continue
        code = hits[0].get("code")
        if code and code not in seen:
            seen.add(code)
            unique_codes.append(code)

    cache = ensure_cache(unique_codes, offline=args.offline, limit=args.limit)
    rows = build_rows(mapping, yqwy_map, verified_classes, cache)
    write_csv(rows)
    save_json(OUT_JSON, rows)
    summary = summarize(rows, cache, unique_codes)
    log(json.dumps({
        "row_count": summary["row_count"],
        "unique_top1_official_codes": summary["unique_top1_official_codes"],
        "api_success_unique_codes": summary["api_success_unique_codes"],
        "api_failure_unique_codes": summary["api_failure_unique_codes"],
        "row_counts_by_official_status": summary["row_counts_by_official_status"],
        "row_counts_by_jitilin_entry": summary["row_counts_by_jitilin_entry"],
        "verified_correction_rows": summary["verified_correction_rows"],
        "summary_json": str(SUMMARY_JSON.relative_to(ROOT)),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
