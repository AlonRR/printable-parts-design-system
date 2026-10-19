#!/usr/bin/env python3
"""Compare two folders of screenshots pixel for pixel: the proof that a change drew nothing new (D44).

Run from the project folder:  uv run python scripts/compare-shots.py BEFORE AFTER
Needs: pillow (pyproject.toml; uv run installs it).

Every file under BEFORE is paired with the one at the same path under AFTER, as check-previews.py
--out writes them (one per preview, theme and device). A pair is the same when both images have one
size and mode and no channel of any pixel differs, alpha included. The run fails (exit 1) if a pair
differs, if a file is in one folder only, or if there is nothing to compare: an empty folder, or a
wrong path, would pass everything. It prints the counts, then each difference.

Pillow's getbbox() reads only the alpha channel of an image that has one (alpha_only, its default),
so the difference of two opaque images, which is transparent everywhere, has no box however its
colours differ: a comparison through RGBA that way finds nothing. Here every channel is read.
tests/test-compare-shots.sh holds each failure to a control.
"""
import argparse, pathlib, sys
from PIL import Image, ImageChops

def files(folder):
    return {p.relative_to(folder).as_posix() for p in folder.rglob("*") if p.is_file()}

def differs(before, after):
    """Why two images are not the same, or None."""
    with Image.open(before) as a, Image.open(after) as b:
        if a.size != b.size or a.mode != b.mode:
            return f"{a.size[0]} x {a.size[1]} {a.mode} before, {b.size[0]} x {b.size[1]} {b.mode} after"
        box = ImageChops.difference(a.convert("RGBA"), b.convert("RGBA")).getbbox(alpha_only=False)
        return None if box is None else f"pixels differ from {box[0]},{box[1]} to {box[2]},{box[3]}"

def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("before", type=pathlib.Path, help="the screenshots before the change")
    ap.add_argument("after", type=pathlib.Path, help="the screenshots after it")
    args = ap.parse_args()
    for folder in (args.before, args.after):
        if not folder.is_dir():
            print(f"FAIL {folder} is not a folder\n1 failing")
            return 1
    before, after = files(args.before), files(args.after)
    pairs = sorted(before & after)
    bad = [f"{name}: {why}" for name in pairs if (why := differs(args.before / name, args.after / name))]
    differ = len(bad)
    bad += [f"{name}: only before" for name in sorted(before - after)] + [f"{name}: only after" for name in sorted(after - before)]
    if not pairs:
        bad.append("nothing to compare: no file is in both folders")
    print(f"{len(before)} before, {len(after)} after; {len(pairs)} pairs compared, {differ} differ, "
          f"{len(before - after)} only before, {len(after - before)} only after")
    for b in bad:
        print(f"FAIL {b}")
    print(f"{len(bad)} failing")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
