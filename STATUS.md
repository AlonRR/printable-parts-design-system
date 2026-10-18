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
- **D18.** Closed: yes (15 Oct 2026). What Skådis Air had to add to the system in its own page (read at
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
- **D20.** Closed: yes (15 Oct 2026). Skådis Air's commit hooks and CI checks, copied
  from `AlonRR/skadis-air` `b55c32d` (`.pre-commit-config.yaml`, `.githooks/`, `tests/test-hooks.sh`,
  `tests/test-yamllint.sh`, `tests/test-workflow.sh`, `.editorconfig`, `.markdownlint-cli2.yaml`,
  `.yamllint.yaml`), adapted only where this repository differs (its byte-exact files are the font
  licence texts; no submodule; ruff for the scripts; no Pages workflow). CI gains three jobs: every
  hook with the hooks' tests, the identity of every pushed commit, and a full-history secret scan.
  To pass the hooks, `tokens.json` is indented two spaces (content unchanged; `tokens.css` rebuilds
  byte for byte) and `bundle.css` lost three odd indents. The history scan found one match, inside
  the base64 font `bundle.css` embedded until D9: shown to decode to `fonts/FiraCodeNF-Bold.woff2`
  byte for byte, and allowed by its fingerprint in `.gitleaksignore`. With T22 done, all five jobs
  are green on `b882141` (run 32) and `47891f1` (run 33).
- **T21.** Closed: `v0.3.0` is tagged on `937f5c3` (tag object `abbe841`, SSH-signed, GitHub shows
  it verified) and released on GitHub, 15 Oct 2026, by the admin session on the owner's machine,
  on the owner's first-hand yes there; tag and release checked on GitHub from here. It carries
  D18, D19, D20 and D24.
  (The entry went missing from this file in `937f5c3`, cut off by the D24 edit; restored here.)
- **T22.** Closed: the owner set the repository variables `EXPECT_EMAIL` and `EXPECT_NAME`,
  15 Oct 2026; the identity job was re-run on the D20 commits.
- **A23.** Closed: yes. `CLAUDE.md` carries the starter's reply rules (`AlonRR/engineering-practices`
  `e843d96`): what each question letter asks for, a new question asked in the body first, every
  reply ending with an "Open:" list, and the final report saying what was recorded where.
- **D24.** Closed: (b). `fonts/licenses/README.md` names `FONTS.md` and this repository in plain
  text. `build-tokens.py` now fails if a document in `fonts/`, which the tools copy, links out of
  `fonts/` or to this repository; it fails on both earlier forms of the link (`../../FONTS.md`,
  and the URL D18 put in).
- **D25.** Closed: (a), 16 Oct 2026. The 45 % goes to the 3D view alone; the plan bar keeps to one
  row with "Reset view" over the view; the status bar leaves the sticky part; side by side in
  landscape; not sticky on short screens; the checks add short screens with a minimum view height
  and a focused control never covered; the phone screenshot keeps the device's height.
- **D26.** Closed: (b), 16 Oct 2026 (both options were shown as one image, light and dark). Every
  selected state is `action-tint` with an `action` ring; the chosen Choice's radio holds an
  `action` dot; only the primary button is filled. The Sides box is drawn pressed or not, the
  radio's size, with the tick over it in the same grid cell. `check-previews.py` fails on any other
  `action` fill (74 failures on the old fill), on a Sides box not the radio's size (16, as first
  drawn at the small text's size) and on a tick off its box's centre (8, as first drawn 1.25px
  low; a control that moves the tick out of the box fails all 8). Chromium rounds the font's
  ascent, so a tick sits up to 1px low, within the labels' 1.5px.
- **D27.** Closed: (a), 16 Oct 2026. The `choice` border and its token go.
- **D28.** Closed: (a), 16 Oct 2026. Below the breakpoint, everything in the header but Undo and Redo
  goes into one labelled "More…" menu.
- **D29.** Closed: (b), 16 Oct 2026. Ligatures stay on in prose and go off in the plan line and in
  file names, so data shows as typed.
