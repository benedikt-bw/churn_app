# Dashboard data

This directory contains the small dataset needed to run the dashboard from a
fresh clone or from the Docker image.

## Bundled sample

`churn_sample.parquet` is a deterministic 1,000-row sample derived from the
local engineered churn snapshot dataset. It contains 250 rows from each
snapshot day and retains approximately the original churn rate within each
snapshot, with at least ten churned examples where the source data permits it.

Only the columns consumed by the dashboard are retained. Original `userId`
values are replaced consistently with sequential identifiers, and the sample
contains no names, locations, event text, or other direct identifiers.

Regenerate it from the ignored full dataset with:

```bash
uv run python -m scripts.create_sample
```

The sampling seed is fixed at `42`. The full input remains excluded from Git.

## Schema

| Column | Meaning |
| --- | --- |
| `userId` | Remapped listener identifier |
| `snapshot_day` | Day represented by the prepared snapshot |
| `label` | Binary churn outcome (`0` or `1`) |
| `active_days` | Number of active days in the observation window |
| `gender` | Recorded gender category |
| `operating_system` | Parsed operating-system category |
| `browser` | Parsed browser category |
| `last_level` | Most recent free or paid subscription level |
| `avg_songs_session` | Average songs played per session |
| `hours_since_last_session` | Hours since the listener's last session |
| `is_new_user` | Binary new-listener indicator |

## Provenance

The full engineered dataset was created by the project author from a publicly
available music-streaming source dataset for a final machine-learning project
at École Polytechnique. The source data has no restrictions that prevent reuse
or redistribution of this derived sample.

The upstream raw event data is not distributed by this repository. The
committed Parquet file contains only a deterministic sample of the engineered
dashboard fields, with source user identifiers replaced by sequential values.
