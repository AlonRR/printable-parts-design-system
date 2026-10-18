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
  31 % on an 800 × 360 phone.
- **D53** (17 Oct 2026): On the two screens zoomed to 320px wide, the open View… menu scrolls
  inside itself. Why: there is little room below the view there, and over the view it would hide
  the part (D42).
- **D54** (18 Oct 2026): A short screen also goes side by side from `breakpoint-side-size-w` by
  `breakpoint-side-size-h` (904 × 408), on its size alone, values taken from a sweep of every
  short screen. Why: after D52 every phone held sideways stacked, and the part scrolled out of
  sight while a value changed; from that size side by side keeps the view at 40 %.

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
- **D68** (18 Oct 2026, to be built): A field's block padding is derived from `control-h` and its
  line, so every input is exactly `control-h` tall, and `field-pad-y` goes. Why: with a mouse a
  field is 37.3px against a button's 36.
- **D69** (18 Oct 2026, to be built): A `Select` component, the native `<select>` drawn from
  tokens; `Choice` for up to about seven short options, `Select` for longer lists. Why: a long
  list, such as printer models, had no control.

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
- **D44** (17 Oct 2026, to be built): A `/simplify` cleanup pass over the changes since `11a868d`
  once the other work has landed, each cleanup through the full gate and a before-and-after pixel
  comparison of every preview. Why: one cleanup once the features settle, proved to change
  nothing a tool sees.
- **D55** (18 Oct 2026): Playwright is pinned at 1.64, whose engines are Chromium 156, WebKit 27.2
  and Firefox 157. Why: 1.56's Firefox 142 was older than every Firefox in the target but ESR 140,
  so CI checked a fallback instead of the menu current Firefox draws.
- **D60** (18 Oct 2026, to be built): A fallback pass in `check-previews.py` and one more CI job,
  rendering the previews with the `position-area` block and `ascent-override` taken out. Why:
  since D55 no engine CI runs draws two fallbacks still in the target, Firefox ESR 140's View…
  menu and Safari's labels.
- **D61** (18 Oct 2026): The preview controls take their engine from `PREVIEW_ENGINE`, not
  `BROWSER`, in the test, the workflow and the docs. Why: many tools read `BROWSER` as a web
  browser's command, and a shell with `BROWSER=true` failed every control. Built: the test runs
  one control again in a shell with `BROWSER=true`, and `test-workflow.sh` refuses `BROWSER` in
  the workflow.
- **D65** (18 Oct 2026): CI pins `ubuntu-24.04`. Why: `ubuntu-latest` moves to a new image, and
  Linux's text widths already moved D54's measured edge; a move is its own step, with the sweep
  run on it. Built: every job, and `test-workflow.sh` refuses `ubuntu-latest`.
