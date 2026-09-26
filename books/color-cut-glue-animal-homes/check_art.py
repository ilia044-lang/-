#!/usr/bin/env python3
"""
Report which artwork the book still needs.

Run it against raw/ (what came out of the generator) or art/ (what has been
normalised). It knows the full manifest the two builders look for, so it answers
one question exactly: can we build the book yet, and if not, what is missing?

    python3 check_art.py --dir raw
    python3 check_art.py --dir art --quiet     # exit 1 if anything is missing
"""
import argparse, os, sys

from build_interior import HABITATS, SCENES

REQUIRED_COVER = ["cover_hero.png"]
OPTIONAL = ["cover_scissors.png", "bubi_mascot.png"]


def manifest():
    groups = {}
    for hab, animals in HABITATS.items():
        groups[f"coloring / {hab}"] = [f"color_{hab}_{a}.png" for a in animals]
    groups["habitat scenes"] = [f"scene_{h}.png" for h, _ in SCENES]
    groups["cover"] = list(REQUIRED_COVER)
    return groups


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="art")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    have = {f.lower() for f in os.listdir(a.dir)} if os.path.isdir(a.dir) else set()
    groups = manifest()
    total = sum(len(v) for v in groups.values())
    missing_all = []

    for name, files in groups.items():
        missing = [f for f in files if f.lower() not in have]
        missing_all += missing
        got = len(files) - len(missing)
        mark = "OK " if not missing else "-- "
        if not a.quiet:
            print(f"{mark} {name:<24} {got}/{len(files)}")
            for m in missing:
                print(f"       missing  {m}")

    extra = [f for f in OPTIONAL if f.lower() in have]
    done = total - len(missing_all)
    print(f"\n{done}/{total} required files present in {a.dir}/"
          + (f"  (+{len(extra)} optional)" if extra else ""))
    if missing_all:
        print(f"{len(missing_all)} still to generate. "
              f"Cut-out sheets need no files of their own - they reuse the "
              f"coloring artwork.")
        sys.exit(1)
    print("Ready to build.")


if __name__ == "__main__":
    main()
