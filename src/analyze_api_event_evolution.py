

from pathlib import Path
import pandas as pd


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

OUTPUT_FILE = (
    RESULTS_DIR
    / "api_event_evolution_summary.csv"
)


# ============================================================
# LOAD SNAPSHOTS
# ============================================================

files = sorted(
    SNAPSHOT_DIR.glob("snapshot_*.parquet")
)

if not files:
    raise FileNotFoundError(
        f"No snapshot files found in: {SNAPSHOT_DIR}"
    )


# ============================================================
# COLUMNS NEEDED
# ============================================================

columns = [
    "station_eva",
    "station_name",
    "stop_id",
    "train_number",
    "train_type",
    "line",
    "event_type",
    "planned_time",
    "changed_time",
    "delay_minutes",
    "collected_at"
]


# ============================================================
# LOAD AND COMBINE
# ============================================================

data = []

for file in files:

    df = pd.read_parquet(
        file,
        columns=columns
    )

    snapshot_time = pd.to_datetime(
        file.stem.replace("snapshot_", ""),
        format="%Y-%m-%d_%H-%M"
    )

    df["snapshot_time"] = snapshot_time

    data.append(df)


all_data = pd.concat(
    data,
    ignore_index=True
)


# ============================================================
# DATA TYPES AND NORMALIZATION
# ============================================================

all_data["planned_time"] = pd.to_datetime(
    all_data["planned_time"],
    errors="coerce"
)

all_data["collected_at"] = pd.to_datetime(
    all_data["collected_at"],
    errors="coerce"
)

all_data["delay_minutes"] = pd.to_numeric(
    all_data["delay_minutes"],
    errors="coerce"
)


# ============================================================
# EVENT KEY
# ============================================================

# Normalize planned_time to a consistent string format.
# Missing planned_time remains missing and is explicitly
# represented in the event key.

planned_time_key = (
    all_data["planned_time"]
    .dt.strftime("%Y-%m-%d %H:%M:%S")
    .fillna("MISSING_PLANNED_TIME")
)

all_data["event_key"] = (
    all_data["station_eva"].astype(str)
    + "_"
    + all_data["stop_id"].astype(str)
    + "_"
    + all_data["train_number"].astype(str)
    + "_"
    + planned_time_key
    + "_"
    + all_data["event_type"].astype(str)
)


# ============================================================
# CHECK EVENT / SNAPSHOT UNIQUENESS
# ============================================================

duplicates = (
    all_data
    .groupby(
        ["event_key", "snapshot_time"],
        dropna=False
    )
    .size()
    .reset_index(name="count")
)

duplicates = duplicates[
    duplicates["count"] > 1
]

print("=" * 70)
print("DB API – EVENT EVOLUTION")
print("=" * 70)

print("\nRows:", len(all_data))

print(
    "Unique event keys:",
    all_data["event_key"].nunique()
)

print(
    "Duplicate event/snapshot combinations:",
    len(duplicates)
)


# Stop instead of silently selecting an arbitrary record.
if not duplicates.empty:

    print("\nWARNING: Duplicate event/snapshot combinations found.")

    print(
        duplicates
        .head(20)
        .to_string(index=False)
    )

    raise ValueError(
        "Analysis stopped because duplicate event/snapshot "
        "combinations exist. Investigate them before proceeding."
    )


# ============================================================
# ONE ROW PER EVENT / SNAPSHOT
# ============================================================

event_snapshot = all_data[
    [
        "event_key",
        "station_eva",
        "station_name",
        "stop_id",
        "train_number",
        "train_type",
        "line",
        "event_type",
        "planned_time",
        "snapshot_time",
        "delay_minutes"
    ]
].copy()


# ============================================================
# EVENT METADATA
# ============================================================

# Use the first actual observation for each event.
# This avoids combining first non-null values from different rows.

event_metadata = (
    event_snapshot
    .sort_values(
        ["event_key", "snapshot_time"]
    )
    .drop_duplicates(
        subset=["event_key"],
        keep="first"
    )
)

event_metadata = event_metadata[
    [
        "event_key",
        "station_eva",
        "station_name",
        "stop_id",
        "train_number",
        "train_type",
        "line",
        "event_type",
        "planned_time"
    ]
].copy()


# ============================================================
# NUMBER OF SNAPSHOTS PER EVENT
# ============================================================

event_counts = (
    event_snapshot
    .groupby("event_key")
    .agg(
        snapshots_observed=(
            "snapshot_time",
            "nunique"
        ),
        first_snapshot=(
            "snapshot_time",
            "min"
        ),
        last_snapshot=(
            "snapshot_time",
            "max"
        )
    )
    .reset_index()
)


# ============================================================
# EVENTS OBSERVED MULTIPLE TIMES
# ============================================================

repeated_events = event_counts[
    event_counts["snapshots_observed"] >= 2
].copy()

print(
    "\nEvents observed in >=2 snapshots:",
    len(repeated_events)
)


# ============================================================
# VALID DELAY OBSERVATIONS
# ============================================================

# A valid delay observation is a non-null delay_minutes value.
# Negative values are retained because this analysis describes
# API-reported delay changes, including early running.

