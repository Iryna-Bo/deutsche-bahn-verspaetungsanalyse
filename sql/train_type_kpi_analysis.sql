
-- ============================================================
-- TRAIN TYPE KPI ANALYSIS – MARCH 2025
-- Data source: Deutsche Bahn historical data (Parquet)
-- SQL engine: DuckDB
-- Analysis unit: Scheduled Station Event
-- ============================================================

WITH base AS (
    SELECT
        train_type,
        delay_in_min,
        arrival_is_canceled,
        departure_is_canceled,
        is_replacement_train
    FROM read_parquet(
        'https://huggingface.co/datasets/piebro/deutsche-bahn-data/resolve/main/monthly_processed_data/data-2025-03.parquet'
    )
    WHERE train_type IN ('S', 'RB', 'RE', 'IC', 'ICE')
      AND COALESCE(
          departure_planned_time,
          arrival_planned_time
      ) IS NOT NULL
),

train_type_kpis AS (
    SELECT
        train_type,

        COUNT(*) AS observations,
        COUNT(delay_in_min) AS delay_observations,

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
        ) AS canceled_events,

        COUNT(*) FILTER (
            WHERE is_replacement_train = TRUE
        ) AS replacement_events

    FROM base
    GROUP BY train_type
)

SELECT
    train_type,
    observations,
    delay_observations,

    ROUND(median_delay, 2) AS median_delay,
    ROUND(p95_delay, 2) AS p95_delay,

    delay_5_plus,
    ROUND(
        100.0 * delay_5_plus / delay_observations, 2
    ) AS pct_delay_5_plus,

    delay_15_plus,
    ROUND(
        100.0 * delay_15_plus / delay_observations, 2
    ) AS pct_delay_15_plus,

    delay_60_plus,
    ROUND(
        100.0 * delay_60_plus / delay_observations, 2
    ) AS pct_delay_60_plus,

    canceled_events,
    ROUND(
        100.0 * canceled_events / observations, 2
    ) AS pct_canceled,

    replacement_events,
    ROUND(
        100.0 * replacement_events / observations, 2
    ) AS pct_replacement

FROM train_type_kpis
ORDER BY observations DESC;
