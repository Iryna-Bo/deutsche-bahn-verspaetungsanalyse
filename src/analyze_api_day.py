from pathlib import Path
import pandas as pd
import numpy as np


# ============================================================
# CONFIG
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

SNAPSHOT_DIR = (
    BASE_DIR
    / "data"
    / "processed"
    / "api_current"
    / "db-api-snapshots-12.00-11.50"
)

RESULTS_DIR = BASE_DIR / "results" / "api_day"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD FILES
# ============================================================

files = sorted(SNAPSHOT_DIR.glob("snapshot_*.parquet"))

print("=" * 70)
print("DB API – 24h snapshot analysis")
print("=" * 70)

print(f"\nSnapshot directory:")
print(SNAPSHOT_DIR)

print(f"\nFiles found: {len(files)}")

if not files:
    raise FileNotFoundError("No snapshot files found.")

# ------------------------------------------------------------
# Expected snapshot times
# ------------------------------------------------------------

expected_times = pd.date_range(
    start="2026-09-21 12:00",
    end="2026-09-22 11:50",
    freq="10min"
)

# Read actual snapshot times from filenames
actual_snapshots = []

for file in files:
    try:
        timestamp_text = file.stem.replace(
            "snapshot_", ""
        )

        timestamp = pd.to_datetime(
            timestamp_text,
            format="%Y-%m-%d_%H-%M"
        )

        actual_snapshots.append({
            "file": file.name,
            "timestamp": timestamp
        })

    except Exception:
        print(
            f"WARNING: Could not parse timestamp "
            f"from filename: {file.name}"
        )

# ------------------------------------------------------------
# Match actual snapshots to expected 10-minute slots
# ------------------------------------------------------------

tolerance = pd.Timedelta(minutes=2)

matched = []
unmatched_actual = set(
    item["file"] for item in actual_snapshots
)

missing_expected = []

for expected in expected_times:

    candidates = [
        item for item in actual_snapshots
        if abs(item["timestamp"] - expected) <= tolerance
    ]

    if candidates:

        # Select the closest snapshot
        best = min(
            candidates,
            key=lambda x: abs(x["timestamp"] - expected)
        )

        matched.append({
            "expected": expected,
            "actual": best["timestamp"],
            "file": best["file"],
            "difference_minutes": (
                best["timestamp"] - expected
            ).total_seconds() / 60
        })

        unmatched_actual.discard(best["file"])

    else:
        missing_expected.append(expected)

print(f"Expected snapshots: {len(expected_times)}")
print(f"Files found:         {len(files)}")
print(f"Matched snapshots:   {len(matched)}")
print(f"Missing snapshots:   {len(missing_expected)}")

if missing_expected:

    print("\nMissing snapshot time points:")

    for timestamp in missing_expected:
        print(
            "  ",
            timestamp.strftime("%Y-%m-%d %H:%M")
        )

# ------------------------------------------------------------
# Report small timing deviations
# ------------------------------------------------------------

timing_deviations = [
    item for item in matched
    if item["difference_minutes"] != 0
]

if timing_deviations:

    print("\nMinor timing deviations:")

    for item in timing_deviations:

        print(
            f"  expected "
            f"{item['expected'].strftime('%Y-%m-%d %H:%M')} "
            f"-> actual "
            f"{item['actual'].strftime('%Y-%m-%d %H:%M')} "
            f"({item['difference_minutes']:+.0f} min)"
        )


# ============================================================
# INSPECT ALL SNAPSHOTS
# ============================================================

snapshot_info = []
all_sample_columns = None

for file in files:

    df = pd.read_parquet(file)

    if all_sample_columns is None:
        all_sample_columns = list(df.columns)

    snapshot_time = file.stem.replace(
        "snapshot_", ""
    )

    snapshot_info.append({
        "file": file.name,
        "snapshot_time": snapshot_time,
        "rows": len(df),
        "columns": len(df.columns),
        "stations": df["station_eva"].nunique(),
        "trains": df["train_number"].nunique(),
        "missing_delay": df["delay_minutes"].isna().sum(),
        "negative_delay": (df["delay_minutes"] < 0).sum(),
        "delay_ge_5": (df["delay_minutes"] >= 5).sum(),
        "delay_ge_15": (df["delay_minutes"] >= 15).sum(),
        "delay_ge_60": (df["delay_minutes"] >= 60).sum(),
        "min_delay": df["delay_minutes"].min(),
        "max_delay": df["delay_minutes"].max(),
        "median_delay": df["delay_minutes"].median(),
        "p95_delay": df["delay_minutes"].quantile(0.95),
        "p99_delay": df["delay_minutes"].quantile(0.99),
        "duplicate_rows": df.duplicated().sum(),
    })

