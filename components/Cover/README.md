# Cover

Cover art for Parametric window sealer, 960 × 288 px: the wall of printed pieces in the model colours (`model-panel`, `model-joint`, `model-tape`, `model-tpu`), the tool's name and one line on what it does.

It is artwork for use outside the tool: the design system's gallery card, the repository's social preview, a README banner. It is drawn at a fixed size and does not reflow, so it is never placed in the tool itself, whose first screen is the workbench and its welcome dialog. For that reason `scripts/check-previews.py` skips its overflow checks on the phone, and lets its preview carry its own styles.
