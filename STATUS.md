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

## Next

1. `v0.6.0`'s tag and GitHub release, once CI is green on `main` with the repository public
   (A76); then Skådis Air is told. Release immutability stays off (D77).
2. D75: the plan bar on one row beside the sidebar, and one derived height in place of the three
   swept side-by-side breakpoints, measured first; a version after `v0.6.0`.

## Open questions

None.

## Releases and tags

- **Making a release.** Date the version's entry in `CHANGELOG.md`; `build-tokens.py --tag vX.Y.Z`
  must pass; land the release commit on `main` by fast-forward once CI is green on it. A cloud
  session cannot push tags, so the admin session on the owner's machine makes the signed tag and
  the GitHub release, under the owner's standing approval (T36); then check both on GitHub.
- **Releases here start at `v0.6.0`** (D74). This repository holds the tags `v0.1.0` and `v0.2.0`
  on the rewritten history (A66); the owner's self-hosted forge holds all six earlier tags,
  `v0.1.0` to `v0.5.1`, re-signed. The releases of `v0.4.0` to `v0.5.1` stay in the private archive
  repository, `AlonRR/printable-parts-design-system-archive` (D73); `v0.3.0`'s was deleted (A72).
  Their notes are in `CHANGELOG.md`.
- **A released tag is for good.** With GitHub's immutable releases on, a released tag cannot be
  moved, and once deleted its name cannot be created again under the repository's name, even in a
  new repository (A72). Release only a commit that is final.
- **Commit IDs** in the documents name the rewritten commits. Commit messages from before
  18 Oct 2026, and CI runs from before then, use the IDs they were written with.
- **CI** cannot start jobs on this repository while it is private (T63); until it is public, the
  local gate in `CLAUDE.md` is the check.
