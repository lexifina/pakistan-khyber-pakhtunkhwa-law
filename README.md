# Khyber Pakhtunkhwa: law history in git

The Acts, Ordinances and Regulations of the Province of Khyber Pakhtunkhwa (Pakistan) as a git history: one file per section, one paragraph per line, so `git blame`, `git log` and `git diff` work line by line. The text is the English text of the Khyber Pakhtunkhwa Code (KP Code).

It follows the shared design of [lexifina/global-law](https://github.com/lexifina/global-law).

## What this repository holds

The record starts with 284 current-text baselines. Official PDFs also establish source-dated as-enacted wording for five acts: the Code of Criminal Procedure (Khyber Pakhtunkhwa) (Amendment) Act, 2025, two Provincial Assembly acts of 2026, the Climate Action Board Act, 2025, and the Judicial Officers Welfare Fund Act, 2025. A snapshot that includes their labelled correction commits has 289 versions; a snapshot before those corrections has 284. The other 279 acts have one current-text baseline each. The KP Code holds legislation "in revised form": amendments made by later laws are incorporated into the text, and it generally does not publish earlier consolidated wording.

| Commit category | Count when the five corrections are included | What it records |
| --- | ---: | --- |
| First-version baseline | 284 | One current-text version of each act |
| Correction | 5 | Source-dated as-enacted versions before the five corresponding baselines |

These corrections leave every current law-text file unchanged. Later source-dated versions can extend this history when their wording is established from official text.

| Folder | What |
| --- | --- |
| one folder per law (by its title, e.g. `the-khyber-pakhtunkhwa-trade-testing-board-act-2025/`) | the law as revised: `000-title.md` (publication note, long title and preamble), one file per section, one per Schedule |
| `data/amendments.csv` | every footnote of the revised text, which says which law inserted, substituted or omitted which words |

The laws are added in parts of about fifty, in the order of the KP Code's list (newest first). A law is left out until it can be read reliably: laws titled as repealed, scans without a text layer, PDFs whose layout the parser does not yet handle, and any PDF whose text fails the independent check below.

## Source

[Khyber Pakhtunkhwa Code](https://kpcode.kp.gov.pk/homepage/list_all_law), Law, Parliamentary Affairs and Human Rights Department, Government of Khyber Pakhtunkhwa: one PDF per law. Each PDF's sha256 is recorded with its version in `data/versions.json`.

## Dates

When included, the five as-enacted versions use their PDFs' Gazette publication and "come into force at once" clauses: 13 February 2025 for the Criminal Procedure amendment, 15 May 2025 for the Judicial Officers Welfare Fund Act, 18 September 2025 for the Climate Action Board Act, and 7 May 2026 for each Provincial Assembly act. Their current-text baselines, and the 279 other baseline versions, retain the day on which the revised text was retrieved, at noon in Peshawar (Asia/Karachi). A retrieval day is not an enactment or amendment day; the KP Code gives no general "as amended up to" date for its revised texts.

## How it is built

Lexifina reads the sources listed here and records each act's dated versions, and the laws that made each change, in one corpus file. `tools/build.py` writes this repository from that file, and the same corpus always gives the same commit hashes; `REPRODUCE.md` gives the details and the checks. A model (Claude) wrote Lexifina's code; it wrote no legal text, and no model runs when the history is built.

The text layer of each PDF (no OCR) becomes one file per section. The table of contents, the running heads (the law's title and number at the top of every page), page numbers, the watermark and footnote numbers are left out. The footnotes are kept in `data/amendments.csv`. Square brackets marking amended words stay as printed. Chapter and part headings stand above the first section under them. In membership tables the designation column ("Chairperson", "Member") is read after the cell beside it, as printed. Older laws printed with marginal notes (the section headings in the margin) are read by a second set of layout rules; the marginal notes are left out.

## How it is checked

Every version is read back from git on the day it took effect and must match the corpus. A second, independent reading of every PDF (a different PDF engine) must contain every letter and digit of each law in the same order, with nothing in the body left out. Results are in `REPRODUCE.md`.

## What "author" means

The publisher (the Law, Parliamentary Affairs and Human Rights Department) is the author of the baseline commits, with an e-mail address that cannot exist. Lexifina authors the labelled correction commits and is the committer.

## Limits

Earlier as-enacted wording is established for only five acts and appears in snapshots containing their correction commits. The other 279 acts have no earlier version in this record, and amended Acts generally cannot be reconstructed from the revised PDF alone. The KP Code is "developed only for informational purposes"; the authoritative text is the Khyber Pakhtunkhwa Gazette. Federal laws that apply in the province are in [lexifina/pakistan-law](https://github.com/lexifina/pakistan-law). For the older laws printed with marginal notes, the section headings (printed only in the margin) are not in the text.

## Licence

See [LICENSE](LICENSE): the laws are reproduced under the Copyright Ordinance, 1962, s. 57(1)(q)(i). Source: Khyber Pakhtunkhwa Code, Law, Parliamentary Affairs and Human Rights Department, Government of Khyber Pakhtunkhwa.
