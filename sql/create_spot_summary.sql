DROP TABLE IF EXISTS marts.spot_summary;

CREATE TABLE marts.spot_summary AS 
WITH base AS (
    SELECT 
        -- CSVの生テキストから先頭10文字（YYYY-MM-DD）だけを切り出す
        SUBSTR(受渡日, 1, 10) AS 受渡日,
        * EXCLUDE (受渡日)
    FROM read_csv_auto('data/spot_summary_*.csv', encoding='shift_jis', all_varchar=true)
)
SELECT 
    受渡日,
    
    -- 4月始まりの年度
    CASE 
        WHEN CAST(SUBSTR(受渡日, 6, 2) AS INTEGER) >= 4 
        THEN SUBSTR(受渡日, 1, 4) || '年度'
        ELSE CAST(CAST(SUBSTR(受渡日, 1, 4) AS INTEGER) - 1 AS VARCHAR) || '年度'
    END AS 年度,
    
    -- 順序月
    CASE 
        WHEN CAST(SUBSTR(受渡日, 6, 2) AS INTEGER) >= 4 THEN CAST(SUBSTR(受渡日, 6, 2) AS INTEGER) - 3
        ELSE CAST(SUBSTR(受渡日, 6, 2) AS INTEGER) + 9 
    END AS 順序月,
    
    -- 月
    CAST(SUBSTR(受渡日, 6, 2) AS INTEGER) AS 月,
    
    * EXCLUDE (受渡日)

FROM base;