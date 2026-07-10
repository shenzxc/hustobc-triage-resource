# HUST-OBC Triage-and-Audit Resource

A reproducible **triage-and-audit resource** over all **9,408 undeciphered character classes
of HUST-OBC**, plus **279 verified metadata corrections**, and the companion methods paper.

This repository is the citable release archive (archived on Zenodo). The research code and
full analysis live in a separate working repository.

## What's here

| Path | Contents |
|---|---|
| `data_package/triage_resource.csv` / `.json` | 9,408 rows — one per undeciphered HUST-OBC class: its shape-similar official code, that code's reading/status, whether the *Jiaguwenzi Gulin* (Jitilin) already discusses it, and a constructive-identity code for `Y+H` classes. |
| `data_package/yh279_corrections.csv` / `.json` | 279 verified metadata corrections (classes labelled undeciphered that already carry an official reading), each reproducible via a per-row API URL. |
| `data_package/*_data_dictionary.md` | Field-by-field definitions. |
| `data_package/build_triage_resource.py` | Deterministic builder. |
| `data_descriptor.md` | Data Descriptor manuscript (draft). |
| `methods_paper_preprint.pdf` | Methods paper preprint. |
| `figures/` | Paper figures (PDF). |

## Key idea

An "undeciphered" label in an OBS dataset means "no single consensus transcription," **not**
"not yet studied." A majority of officially-undeciphered characters already have a discussion
entry in the *Jitilin* (55.5–71.5% across five random samples, mean 63.2%; 65% among
shape-known-like candidates). This resource makes that visible at dataset scale, functioning as
a **filtered target space** that separates genuinely-unclaimed characters from already-discussed
ones — and audits 279 stale "undeciphered" labels as a by-product.

## Provenance & licensing

- HUST-OBC images: CC BY 4.0 (Wang et al., *Scientific Data*, 2024).
- Official readings / codes / cross-references: Yinqi Wenyuan platform (Anyang Normal
  University), reproduced as **factual data** via its public, login-free API.
- **No copyrighted scans or fonts are redistributed** — only character codes, page/entry
  identifiers, factual readings, and reproduction URLs. See `data_package/LICENSE`.

## Citation

Cite the Zenodo DOI of this release: **10.5281/zenodo.21290640**
(https://doi.org/10.5281/zenodo.21290640). See `data_package/CITATION.cff`.

## Note

We do **not** claim autonomous machine decipherment. This is a triage-and-audit methodology
that concentrates expert effort on genuinely unclaimed characters; all character readings are
attributed to prior published palaeographic scholarship.
