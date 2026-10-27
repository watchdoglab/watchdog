CREATE TABLE customers (
  id SERIAL PRIMARY KEY,
  email TEXT NOT NULL,
  name TEXT
);
CREATE TABLE cards (
  id SERIAL PRIMARY KEY,
  customer_id INT REFERENCES customers(id),
  pan TEXT NOT NULL,
  cvv TEXT,
  expiry TEXT
);
CREATE TABLE invoices (
  id SERIAL PRIMARY KEY,
  customer_id INT REFERENCES customers(id),
  amount_cents INT
);