- **D30.** Closed: (a), 16 Oct 2026 (both options shown as one image). Zoom in and Zoom out beside
  Reset view, a Front · Back · Top Choice at the view's bottom left, the drawing focusable with a
  ring inside the view, turned by the arrow keys and zoomed by `+` and `-` (the tool's script), and
  named as an image described by the plan line. The view lays its controls out in rows, so they
  never overlap and a drag between them reaches the drawing; a short screen's view grows to fit
  them. `check-previews.py` fails on each part: 50 failures on the old Workbench (5 checks on 10
  pages); the drag check 20 (every screen) before the rows let pointers through; controls refused:
  no inside ring (10 of 10), the choice laid over the tools (overlap on 10 of 10), the short-screen
  growth removed (the zoomed screen, 2 of 2). On a landscape phone and at 400 % zoom the controls
  take most of the view.
- **D31.** Closed: (a), 16 Oct 2026. The step rail is optional: one form until it outgrows a screen,
  then the rail, with each step's name shown and announced.
- **D32.** Closed: (a), 16 Oct 2026. A CHANGELOG with migration notes, the version in `tokens.css`
  checked against the tag in CI, and `ws-` names for `tokens.css`'s classes, released as `v0.4.0`.
- **D33.** Closed, 16 Oct 2026: metric is the default and imperial stays optional, for accessibility
  (the owner). DESIGN says so and why. The house rule "metric only" covers this repository's own
  docs, not a setting the tools offer their users.
- **A34.** Closed: yes, 16 Oct 2026, and done on the branch, with D25, D27 to D29, D31 and D32, each
  test-first, each check proved able to fail: the prose and previews agree, with checks against
  drift (`37e53ac`); the build fails on any typed value (`d92f8dc`); live regions, form wiring and
  the stage's contrast (`d6f6089`); the phone stage and the header's More… (`d145f48`); named
  steps, data as typed, no `choice` (`9759bc2`); every icon as wide as it draws (`f8b01f7`); the
  small items (`e4e5e3a`); one version, a changelog and `ws-` names (`3e34699`). What is in
  `v0.4.0` and how a tool moves to it is in `CHANGELOG.md`. Not done: the project layers still live
  in the base files, and CI still runs on both push and pull request.
- **A35.** Closed: (a), 16 Oct 2026: `v0.4.0` is released once D30 is in, so its breaking changes
  come in one release. Its changelog entry is dated, and `build-tokens.py` now refuses a tag on an
  entry still marked unreleased (a new control, 24 of 24 refused). The tag is pushed from the
  owner's machine (a cloud session cannot push tags): T36.
- **T36.** Closed, 16 Oct 2026: `v0.4.0` is tagged on `691bca9` (tag object `30af672`, SSH-signed,
  tagger the owner's no-reply identity, GitHub shows it verified) and released (not a draft or a
  pre-release, the notes as sent), by the admin session on the owner's machine, on the owner's yes
  there; the tag's CI run (58) passed all five jobs, its tag step included. Checked on GitHub by
  this session. The admin session relays that the owner made it standing there: its future tag
  and release requests from this session go ahead without a separate ask, after the same checks
  (relayed). The Skådis Air session has the migration notes.
- **D36.** Closed: (c), 16 Oct 2026 (below). Asked as: the view's controls on a phone, where they crowd the view (on a landscape phone
  39 px of it stays clear). Asked 16 Oct 2026; the owner asked how maps do it, as phone users
  know the gestures. Found, 16 Oct 2026:
  - Apple turns MapKit JS's zoom control off on phones by default (an Apple engineer,
    [forum](https://developer.apple.com/forums/thread/665142)) (relayed); Apple Maps zooms with a
    pinch or a one-finger double-tap and drag
    ([iPhone User Guide](https://support.apple.com/en-asia/guide/iphone/view-maps-iph10d7bdf26/12.0/ios))
    (relayed).
  - Google's Maps JavaScript API shows its zoom and pan control on every map, "the same across
    mobile and desktop devices"
    ([docs](https://developers.google.com/maps/documentation/javascript/controls)) (verified: read).
  - Google's `<model-viewer>`, a 3D viewer, has no zoom buttons: mouse, touch and arrow keys, with
    a prompt "Use mouse, touch or arrow keys to move" ([docs](https://modelviewer.dev/docs/))
    (verified: read its docs data).
  - WCAG 2.5.1 (A) gives this very case as its example: a map that zooms by pinch also has plus and
    minus buttons, for people who cannot pinch (a head pointer, eye gaze, speech); keyboard keys do
    not count ([Understanding 2.5.1](https://www.w3.org/WAI/WCAG22/Understanding/pointer-gestures)).
    2.5.7 (AA) asks the same for dragging
    ([Understanding 2.5.7](https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements))
    (verified: read). Taps alone leave no one-finger way to zoom out: a two-finger tap is
    multipoint, a double-tap and drag is a path.

  Options: (a) everything on screen, as built; (b) no zoom buttons or view choice on a touch
  screen, as Apple does, which fails 2.5.1 and 2.5.7; (c) below the breakpoint and on short
  screens, "Reset view" and "View…", which opens Zoom in, Zoom out and Front · Back · Top as a
  popover, as the header's More… does (D28) (recommended). Shown as a mock, phone upright and on
  its side.

  Done, on the branch, for `v0.5.0`: below the breakpoint and on a short screen the view shows Reset
  view and View…, a native popover anchored under its button, holding Zoom in, Zoom out and Front ·
  Back · Top; a wide screen shows them all, as before. `check-previews.py` checks it (8 failures on
  the D30 layout, the phones and the zoomed screen), on one more screen, a large phone on its side
  (932 × 430, wide and short); controls refused: View… on show on the desktop (2 of 2), the menu
  not anchored (8 of 8), the short-screen collapse removed (the 932 × 430 screen, 2 of 2).
- **A37.** Closed: yes, 16 Oct 2026: `v0.5.0` is released now. The owner asked whether it is large
  enough for a minor version rather than `0.4.1`. It is, as Semantic Versioning counts what a tool
  must do, not size: with the `v0.4.0` markup the new stylesheet stretches the Front · Back · Top
  choice into tall tiles over the view (rendered, phone and desktop), so a tool must change its
  markup to follow. `CHANGELOG.md` now says so: a patch can be copied over with no change to a
  tool's markup or CSS. Released, 16 Oct 2026: tagged on `38b9cae` (tag object `06aec76`,
  SSH-signed, verified on GitHub) and released (not a draft or a pre-release, the notes as sent)
  by the admin session under the standing approval it reports there (relayed); the tag's CI run
  (66) passed all five jobs, its tag step included. Checked on GitHub by this session. The Skådis
  Air session that had the `v0.4.0` notes was archived by then; the new one (asking the owner
  whether to adopt `v0.4.0`) is told to take `v0.5.0`, and `docs/adoption-skadis-air.md` says so.
- **A38.** Closed: yes, 17 Oct 2026, and done on branch `fix/v0.5.1`, each step test-first, each
  check shown failing on the old files and held to controls; `CHANGELOG.md`, v0.5.1, says what a
  tool sees. The wide header's rules apply, and the build fails on a media-query rule undone later
  (`d8aa1c2`). The WebKit menu keeps to its rows, `align-content:start` (the review's flex box was
  measured as wide as the screen), and the build fails on a grid popover without it (`c359c4e`).
  `tests/test-check-previews.sh`, one control per check, in CI (`17b9298`). Rendered states: rings
  and what clips them, hover, selected, disabled, invalid; the header's actions row, a popover the
  browser makes `overflow:auto`, had clipped its rings and scrolled "Dark theme" out of sight at
  896 px (`abdc47d`). More… opened, the phone stage pinned, 44 px touch, ARIA, a 49 px header made
  48 (`75b8243`). Text contrast as drawn, and the build's typed-value holes; every CSS control in
  `tests/test-build-tokens.sh` had been refused by the prefix rule, whatever its own rule did, and
  each now counts only with its own message (`5ec8de1`). Coverage: every class shown and named
  (`c31d804`). Forced colours (`478bda9`). The Dialog and a `scrim` token (`7beb6b3`). Rhythm
  (`334f41f`). The steps from v0.2.0 (`39905a1`): Skådis Air took `v0.3.0` on 15 Oct and `v0.5.0`
  on 16 Oct, so the review's "copies v0.2.0" came from a read of `b55c32d`, before them. The docs
  against the code, re-audited: 17 open, all fixed (`e648111`). Verified only in Chromium, apart
  from the menu, also measured in WebKit 26.0 and Firefox 142 (D40). Left from the review, not in
  A38: the view's focus ring on `model-panel` in dark (1.02:1), a popover left open across the
  breakpoint (the tool's script), no `main` landmark, Gallery and PieceMap without a group name,
  the Dialog's `menu` without items, no hint naming + and −, icons 0.7 to 1.75 px below the
  capitals, two ellipsis forms, More… items centred, `surface-sunken` lighter than `surface-raised`
  in dark, and the fonts' size (theme 11).
- **A50.** Closed: yes, 17 Oct 2026: `v0.5.1` is released as A38 left it, a patch, with D49's
  squeezed name at 896 px known. The entry is dated and the build passes as `--tag v0.5.1`; the
  release commit lands on `main` by fast-forward, and the tag and release go to the admin session
  on the owner's machine. Released, 17 Oct 2026: `main` fast-forwarded to `156bf36` after its CI
  run (39016245908) passed all five jobs; tagged on it (tag object `42ca73e`, SSH-signed, tagger
  the owner's no-reply identity, GitHub shows it verified) and released (not a draft or a
  pre-release, the body equal to the entry) by the admin session under its standing approval
  (relayed); the tag's CI run (39016756053) passed all five jobs. Checked on GitHub by this
  session.
- **D39.** Closed: (a), 17 Oct 2026: the short button label on a phone, with a token for the
  sentence's floor and a check. Built on `feat/piece-mark` (`08f4f49`), in `v0.6.0`
  (unreleased): wherever the plan bar is one row the primary button shows "Download...", the rest
  of its label in a `.ws-plan__long` span hidden from view only, so its name stays whole; the
  ellipsis stays on screen, as DESIGN asks of a button that opens a dialog. The sentence beside
  it, 70 px at 375 px wide and 15 px at 320 before, is 172 and 117 px (Chromium). A new token,
  `plan-line-min` (7rem, 112 px, the largest half rem under the 117 px measured at 320 px), is its
  least width; `check-previews.py` fails a screen where the sentence is narrower (on the old
  markup 375 × 800, 375 × 667, 320 × 256 and 320 × 180, in both themes) and a button whose label
  has a part hidden from screen readers, each with a control. Chromium names the button "Download
  the pieces ..." on every screen, a space between its parts, which speech does not change. The question, the plan sentence on a phone (theme 3): (a)
  A short primary label below the breakpoint ("Download" for "Download the pieces..."), so the
  sentence keeps about two lines of 15 to 25 characters, and a check with a token for its floor
  (recommended; a markup change, so a minor version). (b) A floor for the sentence, the button
  moving under it when there is no room: two pinned rows, a smaller view. (c) As now: the
  sentence for screen readers only.
- **D40.** Closed: (a), 17 Oct 2026: the stated target and `check-previews.py` in Chromium, WebKit
  and Firefox in CI. Built on `feat/piece-mark` (`667c98f`), in `v0.6.0`
  (unreleased): README.md, "Browsers", states the target, what the system relies on and the first
  version of each engine with it; `check-previews.py --browser chromium|webkit|firefox` prints the
  engine and fails if the page's user agent is another's (a control: a copy that always launches
  Chromium, asked for WebKit, is refused); CI's `previews` job runs once per engine, each installing
  only its own, with its own screenshots (`tests/test-workflow.sh`: 4 new checks, 4 new controls).
  First run on `08f4f49`'s files (Windows, Playwright 1.56): Chromium 141.0.7390.37 116 pages,
  0 failing; WebKit 26.0 116 pages, 192 failing; Firefox 142.0.1 116 pages, 30 failing. None was a
  fault in the system; three causes, each in the check's method or a stated fallback: WebKit's
  `focus()` scrolls nothing (192, the focus check on every page that scrolls; its Tab key does
  scroll); Firefox's `focus()` leaves a control partly in sight where it is (4, 'Hung', an unchosen
  radio no Tab stops on, on the 375 × 800 phone); Firefox 142 has no `position-area`, so View…
  opens mid-screen, the fallback (26, every screen with View…). The focus check now scrolls each
  focused control into view, nearest, as Tab does (no change in Chromium; the
  `scroll-padding-top:0` control is still refused in all three engines), and where an engine has no
  `position-area` only the fallback is checked (opens, on the screen, with its items), the run
  saying so. After: 116 pages, 0 failing, in each engine. Run beside the two other engines,
  Firefox once put a step button's capitals 4.5 and 6.5px off centre (2 of 3 loaded runs; none
  of 6 alone): the centring and tick scans now wait two frames after scrolling, before the
  screenshot (0 of 4 loaded runs). Left out outside Chromium, and named in
  each run's output: fonts and hovers (they read through CDP); in WebKit, forced colours (it
  matches the media query but keeps the author's colours, measured). The names check now reads each
  engine's own accessibility tree (WebKit and Firefox read CSS alt text too, measured). WebKit 26.0
  has no `ascent-override` (measured), and every one of the 712 labels is still within 1.5px. Of
  the controls, run locally in WebKit and Firefox: the focus, pinning, 40 % and More… controls are
  refused in both; the View… menu taller than 320 × 180 is refused in WebKit by the "covers the
  view" check (WebKit moves the menu up onto the screen) and passes in Firefox, which never anchors
  it. Found on the way, for the owner: Playwright 1.56's Firefox (142) is older than every Firefox
  in the target but ESR 140 (on 18 Oct 2026 Firefox is 158, ESR 153 and 140, relayed from Mozilla's
  release calendar), so CI checks the ESR fallback, not the anchored menu current Firefox draws;
  Playwright 1.59 is the first with a Firefox from 147 (148.0.2) and 1.64 has Firefox 157, WebKit
  27.2 and Chromium 156 (relayed from its release notes); moving the pin moves Chromium too.
  The question, browsers (theme 5): (a) State a target, the
  current and previous major Safari (iOS too), Chrome and Firefox, and Firefox ESR, and run
  `check-previews.py` in Chromium, WebKit and Firefox in CI (recommended: it would have caught the
  WebKit menu). (b) State the target; check in Chromium only. (c) Neither.
- **D41.** Closed: (a), 17 Oct 2026: a least width for side by side (a token, about 48rem); a
  narrower landscape screen stacks and pins nothing, and the four screens join the checks. Built
  on `feat/piece-mark` (`e2d1831`), in `v0.6.0` (unreleased): the token
  `breakpoint-side-min` (48rem); the four screens and a 720 × 520 window join the checks, where
  the view had been 126, 111, 104 and 16 px (34, 31, 29 and 9 %) and is now 45 % on each; the
  pinned check fails if a stacked landscape screen pins anything (it failed on the window before
  the fix); at 320 × 180 the More… and View… menus ran off the screen and now end at its bottom
  edge and scroll. The question, narrow landscape screens (theme 2): (a) The side-by-side layout also needs
  a minimum width (a token, about 48rem); narrower landscape screens stack, with nothing pinned,
  as a short screen does, so the view keeps 45 % and the page scrolls (recommended). (b) Keep them
  side by side, with the plan and status bars as one row across both columns. Either way
  667 × 375, 740 × 360, 640 × 360 and 320 × 180 join the checked screens.
- **D42.** Closed: (a), 17 Oct 2026: View… opens below the view, and the tool's script closes it
  when a view is picked. Built on `feat/piece-mark` (`c1cc1ad`), in `v0.6.0`
  (unreleased): the open menu is anchored to the view, below it, its right edge under View…'s;
  it covered 19 to 53 % of the view on the ten screens where View… shows and covers none on each;
  `check-previews.py` fails if it covers any of the view, sits above it, leaves its column or runs
  off the screen, and runs the Workbench README's lines for the tool's script on the preview,
  failing if a pick leaves the menu open. Without anchoring it still opens mid-screen (D40). On
  the screens zoomed to 320 px wide the room below the view is short, so it scrolls inside (85 of
  140 px at 320 × 256, 43 at 320 × 180). The question, the open View… menu covers 25 to 44 % of
  the view (theme 8): (a) Open it below the view, over the plan bar, so the part stays in sight
  while zooming, and have the tool's script close it when a view is picked (recommended). (b) Keep
  it under its button.
- **D44.** Closed: (a), 17 Oct 2026, to be built: `/simplify` over `370421e..feat/piece-mark`
  once the others have landed, each cleanup it applies through the full gate and a before-and-after
  pixel comparison of every preview. The question, when and how to run `/simplify` (a cleanup
  pass for reuse and simpler code) on this code: (a) On the changes since `370421e` once A38 was
  settled (recommended). (b) Read-only, applying nothing. (c) Not at all.
- **D47.** Closed: (a) the dot, 17 Oct 2026. Found in A38: a focused, selected PieceMap cell
  differed from a focused, unselected one by colour alone (1.13:1), as a cell's bold says it has
  its own fill (`data-own`). The owner first chose a mark in the cell, written as the Sides box's
  tick; a tick means pick several (D26) and a piece is one of a pick-one, so it was built with the
  chosen radio's dot, shown beside the tick on a page, and the owner chose the dot. Built on
  `feat/piece-mark` (`38012a9`), in `v0.5.2` (unreleased, a patch): `check-previews.py` fails on
  a selected cell with no mark, a mark on a cell not selected, and the two alike in forced colours.
- **D49.** Closed: (c), 17 Oct 2026. Found in A38: at 896 px the wide header's row left the
  tool's name 80 of its 141 px in the Workbench preview and 20 px ("W…") beside the version in the
  Header preview. The owner first chose (a), a least width with the version going into More…;
  measured before building, a wide screen hides More…, so desktops would lose the version for 80 px
  ("Window…") at 896 px. Asked again with three ways, shown live on a page, the owner chose (c):
  the header keeps its phone row (More…) below a width of its own, `breakpoint-header` (64rem, a
  new token), so in the previews the name and the version are whole at every checked width from
  56rem, and on windows 56 to 64rem wide Reset, Save, Load and the theme toggle sit behind More….
  Built on `feat/piece-mark` (`eb40069`), in `v0.5.2` (unreleased, a patch: the files copied
  over; since renamed `v0.6.0`, a minor, for D39): `check-previews.py` fails if the name is cut from 56rem up (it failed 5
  times on the old stylesheet) and checks the header's row on a new 1,024 px screen;
  `build-tokens.py` fails on a header rule at the layout's breakpoint.
- **D51.** Closed: (a), 17 Oct 2026. Built with D39, on `feat/piece-mark` (`08f4f49`), in
  `v0.6.0` (unreleased): below `breakpoint-header` the version tag is in the More…
  menu, after the actions, not in the row; from it, beside the name. The markup carries a second
  copy in `.ws-header__actions`, and the copy not on show is `display:none`, so a screen reader
  hears one version (on a phone, in the open menu). A header without More… keeps its version in
  its row. `check-previews.py` fails if the row holds a version below `breakpoint-header` (on the
  old markup, all 15 checked screens narrower than 64rem, in both themes: the name 65 of 120 px at
  375 px wide, 10 at 320, whole on the wider ones) and if more or fewer than one shows, each with a
  control. Found after D49 (c): on a phone the
  header's name is cut, by the version tag and Undo and Redo's labels. Measured on `eb40069`, of
  120 px: Header preview (with version) 10 at 320 px, 50 at 360, 65 at 375, 104 at 414; Workbench
  preview (no version) 66 at 320, 106 at 360, whole from 375. (a) The version tag goes into More…
  on a phone (a markup change, in v0.6.0 anyway): the Header preview then matches the Workbench
  (recommended). (b) Undo and Redo icon-only on a phone, labels kept for screen readers: whole
  from 360 px, but breaks the rule that every icon sits beside a text label. (c) Both. (d) As now.
- **D52.** Closed: (a), 17 Oct 2026, built on `feat/piece-mark` (`537aea8`), in
  `v0.6.0` (unreleased): a short screen (`breakpoint-short` or less tall) goes side by side only
  from `breakpoint-side-short`, a new token, 61rem (976 px); narrower, it stacks and pins nothing,
  the view at 45 %. Its value is swept, not guessed: on `c1cc1ad` (Chromium, 360, 375, 390, 400,
  430 and 470 px tall, mouse and touch, every 8 px from 768 to 1,280 and every 1 px from 956 to
  980) the widest side-by-side short screen under 40 % was 964 px (37 % at 360 tall, 39 % at 375);
  after the change no short screen side by side is under 40 %, the narrowest, 976 × 360, at 47 %.
  So the 844 × 390 and 932 × 430 phones held sideways, side by side before at 41 and 47 %, now
  stack too, at 45 %. `check-previews.py` draws 800 × 360 (touch), a 900 × 400 window (mouse) and
  976 × 360 (`breakpoint-side-short`); on the old stylesheet the first two failed (111 px, 31 %;
  139 px, 35 %). `build-tokens.py` fails if the side-by-side query lets a short screen through.
  The question, as asked: found after D41 (a) (`e2d1831`), short landscape screens from
  48rem up to 960 px wide still go side by side, and there the view gets under D25's 40 %,
  measured in Chromium on `e2d1831`: 360 px tall, 28 to 37 % from 768 to 960 px (mouse) and 31 to
  37 % (touch; 800 × 360, a common phone held sideways, 31 %); 390 tall, 33 to 39 % up to 912
  (mouse), 36 to 37 % (touch); 400 tall, 35 to 40 % up to 912 (mouse), 38 % (touch); 430 tall,
  39 % at 880 to 896 (mouse only); none at 480. The plan bar wraps to two or three rows (134 to
  160 px) in the narrow stage column, and with a mouse the status bar's hint wraps to two lines
  (56 px against 41). The checked 844 × 390 touch screen gets 41 %, so no check caught it. (a) A
  short screen stacks unless it is at least about 61rem (976 px) wide, pinning nothing, the view
  at 45 %, as below 48rem (recommended; CSS and a token). (b) Keep side by side and shrink the
  bars on a short screen (the sentence to two lines, the hint to one); not measured. (c) As now.
  Either way 800 × 360 (touch) and a 900 × 400 mouse window join the checked screens.
- **D53.** Closed: (b), 17 Oct 2026: leave it; the menu scrolls inside on the two screens zoomed to
  320 px wide. Found after D42 (`c1cc1ad`): on the two screens zoomed to 320 px wide there is
  little room below the view, so the open View… menu (140 px) scrolls inside: 85 px shows at
  320 × 256 and 43 px at 320 × 180 (80 px under its button before). (a) Fall back to its old place,
  under its button over the view, only where it does not fit below (CSS; the check allows covering
  the view only then). (b) Leave it scrolling inside (recommended).
- **D54.** Closed: (b), 18 Oct 2026, built on `feat/piece-mark` (`b770659`; its edge controls made
  to hold in Linux's Chromium in `db45587`, and this record in `2083e11`), in `v0.6.0`
  (unreleased): side by side for any short screen at least 904px wide and 408px tall
  (`breakpoint-side-size-w`, 56.5rem, by `breakpoint-side-size-h`, 25.5rem, two new tokens), on size
  alone, whatever the pointer. First measured on Chromium 141 (worst case a 904 × 408 mouse window
  at 40.7 %), then swept again on the new engines (D55) before it was built: a pixel apart, 768 to
  1,280px wide by 360 to 480px tall, a mouse and touch, 124,146 screens in each of Chromium 156,
  WebKit 27.2 and Firefox 157, by `scripts/sweep-side-by-side.py`, new, with its test
  (`tests/test-sweep-side-by-side.sh`, 8 controls, 8 refused); on Windows the three engines agree
  within 0.06px, and in CI, on Linux, WebKit's and Firefox's sweeps match Windows' to the pixel.
  Linux's Chromium sets the bars' text narrower: there the plan bar's extra row falls at 872 to
  887px, every short screen keeps 40 % from 896px wide by 378px tall, and the worst side by side,
  904 × 408 with a mouse, gets 44.3 %, so the rule holds there with more to spare (CI run
  39103604975). The numbers below are Windows'. The boundary did not move: from 901px wide every
  short screen keeps 40 % from 403px tall, while from 877 to 900px the plan bar takes one more row
  (its bars 260.7px tall with a mouse) and would need 434px; so the decided values, the next half
  rem up, stand, with 3 and 5px to spare. Worst case after, in all three: a 904 × 408 mouse window,
  the view 166.2px, 40.7 %; 84,594 of the 124,146 screens side by side, 0 under 40 %. On the
  Workbench preview, before and after (Chromium, WebKit and Firefox alike): 932 × 430 stacked at 45
  %, now side by side at 47.2 %; 915 × 412 44.9 %, 926 × 428 46.9 %, 956 × 440 48.4 %, 904 × 408
  40.7 %, all stacked at 45 % before; 844 × 390, 900 × 408 and 904 × 400 still stack, at 45 %.
  `check-previews.py` draws 904 × 408 and two mouse windows that stack, 900 × 408 and 904 × 400
  (side by side 36.1 and 39.5 %; in Linux's Chromium 44.3 and 43.2 %, so the first CI run,
  39102537505, failed two controls that expected the 40 % check to refuse them there: they now
  expect the layout check, which refuses them everywhere, `db45587`), and fails if a checked screen
  puts the sidebar anywhere but where its decision says (`SIDE_BY_SIDE`): on the old stylesheet 932
  × 430 and 904 × 408, 4 failures in two themes; controls 89 of 89 refused (84 before), among them
  844 × 390 side by side, which keeps 41 % and so passes every other check. `build-tokens.py` fails
  if the side-by-side query lacks the clause (43 of 43 controls refused, 42 before). Asked again on
  17 Oct 2026, with the sweep; first answered (b), 17 Oct 2026, to be built after D39 and D51: side
  by side again where a short screen keeps 40 %, a height-aware rule from a measured sweep. Found
  after D52 (`537aea8`): with `breakpoint-side-short` at 61rem, every phone held sideways stacks,
  844 × 390 and 932 × 430 included, which had kept the view at 41 % and 47 % side by side; stacked,
  the short screen pins nothing, so the part scrolls out of sight while a value is changed. (a) Keep
  it. (b) Side by side again where a short screen keeps 40 % (a height-aware rule from a measured
  sweep) (recommended). (c) Shrink the bars on short side-by-side screens instead; not measured.
- **D55.** Closed: (c), 18 Oct 2026, built on `feat/piece-mark` (`2d2b8a6`), in `v0.6.0`
  (unreleased): the pin moves to Playwright 1.64.0 (`pyproject.toml`, `uv.lock`, only Playwright
  moved), whose engines report Chromium 156.0.8078.4, WebKit 27.2 and Firefox 157.0 (read from the
  installed browsers; the relayed numbers were right). CI installs the engine from the lock
  (`uv run --locked python -m playwright install`), so it follows with no change to the workflow.
  Before, on Playwright 1.56 (Windows, the files of `667c98f`): 116 pages, 0 failing, in each of
  Chromium 141, WebKit 26.0 and Firefox 142. First run on 1.64: the check stopped on its first page,
  as Playwright 1.64 has no `page.accessibility`, which the names check read, in any engine.
  Fixed in the check: Chromium's names come from its own tree through CDP
  (`Accessibility.getFullAXTree`, which the old call read), WebKit's and Firefox's from Playwright's
  reading of the page (`aria_snapshot`), as Playwright reads no other engine's tree now; the run
  names that gap ("tree"). Then Chromium 156 and WebKit 27.2: 116 pages, 0 failing; Firefox 157:
  2 failing and a reload that timed out, in one run, and 1 failing in the next, all on the 320 ×
  180 and 932 × 430 Workbench, one cause, the check's: Firefox 157 moves the page a pixel back by
  itself one to three frames after `scrollIntoView` (167 to 166px, measured), so a label's place,
  read two frames after the scroll, was a pixel off its screenshot, its border inside the scan: a
  step button's capitals read 4.5 and 6.5px off centre (5 of 20 fresh launches on one page). The
  label and mark scans now read the control's place again after the screenshot and scan again if
  it moved (0 of 300 scans off in 20 launches, 4 scanned again). The 'Undo' outside the window and
  the reload timeout came once, on the page that failed, and not again in four full runs.
  After: 116 pages, 0 failing, in each engine. Firefox anchors the View… menu: `anchored 26`
  (0 on Firefox 142), so the anchored-menu checks run in all three engines, and no job draws the
  fallback (D60). Controls: 84 of 84 refused in Chromium 156; the two names controls refused in
  WebKit 27.2 and Firefox 157 too, through Playwright's reading; of the six View… controls, WebKit
  27.2 refuses all six with their own messages, and Firefox 157 five (three of them need an
  anchored menu, which Firefox 142 never drew) and the sixth, the menu taller than 320 × 180, by "covers
  98 % of the view", as Firefox moves it up onto the screen, as WebKit 26.0 did. What each engine supports, measured: Firefox 157 emulates a phone (`is_mobile`;
  a page with no viewport tag is 980px wide on a 375px phone, as in Chromium and WebKit), so the
  check's Firefox exception goes; WebKit 27.2 has `ascent-override` (FontFace; 26.0 had none);
  WebKit 27.2 still keeps the author's colours in forced colours, so that is still skipped there;
  the focus check still needs its scroll into view (without it, WebKit 27.2 fails 194 times and
  Firefox 157 4, as 26.0 and 142 failed 192 and 4). README.md, "Browsers", the check's comments and
  its "not checked" lines say so. Measured beside 1.56 on 32 pages (the Workbench and Header
  previews on every screen, light): Chromium 156 moves no number: the view 47.4 % at 976 × 360
  (`breakpoint-side-short`), 45 % on every stacked screen, the plan sentence 171.6px at 375px wide
  and 116.6px at 320 (`plan-line-min` 112px), the header's name whole from 56rem. WebKit 27.2 moves
  to Chromium's numbers on the four side-by-side screens (976 × 360: the view 174 to 170.6px, 48.3 to
  47.4 %; 960 × 800: 578 to 572.9px), likely from `ascent-override`; Firefox moves only the menu,
  now below the view. Found on the way: installing 1.64's engines deleted 1.56's from the shared
  browser folder, so a checkout still on 1.56 needs `playwright install` again; and a shell with
  `BROWSER` set to a web browser's command (an agent's has `BROWSER=true`) fails every preview
  control (D61).
- **D56.** Closed: (a), 18 Oct 2026, built on `feat/piece-mark` in the commit after `f82b4e3`, in
  `v0.6.0` (unreleased): `Stepper`, a number field with two Buttons after it, ↓ and ↑, modelled on
  Skådis Air's (`ab4b630`, `web/src/form.ts` `numberField`, its C253). Markup: `label.ws-label`
  naming the field by its `id` (inside a label, the buttons' names would join the field's), then
  `div.ws-stepper` with the Field's `input.ws-input` (`inputmode="decimal"`; `data-step`,
  `data-min`, `data-max`, `data-on-step`) and two `button.ws-btn.ws-stepper__btn`, reading ↓ and
  ↑ (U+2193, U+2191, in the font's subset, checked with fontTools and by the font check), named
  `Smaller <label>` and `Larger <label>`. DESIGN.md says an arrow with a name is the button's text,
  not an icon. CSS, tokens only: a flex row, `gap` `space-1`, the buttons `space-2` inline padding
  and at least `control-h` wide (27px wide at the padding alone, under the 44px touch size), and
  stretched to the field's height, as a field is 37.3px with a mouse and a button 36: centred,
  their edges missed the field's by 0.64px; so a Stepper's buttons are "at least `control-h`"
  in the height check, and check 33 holds them to the field's top and bottom (D62). The field
  gives way on a narrow sidebar (`flex:1 1 auto; min-width:0`); the Workbench preview's track
  width is a Stepper, so the row is checked on every screen, 320px wide among them. A
  `type="number"` field in one loses its spin buttons: `appearance:textfield` hides them in
  Firefox, the `::-webkit-` spin buttons' rule in Chromium and WebKit, neither alone in all three
  (measured); the check reads the first, as the second has no computed style. At a limit the
  button says so with `aria-disabled="true"`, chosen over `disabled`: a focused button that
  becomes disabled loses its focus in Firefox 157, to the page (Chromium 156 and WebKit 27.2 keep
  it; measured); `.ws-btn[aria-disabled=true]` is drawn as a disabled Button, no hover. The
  behaviour is the README's lines for the tool's script. `check-previews.py` check 33 (the parts,
  names, label, width and line-up) and check 34 (the README's lines run on the previews: ↑ and ↓
  pressed, ArrowUp and ArrowDown as real key presses in the field as it is and switched to
  `type=number`, where the browser steps as well unless stopped; a step, onto the steps, a comma,
  the limits and their `aria-disabled`, one `input` event per change and none at a limit, below
  zero from 0, and the spin buttons). The units check reads a field's labels, so a Stepper's
  `for` label still counts. Written first and run on the stylesheet before with the README's lines
  left out: 123 failing on the Stepper preview (light, a phone and a desktop, Chromium 156): 99 of
  the lines' kind, 18 of the markup's, 4 of `aria-disabled`'s states, 2 of coverage. After: 132
  pages, 0 failing, in each of Chromium 156, WebKit 27.2 and Firefox 157 (128 before); the preview
  controls 126 of 126 refused (100 before), the 26 new each with its own message. D56 to D59 come
  from Skådis Air's report to this repository (its A255, 18 Oct 2026).
- **D57.** Closed: (a), 18 Oct 2026, built on `feat/piece-mark` (`f82b4e3`), in
  `v0.6.0` (unreleased): `hidden` always hides anything the system styles. The cause: the
  browser's own `[hidden]{display:none}` loses to any class that sets a display, by order at equal
  specificity and by specificity otherwise. One rule in `bundle.css`,
  `[hidden]:not([hidden=until-found i]){display:none !important}`: `!important`, as the wide View…
  menu's `display:contents` (`.ws-stage__menu:not(:popover-open)`, as specific and later) and the
  header's version (three classes) beat it otherwise; `until-found` keeps the browser's meaning.
  `check-previews.py` (check 31) gives every HTML element of every page the attribute in turn and
  fails if its display is not `none` (a `display:contents` box has no box of its own but draws its
  children). Written first and run on the old stylesheet: 112 failing on the 30 light pages of a
  phone and a desktop (Chromium 156), every Choice among them; with the rule, 0 of 1,014 elements.
  The full run after: 128 pages, 0 failing, 5,632 elements given the attribute, in each of Chromium
  156, WebKit 27.2 and Firefox 157; the preview controls 100 of 100 refused (89 before). Two
  controls: the rule left out (a hidden Choice drawn, `display flex`) and the rule without
  `!important` (the wide View… menu drawn, `display contents`). The Choice README shows a switch
  between groups ("Boards | Connectors" above one Choice per group, the others `hidden`) with the
  lines a tool's script needs; run once in Chromium, they hide the other list and bring back the
  type last chosen in each group. Skådis Air's report: its A255, C253 and C179.
- **D58.** Closed: (a), 18 Oct 2026, built on `feat/piece-mark` (`f82b4e3`), in
  `v0.6.0` (unreleased): `theme-init.js`, a file of the system (MPL-2.0 in `REUSE.toml`), which a
  tool loads first in its head, `<script src="theme-init.js" data-key="skadis-air-theme"></script>`,
  so a content security policy without `'unsafe-inline'` runs it. It sets `data-theme` to the theme
  stored under the key `data-key` names (`printable-parts-theme` without one), `"light"` or
  `"dark"`, Skådis Air's key and values; with nothing stored, another value, or storage missing or
  refused, to the system setting's, as Skådis Air's own did. The brief said to leave `data-theme`
  unset there, to follow the system; but `tokens.css` themes the page through `data-theme` alone
  (light without it, no `prefers-color-scheme` rule), so a dark system would get a light first
  paint, and DESIGN.md has whatever follows the theme watch `data-theme`. Built with the system's
  setting; the session that relayed the decision agreed (18 Oct 2026). The key comes from the
  script tag, as a shared file cannot carry one tool's name. `check-previews.py` (check 32, `--device
  theme` alone) serves a page from a reserved name (`example.test`, an origin as a tool's page has)
  and runs eight cases in fresh contexts, storage seeded before any script
  or made to throw: stored dark, stored light, nothing stored on a dark and on a light system, an
  unknown value, storage refused on a dark and on a light system, and a key of the tool's own; it
  fails if `data-theme` is not the case's when the script has run, before the stylesheet is read,
  if the page is first drawn in another `color-scheme`, or if the script throws. 8 of 8 in
  Chromium 156, WebKit 27.2 and Firefox 157. On the brief's version (unset with nothing stored) 5
  of 8 fail, on Skådis Air's own file 3 of 8 (its key, no `data-key`). Nine controls, each refused
  with its own message: stored dark ignored, stored light ignored, the system ignored,
  `data-theme` left unset, an unknown value kept, a setter that throws on refused storage, one that
  sets the theme on `DOMContentLoaded` (after the first paint), `data-key` ignored; and the file
  missing. DESIGN.md, "Light or dark" and "Reference implementations", points to it; README's
  adoption steps copy and load it.
- **D59.** Closed: (a), 18 Oct 2026, built on `feat/piece-mark` (`f82b4e3`), in
  `v0.6.0` (unreleased): the Disclosure README documents a toggle that must sit in a row of
  buttons (Skådis Air's "Show all files" beside "Download all"): a `button.ws-btn` with
  `aria-expanded` and `aria-controls`, its section `hidden` while closed, and the lines for the
  tool's script that flip both; run once in Chromium, they do. No new CSS.
- **D60.** Open, found in D55, 18 Oct 2026: two fallbacks in the target that no CI job draws any
  more. The View… menu without anchoring, as Firefox ESR 140 shows it (last checked in Firefox 142:
  it opens on the screen with its items); and labels without `ascent-override`, as every released
  Safari draws them (MDN lists it in Safari Technology Preview only; last measured in WebKit 26.0:
  all 712 labels within 1.5px). Firefox 157 keeps anchoring with
  `layout.css.anchor-positioning.enabled` off (measured), so no preference brings the old menu
  back. (a) Accept: README.md, "Browsers", states both, with their last measurements. (b) A
  fallback pass in the check, one more CI job: render the previews with the
  `@supports (position-area…)` block and `ascent-override` taken out of copies of the stylesheets, as a
  browser without them reads them (recommended: the fallbacks stay checked, a change to the check
  and the workflow). (c) Keep Playwright 1.56 beside 1.64 for one job: a second lock; not
  recommended.
- **D61.** Open, found in D55, 18 Oct 2026: `tests/test-check-previews.sh` takes its engine from
  `BROWSER`, the variable many tools read as the command for a web browser; an agent's shell here
  has `BROWSER=true`, so every control failed with "invalid choice: 'true'" until run as
  `BROWSER=chromium`. README.md says so now. (a) The test refuses a `BROWSER` that names no engine,
  with that hint, and a control (recommended). (b) Rename it (`ENGINE`) in the test, the workflow
  and the docs. (c) Leave it, as documented.
- **D62.** Open, found in D56, 18 Oct 2026: a field is taller than a button with a mouse, 37.3px
  against `control-h`'s 36 (its line, 22.5px, and `field-pad-y` twice, 6.4px each, and its
  border), in Chromium 156, WebKit 27.2 and Firefox 157 alike; on a touch screen both are 44. A
  Stepper's buttons take the field's height, so they line up either way. (a) Derive a field's
  block padding from `control-h` and its line, as `.ws-summary` does, so every input is exactly
  `control-h` tall and `field-pad-y` goes (recommended: one height for every control; every field
  1.3px shorter with a mouse, a change a tool sees). (b) Leave it.
- **Build order** (18 Oct 2026): D49 (c), D41, D42, D52, D39 with D51, D40, D55, D54, D57 with D58
  and D59, D56, D44. D39 changes a tool's markup, so the next version is `v0.6.0`, a minor.
