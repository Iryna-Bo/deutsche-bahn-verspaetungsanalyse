import duckdb

result = duckdb.sql(
    """
    SELECT
        train_type,
        COUNT(*) AS total_events,
        COUNT(CASE WHEN delay_minutes > 0 THEN 1 END) AS delayed_events,
        ROUND(AVG(delay_minutes), 2) AS avg_delay,
        MAX(delay_minutes) AS max_delay
    FROM 'data/processed/test_db_snapshot.parquet'
    GROUP BY train_type
    ORDER BY delayed_events DESC
    """
)

print(result)