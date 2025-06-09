-- 1. ¿Cuál es el promedio, mínimo, máximo y desviación estándar del límite de las cuentas de usuarios?
SELECT
    AVG(account_limit),
    MIN(account_limit),
    MAX(account_limit),
    SQRT(
        SUM(CAST(account_limit AS REAL) * account_limit) / COUNT(*) - AVG(account_limit) * AVG(account_limit) -- desviación estándar poblacional
        -- SUM(CAST(account_limit AS REAL) * account_limit) / (COUNT(*) - 1) - AVG(account_limit) * AVG(account_limit) -- desviación estándar muestral
    ) AS "STDDEV(account_limit)"
FROM Dim_Account;

-- 2. ¿Cuántos clientes poseen más de una cuenta?
WITH accounts_per_customer AS (
    SELECT 
        customer_key,
        COUNT(DISTINCT account_key) AS account_count
    FROM Fact_Transaction
    GROUP BY customer_key
) SELECT COUNT(*)
FROM accounts_per_customer
WHERE account_count > 1;

-- 3. ¿Cuál es el monto promedio y el número de transacciones del mes de junio?
SELECT 
    AVG(amount),
    COUNT(*)
FROM Fact_Transaction
JOIN Dim_Date
ON Dim_Date.date_key = Fact_Transaction.date_key
WHERE Dim_Date.date_month = 6;

-- 4. ¿Cuál es el id de cuenta con la mayor diferencia entre su transacción más alta y más baja?
SELECT 
    Dim_Account.account_id_src,
    MAX(Fact_Transaction.amount) - MIN(Fact_Transaction.amount) AS delta
FROM Dim_Account
JOIN Fact_Transaction ON Fact_Transaction.account_key = Dim_Account.account_key
GROUP BY Dim_Account.account_id_src
ORDER BY delta DESC
LIMIT 1;

-- 5. ¿Cuántas cuentas tienen exactamente 3 productos y, además, uno de esos productos es "Commodity"?
WITH products_per_account AS (
    SELECT 
        Dim_Account.account_key,
        COUNT(DISTINCT Dim_Product.product_key) AS product_count,
        MAX(CASE WHEN Dim_Product.product_name = 'Commodity' THEN 1 ELSE 0 END) AS commodity
    FROM Dim_Account
    JOIN Bridge_Account_Product ON Bridge_Account_Product.account_key = Dim_Account.account_key
    JOIN Dim_Product ON Dim_Product.product_key = Bridge_Account_Product.product_key
    GROUP BY Dim_Account.account_key
) SELECT COUNT(*)
FROM products_per_account
WHERE product_count = 3
AND commodity = 1;

-- 6. ¿Cuál es el nombre del cliente que, en total entre todas sus cuentas, ha realizado la mayor 
--    cantidad de transacciones de tipo sell?
SELECT 
    Dim_Customer.customer_name,
    COUNT(*) AS sell_count
FROM Dim_Customer
JOIN Fact_Transaction ON Fact_Transaction.customer_key = Dim_Customer.customer_key
    AND Fact_Transaction.transaction_code = 'sell'
GROUP BY Dim_Customer.username || Dim_Customer.customer_name
ORDER BY sell_count DESC
LIMIT 1;

-- 7. ¿Cuál es el usuario del cliente cuya cuenta tiene entre 10 y 20 transacciones de tipo “buy”,
--    y que presenta el promedio de inversión más alto por operación de este tipo?
WITH between_10_and_20_buys AS (
    SELECT 
        Dim_Customer.username,
        AVG(Fact_Transaction.amount) avg_amount,
        COUNT(*) AS buy_count
    FROM Dim_Customer
    JOIN Fact_Transaction ON Fact_Transaction.customer_key = Dim_Customer.customer_key
        AND Fact_Transaction.transaction_code = 'buy'
    GROUP BY Dim_Customer.username || Dim_Customer.customer_name
) SELECT 
    username,
    avg_amount
FROM between_10_and_20_buys
WHERE buy_count >= 10 AND buy_count <= 20
ORDER BY avg_amount DESC
LIMIT 1;

-- 8. ¿Cuál es el promedio de transacciones de compra y de venta por acción (campo “symbol”)?
SELECT
    symbol,
    AVG(CASE WHEN transaction_code = 'buy'  THEN CAST(amount AS REAL) END) AS avg_buy,
    AVG(CASE WHEN transaction_code = 'sell' THEN CAST(amount AS REAL) END) AS avg_sell
FROM Fact_Transaction
GROUP BY symbol
ORDER BY symbol
LIMIT 10;

-- 9. ¿Cuáles son los diferentes beneficios que tienen los clientes del tier “Gold”?
SELECT DISTINCT
    Dim_Benefit.benefit_name
FROM Dim_Tier
JOIN Bridge_Customer_Tier_Benefit ON Bridge_Customer_Tier_Benefit.tier_key = Dim_Tier.tier_key
JOIN Dim_Benefit ON Dim_Benefit.benefit_key = Bridge_Customer_Tier_Benefit.benefit_key
WHERE Dim_Tier.tier_name = 'Gold';

-- 10. Obtener la cantidad de clientes por rangos etarios ([10–19], [20–29], etc.), que hayan realizado al menos una
--     compra de acciones de “amzn”. La edad debe calcularse como la diferencia entre la fecha de corte 2025-05-16 y
--     el campo “birthdate
WITH amzn_buyers_ages AS (
    SELECT DISTINCT
        Dim_Customer.customer_key,
        CAST((julianday('2025-05-16') - julianday(Dim_Customer.birthdate)) / 365.25 AS INTEGER) customer_age
    FROM Dim_Customer
    JOIN Fact_Transaction ON Fact_Transaction.customer_key = Dim_Customer.customer_key
        AND Fact_Transaction.symbol = 'amzn'
        AND Fact_Transaction.transaction_code = 'buy'
) SELECT
    CASE
        WHEN customer_age < 10 THEN '[<10]'
        WHEN customer_age BETWEEN 10 AND 19 THEN '[10-19]' 
        WHEN customer_age BETWEEN 20 AND 29 THEN '[20-29]' 
        WHEN customer_age BETWEEN 30 AND 39 THEN '[30-39]' 
        WHEN customer_age BETWEEN 40 AND 49 THEN '[40-49]' 
        WHEN customer_age BETWEEN 50 AND 59 THEN '[50-59]' 
        WHEN customer_age BETWEEN 60 AND 69 THEN '[60-69]' 
        WHEN customer_age BETWEEN 70 AND 79 THEN '[70-79]' 
        WHEN customer_age BETWEEN 80 AND 89 THEN '[80-89]'
        WHEN customer_age >= 90 THEN '[90+]'
    END AS age_group,
    COUNT(*) customer_count
FROM amzn_buyers_ages
GROUP BY age_group
ORDER BY age_group;