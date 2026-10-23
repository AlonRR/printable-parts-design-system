# Status

Where the work stands. Every decision cited here is in [`docs/decisions.md`](docs/decisions.md);
what each version changed for a tool is in [`CHANGELOG.md`](CHANGELOG.md).

## v0.6.0 (19 Oct 2026)

Built on the branch `feat/piece-mark` and landed on `main` with its release commit (A76), in this
order:

- D49: the header keeps its phone row up to `breakpoint-header` (64rem).
- D41, D52 and D54: when a landscape or short screen puts the sidebar beside the stage.
- D42: the open View… menu sits below the 3D view.
- D39 with D51: the short primary label on a phone, and the version tag in More….
- D47: a selected PieceMap cell shows the radio's dot.
- D40 and D55: the browser target, and the previews checked in Playwright 1.64's Chromium,
  WebKit and Firefox.
- D57, D58 and D59: `hidden` always hides, `theme-init.js`, and the Disclosure toggle pattern.
- D56: the `Stepper` component.
- A66 with A71: the history rewritten and re-signed.
- D70: the documentation clean-up (this document, `docs/decisions.md`, the README and
  `DESIGN.md` rewritten, the finished working documents removed).
- D61 with D65: the preview controls read `PREVIEW_ENGINE`, never `BROWSER`, and every CI job runs
  on `ubuntu-24.04`.
- D60: `check-previews.py --fallbacks`, the View… menu without anchoring and labels without the
  font-metric overrides, and a CI job that runs it in WebKit.
- D68 (`8649fc0`): every field exactly `control-h` tall, its block padding derived from it;
  `field-pad-y` gone.
- D69: the `Select` component, the native `<select>` with a chevron from the font.
- D44: the `/simplify` pass over the changes since `11a868d`, in two commits: (a), `88a15ed`, the
  stylesheet and tokens, and (b), the commit after it, the checks and their tests. Neither changes
  a pixel of any preview, in any engine, nor what any check catches; `scripts/compare-shots.py`
  compares the screenshots.

D39 and D51 change a tool's markup, so the version is a minor one.

## v0.7.0 (21 Oct 2026)

Built on the branch `feat/piece-mark` and landed on `main` with its release commit (A81):

- D75 with D79 (a): beside the sidebar the plan bar keeps one row, its sentence at most two
  lines beside the short label, and the status bar one row, its hint cut short; one height H,
  derived from the bars' tokens by `build-tokens.py` (16.5rem), replaces `breakpoint-side-short`,
  `breakpoint-side-size-w` and `breakpoint-side-size-h`, and `plan-line-basis` goes.
  `sweep-side-by-side.py` now sweeps that rule. No markup changes; four tokens leave
  `tokens.css`, so the version is a minor one. The numbers are in `docs/decisions.md` (D75).

## v0.8.0 (21 Oct 2026)

The owner's answers of 21 Oct 2026 to an audit of `v0.7.0` against interface design and
engineering practice, built on the branch `fix/audit-findings`, one commit each, and landed on
`main` with its release commit (A92), in this order:

- A86 and D87: the More… menu's items line up, their icons in one column, and picking one closes
  it, with lines the Header README gives a tool's script. A tool adds those lines, so the version
  is a minor one.
- A86: the plan sentence says it is an example first, in a sentence that shows whole on every
  screen.
- D89: an ellipsis is the one character `…` in every label; a tool changes its labels.
- D90: dark `surface-sunken` is darker than `surface`, the surfaces' depth order checked in every
  theme.
- D91: a tool relies on `tokens.css`'s custom properties; `tokens.json` is the source.
- D88 (a): the icons raised onto their labels' capitals by `--icon-rise`, which the build derives
  from the font, and checked on the pixels in every engine.

## v0.8.1 (unreleased)

Skådis Air's request for two components (its A319), and the owner's answers of 23 Oct 2026,
built on the branch `feat/help-and-busy`, one commit each, and landed on `main` with its release
commit (A96). Neither changes what a tool must do, so the version is a patch:

- D94 (a): `Help`, a field's help folded behind an "i" beside its label, the one button whose
  icon stands alone, checked by `check-previews.py` check 36.
- D95 (a): the busy ring over a part being rebuilt, the system's one motion and one gradient,
  held by `build-tokens.py` rule 11 and `check-previews.py` check 37; and the build refuses a
  typed percentage, which it never did.

## Next

