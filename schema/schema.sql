PRAGMA foreign_keys = ON;

CREATE TABLE Dim_Date(
    date_key INTEGER PRIMARY KEY,
    date_year INT,
    date_month INT
);

CREATE TABLE Dim_Customer(
    customer_key INTEGER PRIMARY KEY,
    customer_name TEXT,
    username TEXT,
    birthdate DATE
);

CREATE TABLE Dim_Account(
    account_key INTEGER PRIMARY KEY,
    account_id_src INTEGER,
    account_limit INTEGER
);

CREATE TABLE Dim_Product(
    product_key INTEGER PRIMARY KEY,
    product_name TEXT
);

CREATE TABLE Bridge_Account_Product(
    account_key INTEGER NOT NULL,
    product_key INTEGER NOT NULL,
    FOREIGN KEY (account_key) REFERENCES Dim_Account(account_key),
    FOREIGN KEY (product_key) REFERENCES Dim_Product(product_key)
);

CREATE TABLE Dim_Tier(
    tier_key INTEGER PRIMARY KEY,
    tier_name TEXT
);

CREATE TABLE Dim_Benefit(
    benefit_key INTEGER PRIMARY KEY,
    benefit_name TEXT
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
    transaction_code TEXT,
    symbol TEXT,
    amount INTEGER,
    FOREIGN KEY (account_key) REFERENCES Dim_Account(account_key),
    FOREIGN KEY (customer_key) REFERENCES Dim_Customer(customer_key),
    FOREIGN KEY (date_key) REFERENCES Dim_Date(date_key)
);

PRAGMA foreign_key_check;