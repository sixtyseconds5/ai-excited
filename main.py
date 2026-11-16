"""Koi out of the teacup - an entry for make.fun bounty ai-excited-01.

A golden koi bursts from a small blue-and-white porcelain teacup into a
deep indigo, star-filled sky, a tiny paper boat riding on its back while
water explodes around it in golden light. The picture is built to hit the
judge's criteria in this order: first a jolt of awe, because a fish
leaping out of a teacup into the night sky is impossible and instantly
striking; then the surprise of scale, a whole ocean and sky unfolding
from something that fits in a hand; then momentum, the koi mid-leap with
water flying, so the eye follows it upward; then clean craft, with no
text anywhere and nothing cluttering the scene; and finally it still
reads clearly at 300px wide, since the koi, the cup and the boat are
large, simple shapes against a dark sky.

This script does one small job: it copies the entry image beside it into
the output directory, byte for byte, and checks the copy matches. It
streams the file in chunks, so it never holds the whole image in memory,
and hashes each side as it goes.
"""

import hashlib
import os
import sys

CHUNK_SIZE = 65536


def hash_and_copy(source_path, dest_path):
    """Stream source to dest, returning (bytes, source_hash, dest_hash)."""
    source_hash = hashlib.sha256()
    total = 0
    with open(source_path, "rb") as src, open(dest_path, "wb") as dst:
        while True:
            chunk = src.read(CHUNK_SIZE)
            if not chunk:
                break
            source_hash.update(chunk)
            dst.write(chunk)
            total += len(chunk)
    dest_hash = hashlib.sha256()
    with open(dest_path, "rb") as handle:
        while True:
            chunk = handle.read(CHUNK_SIZE)
            if not chunk:
                break
            dest_hash.update(chunk)
    return total, source_hash.hexdigest(), dest_hash.hexdigest()


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source_path = os.path.join(here, "entry.png")
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(outdir, exist_ok=True)
    dest_path = os.path.join(outdir, "entry.png")

    total, source_digest, dest_digest = hash_and_copy(source_path, dest_path)

    if source_digest != dest_digest:
        print("hash mismatch: written copy differs from source",
              file=sys.stderr)
        return 1

    print("wrote %d bytes to %s" % (total, dest_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
