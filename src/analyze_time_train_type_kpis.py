import duckdb

URL = (
    "https://huggingface.co/datasets/piebro/deutsche-bahn-data/"
    "resolve/main/monthly_processed_data/data-2025-03.parquet"
)

TRAIN_TYPES = ["S", "RB", "RE", "IC", "ICE"]

con = duckdb.connect()

query = f"""
WITH base AS (
    SELECT
        train_type,
        delay_in_min,
        arrival_is_canceled,
        departure_is_canceled,
        EXTRACT(
            HOUR FROM COALESCE(
                departure_planned_time,
                arrival_planned_time
            )
        ) AS hour
    FROM read_parquet('{URL}')
    WHERE train_type IN ({",".join("'" + t + "'" for t in TRAIN_TYPES)})
      AND COALESCE(departure_planned_time, arrival_planned_time) IS NOT NULL
),

classified AS (
    SELECT
        train_type,
        delay_in_min,
        arrival_is_canceled,
        departure_is_canceled,
        CASE
            WHEN hour BETWEEN 0 AND 5 THEN '00–05 Nacht'
            WHEN hour BETWEEN 6 AND 9 THEN '06–09 Morgen'
            WHEN hour BETWEEN 10 AND 13 THEN '10–13 Vormittag/Mittag'
            WHEN hour BETWEEN 14 AND 17 THEN '14–17 Nachmittag'
            WHEN hour BETWEEN 18 AND 21 THEN '18–21 Abend'
            WHEN hour BETWEEN 22 AND 23 THEN '22–23 Spätabend'
        END AS time_period
    FROM base
)

SELECT
    train_type,
    time_period,

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
    train_type,
    time_period

ORDER BY
    train_type,
    CASE time_period
        WHEN '00–05 Nacht' THEN 1
        WHEN '06–09 Morgen' THEN 2
        WHEN '10–13 Vormittag/Mittag' THEN 3
        WHEN '14–17 Nachmittag' THEN 4
        WHEN '18–21 Abend' THEN 5
        WHEN '22–23 Spätabend' THEN 6
    END;
"""

result = con.execute(query).fetchdf()

print(result.to_string(index=False))