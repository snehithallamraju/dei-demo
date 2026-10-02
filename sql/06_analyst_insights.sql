-- STEP: DATA ANALYST
-- Now answer the business question: why are repeat orders dropping?

-- 1. The trend: fewer customers come back each month
SELECT order_month,
       round(100 * avg(reordered_within_30_days), 1) AS reorder_rate_pct
FROM orders_clean
WHERE reordered_within_30_days IS NOT NULL
GROUP BY 1 ORDER BY 1;

-- 2. The driver: late deliveries kill repeat orders
SELECT CASE WHEN is_late = 1 THEN 'Late (over 45 min)' ELSE 'On time' END AS delivery,
       count(*)                                      AS orders,
       round(100 * avg(reordered_within_30_days), 1) AS reorder_rate_pct
FROM orders_clean
WHERE reordered_within_30_days IS NOT NULL
GROUP BY 1;

-- 3. Where: late deliveries are concentrated in two areas
SELECT area,
       round(avg(delivery_minutes), 1)   AS avg_delivery_min,
       round(100 * avg(is_late), 1)      AS late_pct
FROM orders_clean
GROUP BY 1 ORDER BY late_pct DESC;
