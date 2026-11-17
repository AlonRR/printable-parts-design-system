#!/usr/bin/env python3
"""A coverage floor that only goes up: coverage.py's `fail_under`, ratcheted.

    coverage_ratchet.py raise [--coverage-json coverage.json] [--pyproject pyproject.toml]
    coverage_ratchet.py guard --against REF [--pyproject pyproject.toml]
    coverage_ratchet.py unmeasured DIR... [--coverage-json coverage.json] [--exclude GLOB]...

raise  Reads the measured total from `coverage json` output and, if it is above the
       `[tool.coverage.report] fail_under` in pyproject.toml, moves the floor up to it, rounded
       down to the configured `precision` (0 decimals unless set). It never lowers the floor, and
       it changes no other byte of the file. Run it after a full, passing run, and commit the
       bump with the change that earned it.
guard  Fails (exit 1) if the floor in the working tree's pyproject.toml is lower than at REF, or
       missing where REF has one: the ratchet's other half, for a commit hook or CI, so the floor
       is never lowered quietly to let a change through.
unmeasured
       Fails (exit 1) if a .py file under DIR is missing from the coverage report. With
       `include =` patterns, or `source =` over a folder that is not a package, coverage leaves
       out a file no process ran rather than counting it at 0 %, so the total rises when a
       script loses its last test.
       Paths are relative to the current directory; --exclude takes globs for files run by hand.

Exit status: 0 done; 1 guard refused or files unmeasured; 2 bad input (no total, unreadable
file, unknown REF, missing DIR).
Standard library only (Python 3.11+ for tomllib).
"""

from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
import tomllib
from pathlib import Path

TABLE = "[tool.coverage.report]"


class BadInput(Exception):
    pass


def report_settings(text: str) -> dict:
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise BadInput(f"pyproject.toml does not parse: {exc}") from exc
    return data.get("tool", {}).get("coverage", {}).get("report", {})


def floor_to(value: float, digits: int) -> float | int:
    scale = 10**digits
    floored = math.floor(round(value * scale, 6)) / scale
    return int(floored) if digits == 0 else floored


def measured_total(path: Path) -> float:
    try:
        total = json.loads(path.read_text(encoding="utf-8"))["totals"]["percent_covered"]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise BadInput(f"{path}: no totals.percent_covered ({exc})") from exc
    if not isinstance(total, (int, float)):
        raise BadInput(f"{path}: totals.percent_covered is not a number")
    return float(total)


def set_fail_under(text: str, value) -> str:
    """Return text with fail_under in [tool.coverage.report] set to value, nothing else changed."""
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines(keepends=True)
    start = next((i for i, line in enumerate(lines) if line.strip() == TABLE), None)
    if start is None:
        sep = "" if not text or text.endswith(("\n", "\r\n")) else newline
        gap = newline if text.strip() else ""
        return f"{text}{sep}{gap}{TABLE}{newline}fail_under = {value}{newline}"
    end = next(
        (i for i in range(start + 1, len(lines)) if re.match(r"\s*\[", lines[i])), len(lines)
    )
    for i in range(start + 1, end):
        match = re.match(r"(\s*fail_under\s*=\s*)([^#\r\n]*?)(\s*(#.*)?)(\r?\n)?$", lines[i])
        if match:
            lines[i] = f"{match.group(1)}{value}{match.group(3)}{match.group(5) or ''}"
            return "".join(lines)
    lines.insert(start + 1, f"fail_under = {value}{newline}")
    return "".join(lines)


def cmd_raise(args) -> int:
    text = ""
    if args.pyproject.exists():
        with open(args.pyproject, encoding="utf-8", newline="") as fh:  # keep CRLF as it is
            text = fh.read()
    settings = report_settings(text)
    total = measured_total(args.coverage_json)
    digits = int(settings.get("precision", 0))
    current = settings.get("fail_under")
    new = floor_to(total, digits)
    if current is not None and new <= float(current):
        print(f"fail_under stays {current} (measured {total:.2f})")
        return 0
    args.pyproject.write_text(set_fail_under(text, new), encoding="utf-8", newline="")
    print(
        f"fail_under {current if current is not None else 'unset'} -> {new} (measured {total:.2f})"
    )
    return 0


def cmd_guard(args) -> int:
    rel = args.pyproject.resolve()
    top = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        check=False,
        cwd=rel.parent,
        capture_output=True,
        text=True,
    )
    if top.returncode != 0:
        raise BadInput(f"not in a git repository: {rel.parent}")
    path_in_repo = rel.relative_to(Path(top.stdout.strip()).resolve()).as_posix()
    old = subprocess.run(
        ["git", "show", f"{args.against}:{path_in_repo}"],
        check=False,
        cwd=rel.parent,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if old.returncode != 0:
        raise BadInput(f"cannot read {path_in_repo} at {args.against}: {old.stderr.strip()}")
    before = report_settings(old.stdout).get("fail_under")
    now = report_settings(args.pyproject.read_text(encoding="utf-8")).get("fail_under")
    if before is None:
        print(f"no floor at {args.against}; now {now}")
        return 0
    if now is None or float(now) < float(before):
        print(
            f"REFUSED: fail_under was {before} at {args.against}, is now "
            f"{'unset' if now is None else now}. The floor only goes up."
        )
        return 1
    print(f"fail_under {before} at {args.against}, {now} now: ok")
    return 0


def reported_files(path: Path) -> set[Path]:
    try:
        files = json.loads(path.read_text(encoding="utf-8"))["files"]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise BadInput(f"{path}: no files table ({exc})") from exc
    return {Path(key.replace("\\", "/")).resolve() for key in files}


def cmd_unmeasured(args) -> int:
    seen = reported_files(args.coverage_json)
    missing = []
    for folder in args.dirs:
        if not folder.is_dir():
            raise BadInput(f"not a folder: {folder}")
        for path in sorted(folder.rglob("*.py")):
            shown = path.as_posix()
            if any(Path(shown).match(glob) for glob in args.exclude):
                continue
            if path.resolve() not in seen:
                missing.append(shown)
    for shown in missing:
        print(f"UNMEASURED: {shown} is not in the coverage report (no process ran it)")
    if missing:
        return 1
    print(f"every .py file under {', '.join(d.as_posix() for d in args.dirs)} is in the report")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("raise", help="move fail_under up to the measured total")
    r.add_argument("--coverage-json", type=Path, default=Path("coverage.json"))
    r.add_argument("--pyproject", type=Path, default=Path("pyproject.toml"))
    g = sub.add_parser("guard", help="refuse a floor lower than at REF")
    g.add_argument("--against", required=True)
    g.add_argument("--pyproject", type=Path, default=Path("pyproject.toml"))
    u = sub.add_parser("unmeasured", help="refuse a .py file missing from the coverage report")
    u.add_argument("dirs", nargs="+", type=Path)
    u.add_argument("--coverage-json", type=Path, default=Path("coverage.json"))
    u.add_argument("--exclude", action="append", default=[])
    args = ap.parse_args(argv)
    commands = {"raise": cmd_raise, "guard": cmd_guard, "unmeasured": cmd_unmeasured}
    try:
        return commands[args.cmd](args)
    except BadInput as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
