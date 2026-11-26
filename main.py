#!/usr/bin/env python3
"""Ship the cron job's one-line resignation letter to the make.fun output dir."""

import hashlib
import os
import shutil
import sys
from pathlib import Path

EXPECTED_SHA256 = "38079883b43679f6626807b516d678479ef65abf17be2b14fa74602653d2fcc4"
MAX_CHARS = 140
DEFAULT_OUTPUT_DIR = "/output"


def fail(message: str) -> int:
    print(f"error: {message}", file=sys.stderr)
    return 1


def main() -> int:
    source = Path(__file__).resolve().parent / "entry.txt"

    if not source.is_file():
        return fail(f"entry.txt not found at {source}")

    try:
        raw = source.read_bytes()
    except OSError as exc:
        return fail(f"could not read {source}: {exc}")

    digest = hashlib.sha256(raw).hexdigest()
    if digest != EXPECTED_SHA256:
        return fail(
            f"sha256 mismatch: expected {EXPECTED_SHA256}, got {digest}"
        )

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        return fail(f"entry.txt is not valid UTF-8: {exc}")

    line = text[:-1] if text.endswith("\n") else text
    count = len(line)

    if count < 1:
        return fail("entry.txt is empty")
    if count > MAX_CHARS:
        return fail(f"entry.txt is {count} characters; limit is {MAX_CHARS}")
    if not line.strip():
        return fail("entry.txt contains only whitespace")

    output_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", DEFAULT_OUTPUT_DIR))

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return fail(f"could not create output directory {output_dir}: {exc}")

    if not output_dir.is_dir():
        return fail(f"output path exists but is not a directory: {output_dir}")
    if not os.access(output_dir, os.W_OK):
        return fail(
            f"output directory is not writable (check permissions or "
            f"MAKEFUN_OUTPUT_DIR): {output_dir}"
        )

    destination = output_dir / "entry.txt"
    if destination.is_dir():
        return fail(f"destination exists and is a directory, not a file: {destination}")

    try:
        shutil.copyfile(source, destination)
    except shutil.SameFileError:
        print(f"entry.txt is already in place at {destination}; skipping copy")
    except OSError as exc:
        return fail(f"could not write {destination}: {exc}")

    print(line)
    print(f"characters: {count}")
    print(f"sha256: {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
