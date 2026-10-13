# Prompt for a Claude Code cloud session

Paste everything below the line. Attach `printable-parts-design-system.zip` to the session (or put the unzipped folder in the working directory) first.

---

You are setting up a new repository from the folder `printable-parts-design-system` (unzip `printable-parts-design-system.zip` if it came as a zip). It is the shared design system for two of my browser tools that generate 3D-printable parts: Parametric window sealer (AlonRR/parametric-window-sealer) and Skådis Air (AlonRR/skadis_ultralight_generator). Read `README.md`, `DESIGN.md` and `FONTS.md` in it first.

**Do, in this order. Plan first, then build; ask me before anything outside this list.**

1. **Verify the folder as it is.** `pip install -r requirements.txt`, then run `python3 scripts/build-tokens.py` and `python3 scripts/check-contrast.py`. Both must pass, and `git diff` of `tokens.css` after the build must be empty. If either fails, find the cause and fix it at the source (`tokens.json`, `bundle.css` or the script), never by hand-editing `tokens.css`.
2. **Open every `components/*/preview.html` in a headless browser** (Playwright with Chromium), loading `tokens.css`, then `components/bundle.css`, with `data-theme` set to `light` and then `dark`. Screenshot each. Check: no missing-glyph boxes (icons and the radio mark render), text is vertically centred in buttons, the chosen Choice button shows a filled button with an inverted radio, nothing overflows at 375px wide. Fix real defects at the source and tell me what you changed.
3. **Create the repository.** `git init`, branch `main`, one commit per concern (design system files; CI), a private GitHub repo named `printable-parts-design-system` under AlonRR, push. If you cannot create it (no permission or no `gh` auth), stop and tell me exactly what is needed; do not look for another way to push. Do not choose a licence: leave the README note as it is.
4. **Confirm CI passes** on the first push (`.github/workflows/check.yml`). If it fails, fix the cause and push again.
5. **Report**: the repo URL, what CI did, what you fixed in step 2, and anything in `FONTS.md` marked "to be confirmed" that you were able to verify from the upstream licence files (link them). Do not change the licence statements on your own.

**Rules for this work**

- Fix causes, not symptoms. No per-component nudges (no magic padding or margins to line things up); change the token, the variable or the font setup, and extend the checks in `scripts/` so the same mistake fails the build next time.
- No value is typed twice: colours, sizes, gaps and type come from `tokens.json`; `bundle.css` reads variables only and contains no hex colours.
- One typeface (FiraCode Nerd Font), Codicons for icons, always beside a text label and `aria-hidden`. Pick-one options are `Choice` buttons with a radio mark; ticks mean pick-several.
- Metric units in any wording you write.
- Do not open pull requests or push to the two tool repositories. If you think they should adopt this system, write the proposed steps in your report instead.
- Do not add secrets, tokens or credentials to any file.
- Keep your report short: outcome first, then what I need to do, if anything.
