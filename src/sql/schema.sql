-- Dropping existing tables if they exist to avoid conflicts
DROP TABLE IF EXISTS citations;
DROP TABLE IF EXISTS entry_types;
DROP TABLE IF EXISTS default_fields;
DROP TABLE IF EXISTS default_entry_fields;


BEGIN;
-- This is for storing predefined entry types (e.g., article, book, inproceedings)
CREATE TABLE entry_types (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE
);

-- This is for storing the citations with flexible JSONB fields
CREATE TABLE citations (
  id SERIAL PRIMARY KEY,
  entry_type_id INTEGER REFERENCES entry_types(id),
  citation_key TEXT NOT NULL UNIQUE,
  fields JSONB NOT NULL DEFAULT '{}'::jsonb
);

-- This is for storing predefined field names (e.g., title, author, year)
CREATE TABLE default_fields (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE
);

-- This is for linking entry types to their default fields
CREATE TABLE default_entry_fields (
  entry_type_id INTEGER REFERENCES entry_types(id),
  default_field_id INTEGER REFERENCES default_fields(id),
  PRIMARY KEY (entry_type_id, default_field_id)
);


-- Indices to improve query performance
-- GIN index for fast jsonb containment queries on citation fields
CREATE INDEX IF NOT EXISTS citations_fields_gin ON citations USING GIN (fields);

-- Index for filtering by entry_type_id (useful when listing citations by type)
CREATE INDEX IF NOT EXISTS citations_entry_type_idx ON citations (entry_type_id);

-- Expression index for commonly queried scalar inside the JSONB (e.g., year)
CREATE INDEX IF NOT EXISTS citations_fields_year_idx ON citations ((fields->>'year'));

-- Index to speed up lookups of which entry types reference a given default field
CREATE INDEX IF NOT EXISTS default_entry_fields_by_field_idx ON default_entry_fields (default_field_id);

COMMIT;
