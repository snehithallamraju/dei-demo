-- STEP: DATA GOVERNANCE / MDM  (part 3)
-- Same question, after matching every spelling to its golden record.
SELECT
  m.golden_name                                                AS restaurant,
  count(*)                                                     AS orders,
  round(sum(TRY_CAST(replace(r."Amount", '₹', '') AS DOUBLE))) AS revenue_inr
FROM orders_raw r
JOIN restaurant_master m ON r."Restaurant Name" = m.source_name
GROUP BY 1
ORDER BY revenue_inr DESC;
-- The real #1 was hiding. Every dashboard and every AI answer built on the raw names was wrong.
