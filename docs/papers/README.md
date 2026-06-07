# Arkheionx papers

Technical papers and standalone artifacts for Arkheionx. These are explanatory
documents, **not** audit reports: they do not confirm vulnerabilities, do not
assign severity, and do not stand in for human security review.

## Arkheionx v4 technical paper

A serious, minimal technical overview of the local review-map workflow, written
to be read on its own without the website.

- [Markdown source](arkheionx-v4-technical-paper.md)
- [PDF](arkheionx-v4-technical-paper.pdf) (also served at
  `https://arkheionx.dev/arkheionx-v4-technical-paper.pdf`)
- [HTML](arkheionx-v4-technical-paper.html)

Author: Yudistira Putra. Version: v4.0.0. Every command excerpt in the paper is
real engine output from the bundled
[demo fixture](../../examples/vault-strategy-oracle-fixture/README.md), abridged
for length.

## Rebuilding

The PDF and HTML are generated from the Markdown source by a self-contained
build script with no third-party dependencies, no network access, and no
external fonts or CDN:

```sh
python3 scripts/build_technical_paper.py
```

The script ([`scripts/build_technical_paper.py`](../../scripts/build_technical_paper.py))
typesets the PDF directly using the standard PDF fonts, writes the HTML, and
copies the PDF into `site/public/` for the website. When `pdfinfo` and
`pdftotext` are available it also checks the page count and confirms the title,
author, and headings are present and extractable.

See the documentation index in [`docs/README.md`](../README.md) for the rest of
the project docs.