1. D80: measure whether a landscape screen narrower than `breakpoint-side-min` (48rem), such as
   740 × 360 or 667 × 375, can go side by side with one-row bars, the 3D view's width as well as
   its height; after `v0.8.1`.

The preview control "code in the browser's monospace" let a mistake through once in CI's Chromium
on Linux (run 39225004789, first attempt). The cause: `HIDDEN_JS` takes every box out and puts it
back just before the font walk, and `CSS.getPlatformFontsForNode` reads the layout as it stands
without making one, so a box not laid out yet reported no font, which read as no fallback. Right
after `HIDDEN_JS` the Dialog's `<code>` reported no font in 97 of 100 runs, none of 100 when laid
out first; CI's walk counted 2921 to 3356 nodes on the same files. The walk now lays the page out
first, and fails a run where an element with text of its own reads no font; a control that hides
the body at that step, standing in for the race, passes the old check and is refused by the new.
`icon_names` also reads right after `HIDDEN_JS`, through the accessibility tree, and has no such
race: in fresh pages of Icons, Button and Workbench, 0 of 300 reads right after it differed from a
laid-out read or came back empty, in each of Chromium 156, WebKit 27.2 and Firefox 157, and the
Header with an icon read aloud was caught in 100 of 100; with the body hidden at that step, as a
stale read would look, 100 of 100 reads differed in each engine, so the probe could see one.

`v0.6.0` was released on 19 Oct 2026 (A76): the release commit `020baf0` on `main`, the
repository made public, CI green on `main` in all 8 jobs (run 39225004789, its second attempt;
the first passed all but the control above), the signed tag (tag object `3a339bc`, verified on
GitHub) and the GitHub release, its notes the changelog entry, not immutable (D77). Skådis Air's
session was told, with the steps.

`v0.7.0` was released on 21 Oct 2026 (A81): the release commit `3d07f0a` on `main`, CI green on
it in all 8 jobs (run 39555652844), the signed tag (tag object `1741082`, verified on GitHub) and
the GitHub release, its notes the changelog entry, not immutable (D77). Skådis Air's session was
told, with the steps.

`v0.8.0` was released on 21 Oct 2026 (A92): the release commit `47a45a2` on `main`, CI green on
it in all 8 jobs (run 39645376384), the signed tag (tag object `c655f87`, verified on GitHub) and
the GitHub release, its notes the changelog entry, not immutable (D77). The owner sent the tag
script's command (T93), as for `v0.7.0`. Skådis Air's session was told, with the steps: for it,
copying `tokens.css` and `components/bundle.css`.

## Open questions

None.

## Releases and tags

- **Making a release.** Date the version's entry in `CHANGELOG.md`; `build-tokens.py --tag vX.Y.Z`
  must pass; land the release commit on `main` by fast-forward, and tag it once CI is green on it.
  A cloud session cannot push tags, so a session on the owner's machine makes the signed tag and
  the GitHub release (the admin session under the owner's standing approval, T36, or the session
  he approves it for, as A76); then check both on GitHub. On the owner's machine the auto-mode
  check can refuse the tag push as a new public surface even with the owner's approval, as it did
  for `v0.7.0`: write the tag and release steps as one script under `build/`, and the owner sends
  its exact command as a message, which the check lets through (T82).
- **Releases here start at `v0.6.0`** (D74). This repository holds the tags `v0.1.0` and `v0.2.0`
  on the rewritten history (A66), `v0.6.0`, `v0.7.0` and `v0.8.0`; the owner's self-hosted forge
  holds all six earlier tags, `v0.1.0` to `v0.5.1`, re-signed. The releases of `v0.4.0` to
  `v0.5.1` stay in the private archive repository, `AlonRR/printable-parts-design-system-archive`
  (D73); `v0.3.0`'s was deleted (A72). Their notes are in `CHANGELOG.md`.
- **A released tag is for good.** With GitHub's immutable releases on, a released tag cannot be
  moved, and once deleted its name cannot be created again under the repository's name, even in a
  new repository (A72). Release only a commit that is final.
- **Commit IDs** in the documents name the rewritten commits. Commit messages from before
  18 Oct 2026, and CI runs from before then, use the IDs they were written with.
- **CI** runs on every push since the repository went public (19 Oct 2026); while it was private,
  GitHub refused every job for a billing reason (T63), and the local gate in `CLAUDE.md` was the
  check.
