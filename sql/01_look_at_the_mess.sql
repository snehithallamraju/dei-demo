-- STEP: DATA ENGINEER
-- "Real data never arrives clean." Show the room what we are dealing with.

-- 1. A random sample: mixed date formats, rupee signs, "min" suffixes, messy casing
SELECT * FROM orders_raw USING SAMPLE 10 ROWS (reservoir, 7);

-- 2. How bad is it?
SELECT
  count(*) FILTER (WHERE "Order ID" IS NULL)                   AS missing_order_ids,
  count(*) - count(DISTINCT "Order ID")                        AS duplicate_or_missing_ids,
  count(*) FILTER (WHERE "Amount" IS NULL)                     AS missing_amounts,
  count(*) FILTER (WHERE "Amount" LIKE '₹%')                   AS amounts_with_rupee_sign,
  count(*) FILTER (WHERE "Order Date" LIKE '%/%')              AS dates_dd_mm_yyyy,
  count(*) FILTER (WHERE regexp_matches("Order Date", '^[A-Za-z]')) AS dates_like_jan_01,
  count(DISTINCT "Area")                                       AS area_spellings_for_8_areas
FROM orders_raw;
