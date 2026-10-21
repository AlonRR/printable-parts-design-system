# Decisions

The record of every closed decision, approval and question in this repository: what was
decided, when, and why. The rules themselves live in [`DESIGN.md`](../DESIGN.md), the component
READMEs and the checks; this page is where an ID cited in them resolves. What is still to be
built is in [`STATUS.md`](../STATUS.md).

Each ID's letter says what was asked: **A** an approval for an action, **D** a decision between
options, **Q** a question only the owner could answer, **T** a step the owner carried out. The
numbers are one pool across the letters (36 was given twice, as T36 and D36); a number missing
here was not used in this repository.
An ID cited with an owner ("Skådis Air's A255") belongs to that repository, not to this one.

- [Repository and process](#repository-and-process)
- [Licences and fonts](#licences-and-fonts)
- [Versions and releases](#versions-and-releases)
- [Publishing and the history rewrite](#publishing-and-the-history-rewrite)
- [Adoption in the tools](#adoption-in-the-tools)
- [Layout and the workbench](#layout-and-the-workbench)
- [Controls and visual rules](#controls-and-visual-rules)
- [Checks, browsers and CI](#checks-browsers-and-ci)

## Repository and process

- **Q1** (14 Oct 2026): Python runs through uv only; `pyproject.toml` and `uv.lock` replace
  `requirements.txt`, and CI and the docs use `uv run`. Why: one locked environment, the same
  locally and in CI.
- **Q2** (13 Oct 2026): `main` was reset to a rebuilt history. Why: the first commits carried the
  platform's default identity, attribution trailers and unscoped subjects.
- **Q5** (14 Oct 2026): `main` moves only by fast-forward pushes, and is GitHub's default branch.
  Why: a forge's merge button makes the forge the committer.
- **D20** (15 Oct 2026): Skådis Air's commit hooks and CI checks are taken in, adapted only where
  this repository differs. Why: one set of conventions across the owner's repositories, changed
  in one place.
- **T22** (15 Oct 2026): The owner set the repository variables `EXPECT_EMAIL` and `EXPECT_NAME`,
  which CI's identity check compares every pushed commit against.
- **A23** (15 Oct 2026): `CLAUDE.md` carries the reply rules of the owner's session starter:
  question IDs, a list of open items, and a line saying what was recorded where. Why: the same
  rules as every other repository the owner works in.

## Licences and fonts

- **Q6** (14 Oct 2026): The licence texts and credits of the fonts and icons ship in
  `fonts/licenses/`, byte for byte from upstream. Why: the subsets carry no licence inside the
  font, and the OFL accepts the notice as a file beside it.
- **D8** (14 Oct 2026): MPL-2.0 for code, CERN-OHL-S-2.0 for documentation, the fonts under their
  own licences, in the REUSE layout; `reuse lint` runs in the gate and in CI. Why: the same split
  as the tools that use the system.
- **D9** (14 Oct 2026): The fonts ship once, as files that `tokens.css` loads; `bundle.css` holds
  no font, and the build fails if one comes back. Why: embedded as base64 they made `bundle.css`
  453 KB; without them it is 10 KB.
- **D24** (15 Oct 2026): `fonts/licenses/README.md` names `FONTS.md` and this repository in plain
  text, and the build fails on a link out of `fonts/` or to this repository. Why: a tool copies
  `fonts/` alone, where such a link leads nowhere.

## Versions and releases

- **T14** (14 Oct 2026): The owner tagged `v0.1.0`. Why: a cloud session cannot push tags.
- **T16** (14 Oct 2026): The owner tagged `v0.2.0`, with D15's tokens.
- **T21** (15 Oct 2026): `v0.3.0` was tagged and released from the owner's machine, with D18,
  D19, D20 and D24.
- **D32** (16 Oct 2026): One version, in `tokens.json`, `tokens.css` and `pyproject.toml`; a
  changelog with migration notes; the version checked against the tag in CI; a `ws-` prefix on
  every class. Why: a tool that copies the files must know what changed and how to follow.
- **A35** (16 Oct 2026): `v0.4.0` is released once D30 is in, and the build refuses a tag on an
  entry still marked unreleased. Why: its breaking changes reach a tool in one release.
- **T36** (16 Oct 2026): `v0.4.0` was tagged and released from the owner's machine. Later tag and
  release requests from this repository go ahead there under a standing approval, after the same
  checks.
- **A37** (16 Oct 2026): `v0.5.0` is a minor version, not `v0.4.1`. Why: versions count what a
  tool must do, not the size of the change, and with the `v0.4.0` markup its stylesheet draws the
  view choice over the 3D view.
- **A50** (17 Oct 2026): `v0.5.1` is released as A38 left it, a patch, with D49's cut-off name
  known. Why: its fixes need no change to a tool's markup.
- **A76** (19 Oct 2026): `v0.6.0` is released: its entry dated, the release commit landed on
  `main` by fast-forward, the repository made public, CI waited for on `main`, then the signed tag
  and the GitHub release, and Skådis Air told. Why: the build order (D47 to D44) is complete.
- **D77** (19 Oct 2026): Release immutability stays off in this repository. Why: a release can
  still be corrected, the signed tags already prove what each release holds, and an immutable
  release reserves its tag name for good (A72).
- **A78** (19 Oct 2026): A standing approval for sessions on the owner's machine and cloud sessions
  to push to this repository now that it is public: feature branches, and `main` by
  fast-forward only, never force, with the push secret gate where there is one. Why: the
  repository is worked on from GitHub, and every other public remote stays the owner's to push
  to.
- **A81** (21 Oct 2026): `v0.7.0` is released as `v0.6.0` was: its entry dated, the release commit
  landed on `main` by fast-forward, CI waited for on `main`, then the signed tag and the GitHub
  release, and Skådis Air told. Why: D75 with D79 is built and checked, and CI passed on the
  branch (run 39277085902, 8 of 8 jobs).
- **T82** (21 Oct 2026): The owner sent the command that tagged and released `v0.7.0`. Why: the
  auto-mode check on the owner's machine refused the tag push as a new public surface, and lets a
  command the owner sends through.

## Publishing and the history rewrite

- **D62** (18 Oct 2026): Rewrite the history before the repository goes public. Why: the owner's
  machine's hostname was in 4 commit messages and 36 old versions of `STATUS.md`, and before the
  first public push a rewrite costs least.
- **T63** (18 Oct 2026): GitHub Actions refused every job on this private repository for a
  billing reason. The owner chose to make the repository public, where GitHub's standard runners
  are free, rather than change billing.
- **A66** (18 Oct 2026): The history was rewritten with `git filter-repo`, the hostname replaced
  in every commit message and every version of every file, and every commit and tag re-signed
  with the owner's key; each of the 87 commits was paired with its original and checked before
  any push. Commit IDs in the docs name the rewritten commits; older commit messages keep the IDs
  they were written with.
- **A71** (18 Oct 2026): A66 redone from the untouched mirror, with the push gate's
  `secret-gate: allow` comment on the base64 font line in the 7 old versions of
  `components/bundle.css` that hold it. Why: that line matches a key pattern by chance, a false
  positive; nothing else changed.
- **A72** (18 Oct 2026): Moving the release tags `v0.3.0` to `v0.5.1` onto the rewritten commits
  failed. GitHub's immutable releases lock a released tag, and once such a tag is deleted, GitHub
  refuses to create that tag name again under the repository's name, even in a new repository
  and with immutable releases off.
- **D73** (18 Oct 2026): The old repository was renamed `AlonRR/printable-parts-design-system-archive`
  and kept private, with the old history and its `v0.4.0` to `v0.5.1` releases; a new repository
  took the name, with the rewritten history and the tags `v0.1.0` and `v0.2.0`. Why: the released
  tag names could not be moved (A72).
- **D74** (18 Oct 2026): This repository's releases start at `v0.6.0`. `v0.3.0` to `v0.5.1` are
  tagged on the owner's self-hosted forge, re-signed, and their notes are in `CHANGELOG.md`. Why:
  GitHub refuses those four tag names here (A72).
- **D70** (18 Oct 2026): The repository goes public once the documentation clean-up and `v0.6.0`
  are on `main`. Why: a public reader should meet finished documents and a current release.

## Adoption in the tools

- **Q7** (14 Oct 2026): Skådis Air adopts the system first. Why: one tool at a time; the second
  copies what the first built.
- **D10** (14 Oct 2026): For Skådis Air, `Choice` buttons for the board type. Why: pick-one
  options are buttons with a radio mark, all in sight.
- **D11** (14 Oct 2026): For Skådis Air, a dark theme with a toggle in the header. Why: the system
  has both themes, and the user chooses.
- **D12** (14 Oct 2026): For Skådis Air, the introduction in the sidebar. Why: the stage keeps the
  screen for the part.
- **D13** (14 Oct 2026): For Skådis Air, one form before numbered steps. Why: a short tool needs no
  steps (see D31).
- **Q17** (14 Oct 2026): The Skådis Air session was told of D15 and to copy from `v0.2.0`.
- **D18** (15 Oct 2026): What Skådis Air had added to the system in its own page moved into the
  system: `color-scheme` per theme, `ws-page`, the warning Notice, the stage's canvas contract,
  the mouse and touch hints, and the plan bar's parts. Why: a rule every tool needs belongs in the
  system, not in one tool's page.
- **D19** (15 Oct 2026): `DESIGN.md` links Skådis Air's theme, framing and copy code and its
  browser test as the reference implementations, pinned to one commit; no TypeScript moves here.
  Why: the code stays in the tools, and the next tool copies from a known version.
- **D64** (18 Oct 2026): `theme-init.js` reads its storage key from `data-key` on its script tag,
  `printable-parts-theme` without one. Why: each tool keeps its own key, and a choice already
  stored still holds.
- **D91** (21 Oct 2026): A tool relies on `tokens.css`'s custom properties, never on `tokens.json`,
  which is the source (a); not `tokens.json` too, with a version of its own layout (b). Why: a tool
  copies `tokens.css` and not `tokens.json`, yet the README sent tools to `tokens.json` for the
  model colours, and nothing said whether its layout could change. Neither tool reads it: Skådis
  Air reads its model colours from the page, through `getComputedStyle`. Built (`v0.8.0`): the
  README and DESIGN.md say what a tool can see, and point the model colours at the `--model-*`
  properties.

## Layout and the workbench

- **Q3** (14 Oct 2026): The covers are fixed-size art for use outside the tools, and the phone
  checks skip them. Why: they never appear in a tool, so they need not reflow.
- **Q4** (14 Oct 2026): Inputs, selects, PieceMap cells and Disclosure summaries are at least
  `control-h` tall: 36px with a mouse, 44px on a touch screen. Why: every control is a touch
  target.
- **D15** (14 Oct 2026): The part always fits the stage: framed to `stage-fit` when it or its size
  changes, the angle kept and the camera pulled back on a resize, zoom out stopping at
  `stage-min-fill`, no panning off the stage, and Reset view back to the first view. Why: the part
  is what the page is for, and must never be lost off the screen.
- **D25** (16 Oct 2026): On a phone the 3D view alone gets 45 % of the screen, pinned, with the
  plan bar pinned under it as one row and Reset view over the view; the status bar scrolls; a
  landscape phone goes side by side; a short screen pins nothing. Why: the plan and status bars
  inside the stage left the view 0 to 71px.
- **D28** (16 Oct 2026): Below a width, everything in the header but Undo and Redo goes into one
  labelled More… menu. Why: the full row does not fit a phone.
- **D30** (16 Oct 2026): The 3D view works without a pointer: Reset view, Zoom in and Zoom out, a
  Front · Back · Top choice, and a focusable drawing that the arrow keys turn and + and − zoom,
  named and described by the plan line. Why: WCAG 2.1.1 and 2.5.7; every gesture has a press.
- **D31** (16 Oct 2026): The step rail is optional: one form until it outgrows a screen, then the
  rail, each step's name shown beside its number and announced. Why: a short tool needs no steps,
  and a number alone says nothing.
- **D36** (16 Oct 2026): On a phone and a short screen the view shows Reset view and View…, a menu
  holding Zoom in, Zoom out and Front · Back · Top; a wide screen shows them all. Why: the view
  stays clear for pinch and drag, and WCAG 2.5.1 still gets a press for everyone who cannot.
- **D39** (17 Oct 2026): Wherever the plan bar is one row, the primary button shows a short label
  ("Download..."), the rest hidden from view only, and the sentence beside it keeps
  `plan-line-min`. Why: beside the full label the sentence had 15px at 320px wide.
- **D41** (17 Oct 2026): A landscape screen goes side by side only from `breakpoint-side-min`
  (48rem); narrower, it stacks and pins nothing. Why: side by side, a 740 × 360 phone left the
  view 111px, 31 % of the screen.
- **D42** (17 Oct 2026): The open View… menu sits below the view, over the plan bar, and the
  tool's script closes it when a view is picked. Why: under its button it covered 25 to 44 % of
  the view.
- **D49** (17 Oct 2026): The header keeps its phone row, with More…, below its own width,
  `breakpoint-header` (64rem). Why: from the layout's breakpoint the full row left the tool's
  name 20 to 80px.
- **D51** (17 Oct 2026): Below `breakpoint-header` the version tag is in the More… menu, not in the
  row. Why: beside the name it cut a phone's name to 10 of 120px.
- **D52** (17 Oct 2026): A short screen goes side by side only from `breakpoint-side-short`
  (61rem); narrower, it stacks. Why: below it the plan bar wrapped and the view fell under 40 %,
  31 % on an 800 × 360 phone. Replaced by D75 in `v0.7.0`.
- **D53** (17 Oct 2026): On the two screens zoomed to 320px wide, the open View… menu scrolls
  inside itself. Why: there is little room below the view there, and over the view it would hide
  the part (D42).
- **D54** (18 Oct 2026): A short screen also goes side by side from `breakpoint-side-size-w` by
  `breakpoint-side-size-h` (904 × 408), on its size alone, values taken from a sweep of every
  short screen. Why: after D52 every phone held sideways stacked, and the part scrolled out of
  sight while a value changed; from that size side by side keeps the view at 40 %. Replaced by D75
  in `v0.7.0`.
- **D75** (19 Oct 2026, after `v0.6.0`): Keep the plan bar on one row when the sidebar sits beside
  the stage, and replace the three swept side-by-side breakpoints with one derived height,
  measured first. Why: the breakpoints (D52, D54) work around the bar wrapping in the stage's
  column, and their values move with each engine's and system's text widths. Found by D44's
  review. Built (19 Oct 2026, `v0.7.0`, with D79 (a)): beside the sidebar the plan bar keeps the
  phone's row and the status bar one row, its hint cut with an ellipsis, so the bars are one
  height on every screen side by side (48, 62.7 and 41px with a mouse, 48, 69 and 41px on touch,
  in Chromium 156, WebKit 27.2 and Firefox 157); and a screen goes side by side from
  `breakpoint-wide`, or landscape from `breakpoint-side-min`, and either way from H tall, which
  `build-tokens.py` derives from the bars' tokens, touch setting it at 16.5rem (264px).
  `plan-line-basis`, `breakpoint-side-short`, `breakpoint-side-size-w` and
  `breakpoint-side-size-h` are gone. Swept a pixel apart, 700 to 1,280px wide and 240 to 480px
  tall, 140,021 screens a pointer: in each engine and pointer every screen goes side by side as
  the rule says, the bars are one row of one height, and none side by side gives the view under
  40 %, the worst 768 × 264 at 40.2 % on touch and 42.5 % with a mouse. Against
  `v0.6.0`, 39,744 screens a pointer go from stacked to side by side (768 to 975 × 264 to 479,
  phones held sideways from 800 × 360 among them), and 7,320 the other way, 976 to 1,280 × 240 to
  263, where side by side left the view 21 to 35 %.
- **D79** (19 Oct 2026): Beside the sidebar the plan bar's sentence keeps two lines, as on a phone
  (a), not three. Why: three would show 57 characters at 768px wide instead of 34, and need H
  18rem, so fewer screens side by side.
- **D80** (21 Oct 2026): Measure first whether a landscape screen narrower than
  `breakpoint-side-min` (48rem) can go side by side, the 3D view's width as well as its height,
  for a version after `v0.7.0` (a). Why: D41's reason was the wrapping plan bar, and with one-row
  bars (D75) the bars fit from about 631px wide, so 740 × 360 and 667 × 375, phones held sideways,
  could go side by side; but the stage beside the sidebar would be only about 300 to 370px wide.
- **A86** (21 Oct 2026): Two fixes that need no decision, from an audit of `e6668f4` (`v0.7.0`)
  against interface design and engineering practice, before D80: the More… menu's items line up,
  their icons in one column, and the plan sentence's example leads it. Why: centred, the menu's
  four icons started up to 33.5px apart on a phone; and the sentence's last words are the first
  the two-line clamp cuts. Built (`v0.8.0`): the menu's buttons start their content at their edge,
  and `check-previews.py` fails if the open menu's icons start more than 0.5px apart; the
  Workbench preview's sentence starts "Example wall.", and `check-previews.py` fails a screen where
  the plan sentence's first sentence is cut. "Example wall: replace the sizes with yours." first
  was still cut on the two 320px screens, two lines of about 14 characters, so the example says so
  in a sentence of its own.
- **D87** (21 Oct 2026): Picking an action in the More… menu closes it (a), with lines the Header
  README gives a tool's script, as View… closes on a pick (D42); not left open (b). Why: open, it
  covers up to a third of the 3D view on a phone, and Reset's change happened behind it. The Dark
  theme toggle closes it too, and the new theme shows at once. Built (`v0.8.0`):
  `check-previews.py` runs the lines on every preview with More… and picks each action in turn;
  on the `v0.7.0` files all four picks left it open, on the Header and Workbench previews.

## Controls and visual rules

- **D26** (16 Oct 2026): Every selected state is `action-tint` with an `action` ring; the chosen
  radio holds an `action` dot; only the primary button is filled; the Sides box is drawn pressed
  or not, at the radio's size. Why: the one filled thing on a screen is the next step, and a
  selection never relies on colour alone.
- **D27** (16 Oct 2026): The `choice` border and its token go. Why: every Choice has a default, so
  none needs an unchosen colour.
- **D29** (16 Oct 2026): Ligatures stay on in prose and go off in inputs, numbers, the plan line
  and file names. Why: data shows exactly as typed.
- **D33** (16 Oct 2026): Metric is the default, and imperial stays an option in the tools. Why:
  accessibility, for people who read inches more easily. The rule "metric only" covers this
  repository's own documents.
- **D47** (17 Oct 2026): A selected PieceMap cell shows the chosen radio's dot. Why: focused, a
  selected and an unselected cell differed by colour alone (1.13:1); a piece is one of a pick-one,
  and a tick means pick several.
- **D56** (18 Oct 2026): A `Stepper` component: a number field with ↓ and ↑ Buttons, the lines a
  tool's script needs, and checks. Why: from Skådis Air's report; a phone's decimal keypad has no
  minus sign, and ↓ reaches below zero.
- **D57** (18 Oct 2026): The `hidden` attribute hides anything the system styles. Why: the
  browser's own `[hidden]` rule loses to any class that sets a display.
- **D58** (18 Oct 2026): `theme-init.js`, a file of the system loaded first in the head, sets
  `data-theme` from the stored choice, or else the system setting. Why: `tokens.css` themes
  through `data-theme` alone, so a dark system would get a light first paint; and a file runs
  under a content security policy without `'unsafe-inline'`.
- **D59** (18 Oct 2026): The Disclosure README shows a toggle Button for a row of buttons
  (`aria-expanded`, `aria-controls` and `hidden`), with no new CSS. Why: a `details` summary
  cannot sit in a row of buttons.
- **D68** (18 Oct 2026): A field's block padding is derived from `control-h` and its line, so
  every input is exactly `control-h` tall, and `field-pad-y` goes. Why: with a mouse a field is
  37.3px against a button's 36. Built in `8649fc0`: the padding is what `control-h` leaves of the
  line and the border, so a field is 36px with a mouse in Chromium 156, WebKit 27.2 and Firefox 157, and 44px
  on touch as before; `check-previews.py` holds every field and a Stepper's buttons to exactly
  `control-h`.
- **D69** (18 Oct 2026): A `Select` component, the native `<select>` drawn from tokens; `Choice`
  for up to about seven short options, `Select` for longer lists. Why: a long list, such as
  printer models, had no control. Built in the commit after `8649fc0`: a `select.ws-input` with
  `appearance: none` in a `span.ws-select`, whose `::after` draws the Codicon `chevron-down` from
  the font in a `control-h` square over the select's end, letting a press through, with empty
  alternative text. Why the font's glyph: it is text, so it takes `ink` and the user's colours in
  forced colours, where an image or a mask drawn with a background would not. `check-previews.py`
  check 35 measures the chevron on the pixels.
- **D88** (21 Oct 2026): Raise every icon onto its label's capitals by the font's own offset,
  through one token, checked on the pixels in every engine (a); not accept the offsets (b), unless
  the engines round that fraction of a pixel away. Why: the font centres its icons 88.5 of its
  1,950 units under its capitals, so they sat 0.5 to 0.75px low in WebKit and Firefox and 1 to
  1.75px in Chromium; left open since A38. Built (`v0.8.0`): `build-tokens.py` derives
  `--icon-rise` (0.0454em) from the font, the Codicons' median centre (600 units, as in every set
  measured: all 1,216 icon glyphs, the 408 Codicons, the 68 the previews use) against half the cap
  height; `.ws-ic` is raised by `top`, which Chromium draws a whole pixel, where `translate`
  moved it half and left it 1.25px low. Over every screen the previews are drawn on, 244 icons an
  engine, an icon now sits within 0.75px of its capitals in Chromium 156 and 0.5px in WebKit 27.2
  and Firefox 157, and within 1px in the fallback pass, where the bold primary button's icon went
  from 0.5px high to 1px. `check-previews.py` holds it to 1.25px: Chromium can place the baseline and
  the icon's box a pixel apart, and the scan steps a quarter pixel. Left low, Chromium reads 1.75px
  on 12 of 14 icons, and fails.
- **D89** (21 Oct 2026): An ellipsis is the one character `…` in every label (a), the menus' form,
  not three full stops (b). Why: a phone showed "Download..." beside More… and View…, two forms
  for one meaning, and three full stops take three of the monospace font's cells where `…` takes
  one. Built (`v0.8.0`): the Button and Workbench previews and the docs that give a label;
  `check-previews.py` fails three full stops in a preview, or in what a doc tells a tool to write,
  outside its code blocks of script, where a spread is code. A tool changes its labels.
- **D90** (21 Oct 2026): The dark surfaces keep light's depth order (a), the well
  (`surface-sunken`) darker than the page (`surface`) and the page than a panel
  (`surface-raised`); not kept as it was (b). Why: in dark the well was the lightest surface,
  relative luminance 0.023 against the panel's 0.014, so a drawing area read as raised. Built
  (`v0.8.0`): dark `surface-sunken` is `#0c1217` (0.0057), its step down from the panel 1.155:1, as
  light's is 1.153:1, rather than light's step from the page, which gave a near-black `#05080a`;
  `check-contrast.py` fails the order in any theme, held to two controls.

## Checks, browsers and CI

- **A34** (16 Oct 2026): The first review's fixes, with D25 to D33, each test-first and each check
  shown able to fail, released as `v0.4.0`: the docs and previews agree, the build fails on any
  typed value, live regions announce, the phone stage, named steps, data as typed, every icon as
  wide as it draws.
- **A38** (17 Oct 2026): The second review's fixes that need no decision, released as `v0.5.1`:
  the wide header's rules, the WebKit menu, every check held to a control, rendered states,
  forced colours, the dialog's scrim and the vertical rhythm. Left out of it: the view's focus
  ring on `model-panel` in dark (1.02:1), a popover left open across the breakpoint, no `main`
  landmark, Gallery and PieceMap without a group name, the Dialog's `menu` without items, no hint
  naming + and −, icons 0.7 to 1.75px below the capitals, two ellipsis forms, More… items
  centred, `surface-sunken` lighter than `surface-raised` in dark, and the size of the fonts.
- **D40** (17 Oct 2026): A stated browser target, the current and previous major versions of
  Safari (iOS too), Chrome and Firefox, and Firefox ESR; `check-previews.py` runs in Chromium,
  WebKit and Firefox in CI. Why: a WebKit-only fault, `v0.5.0`'s full-screen View… menu, passed a
  Chromium-only check.
- **D44** (17 Oct 2026, built 19 Oct): A `/simplify` cleanup pass over the changes since
  `11a868d` once the other work has landed, each cleanup through the full gate and a
  before-and-after pixel comparison of every preview. Why: one cleanup once the features settle,
  proved to change nothing a tool sees. Built in two commits. (a), `88a15ed`, the cleanups of the
  stylesheet and tokens that keep behaviour: one rule each for the hover tint (a selector list, not `:is()`, so each keeps its
  weight), the selected look and its bold, which leaves the PieceMap cell out (D47), and
  `.ws-sr` with `.ws-plan__long`; D68's padding from one derived token, `control-pad-y`; the touch
  `control-h` as the token's touch value, written by the build, so `bundle.css` sets no custom
  property; and two dead declarations gone (`font:inherit` before `.ws-tile`'s `font`, `font-family`
  before `.ws-workbench`'s). The radio mark's rules were already one each and stay: folding the
  PieceMap cell's own `display` into the Choice radio's would change that radio's computed
  `vertical-align`. The proof: 544 screenshot pairs, the same pixel for pixel in Chromium, WebKit,
  Firefox and the fallback pass, and a dump of every computed style and box in every preview in
  Chromium, at rest, each control hovered and focused, a step both current and done, and a control
  marked `aria-disabled` (2.9 million values; the same between two runs of the old tree). Only the
  new token and that last hover differ: the strictest guard now holds for every control.
  Screenshots cannot show a hover or a state no preview draws, so the dump is what proves those.
  (b), the commit after `88a15ed`, the cleanups of the checks and their tests, each check catching
  what it caught. In `check-previews.py`: one `rem_px()` for every screen size read from a
  breakpoint, and each screen carrying where its sidebar goes, so `SIDE_BY_SIDE`, its drift guard
  and that guard's control go (146 preview controls, from 147); the layout check's findings keyed
  by the name each prints under, read in one loop, and its counts taken from the lists its checks
  read; one in-page prelude, `window.ck`, installed in every context, for the helpers the page
  functions had copied (an element's class and name, shown and visible, a Choice's face, a label's
  own words, the probes for a colour, a length and `control-h`, the two-frame wait, colour
  parsing), the stricter copy kept where they differed: an SVG element's class read through
  `baseVal`, a label's words joined with a space and the white space folded (the units check
  joined them with none), and the parser that refuses a colour it cannot read (the forced-colour,
  mark and centring checks read any numbers in it); one `steady()`, a screenshot until the
  control stops moving, for the labels, marks and chevrons; the hover check in three trips to the
  page per control, not six; a Stepper press one trip shorter; and the chevron's last read without
  a scroll. `sweep-side-by-side.py` takes `rem_px()` and the prelude from it. `build-tokens.py`
  parses `bundle.css`'s rules once, their declarations as pairs (`content` is declared twice in
  three rules), `@font-face` among them, and prints the side-by-side query and its size-only part
  (`--query`), which the tests now read instead of typing; `tests/controls.sh` holds the copy,
  judge, css, sub and gone helpers of three tests; and `test-check-previews.sh` leaves out its base
  run under `PREVIEWS_CHECKED=1`, which the gate and CI's Chromium job set right after the full
  check. Left as it was: the focus check names an SVG child of the drawing `rect.[object`, as a
  control's matched line does. The proof: each control's matched lines the same before and after
  (146 preview controls, 45 build, 5 contrast, 8 sweep, and the workflow test's 16), each engine's
  summary and the sweep's the same in Chromium, WebKit and Firefox, but for Chromium's count of
  nodes drawn in a font, which differs between runs of one tree (3604, 3609 and 3658 for
  `88a15ed`), and 544 screenshot pairs the same in every channel (`scripts/compare-shots.py`). That script replaces the comparison (a) was
  proved with, which went through Pillow's `getbbox()` on RGBA: it reads only the alpha channel,
  so it could not see a colour change in an opaque screenshot. Run again with the new one, (a)'s
  544 pairs are the same.
- **D55** (18 Oct 2026): Playwright is pinned at 1.64, whose engines are Chromium 156, WebKit 27.2
  and Firefox 157. Why: 1.56's Firefox 142 was older than every Firefox in the target but ESR 140,
  so CI checked a fallback instead of the menu current Firefox draws.
- **D60** (18 Oct 2026): A fallback pass in `check-previews.py` and one more CI job,
  rendering the previews with the `position-area` block and `ascent-override` taken out. Why:
  since D55 no engine CI runs draws two fallbacks still in the target, Firefox ESR 140's View…
  menu and Safari's labels. Built: `--fallbacks` takes out `descent-override` and
  `line-gap-override` too, as Safari reads none of the three (MDN), and the CI job runs it in
  WebKit, where alone it measures the labels: Chromium without the overrides draws them up to 2px
  high, which no browser in the target does.
- **D61** (18 Oct 2026): The preview controls take their engine from `PREVIEW_ENGINE`, not
  `BROWSER`, in the test, the workflow and the docs. Why: many tools read `BROWSER` as a web
  browser's command, and a shell with `BROWSER=true` failed every control. Built: the test runs
  one control again in a shell with `BROWSER=true`, and `test-workflow.sh` refuses `BROWSER` in
  the workflow.
- **D65** (18 Oct 2026): CI pins `ubuntu-24.04`. Why: `ubuntu-latest` moves to a new image, and
  Linux's text widths already moved D54's measured edge; a move is its own step, with the sweep
  run on it. Built: every job, and `test-workflow.sh` refuses `ubuntu-latest`.
- **A85** (21 Oct 2026): Pillow goes from 12.3.0 to 13.0.0 in `uv.lock`, in a commit of our own
  landed by fast-forward. Dependabot's pull request is not merged: GitHub would be the committer,
  and CI's identity check refuses its author. Why: GitHub raised 9 security alerts on Pillow
  12.3.0 on 21 Oct (1 critical, 6 high, 2 medium), all fixed in 13.0.0. Only the checks use it,
  `check-previews.py` and `compare-shots.py`, on screenshots they take themselves; nothing a tool
  copies changes, so there is no release.
