
-- ============================================================
-- STATISTICAL ANALYSIS – MARCH 2025
-- Data source: Deutsche Bahn historical data (Parquet)
-- SQL engine: DuckDB
-- ============================================================

SELECT
    train_type,
    delay_in_min
FROM read_parquet(
    'https://huggingface.co/datasets/piebro/deutsche-bahn-data/resolve/main/monthly_processed_data/data-2025-03.parquet'
)
WHERE train_type IN ('S', 'RB', 'RE', 'IC', 'ICE')
  AND delay_in_min IS NOT NULL;
