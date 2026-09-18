import duckdb

result = duckdb.sql(
    """
    SELECT
        snapshot_id,
        COUNT(*) AS total_events,
        COUNT(CASE WHEN delay_minutes > 0 THEN 1 END) AS delayed_events,
        ROUND(
            100.0 * COUNT(CASE WHEN delay_minutes > 0 THEN 1 END)
            / COUNT(*),
            1
        ) AS delayed_pct,
        ROUND(AVG(delay_minutes), 2) AS avg_delay,
        MAX(delay_minutes) AS max_delay
    FROM 'data/processed/db_api_test_30min_v2.parquet'
    GROUP BY snapshot_id
    ORDER BY snapshot_id
    """
)

print(result)