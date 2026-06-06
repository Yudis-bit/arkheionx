# CLI UX

How Arkheionx presents human terminal output, and how to control it. This is a
presentation layer only — it never changes analysis results, JSON, or written
artifacts.

## Design goals

Fast, clear, structured, and honest. Arkheionx does real local analysis and
guides you to the right artifact; it never fakes work to look busy.

## Honest progress

`arkheionx review-map` and `arkheionx open` show phase lines while they work:

```text
[ok] [1/3] Inspecting repository: 18 Solidity source files, 4 test files (0.13s)
[ok] [2/3] Mapping value flow & review surface: 7 contracts, 21 functions, ... (0.19s)
[ok] [3/3] Writing review artifacts: 9 files -> .arkheionx/out/review-map/ (0.09s)
```

- A spinner runs only while real work is in flight, and only on an interactive
  terminal.
- Phase labels and elapsed times are real. Counts appear only once known.
- There are no fake percentages, no progress bars, and no artificial delays.

## Animation

The in-place spinner is disabled automatically when any of these holds:

- stdout is not an interactive terminal (pipes, captures, redirects);
- `CI` is set;
- `ARKHEIONX_NO_ANIMATION` is set;
- `--json`, quiet, or machine-readable output is requested.

When animation is off, each phase prints a single clean line with no carriage
returns, so logs and scripts stay tidy.

## Color

Color is restrained and opt-in by terminal:

- `ARKHEIONX_COLOR=always` — force color on (human output only);
- `ARKHEIONX_COLOR=never` — force color off;
- `ARKHEIONX_COLOR=auto` (default) — color only on a TTY;
- `NO_COLOR` or `CI` — disable color (unless `ARKHEIONX_COLOR=always`).

Color is never written to JSON, Markdown, Mermaid, or any artifact file.

## Status marks

Status marks use `✓` / `!` / `✗` on UTF-8 terminals and fall back to
`[ok]` / `[warn]` / `[error]` otherwise. Set `ARKHEIONX_ASCII` to force the
ASCII marks.

## Machine-readable and no-write

- `--json` prints valid JSON to stdout and nothing else: no banner, no progress,
  no spinner, no color.
- `--no-write` computes the map in memory only. It writes no files and never
  claims that artifacts were written.

## Exit codes

`arkheionx review-map` follows the workbench convention and prints a matching
`Status:` line in the Boundary section:

- `0` — compiler-confirmed run.
- `1` — heuristic review guidance (the normal static default; **by design**, not
  a crash or a failed analysis).
- `2` — usage/input error (bad path, no Solidity files, invalid `--top`, unknown
  `--target`).

## Quick reference

| Control | Effect |
| --- | --- |
| `ARKHEIONX_NO_ANIMATION` | Disable the spinner |
| `ARKHEIONX_COLOR` | `always` / `never` / `auto` |
| `NO_COLOR` | Disable color |
| `ARKHEIONX_ASCII` | Force ASCII status marks |
| `CI` | Disable animation and color |
| `--json` | Machine-readable output only |
| `--no-write` | In-memory only; write nothing |

See [`START_HERE.md`](START_HERE.md) for a first run and
[`REVIEW_MAP.md`](REVIEW_MAP.md) for the review-map reference.