snapshot_df = pd.DataFrame(snapshot_info)


# ============================================================
# BASIC STRUCTURE
# ============================================================

print("\n" + "=" * 70)
print("1. STRUCTURE")
print("=" * 70)

print("\nColumns:")
for col in all_sample_columns:
    print("  ", col)

print("\nRows per snapshot:")
print(snapshot_df[
    ["snapshot_time", "rows", "stations", "trains"]
].to_string(index=False))


# ============================================================
# OVERALL BASIC METRICS
# ============================================================

print("\n" + "=" * 70)
print("2. BASIC DATA QUALITY")
print("=" * 70)

print("\nTotal rows across snapshots:",
      snapshot_df["rows"].sum())

print("Average rows per snapshot:",
      round(snapshot_df["rows"].mean(), 1))

print("Min rows:",
      snapshot_df["rows"].min())

print("Max rows:",
      snapshot_df["rows"].max())

print("\nDuplicate complete rows across individual snapshots:",
      snapshot_df["duplicate_rows"].sum())

print("\nMissing delay values across snapshots:",
      snapshot_df["missing_delay"].sum())

print("\nNegative delay values across snapshots:",
      snapshot_df["negative_delay"].sum())


# ============================================================
# DELAY DISTRIBUTION
# ============================================================

print("\n" + "=" * 70)
print("3. DELAY DISTRIBUTION")
print("=" * 70)

# For the descriptive summary we calculate from all observations.
delay_values = []

for file in files:
    df = pd.read_parquet(
        file,
        columns=["delay_minutes"]
    )

    delay_values.append(
        df["delay_minutes"].dropna()
    )

delay_all = pd.concat(delay_values, ignore_index=True)

print("\nObservations with delay:")
print(len(delay_all))

print("\nQuantiles:")
print(delay_all.quantile(
    [0, 0.01, 0.05, 0.50, 0.95, 0.99, 0.999, 1]
).to_string())

print("\nThresholds:")

for threshold in [5, 15, 60]:

    count = (delay_all >= threshold).sum()
    share = count / len(delay_all) * 100

    print(
        f"  >= {threshold:>3} min: "
        f"{count:>6} "
        f"({share:.2f}%)"
    )

print("\nNegative delays:")

negative_count = (delay_all < 0).sum()

print(
    f"  < 0 min: {negative_count} "
    f"({negative_count / len(delay_all) * 100:.2f}%)"
)

print("\nVery large negative delays (< -60):")

extreme_negative = (delay_all < -60).sum()

print(
    f"  < -60 min: {extreme_negative} "
    f"({extreme_negative / len(delay_all) * 100:.2f}%)"
)

print("\nVery large positive delays (>= 180):")

extreme_positive = (delay_all >= 180).sum()

print(
    f"  >= 180 min: {extreme_positive} "
    f"({extreme_positive / len(delay_all) * 100:.2f}%)"
)


# ============================================================
# TIMESTAMP VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("4. TIMESTAMP VALIDATION")
print("=" * 70)

timestamp_problems = []

for file in files:

    df = pd.read_parquet(
        file,
        columns=[
            "planned_time",
            "changed_time",
            "collected_at",
            "delay_minutes"
        ]
    )

    df["planned_time"] = pd.to_datetime(
        df["planned_time"],
        errors="coerce"
    )

    df["changed_time"] = pd.to_datetime(
        df["changed_time"],
        errors="coerce"
    )

    df["collected_at"] = pd.to_datetime(
        df["collected_at"],
        errors="coerce"
    )

    missing_planned = df["planned_time"].isna().sum()
    missing_changed = df["changed_time"].isna().sum()
    missing_collected = df["collected_at"].isna().sum()

    # Difference between changed and planned time.
    calculated_delay = (
        df["changed_time"] - df["planned_time"]
    ).dt.total_seconds() / 60

    # Compare only rows where both values exist.
    valid = (
        calculated_delay.notna()
        & df["delay_minutes"].notna()
    )

    if valid.any():

        difference = (
            calculated_delay[valid]
            - df.loc[valid, "delay_minutes"]
        )

        mismatch = (
            difference.abs() > 1
        ).sum()

    else:
        mismatch = 0

    timestamp_problems.append({
        "file": file.name,
        "missing_planned": missing_planned,
        "missing_changed": missing_changed,
        "missing_collected": missing_collected,
        "delay_mismatch_gt_1min": mismatch
    })

