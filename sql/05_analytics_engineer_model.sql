-- STEP: ANALYTICS ENGINEER
-- Turn one-time cleanup into a reusable, tested model that everyone can trust every day.
CREATE OR REPLACE VIEW orders_clean AS
WITH parsed AS (
  SELECT
    trim("Order ID")                                                  AS order_id,
    CAST(COALESCE(
      TRY_STRPTIME("Order Date", '%Y-%m-%d'),
      TRY_STRPTIME("Order Date", '%d/%m/%Y'),
      TRY_STRPTIME("Order Date", '%b %d %Y')) AS DATE)                AS order_date,
    "Customer"                                                        AS customer_id,
    upper(trim("Area"))                                               AS area,
    m.golden_name                                                     AS restaurant,
    TRY_CAST(replace("Amount", '₹', '') AS DOUBLE)                    AS amount_inr,
    TRY_CAST(trim(replace("Delivery Time", 'min', '')) AS INTEGER)    AS delivery_minutes
  FROM orders_raw r
  JOIN restaurant_master m ON r."Restaurant Name" = m.source_name
  WHERE "Order ID" IS NOT NULL
  QUALIFY row_number() OVER (PARTITION BY "Order ID") = 1           -- drop duplicate loads
),
with_next AS (
  SELECT *,
    lead(order_date) OVER (PARTITION BY customer_id ORDER BY order_date, order_id) AS next_order_date
  FROM parsed
)
SELECT
  order_id,
  order_date,
  strftime(order_date, '%Y-%m')                                       AS order_month,
  customer_id,
  area,
  restaurant,
  amount_inr,
  delivery_minutes,
  CASE WHEN delivery_minutes > 45 THEN 1 ELSE 0 END                   AS is_late,
  CASE
    WHEN order_date > DATE '2026-05-31' THEN NULL                     -- too recent to know yet
    WHEN next_order_date <= order_date + INTERVAL 30 DAY THEN 1
    ELSE 0
  END                                                                 AS reordered_within_30_days
FROM with_next;

-- Data tests: every number below should be 0. If one isn't, the pipeline stops.
SELECT
  (SELECT count(*) FROM orders_clean WHERE order_id IS NULL)                     AS test_missing_ids,
  (SELECT count(*) - count(DISTINCT order_id) FROM orders_clean)                 AS test_duplicate_ids,
  (SELECT count(*) FROM orders_clean WHERE order_date IS NULL)                   AS test_unparsed_dates,
  (SELECT count(DISTINCT area) - 8 FROM orders_clean)                            AS test_unexpected_areas;

SELECT * FROM orders_clean LIMIT 5;

-- Publish the trusted model so other tools (the AI step) can use it
COPY (SELECT * FROM orders_clean) TO 'data/orders_clean.parquet' (FORMAT parquet);
