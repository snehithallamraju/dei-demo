-- STEP: DATA ENGINEER
-- Load the raw CSV exactly as it arrived. Everything as text, nothing fixed yet.
CREATE OR REPLACE TABLE orders_raw AS
SELECT * FROM read_csv('data/orders_raw.csv', header = true, all_varchar = true);

SELECT count(*) AS rows_loaded FROM orders_raw;
