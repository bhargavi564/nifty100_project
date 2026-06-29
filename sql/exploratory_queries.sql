SELECT COUNT(*) FROM companies;

SELECT COUNT(*) FROM balancesheet;

SELECT company_id, MAX(year) FROM balancesheet GROUP BY company_id;

SELECT company_id, COUNT(*) FROM stock_prices GROUP BY company_id;

SELECT sector,COUNT(*) FROM companies GROUP BY sector;

SELECT * FROM profitandloss LIMIT 10;

SELECT * FROM financial_ratios LIMIT 10;

SELECT company_id, AVG(close) FROM stock_prices GROUP BY company_id;

SELECT * FROM documents LIMIT 5;

SELECT * FROM prosandcons LIMIT 5;

SELECT COUNT(*) FROM companies;

SELECT COUNT(*) FROM stock_prices;

PRAGMA foreign_key_check;