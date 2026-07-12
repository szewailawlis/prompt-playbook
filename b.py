#!/usr/bin/env python3
"""Merge all CSV files in a folder into one, removing duplicate rows."""

import argparse
import sys
from pathlib import Path

import pandas as pd


def merge_csvs(folder: Path, output: Path) -> pd.DataFrame:
    csv_files = sorted(folder.glob("*.csv"))
    # Don't accidentally re-ingest a previous output file
    csv_files = [f for f in csv_files if f.resolve() != output.resolve()]

    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {folder}")

    frames = []
    for f in csv_files:
        try:
            df = pd.read_csv(f)
        except pd.errors.EmptyDataError:
            print(f"  skipped {f.name}: file is empty")
            continue
        if df.empty and df.columns.empty:
            print(f"  skipped {f.name}: no data")
            continue
        frames.append(df)
        print(f"  read {f.name}: {len(df)} rows")

    if not frames:
        raise ValueError("All CSV files were empty; nothing to merge")

    merged = pd.concat(frames, ignore_index=True)
    before = len(merged)
    merged = merged.drop_duplicates(ignore_index=True)
    print(f"Merged {before} rows -> {len(merged)} after removing duplicates")

    merged.to_csv(output, index=False)
    print(f"Wrote {output}")
    return merged


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge CSVs and dedupe rows")
    parser.add_argument("folder", type=Path, help="Folder containing CSV files")
    parser.add_argument("-o", "--output", type=Path, default=Path("merged.csv"))
    args = parser.parse_args()

    try:
        merge_csvs(args.folder, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
