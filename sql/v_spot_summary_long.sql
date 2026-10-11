CREATE OR REPLACE TABLE marts.spot_summary_long AS 
SELECT 
    受渡日,
    年度,
    順序月,
    月,
    時刻コード,
    REPLACE(REPLACE(エリア名, 'エリアプライス', ''), '(円/kWh)', '') AS エリア,
    エリアプライス
FROM marts.spot_summary
UNPIVOT (
    エリアプライス FOR エリア名 IN (
        "エリアプライス北海道(円/kWh)", 
        "エリアプライス東北(円/kWh)", 
        "エリアプライス東京(円/kWh)", 
        "エリアプライス中部(円/kWh)", 
        "エリアプライス北陸(円/kWh)", 
        "エリアプライス関西(円/kWh)", 
        "エリアプライス中国(円/kWh)", 
        "エリアプライス四国(円/kWh)", 
        "エリアプライス九州(円/kWh)"
    )
);