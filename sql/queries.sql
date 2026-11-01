-- Warehouse is SQLite kpi.db, table operations (SYNTHETIC)
SELECT region, SUM(revenue) AS revenue FROM operations WHERE status='Completed' GROUP BY region ORDER BY revenue DESC;
SELECT category, AVG(revenue) AS aov FROM operations GROUP BY category;