timestamp_df = pd.DataFrame(timestamp_problems)

print(
    timestamp_df[
        [
            "missing_planned",
            "missing_changed",
            "missing_collected",
            "delay_mismatch_gt_1min"
        ]
    ].sum()
)


# ============================================================
# EVENT TYPE
# ============================================================

print("\n" + "=" * 70)
print("5. EVENT TYPES")
print("=" * 70)

event_counts = []

for file in files:

    df = pd.read_parquet(
        file,
        columns=["event_type"]
    )

    counts = df["event_type"].value_counts(dropna=False)

    for event_type, count in counts.items():

        event_counts.append({
            "event_type": str(event_type),
            "rows": int(count)
        })

event_df = pd.DataFrame(event_counts)

event_summary = (
    event_df
    .groupby("event_type")["rows"]
    .sum()
    .sort_values(ascending=False)
)

print(event_summary.to_string())


# ============================================================
# SNAPSHOT DYNAMICS
# ============================================================

print("\n" + "=" * 70)
print("6. SNAPSHOT DYNAMICS")
print("=" * 70)

print(
    snapshot_df[
        [
            "snapshot_time",
            "rows",
            "delay_ge_5",
            "delay_ge_15",
            "delay_ge_60",
            "negative_delay",
            "median_delay",
            "p95_delay",
            "p99_delay"
        ]
    ].to_string(index=False)
)


# ============================================================
# STATION COVERAGE
# ============================================================

print("\n" + "=" * 70)
print("7. STATION COVERAGE")
print("=" * 70)

station_sets = []

for file in files:

    df = pd.read_parquet(
        file,
        columns=["station_eva"]
    )

    station_sets.append(
        set(df["station_eva"].dropna().astype(str))
    )

all_stations = set().union(*station_sets)

print("Unique stations across all snapshots:",
      len(all_stations))

station_counts = pd.Series(
    [
        len(stations)
        for stations in station_sets
    ]
)

print(
    "Stations per snapshot:",
    station_counts.min(),
    "to",
    station_counts.max()
)


# ============================================================
# TRAIN COVERAGE
# ============================================================

print("\n" + "=" * 70)
print("8. TRAIN COVERAGE")
print("=" * 70)

train_sets = []

for file in files:

    df = pd.read_parquet(
        file,
        columns=["train_number"]
    )

    train_sets.append(
        set(df["train_number"].dropna().astype(str))
    )

all_trains = set().union(*train_sets)

print("Unique train numbers across all snapshots:",
      len(all_trains))

train_counts = pd.Series(
    [
        len(trains)
        for trains in train_sets
    ]
)

print(
    "Train numbers per snapshot:",
    train_counts.min(),
    "to",
    train_counts.max()
)


# ============================================================
# SAVE RESULTS
# ============================================================

snapshot_df.to_csv(
    RESULTS_DIR / "api_day_snapshot_quality.csv",
    index=False
)

timestamp_df.to_csv(
    RESULTS_DIR / "api_day_timestamp_quality.csv",
    index=False
)

event_summary.rename(
    "rows"
).to_csv(
    RESULTS_DIR / "api_day_event_types.csv"
)


# ============================================================
# FINAL
# ============================================================

print("\n" + "=" * 70)
print("ANALYSIS FINISHED")
print("=" * 70)

print("\nCreated files:")

print(
    RESULTS_DIR / "api_day_snapshot_quality.csv"
)

print(
    RESULTS_DIR / "api_day_timestamp_quality.csv"
)

print(
    RESULTS_DIR / "api_day_event_types.csv"
)