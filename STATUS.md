# Status

Progress against the brief in [`docs/original-brief.md`](docs/original-brief.md).

| Step | State |
|---|---|
| 1. Verify the folder | Done. `build-tokens.py` regenerates `tokens.css` unchanged; `check-contrast.py` reports 0 failing. |
| 2. Visual check of `components/*/preview.html` (light and dark, 375 px wide) | Done; the defects below are fixed, and `scripts/check-previews.py` now fails CI on each of them. Touch targets done (Q4); the covers are fixed-size art, outside the phone check (Q3). |
| 3. Repository | `AlonRR/printable-parts-design-system` exists. `main` is fast-forwarded to branch `claude/inspiring-babbage-98suc5` (Q5). `main` is GitHub's default branch (set by the owner, 14 Oct). |
| 4. CI (`.github/workflows/check.yml`, runs on every push) | Done. Green on every push; job `tokens` (build, `tokens.css` unchanged, 52 contrast pairs, 0 failing) and, from `b755121`, job `previews` (60 pages checked, screenshots kept as the run's `previews` artifact). Since `f84eb8f` both jobs run through `uv run --locked`. Run 11 (`69dce72`) failed once: the check read a page before its font had been drawn; fixed in the check (`e98a2e9`). |
| 5. Report, incl. the `FONTS.md` "to be confirmed" items | Done: every licence statement in `FONTS.md` matches its upstream file (below). `FONTS.md` is unchanged. |

## Step 2: what the previews showed

`check-previews.py` renders the 15 previews in both themes on a phone (375 px, touch) and a
desktop (960 px). Before the fixes it reported 110 failures; after them, 0. Proved able to fail:
on the files as delivered, on labels pinned off centre, and on a button with a box drawn over it.

Correction (14 Oct): until `7a72294` the phone was a touch screen only for the first two
previews. A full-page screenshot of the 960 px Cover dropped the touch emulation, so the other 13
were checked as a 375 px mouse screen. Fixed in the check (a fresh page per preview, screenshot
last, a guard that fails if the emulation is wrong); with real touch emulation the fixes below
still hold, and the only new failures were the Q4 touch targets.

Correction (15 Oct): the checks ran with touch on, but the saved phone screenshots did not.
Chromium switches the touch emulation off for any capture beyond the window (Playwright's
full-page screenshot, CDP's `captureBeyondViewport`, and an emulated `pointer` media feature
does not survive it either), so every phone screenshot taller than the window was drawn as a
mouse screen: 36 px controls, not 44. The check now grows the window to the page and captures
that, and fails if touch is off when the screenshot is drawn; with the old capture that guard
fails on the 6 phone pages taller than the window.

Fixed, at the source:

- **`<code>` was not in FiraCode.** The browser sets `code` in its own monospace (Liberation Mono
  here, Consolas or Menlo elsewhere): the Dialog's `-print-8` and the Icons names. `bundle.css`
  now sets `code`, `kbd`, `samp` and `pre` in `--font-ui`.
- **The header cut off its buttons on a phone.** `overflow:hidden` hid Redo, Save, Load and the
  theme toggle at 375 px. The header now scrolls sideways instead (`overflow-x:auto`), one row.
- **Choice buttons were 38 px tall, not `control-h` (36 px; 46 px, not 44, on touch).** A `span`
  with `min-height` adds its border; the face is now `box-sizing:border-box`.
- **The Sides tick reached screen readers** (`"\ueab2 Top"`). The generated tick now carries empty
  alternative text (`content:"\eab2" / ""`), the CSS form of `aria-hidden`.
- **The plan bar crushed the stage on a phone.** Its sentence was squeezed into a narrow column
  beside the Download button, the stage drawing overflowed upwards over the header. The plan
  bar now wraps below the breakpoint and stays one row above it.
- **The Workbench preview typed its own layout** (`22rem` sidebar instead of `panel-width`,
  fixed rows): "Next: Fittings" stuck out of the sidebar on the desktop, and on a phone the
  preview kept the desktop columns. The preview now uses the component's own layout, and its
  stand-in drawing fills the stage the way the tool's canvas does.

Checked and correct: icons and the radio mark render from the bundled font in every preview;
the chosen Choice is filled with an inverted radio, 40 options in 4 runs.

Not changed:

- **Label centring.** Capitals sit 0.2 to 1.2 px above the centre of their box. The font
  overrides are right (the H glyph's height equals the font's cap height in both weights);
  Chromium rounds the ascent and descent to whole pixels and floors the top half-leading, which
  with a 22.5 px line box leaves the caps 0.55 px high, plus up to half a pixel from where the
  box falls on the pixel grid. A whole-pixel body line height would bring it to about 0.3 px;
  not worth changing every line of text for. The check allows 1.5 px.
- **The status bar** wraps each hint onto two lines at 960 px and on a phone; two lines just fit
  its 32 px. A longer hint would spill out of it.

## Step 5: the licences `FONTS.md` marks "to be confirmed"

Read on 14 Oct 2026; each link is pinned to the commit that was read. `FONTS.md` is left as it
is: its licence statements are the owner's to change.

- **Fira Code: SIL OFL 1.1.** Confirmed:
  [tonsky/FiraCode `LICENSE`](https://github.com/tonsky/FiraCode/blob/ecd367b040ad92a28b64fa93135775f7e2417b37/LICENSE),
  copyright "The Fira Code Project Authors". The bundled fonts carry the same copyright and say
  `Version 6.002;Nerd Fonts 3.4.0`.
- **Nerd Fonts: the patched fonts keep the base font's licence.** Confirmed: patched fonts are
  OFL 1.1 and the patcher's own code MIT
  ([`LICENSE`](https://github.com/ryanoasis/nerd-fonts/blob/e41135833dd63f1994096d3c61b04bdc52333cc3/LICENSE)),
  and the patched FiraCode folder ships Fira Code's licence byte for byte
  ([`patched-fonts/FiraCode/LICENSE`](https://github.com/ryanoasis/nerd-fonts/blob/e41135833dd63f1994096d3c61b04bdc52333cc3/patched-fonts/FiraCode/LICENSE)).
- **Codicons: icons CC BY 4.0, attribution required.** Confirmed:
  [`LICENSE`](https://github.com/microsoft/vscode-codicons/blob/6b53088f5c55bce7107fb579765364f59cd4ad5d/LICENSE)
  is CC BY 4.0; the code is MIT
  ([`LICENSE-CODE`](https://github.com/microsoft/vscode-codicons/blob/6b53088f5c55bce7107fb579765364f59cd4ad5d/LICENSE-CODE)).
- **Font Awesome Free: icons CC BY 4.0, font files SIL OFL 1.1, attribution required.**
  Confirmed ([`LICENSE.txt`, 6.x](https://github.com/FortAwesome/Font-Awesome/blob/840c215f894f429b26b8c1402a65da835dc5a450/LICENSE.txt)).
  The font files reserve the name "Font Awesome", which nothing here uses. Nerd Fonts lists
  both icon sets as CC BY 4.0
  ([`patched-fonts/FiraCode/README.md`](https://github.com/ryanoasis/nerd-fonts/blob/e41135833dd63f1994096d3c61b04bdc52333cc3/patched-fonts/FiraCode/README.md)).
- **The name of the subset.** Fira Code's licence reserves no font name, and neither does Nerd
  Fonts' OFL section: in both, "Reserved Font Name" appears only in the OFL's own definition.
  So a subset that keeps "FiraCode Nerd Font" reuses no reserved name.
- **Found on the way:** the subsets carry no licence inside the font (name IDs 13 and 14, the
  licence and its URL, are absent; pyftsubset keeps IDs 0 to 6 by default). The OFL accepts the
  notice in those fields or in a file beside the font, so the licence texts must go in as files
  before the repo is shared (now in `fonts/licenses/`, Q6), or the subsets be
  rebuilt with `--name-IDs='*'`.

## History

- An earlier session committed this content as `Claude <noreply@anthropic.com>`, with
  attribution trailers and unscoped subjects. On the owner's instruction the history was deleted
  and rebuilt with the cloud-session starter from `AlonRR/engineering-practices` in place.

## Open questions

- **Q1.** Closed: uv only. `pyproject.toml` and `uv.lock` replace `requirements.txt`; CI, the
  docs and the local gate use `uv run` (`f84eb8f`).
- **Q2.** Closed: the owner chose to reset `main` to the rebuilt history.
- **Q3.** Closed: A. The covers are fixed-size art for use outside the tools and never appear in
  one; their READMEs and `DESIGN.md` say so, and `check-previews.py` skips them on the phone.
- **Q4.** Closed: yes. Inputs, selects, PieceMap cells and Disclosure summaries are at least
  `control-h` tall: 36 px on a desktop, 44 px (`tap`) on a touch screen (`e7ef17e`), and
  `check-previews.py` checks it.
- **Q5.** Closed: yes. `main` is fast-forwarded to the session branch (a fast-forward push, so the
  commits keep the owner as committer). The owner has made `main` GitHub's default branch.
- **Q6.** Closed: yes. The font and icon licence texts and credits are in `fonts/licenses/`, byte
  for byte from upstream (`f48d65a`; moved inside `fonts/` with D8, so they travel with it).
- **Q7.** Closed: Skådis Air first. The plan is
  [`docs/adoption-skadis-air.md`](docs/adoption-skadis-air.md): two changes here, then four parts
  in Skådis Air, carried out in a session on the owner's machine (its pushes go to Gitea first).
- **D8.** Closed: yes. MPL-2.0 for code, CERN-OHL-S-2.0 for documentation, the fonts their own;
  the REUSE layout (`LICENSES/`, `REUSE.toml`), `reuse lint` in the local gate and in CI.
- **D9.** Closed: yes. The fonts ship once, as files, loaded through `tokens.css`; `bundle.css` is
  10 KB and `build-tokens.py` fails if a font comes back into it (`0eac517`).
- **D10 to D13.** Closed, each (a), for Skådis Air: `Choice` buttons for the board type, a dark
  theme with a header toggle, the intro in the sidebar, one form before numbered steps. Recorded
  in [`docs/adoption-skadis-air.md`](docs/adoption-skadis-air.md); they go into Skådis Air's own
  status when the work starts there, on the owner's machine.
- **T14.** Closed: the owner tagged `v0.1.0` on `aa3188e` (`main`) and pushed it, 14 Oct 2026; a
  push of the tag from the cloud session was refused (HTTP 403). `v0.2.0` supersedes it for Skådis Air (T16).
- **D15.** Closed: (a). The part always fits the stage: framed to `stage-fit` (0.85) when it or
  its size changes, the angle kept and the camera pulled back on a resize, zoom out stopping at
  `stage-min-fill` (0.25), no panning off the stage, "Reset view" back to the first view.
  `DESIGN.md` and the Workbench README say so; `check-previews.py` fails if a stage drawing leaves
  its stage view; the Skådis Air plan carries the behaviour and its browser test (part 3).
- **T16.** Closed: the owner tagged `v0.2.0` on `7b43d0c` (`main`, with D15's tokens) and pushed
  it, 14 Oct 2026. Skådis Air copies from `v0.2.0`.
- **Q17.** Closed: yes. The Skådis Air session (on the owner's machine) was told of D15 and to copy
  from `v0.2.0`, 14 Oct 2026; it had already recorded the adoption as its D111.
- **D18.** Yes (15 Oct 2026): what Skådis Air had to add to the system in its own page (read at
  `AlonRR/skadis-air` `a9c9a93`, `web/index.html`) is now in the system. Each theme sets
  `color-scheme`; a `ws-page` base for `<body>`; the Notice's `warning` variant, headline colours
  and an empty Notice taking no room; the stage's canvas contract and `ws-stage__message`; the
  mouse and touch hints; the plan bar's `ws-plan__line` and `ws-plan__actions` (tokens
  `plan-line-basis` and `number-field-w`); the header name's margin, the first control's margin,
  the number field's width, a caption after a Choice run, the Sides margin and caption; the fonts
  licence README links `FONTS.md` by URL, so the link works in a copy. `check-previews.py` gained
  checks 8 to 11 and the canvas and stage-message checks; on the CSS before the change they
  reported 120 failures, all in the new checks, and the plan check fails on the old desktop rule.
  Its page-specific rules (`.tagline`, `.note`, `[data-state]` colours) stay in Skådis Air. Next:
  `v0.3.0` (T21), then Skådis Air copies it and drops its local rules.
- **D19.** Closed: yes (15 Oct 2026). `DESIGN.md`, "Reference implementations", links Skådis Air's
  theme code, framing code and its test, the workbench's browser test and the copy script, pinned
  to `AlonRR/skadis-air` `b55c32d` (each link checked against that commit); the theme's rule is
  among the workbench rules, and the README points there. No TypeScript moved into this repository.
- **D20.** Yes (15 Oct 2026), open: this repository takes Skådis Air's commit hooks and CI checks
  (the `type(scope)` subject rule, the identity of every pushed commit, a secret scan).
- **T21.** Open: tag `v0.3.0` on `main` once D18 is there, and push it (a cloud session cannot).
