# Status

Progress against the brief in [`docs/original-brief.md`](docs/original-brief.md).

| Step | State |
|---|---|
| 1. Verify the folder | Done. `build-tokens.py` regenerates `tokens.css` unchanged; `check-contrast.py` reports 0 failing. |
| 2. Visual check of `components/*/preview.html` (light and dark, 375 px wide) | Not started. Chromium is preinstalled for Playwright in cloud sessions. |
| 3. Repository | `AlonRR/printable-parts-design-system` exists. `main` and branch `claude/inspiring-babbage-98suc5` hold the same rebuilt history. |
| 4. CI (`.github/workflows/check.yml`, runs on every push) | Not yet confirmed green. |
| 5. Report, incl. the `FONTS.md` "to be confirmed" items | Not started. |

## History

- An earlier session committed this content as `Claude <noreply@anthropic.com>`, with
  attribution trailers and unscoped subjects. On the owner's instruction the history was deleted
  and rebuilt with the cloud-session starter from `AlonRR/engineering-practices` in place.

## Open questions

- **Q1.** The house rules say Python dependencies go through `uv` and `pyproject.toml`, but the
  folder ships `requirements.txt`, and CI and the README install it with pip. Convert to
  `pyproject.toml` + `uv`, or keep `requirements.txt` for this repo?
- **Q2.** Closed: the owner chose to reset `main` to the rebuilt history.
