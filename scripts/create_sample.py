"""Create a reproducible, identifier-remapped dashboard sample."""

import argparse
from pathlib import Path

import pandas as pd

from dashboard import FULL_DATA_PATH, REQUIRED_COLUMNS, SAMPLE_DATA_PATH, load_data

DEFAULT_ROWS_PER_SNAPSHOT = 250
DEFAULT_RANDOM_SEED = 42
MIN_CHURNED_ROWS = 10


def sample_snapshot(
    snapshot: pd.DataFrame,
    rows: int,
    random_seed: int,
) -> pd.DataFrame:
    """Sample one snapshot while retaining its approximate churn rate."""
    target_rows = min(rows, len(snapshot))
    churned = snapshot[snapshot["label"] == 1]
    retained = snapshot[snapshot["label"] == 0]

    if churned.empty or retained.empty:
        return snapshot.sample(n=target_rows, random_state=random_seed)

    churned_rows = max(MIN_CHURNED_ROWS, round(snapshot["label"].mean() * target_rows))
    churned_rows = min(churned_rows, len(churned), target_rows - 1)
    retained_rows = min(target_rows - churned_rows, len(retained))
    churned_rows = min(target_rows - retained_rows, len(churned))

    return pd.concat(
        [
            churned.sample(n=churned_rows, random_state=random_seed),
            retained.sample(n=retained_rows, random_state=random_seed),
        ],
        ignore_index=True,
    )


def create_sample(
    source_path: Path,
    output_path: Path,
    rows_per_snapshot: int = DEFAULT_ROWS_PER_SNAPSHOT,
    random_seed: int = DEFAULT_RANDOM_SEED,
) -> pd.DataFrame:
    """Create and write the representative dashboard sample."""
    if rows_per_snapshot <= 0:
        raise ValueError("Rows per snapshot must be greater than zero.")

    source = load_data(source_path)
    samples = [
        sample_snapshot(
            snapshot,
            rows=rows_per_snapshot,
            random_seed=random_seed + int(snapshot_day),
        )
        for snapshot_day, snapshot in source.groupby("snapshot_day", sort=True)
    ]
    sample = pd.concat(samples, ignore_index=True)[list(REQUIRED_COLUMNS)]

    identifiers = {
        identifier: replacement
        for replacement, identifier in enumerate(
            sorted(sample["userId"].unique()), start=1
        )
    }
    sample["userId"] = sample["userId"].map(identifiers).astype("int64")
    sample = sample.sort_values(["snapshot_day", "userId"]).reset_index(drop=True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sample.to_parquet(output_path, index=False, compression="zstd")
    return sample


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=FULL_DATA_PATH)
    parser.add_argument("--output", type=Path, default=SAMPLE_DATA_PATH)
    parser.add_argument(
        "--rows-per-snapshot", type=int, default=DEFAULT_ROWS_PER_SNAPSHOT
    )
    parser.add_argument("--random-seed", type=int, default=DEFAULT_RANDOM_SEED)
    return parser.parse_args()


def main() -> None:
    """Generate the sample from command-line arguments."""
    args = parse_args()
    sample = create_sample(
        source_path=args.source,
        output_path=args.output,
        rows_per_snapshot=args.rows_per_snapshot,
        random_seed=args.random_seed,
    )
    print(f"Wrote {len(sample):,} rows to {args.output}.")


if __name__ == "__main__":
    main()
