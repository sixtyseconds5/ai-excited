# Golden koi, leaping from the teacup: the entry program for make.fun's
# ai-excited-01 ("Make the AI judge excited").
#
# The image is the entry.png beside this file: a colossal golden koi bursting out of
# a blue-and-white porcelain teacup into a starry night sky, a tiny paper boat riding
# on its back, water exploding in golden light. One clear focal shape, an impossible
# scale, frozen mid-leap -- built to hit the judge's criteria in their own order:
# a jolt of awe at first look, a surprise of scale, momentum toward one thrilling
# moment, clean craft with no text, and a shape that still reads at 300 pixels wide.
#
# The program does one thing, deterministically: it copies that image to
# /output/entry.png. A byte copy has nothing in it that can differ between the
# grader's two runs, so both runs write the same bytes. Outside the grader's
# container, MAKEFUN_OUTPUT_DIR stands in for /output:
#   mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
#
# Standard library only, no network, no clock, no randomness.

import os
import shutil
import sys


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(source, os.path.join(out_dir, "entry.png"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
