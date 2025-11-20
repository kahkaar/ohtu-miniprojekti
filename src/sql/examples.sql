-- Using BEGIN and ROLLBACK to avoid making changes
BEGIN;
-- Example SQL snippets for using the citations schema
-- Insert a citation with flexible JSONB fields
INSERT INTO citations (entry_type_id, citation_key, fields)
VALUES (
  1, -- article
  'Smith2020',
  '{"title":"A Survey on ML","year":2020,"author":["Smith","Jones"],"publisher":"OUP"}'::jsonb
);

-- Query examples
-- Find all articles from year 2020
SELECT c.* FROM citations c JOIN entry_types t ON t.id = c.entry_type_id
WHERE t.name = 'article' AND c.fields->>'year' = '2020';

-- Find citations that contain a specific JSON fragment (containment)
SELECT * FROM citations WHERE fields @> '{"publisher":"OUP"}'::jsonb;

-- Update JSON fields (add or overwrite a key)
UPDATE citations SET fields = fields || '{"publisher":"OUP"}'::jsonb WHERE citation_key = 'Smith2020';

-- Remove a key from JSON fields
UPDATE citations SET fields = fields - 'oldkey' WHERE id = 1;

-- Using BEGIN and ROLLBACK to avoid making changes
ROLLBACK;
