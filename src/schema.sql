-- Using BEGIN and COMMIT to ensure atomic execution
BEGIN;
DROP TABLE IF EXISTS book;

CREATE TABLE book (
  id SERIAL PRIMARY KEY,
  title TEXT,
  author TEXT,
  year INTEGER,
  publisher TEXT,
  address TEXT
);

COMMIT;