delay_data = event_snapshot[
    event_snapshot["delay_minutes"].notna()
].copy()


# ============================================================
# NUMBER OF VALID DELAY OBSERVATIONS PER EVENT
# ============================================================

delay_counts = (
    delay_data
    .groupby("event_key")
    .agg(
        delay_observations=(
            "delay_minutes",
            "count"
        )
    )
    .reset_index()
)


# ============================================================
# FIRST / LAST AVAILABLE DELAY
# ============================================================

first_delay = (
    delay_data
    .sort_values(
        ["event_key", "snapshot_time"]
    )
    .drop_duplicates(
        subset=["event_key"],
        keep="first"
    )
)

last_delay = (
    delay_data
    .sort_values(
        ["event_key", "snapshot_time"]
    )
    .drop_duplicates(
        subset=["event_key"],
        keep="last"
    )
)


first_delay = first_delay[
    [
        "event_key",
        "snapshot_time",
        "delay_minutes"
    ]
].rename(
    columns={
        "snapshot_time": "first_delay_snapshot",
        "delay_minutes": "first_delay"
    }
)


last_delay = last_delay[
    [
        "event_key",
        "snapshot_time",
        "delay_minutes"
    ]
].rename(
    columns={
        "snapshot_time": "last_delay_snapshot",
        "delay_minutes": "last_delay"
    }
)


# ============================================================
# EVENT EVOLUTION SUMMARY
# ============================================================

evolution = (
    repeated_events
    .merge(
        event_metadata,
        on="event_key",
        how="left",
        validate="one_to_one"
    )
    .merge(
        delay_counts,
        on="event_key",
        how="left",
        validate="one_to_one"
    )
    .merge(
        first_delay,
        on="event_key",
        how="left",
        validate="one_to_one"
    )
    .merge(
        last_delay,
        on="event_key",
        how="left",
        validate="one_to_one"
    )
)


# Events without delay observations receive zero.
evolution["delay_observations"] = (
    evolution["delay_observations"]
    .fillna(0)
    .astype(int)
)


# ============================================================
# DELAY CHANGE
# ============================================================

# Calculate change only if at least two delay observations
# are available for the event.

sufficient_data = (
    evolution["delay_observations"] >= 2
)

evolution["delay_change"] = pd.NA

evolution.loc[
    sufficient_data,
    "delay_change"
] = (
    evolution.loc[
        sufficient_data,
        "last_delay"
    ]
    -
    evolution.loc[
        sufficient_data,
        "first_delay"
    ]
)


# ============================================================
# CLASSIFY EVOLUTION
# ============================================================

def classify_change(row):

    if row["delay_observations"] < 2:
        return "no_delay_data"

    value = row["delay_change"]

    if pd.isna(value):
        return "no_delay_data"

    if value > 0:
        return "increased"

    if value < 0:
        return "decreased"

    return "stable"


evolution["delay_evolution"] = (
    evolution
    .apply(classify_change, axis=1)
)


# ============================================================
# VALIDATION
# ============================================================

print("\nDelay observation counts:")

print(
    evolution["delay_observations"]
    .value_counts()
    .sort_index()
    .to_string()
)

print("\nDelay evolution categories:")

category_counts = (
    evolution["delay_evolution"]
    .value_counts()
    .reindex(
        [
            "increased",
            "decreased",
            "stable",
            "no_delay_data"
        ],
        fill_value=0
    )
)

category_percentages = (
    category_counts
    / len(evolution)
    * 100
)

category_summary = pd.DataFrame({
    "events": category_counts,
    "percentage": category_percentages
})

print(
    category_summary
    .to_string(
        formatters={
            "percentage": "{:.2f}%".format
        }
    )
)

print(
    "\nTotal classified events:",
    category_counts.sum()
)

assert category_counts.sum() == len(evolution)

assert (
    evolution.loc[
        evolution["delay_observations"] < 2,
        "delay_evolution"
    ]
    .eq("no_delay_data")
    .all()
)


# ============================================================
# SORT AND SAVE NEW CSV
# ============================================================

evolution = evolution.sort_values(
    "delay_change",
    ascending=False,
    na_position="last"
)

evolution.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# MOST INCREASED DELAYS
# ============================================================

display_columns = [
    "station_name",
    "train_number",
    "train_type",
    "event_type",
    "planned_time",
    "snapshots_observed",
    "delay_observations",
    "first_delay",
    "last_delay",
    "delay_change"
]

increased_events = evolution[
    evolution["delay_evolution"] == "increased"
]

print("\nTop 20 events with largest increase:")

print(
    increased_events[
        display_columns
    ]
    .head(20)
    .to_string(index=False)
)


# ============================================================
# MOST DECREASED DELAYS
# ============================================================

decreased_events = evolution[
    evolution["delay_evolution"] == "decreased"
]

print("\nTop 20 events with largest decrease:")

print(
    decreased_events[
        display_columns
    ]
    .sort_values(
        "delay_change",
        ascending=True
    )
    .head(20)
    .to_string(index=False)
)


# ============================================================
# FINAL
# ============================================================

print("\nAnalysis finished.")

print("\nNew file created:")
print(OUTPUT_FILE)
