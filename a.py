#!/usr/bin/env python3
"""Merge all CSV files in a folder into one CSV, removing duplicate rows.

Usage:
    python merge_csvs.py <input_folder> [output_file]

Defaults to writing merged.csv inside the input folder.
"""

import sys
from pathlib import Path

import pandas as pd


def merge_csvs(input_folder: str, output_file: str | None = None) -> Path:
    folder = Path(input_folder)
    if not folder.is_dir():
        raise NotADirectoryError(f"Not a folder: {folder}")

    csv_files = sorted(folder.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {folder}")

    output_path = Path(output_file) if output_file else folder / "merged.csv"
    # Avoid re-ingesting a previous output file living in the same folder
    csv_files = [f for f in csv_files if f.resolve() != output_path.resolve()]

    frames = []
    for f in csv_files:
        try:
            frames.append(pd.read_csv(f))
            print(f"Read {f.name} ({len(frames[-1])} rows)")
        except Exception as e:
            print(f"Skipping {f.name}: {e}", file=sys.stderr)

    if not frames:
        raise ValueError("No CSV files could be read successfully.")

    merged = pd.concat(frames, ignore_index=True)
    before = len(merged)
    merged = merged.drop_duplicates().reset_index(drop=True)
    print(f"Merged {len(frames)} files: {before} rows -> {len(merged)} after deduplication")

    merged.to_csv(output_path, index=False)
    print(f"Saved to {output_path}")
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    merge_csvs(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
