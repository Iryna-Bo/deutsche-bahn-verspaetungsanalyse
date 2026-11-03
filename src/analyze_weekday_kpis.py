import duckdb

URL = (
    "https://huggingface.co/datasets/piebro/deutsche-bahn-data/"
    "resolve/main/monthly_processed_data/data-2025-03.parquet"
)

con = duckdb.connect()

query = f"""
WITH base AS (
    SELECT
        delay_in_min,
        arrival_is_canceled,
        departure_is_canceled,
        planned_event_time
    FROM (
        SELECT
            delay_in_min,
            arrival_is_canceled,
            departure_is_canceled,
            COALESCE(
                departure_planned_time,
                arrival_planned_time
            ) AS planned_event_time
        FROM read_parquet('{URL}')
    )
    WHERE planned_event_time IS NOT NULL
),

classified AS (
    SELECT
        *,
        EXTRACT(ISODOW FROM planned_event_time) AS weekday_num,
        CASE EXTRACT(ISODOW FROM planned_event_time)
            WHEN 1 THEN 'Montag'
            WHEN 2 THEN 'Dienstag'
            WHEN 3 THEN 'Mittwoch'
            WHEN 4 THEN 'Donnerstag'
            WHEN 5 THEN 'Freitag'
            WHEN 6 THEN 'Samstag'
            WHEN 7 THEN 'Sonntag'
        END AS weekday
    FROM base
)

SELECT
    weekday_num,
    weekday,

    COUNT(*) AS observations,

    ROUND(MEDIAN(delay_in_min), 2) AS median_delay,

    ROUND(
        QUANTILE_CONT(delay_in_min, 0.95),
        2
    ) AS p95_delay,

    ROUND(
        100.0 * COUNT(*) FILTER (WHERE delay_in_min >= 5)
        / COUNT(*) FILTER (WHERE delay_in_min IS NOT NULL),
        2
    ) AS delay_5_plus_pct,

    ROUND(
        100.0 * COUNT(*) FILTER (WHERE delay_in_min >= 15)
        / COUNT(*) FILTER (WHERE delay_in_min IS NOT NULL),
        2
    ) AS delay_15_plus_pct,

    ROUND(
        100.0 * COUNT(*) FILTER (WHERE delay_in_min >= 60)
        / COUNT(*) FILTER (WHERE delay_in_min IS NOT NULL),
        2
    ) AS delay_60_plus_pct,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE arrival_is_canceled OR departure_is_canceled
        ) / COUNT(*),
        2
    ) AS cancellation_pct

FROM classified

GROUP BY
    weekday_num,
    weekday

ORDER BY
    weekday_num;
"""

result = con.execute(query).fetchdf()

print(result.to_string(index=False))