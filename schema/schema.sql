-- Limpieza de tablas
DROP TABLE IF EXISTS Dim_Date;
DROP TABLE IF EXISTS Dim_Customer;
DROP TABLE IF EXISTS Dim_Account;
DROP TABLE IF EXISTS Dim_Product;
DROP TABLE IF EXISTS Bridge_Account_Product;
DROP TABLE IF EXISTS Dim_Tier;
DROP TABLE IF EXISTS Dim_Benefit;
DROP TABLE IF EXISTS Bridge_Customer_Tier_Benefit;
DROP TABLE IF EXISTS Fact_Transaction;

-- Activación de foreign keys
PRAGMA foreign_keys = ON;

-- Creación de tablas
CREATE TABLE Dim_Date(
    date_key INTEGER PRIMARY KEY,
    date_year INT NOT NULL,
    date_month INT NOT NULL
);

CREATE TABLE Dim_Customer(
    customer_key INTEGER PRIMARY KEY,
    customer_name TEXT NOT NULL,
    username TEXT NOT NULL,
    birthdate DATE NOT NULL
);

CREATE TABLE Dim_Account(
    account_key INTEGER PRIMARY KEY,
    account_id_src INTEGER NOT NULL,
    account_limit INTEGER NOT NULL
);

CREATE TABLE Dim_Product(
    product_key INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL
);

CREATE TABLE Bridge_Account_Product(
    account_key INTEGER NOT NULL,
    product_key INTEGER NOT NULL,
    FOREIGN KEY (account_key) REFERENCES Dim_Account(account_key),
    FOREIGN KEY (product_key) REFERENCES Dim_Product(product_key)
);

CREATE TABLE Dim_Tier(
    tier_key INTEGER PRIMARY KEY,
    tier_name TEXT NOT NULL
);

CREATE TABLE Dim_Benefit(
    benefit_key INTEGER PRIMARY KEY,
    benefit_name TEXT NOT NULL
);

CREATE TABLE Bridge_Customer_Tier_Benefit(
    customer_key INTEGER NOT NULL,
    tier_key INTEGER NOT NULL,
    benefit_key INTEGER NOT NULL,
    FOREIGN KEY (customer_key) REFERENCES Dim_Customer(customer_key),
    FOREIGN KEY (tier_key) REFERENCES Dim_Tier(tier_key),
    FOREIGN KEY (benefit_key) REFERENCES Dim_Benefit(benefit_key)
);

CREATE TABLE Fact_Transaction(
    transaction_key INTEGER PRIMARY KEY,
    account_key INTEGER NOT NULL,
    customer_key INTEGER NOT NULL,
    date_key INTEGER NOT NULL,
    transaction_code TEXT NOT NULL,
    symbol TEXT NOT NULL,
    amount INTEGER NOT NULL,
    FOREIGN KEY (account_key) REFERENCES Dim_Account(account_key),
    FOREIGN KEY (customer_key) REFERENCES Dim_Customer(customer_key),
    FOREIGN KEY (date_key) REFERENCES Dim_Date(date_key)
);