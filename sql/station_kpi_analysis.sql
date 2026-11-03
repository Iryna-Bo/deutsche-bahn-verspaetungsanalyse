
-- ============================================================
-- STATION KPI ANALYSIS – MARCH 2025
-- Data source: Deutsche Bahn historical data (Parquet)
-- SQL engine: DuckDB
-- Analysis unit: Station-level observations
-- Filter: delay_in_min IS NOT NULL
-- ============================================================

WITH base AS (
    SELECT
        station_name,
        delay_in_min,
        arrival_is_canceled,
        departure_is_canceled
    FROM read_parquet(
        'https://huggingface.co/datasets/piebro/deutsche-bahn-data/resolve/main/monthly_processed_data/data-2025-03.parquet'
    )
    WHERE COALESCE(
        departure_planned_time,
        arrival_planned_time
    ) IS NOT NULL
),

station_kpis AS (
    SELECT
        station_name,

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
    GROUP BY station_name
)

SELECT
    station_name,
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

FROM station_kpis
ORDER BY pct_delay_5_plus DESC;
