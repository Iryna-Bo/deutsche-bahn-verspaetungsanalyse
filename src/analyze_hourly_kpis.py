import duckdb

URL = (
    "https://huggingface.co/datasets/piebro/deutsche-bahn-data/"
    "resolve/main/monthly_processed_data/data-2025-03.parquet"
)

con = duckdb.connect()

query = f"""
WITH base AS (
    SELECT
        COALESCE(
            departure_planned_time,
            arrival_planned_time
        ) AS planned_event_time,

        delay_in_min,
        arrival_is_canceled,
        departure_is_canceled

    FROM read_parquet('{URL}')
),

hourly AS (
    SELECT
        EXTRACT(HOUR FROM planned_event_time) AS hour,

        COUNT(*) AS observations,

        MEDIAN(delay_in_min) AS median_delay,

        QUANTILE_CONT(delay_in_min, 0.95) AS p95_delay,

        COUNT(*) FILTER (
            WHERE delay_in_min >= 5
        ) AS delay_5_plus,

        COUNT(*) FILTER (
            WHERE delay_in_min >= 15
        ) AS delay_15_plus,

        COUNT(*) FILTER (
            WHERE delay_in_min >= 60
        ) AS delay_60_plus,

        COUNT(*) FILTER (
            WHERE arrival_is_canceled = TRUE
               OR departure_is_canceled = TRUE
        ) AS canceled_events

    FROM base
    WHERE planned_event_time IS NOT NULL
    GROUP BY hour
)

SELECT
    CAST(hour AS INTEGER) AS hour,
    observations,

    ROUND(median_delay, 2) AS median_delay,
    ROUND(p95_delay, 2) AS p95_delay,

    delay_5_plus,
    ROUND(
        100.0 * delay_5_plus / observations, 2
    ) AS pct_delay_5_plus,

    delay_15_plus,
    ROUND(
        100.0 * delay_15_plus / observations, 2
    ) AS pct_delay_15_plus,

    delay_60_plus,
    ROUND(
        100.0 * delay_60_plus / observations, 2
    ) AS pct_delay_60_plus,

    canceled_events,
    ROUND(
        100.0 * canceled_events / observations, 2
    ) AS pct_canceled

FROM hourly
ORDER BY hour
"""

result = con.execute(query).fetchdf()

print("\n" + "=" * 110)
print("HOURLY KPI ANALYSIS — MÄRZ 2025")
print("=" * 110)

print(result.to_string(index=False))

print("\n" + "=" * 110)
print("HOURS WITH HIGHEST SHARE OF DELAYS >= 5 MIN")
print("=" * 110)

print(
    result.sort_values(
        "pct_delay_5_plus",
        ascending=False
    ).head(10).to_string(index=False)
)

print("\n" + "=" * 110)
print("HOURS WITH HIGHEST SHARE OF DELAYS >= 15 MIN")
print("=" * 110)

print(
    result.sort_values(
        "pct_delay_15_plus",
        ascending=False
    ).head(10).to_string(index=False)
)

print("\n" + "=" * 110)
print("HOURS WITH HIGHEST SHARE OF DELAYS >= 60 MIN")
print("=" * 110)

print(
    result.sort_values(
        "pct_delay_60_plus",
        ascending=False
    ).head(10).to_string(index=False)
)