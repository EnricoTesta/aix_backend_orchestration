CREATE OR REPLACE TABLE `aix-data-stocks.inference_layer.d_backfill_inference` AS
SELECT F.*
FROM `aix-data-stocks.raw_data_layer.p_signals` P
LEFT JOIN `aix-data-stocks.raw_data_layer.map_ticker_yahoo_bloomberg` T
ON P.Ticker = T.bloomberg_ticker
LEFT JOIN `aix-data-stocks.information_layer.f_prices` F
ON T.yahoo_ticker = F.Ticker
AND P.Obs_Date = F.OBS_DATE
WHERE P.Obs_Date = '?' -- replace with current observation date
