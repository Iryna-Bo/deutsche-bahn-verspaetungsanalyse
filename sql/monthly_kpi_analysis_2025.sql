
-- ============================================================
-- Deutsche Bahn: Monthly KPI Analysis 2025
-- Station cohort: 107 stations from March 2025
-- Analysis unit: Scheduled Station Event
-- ============================================================

WITH station_cohort AS (
    SELECT DISTINCT
        station_name
    FROM read_parquet(
        'https://huggingface.co/datasets/piebro/deutsche-bahn-data/resolve/main/monthly_processed_data/data-2025-03.parquet'
    )
    WHERE station_name IS NOT NULL
),

base AS (

    -- January 2025
    SELECT
        '01' AS month_num,
        'Januar' AS month,
        station_name,
        delay_in_min,
        arrival_is_canceled,
        departure_is_canceled,
        is_replacement_train,
        COALESCE(
            departure_planned_time,
            arrival_planned_time
        ) AS planned_event_time
    FROM read_parquet(
        'https://huggingface.co/datasets/piebro/deutsche-bahn-data/resolve/main/monthly_processed_data/data-2025-01.parquet'
    )

    UNION ALL

    -- February 2025
    SELECT
        '02' AS month_num,
        'Februar' AS month,
        station_name,
        delay_in_min,
        arrival_is_canceled,
        departure_is_canceled,
        is_replacement_train,
        COALESCE(
            departure_planned_time,
            arrival_planned_time
        ) AS planned_event_time
    FROM read_parquet(
        'https://huggingface.co/datasets/piebro/deutsche-bahn-data/resolve/main/monthly_processed_data/data-2025-02.parquet'
    )

    UNION ALL

    -- March 2025
    SELECT
        '03' AS month_num,
        'März' AS month,
        station_name,
        delay_in_min,
        arrival_is_canceled,
        departure_is_canceled,
        is_replacement_train,
        COALESCE(
            departure_planned_time,
            arrival_planned_time
        ) AS planned_event_time
    FROM read_parquet(
        'https://huggingface.co/datasets/piebro/deutsche-bahn-data/resolve/main/monthly_processed_data/data-2025-03.parquet'
    )

    UNION ALL

    -- April 2025
    SELECT
        '04' AS month_num,
        'April' AS month,
        station_name,
        delay_in_min,
        arrival_is_canceled,
        departure_is_canceled,
        is_replacement_train,
        COALESCE(
            departure_planned_time,
            arrival_planned_time
        ) AS planned_event_time
    FROM read_parquet(
        'https://huggingface.co/datasets/piebro/deutsche-bahn-data/resolve/main/monthly_processed_data/data-2025-04.parquet'
    )

    UNION ALL

    -- May 2025
    SELECT
        '05' AS month_num,
        'Mai' AS month,
        station_name,
        delay_in_min,
        arrival_is_canceled,
        departure_is_canceled,
        is_replacement_train,
        COALESCE(
            departure_planned_time,
            arrival_planned_time
        ) AS planned_event_time
    FROM read_parquet(
        'https://huggingface.co/datasets/piebro/deutsche-bahn-data/resolve/main/monthly_processed_data/data-2025-05.parquet'
    )

    UNION ALL

    -- June 2025
    SELECT
        '06' AS month_num,
        'Juni' AS month,
        station_name,
        delay_in_min,
        arrival_is_canceled,
        departure_is_canceled,
        is_replacement_train,
        COALESCE(
            departure_planned_time,
            arrival_planned_time
        ) AS planned_event_time
    FROM read_parquet(
        'https://huggingface.co/datasets/piebro/deutsche-bahn-data/resolve/main/monthly_processed_data/data-2025-06.parquet'
    )

    UNION ALL

    -- July 2025
    SELECT
        '07' AS month_num,
        'Juli' AS month,
        station_name,
        delay_in_min,
        arrival_is_canceled,
        departure_is_canceled,
        is_replacement_train,
        COALESCE(
            departure_planned_time,
            arrival_planned_time
        ) AS planned_event_time
    FROM read_parquet(
        'https://huggingface.co/datasets/piebro/deutsche-bahn-data/resolve/main/monthly_processed_data/data-2025-07.parquet'
    )

    UNION ALL

    -- August 2025
    SELECT
        '08' AS month_num,
        'August' AS month,
        station_name,
        delay_in_min,
        arrival_is_canceled,
        departure_is_canceled,
        is_replacement_train,
        COALESCE(
            departure_planned_time,
            arrival_planned_time
        ) AS planned_event_time
    FROM read_parquet(
        'https://huggingface.co/datasets/piebro/deutsche-bahn-data/resolve/main/monthly_processed_data/data-2025-08.parquet'
    )

    UNION ALL

    -- September 2025
    SELECT
        '09' AS month_num,
        'September' AS month,
        station_name,
        delay_in_min,
        arrival_is_canceled,
        departure_is_canceled,
        is_replacement_train,
        COALESCE(
            departure_planned_time,
            arrival_planned_time
        ) AS planned_event_time
    FROM read_parquet(
        'https://huggingface.co/datasets/piebro/deutsche-bahn-data/resolve/main/monthly_processed_data/data-2025-09.parquet'
    )

    UNION ALL

    -- October 2025
    SELECT
        '10' AS month_num,
        'Oktober' AS month,
        station_name,
        delay_in_min,
        arrival_is_canceled,
        departure_is_canceled,
        is_replacement_train,
        COALESCE(
            departure_planned_time,
            arrival_planned_time
        ) AS planned_event_time
    FROM read_parquet(
        'https://huggingface.co/datasets/piebro/deutsche-bahn-data/resolve/main/monthly_processed_data/data-2025-10.parquet'
    )

    UNION ALL

    -- November 2025
    SELECT
        '11' AS month_num,
        'November' AS month,
        station_name,
        delay_in_min,
        arrival_is_canceled,
        departure_is_canceled,
        is_replacement_train,
        COALESCE(
            departure_planned_time,
            arrival_planned_time
        ) AS planned_event_time
    FROM read_parquet(
        'https://huggingface.co/datasets/piebro/deutsche-bahn-data/resolve/main/monthly_processed_data/data-2025-11.parquet'
    )

    UNION ALL

    -- December 2025
    SELECT
        '12' AS month_num,
        'Dezember' AS month,
        station_name,
        delay_in_min,
        arrival_is_canceled,
        departure_is_canceled,
        is_replacement_train,
        COALESCE(
            departure_planned_time,
            arrival_planned_time
        ) AS planned_event_time
    FROM read_parquet(
        'https://huggingface.co/datasets/piebro/deutsche-bahn-data/resolve/main/monthly_processed_data/data-2025-12.parquet'
    )
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
        / NULLIF(
            COUNT(*) FILTER (
                WHERE delay_in_min IS NOT NULL
            ), 0
        ),
        2
    ) AS delay_5_plus_pct,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE delay_in_min >= 15
        )
        / NULLIF(
            COUNT(*) FILTER (
                WHERE delay_in_min IS NOT NULL
            ), 0
        ),
        2
    ) AS delay_15_plus_pct,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE delay_in_min >= 60
        )
        / NULLIF(
            COUNT(*) FILTER (
                WHERE delay_in_min IS NOT NULL
            ), 0
        ),
        2
    ) AS delay_60_plus_pct,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE arrival_is_canceled
               OR departure_is_canceled
        )
        / NULLIF(COUNT(*), 0),
        2
    ) AS cancellation_pct,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE is_replacement_train
        )
        / NULLIF(COUNT(*), 0),
        2
    ) AS replacement_pct

FROM filtered

GROUP BY
    month_num,
    month

ORDER BY
    month_num;
