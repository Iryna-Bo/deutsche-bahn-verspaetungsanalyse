import duckdb

BASE_URL = (
    "https://huggingface.co/datasets/piebro/deutsche-bahn-data/"
    "resolve/main/monthly_processed_data/data-2025-"
)

MARCH_URL = f"{BASE_URL}03.parquet"

MONTHS = [
    ("01", "Januar"),
    ("02", "Februar"),
    ("03", "März"),
    ("04", "April"),
    ("05", "Mai"),
    ("06", "Juni"),
    ("07", "Juli"),
    ("08", "August"),
    ("09", "September"),
    ("10", "Oktober"),
    ("11", "November"),
    ("12", "Dezember"),
]

con = duckdb.connect()

# ---------------------------------------------------------
# 1. Build monthly queries
# ---------------------------------------------------------

parts = []

for month_num, month_name in MONTHS:
    url = f"{BASE_URL}{month_num}.parquet"

    parts.append(f"""
        SELECT
            '{month_num}' AS month_num,
            '{month_name}' AS month,
            station_name,
            delay_in_min,
            arrival_is_canceled,
            departure_is_canceled,
            is_replacement_train,
            COALESCE(
                departure_planned_time,
                arrival_planned_time
            ) AS planned_event_time
        FROM read_parquet('{url}')
    """)

union_query = "\nUNION ALL\n".join(parts)


# ---------------------------------------------------------
# 2. Filter all months to the same 107 stations
# ---------------------------------------------------------

query = f"""
WITH station_cohort AS (
    SELECT DISTINCT
        station_name
    FROM read_parquet('{MARCH_URL}')
    WHERE station_name IS NOT NULL
),

base AS (
    {union_query}
),

filtered AS (
    SELECT *
    FROM base
    WHERE planned_event_time IS NOT NULL
      AND station_name IN (
          SELECT station_name
          FROM station_cohort
      )
)

SELECT
    month_num,
    month,

    COUNT(*) AS observations,

    ROUND(
        MEDIAN(delay_in_min),
        2
    ) AS median_delay,

    ROUND(
        QUANTILE_CONT(delay_in_min, 0.95),
        2
    ) AS p95_delay,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE delay_in_min >= 5
        )
        / COUNT(*) FILTER (
            WHERE delay_in_min IS NOT NULL
        ),
        2
    ) AS delay_5_plus_pct,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE delay_in_min >= 15
        )
        / COUNT(*) FILTER (
            WHERE delay_in_min IS NOT NULL
        ),
        2
    ) AS delay_15_plus_pct,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE delay_in_min >= 60
        )
        / COUNT(*) FILTER (
            WHERE delay_in_min IS NOT NULL
        ),
        2
    ) AS delay_60_plus_pct,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE arrival_is_canceled
               OR departure_is_canceled
        )
        / COUNT(*),
        2
    ) AS cancellation_pct,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE is_replacement_train
        )
        / COUNT(*),
        2
    ) AS replacement_pct

FROM filtered

GROUP BY
    month_num,
    month

ORDER BY
    month_num;
"""

result = con.execute(query).fetchdf()

print("\n=== MONTHLY KPI ANALYSIS: 2025 / 107 STATIONS ===\n")
print(result.to_string(index=False))