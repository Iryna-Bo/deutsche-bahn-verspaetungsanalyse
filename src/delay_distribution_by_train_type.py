

import duckdb

URL = (
    "https://huggingface.co/datasets/piebro/deutsche-bahn-data/"
    "resolve/main/monthly_processed_data/data-2025-03.parquet"
)

con = duckdb.connect()

query = f"""
WITH base AS (
    SELECT
        train_type AS Zugtyp,
        delay_in_min
    FROM read_parquet('{URL}')
    WHERE train_type IN ('IC', 'ICE', 'RB', 'RE', 'S')
      AND delay_in_min IS NOT NULL
      AND delay_in_min >= 0
),

categorized AS (
    SELECT
        Zugtyp,

        CASE
            WHEN delay_in_min = 0
                THEN '0 Min'
            WHEN delay_in_min BETWEEN 1 AND 4
                THEN '1-4 Min'
            WHEN delay_in_min BETWEEN 5 AND 14
                THEN '5-14 Min'
            WHEN delay_in_min BETWEEN 15 AND 59
                THEN '15-59 Min'
            WHEN delay_in_min >= 60
                THEN 'über 60 Min'
        END AS DelayCategory,

        CASE
            WHEN delay_in_min = 0 THEN 1
            WHEN delay_in_min BETWEEN 1 AND 4 THEN 2
            WHEN delay_in_min BETWEEN 5 AND 14 THEN 3
            WHEN delay_in_min BETWEEN 15 AND 59 THEN 4
            WHEN delay_in_min >= 60 THEN 5
        END AS category_order

    FROM base
)

SELECT
    Zugtyp,
    DelayCategory,
    COUNT(*) AS Count

FROM categorized

GROUP BY
    Zugtyp,
    DelayCategory,
    category_order

ORDER BY
    CASE Zugtyp
        WHEN 'IC' THEN 1
        WHEN 'ICE' THEN 2
        WHEN 'RB' THEN 3
        WHEN 'RE' THEN 4
        WHEN 'S' THEN 5
    END,
    category_order
"""

result = con.execute(query).fetchdf()

print("\n" + "=" * 60)
print("DELAY DISTRIBUTION BY TRAIN TYPE — MARCH 2025")
print("=" * 60)

print(result.to_string(index=False))
