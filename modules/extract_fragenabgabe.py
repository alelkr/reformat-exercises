"""Extract the Fragenabgabe archive while preserving its folder structure."""

from __future__ import annotations

import argparse
from pathlib import Path
from zipfile import ZipFile

DEFAULT_ARCHIVE = r"C:\Users\smaikrau\reformat-exercises\data\Fragenabgabe.zip"
DEFAULT_OUTPUT = r"C:\Users\smaikrau\reformat-exercises\data\Fragenabgabe"


def extract_archive(archive_path: Path, output_dir: Path) -> None:
    """Extract all archive entries into output_dir, preserving their paths."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_root = output_dir.resolve()

    with ZipFile(archive_path) as archive:
        for entry in archive.infolist():
            destination = (output_dir / entry.filename).resolve()
            if destination != output_root and output_root not in destination.parents:
                raise ValueError(
                    f"Archive entry escapes output directory: {entry.filename}"
                )

            archive.extract(entry, output_dir)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract Fragenabgabe.zip while keeping its subfolder structure."
    )
    parser.add_argument(
        "archive",
        nargs="?",
        type=Path,
        default=DEFAULT_ARCHIVE,
        help=f"ZIP archive to extract (default: {DEFAULT_ARCHIVE})",
    )
    parser.add_argument(
        "output",
        nargs="?",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output directory (default: {DEFAULT_OUTPUT})",
    )
    args = parser.parse_args()

    extract_archive(args.archive, args.output)
    print(f"Extracted {args.archive} to {args.output}")


if __name__ == "__main__":
    main()
