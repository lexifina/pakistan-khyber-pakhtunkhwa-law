# Khyber Pakhtunkhwa: law history in git

The Acts, Ordinances and Regulations of the Province of Khyber Pakhtunkhwa (Pakistan) as a git history: one file per section, one paragraph per line, so `git blame`, `git log` and `git diff` work line by line. The text is the English text of the Khyber Pakhtunkhwa Code (KP Code).

It follows the shared design of [lexifina/global-law](https://github.com/lexifina/global-law).

## What this repository holds

**Current text only, not yet a history.** The KP Code holds each law "in revised form": the amendments made by later laws are incorporated into the text, and no earlier consolidated text is published. So each law is one commit holding its whole current text, dated by the day it was retrieved and credited to the department ("oldest version available"), not to an amending Act.

| Folder | What |
| --- | --- |
| one folder per law (by its title, e.g. `the-khyber-pakhtunkhwa-trade-testing-board-act-2025/`) | the law as revised: `000-title.md` (publication note, long title and preamble), one file per section, one per Schedule |
| `data/amendments.csv` | every footnote of the revised text, which says which law inserted, substituted or omitted which words |

The laws are added in parts of about fifty, in the order of the KP Code's list (newest first). A law is left out until it can be read reliably: laws titled as repealed, scans without a text layer, PDFs whose layout the parser does not yet handle, and any PDF whose text fails the independent check below.

## Source

[Khyber Pakhtunkhwa Code](https://kpcode.kp.gov.pk/homepage/list_all_law), Law, Parliamentary Affairs and Human Rights Department, Government of Khyber Pakhtunkhwa: one PDF per law. Each PDF's sha256 is recorded with its version in `data/versions.json`.

## Dates

Each law's version is dated by the day it was retrieved from the KP Code, at noon in Peshawar (Asia/Karachi). That is not the day of its enactment or of its last amendment; the KP Code gives no "as amended up to" date.

## How it is built

Lexifina reads the sources listed here and records each act's dated versions, and the laws that made each change, in one corpus file. `tools/build.py` writes this repository from that file, and the same corpus always gives the same commit hashes; `REPRODUCE.md` gives the details and the checks. A model (Claude) wrote Lexifina's code; it wrote no legal text, and no model runs when the history is built.

The text layer of each PDF (no OCR) becomes one file per section. The table of contents, the running heads (the law's title and number at the top of every page), page numbers, the watermark and footnote numbers are left out. The footnotes are kept in `data/amendments.csv`. Square brackets marking amended words stay as printed. Chapter and part headings stand above the first section under them. In membership tables the designation column ("Chairperson", "Member") is read after the cell beside it, as printed. Older laws printed with marginal notes (the section headings in the margin) are read by a second set of layout rules; the marginal notes are left out.

## How it is checked

Every version is read back from git on the day it took effect and must match the corpus. A second, independent reading of every PDF (a different PDF engine) must contain every letter and digit of each law in the same order, with nothing in the body left out. Results are in `REPRODUCE.md`.

## What "author" means

The author of each commit is the publisher (the Law, Parliamentary Affairs and Human Rights Department), with an e-mail address that cannot exist; the committer is always Lexifina.

## Limits

Only the current revised text is here: no earlier versions, and not the laws as enacted. The KP Code is "developed only for informational purposes"; the authoritative text is the Khyber Pakhtunkhwa Gazette. Federal laws that apply in the province are in [lexifina/pakistan-law](https://github.com/lexifina/pakistan-law). For the older laws printed with marginal notes, the section headings (printed only in the margin) are not in the text.

## Licence

See [LICENSE](LICENSE): the laws are reproduced under the Copyright Ordinance, 1962, s. 57(1)(q)(i). Source: Khyber Pakhtunkhwa Code, Law, Parliamentary Affairs and Human Rights Department, Government of Khyber Pakhtunkhwa.
