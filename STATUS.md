# Status

Where the work stands. Every decision cited here is in [`docs/decisions.md`](docs/decisions.md);
what each version changed for a tool is in [`CHANGELOG.md`](CHANGELOG.md).

## In progress: v0.6.0 (unreleased)

Built on the branch `feat/piece-mark`, in this order:

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

D39 and D51 change a tool's markup, so the version is a minor one.

## Left before the release

1. D61 with D65: the preview controls read `PREVIEW_ENGINE`, and CI pins `ubuntu-24.04`.
2. D60: a fallback pass in `check-previews.py`, and one more CI job.
3. D68: every field exactly `control-h` tall.
4. D69: the `Select` component.
5. D44: the `/simplify` pass over the changes since `11a868d`, with a pixel comparison of every
   preview before and after.
6. `v0.6.0`: date its changelog entry, land it on `main`, tag and release it; then the repository
   goes public (D70).

## Open questions

None.

## Releases and tags

- **Making a release.** Date the version's entry in `CHANGELOG.md`; `build-tokens.py --tag vX.Y.Z`
  must pass; land the release commit on `main` by fast-forward once CI is green on it. A cloud
  session cannot push tags, so the admin session on the owner's machine makes the signed tag and
  the GitHub release, under the owner's standing approval (T36); then check both on GitHub.
- **Releases here start at `v0.6.0`** (D74). This repository holds the tags `v0.1.0` and `v0.2.0`
  on the rewritten history (A66). `v0.3.0` to `v0.5.1` are tagged on the owner's self-hosted
  forge; the releases of `v0.4.0` to `v0.5.1` stay in the private archive repository,
  `AlonRR/printable-parts-design-system-archive` (D73). Their notes are in `CHANGELOG.md`.
- **A released tag is for good.** With GitHub's immutable releases on, a released tag cannot be
  moved, and once deleted its name cannot be created again under the repository's name, even in a
  new repository (A72). Release only a commit that is final.
- **Commit IDs** in the documents name the rewritten commits. Commit messages from before
  18 Oct 2026, and CI runs from before then, use the IDs they were written with.
- **CI** cannot start jobs on this repository while it is private (T63); until it is public, the
  local gate in `CLAUDE.md` is the check.
