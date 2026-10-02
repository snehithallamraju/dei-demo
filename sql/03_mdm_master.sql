-- STEP: DATA GOVERNANCE / MDM  (part 2)
-- A master data table: every spelling points to ONE golden record.
CREATE OR REPLACE TABLE restaurant_master AS
SELECT DISTINCT
  "Restaurant Name" AS source_name,
  CASE
    WHEN lower(trim("Restaurant Name")) IN ('mama''s kitchen', 'mamas kitchen', 'mama''s kitchen - agra')
      THEN 'Mama''s Kitchen'
    ELSE trim("Restaurant Name")
  END AS golden_name
FROM orders_raw;

SELECT * FROM restaurant_master ORDER BY golden_name, source_name;
