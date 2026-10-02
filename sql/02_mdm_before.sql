-- STEP: DATA GOVERNANCE / MDM  (part 1)
-- Ask the room first: "Which restaurant earns the most?"
-- Revenue by restaurant name, exactly as the names appear in the data.
SELECT
  "Restaurant Name"                                            AS restaurant,
  count(*)                                                     AS orders,
  round(sum(TRY_CAST(replace("Amount", '₹', '') AS DOUBLE)))  AS revenue_inr
FROM orders_raw
GROUP BY 1
ORDER BY revenue_inr DESC;
-- Agra Tandoor House looks like #1 ... now read further down the list, slowly.
