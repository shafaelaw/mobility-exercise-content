#!/usr/bin/env python3
"""Validate mobility exercise content against the schema + house rules.

Usage:
    python3 tools/validate.py                 # checks content/exercises.json + content/months/*.json
    python3 tools/validate.py path/to/file.json

House rules (must pass):
  - month is "YYYY-MM"
  - exactly 10 exercises
  - unique ids
  - >= 2 balance moves (fall prevention)
  - every exercise has a non-empty seatedVariant, safetyCue, and steps

Exit code is non-zero if anything fails, so this is CI-friendly.
"""
import json
import re
import sys
import glob
import os

REQUIRED_FIELDS = [
    "id", "name", "category", "durationMinutes", "intensity",
    "defaultPosition", "steps", "seatedVariant", "kneeFriendly", "safetyCue",
]
CATEGORIES = {"mobility", "strength", "balance", "flexibility", "circulation"}
POSITIONS = {"seated", "standing"}
MONTH_RE = re.compile(r"^\d{4}-\d{2}$")


def check_file(path):
    errs = []
    try:
        data = json.load(open(path))
    except Exception as e:  # noqa: BLE001
        return [f"could not parse JSON: {e}"]

    month = data.get("month", "")
    if not MONTH_RE.match(str(month)):
        errs.append(f'month must be "YYYY-MM", got {month!r}')

    exercises = data.get("exercises", [])
    if len(exercises) != 10:
        errs.append(f"expected 10 exercises, found {len(exercises)}")

    ids = [e.get("id") for e in exercises]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        errs.append(f"duplicate ids: {', '.join(map(str, dupes))}")

    balance = sum(1 for e in exercises if e.get("category") == "balance")
    if balance < 2:
        errs.append(f"need >= 2 balance moves, found {balance}")

    for e in exercises:
        eid = e.get("id", "<no id>")
        for f in REQUIRED_FIELDS:
            if f not in e:
                errs.append(f'{eid}: missing field "{f}"')
        if e.get("category") not in CATEGORIES:
            errs.append(f"{eid}: bad category {e.get('category')!r}")
        if e.get("defaultPosition") not in POSITIONS:
            errs.append(f"{eid}: bad defaultPosition {e.get('defaultPosition')!r}")
        if not str(e.get("seatedVariant", "")).strip():
            errs.append(f"{eid}: empty seatedVariant")
        if not str(e.get("safetyCue", "")).strip():
            errs.append(f"{eid}: empty safetyCue")
        if not e.get("steps"):
            errs.append(f"{eid}: empty steps")
    return errs


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    if len(sys.argv) > 1:
        targets = sys.argv[1:]
    else:
        targets = [os.path.join(root, "exercises.json")]
        targets += sorted(glob.glob(os.path.join(root, "months", "*.json")))

    ok = True
    for path in targets:
        errs = check_file(path)
        name = os.path.relpath(path, root)
        if errs:
            ok = False
            print(f"✗ {name}")
            for e in errs:
                print(f"    - {e}")
        else:
            print(f"✓ {name}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
