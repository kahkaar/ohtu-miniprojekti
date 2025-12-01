BEGIN;
-- Initialization script for the citations schema
-- Inserts supported entry types and supported fields from the reference guide.
-- Idempotent: running multiple times won't create duplicates (uses ON CONFLICT DO NOTHING).

-- Insert supported entry types
INSERT INTO entry_types (name) VALUES
  ('article'),  ('book'),       ('mvbook'),
  ('inbook'),   ('bookinbook'), ('suppbook'),
  ('booklet'),  ('collection'), ('mvcollection'),
  ('incollection'), ('suppcollection'), ('manual'),
  ('misc'),     ('online'),     ('patent'),
  ('periodical'), ('suppperiodical'), ('proceedings'),
  ('mvproceedings'), ('inproceedings'), ('reference'),
  ('mvreference'), ('inreference'), ('report'),
  ('set'), ('thesis'), ('unpublished'),
  ('custom'), ('conference'), ('electronic'),
  ('masterthesis'), ('phdthesis'), ('techreport')
ON CONFLICT (name) DO NOTHING;

-- Insert supported entry fields
INSERT INTO default_fields (name) VALUES
  ('abstract'), ('addendum'), ('afterword'), ('annotate'),
  ('author'), ('authortype'), ('bookauthor'), ('bookpagination'),
  ('booksubtitle'), ('booktitle'), ('chapter'), ('commentator'),
  ('date'), ('doi'), ('edition'), ('editor'),
  ('editortype'), ('eid'), ('entrysubtype'), ('eprint'),
  ('eprinttype'), ('eprintclass'), ('eventdate'), ('eventtitle'),
  ('file'), ('foreword'), ('holder'), ('howpublished'),
  ('indextitle'), ('institution'), ('introduction'), ('isan'),
  ('isbn'), ('ismn'), ('isrn'), ('issue'),
  ('issuesubtitle'), ('issuetitle'), ('iswc'), ('journalsubtitle'),
  ('journaltitle'), ('label'), ('language'), ('library'),
  ('location'), ('mainsubtitle'), ('maintitle'), ('month'),
  ('note'), ('number'), ('organization'), ('origdate'),
  ('origlanguage'), ('origlocation'), ('origpublisher'), ('origtitle'),
  ('pages'), ('pagetotal'), ('pagination'), ('part'),
  ('publisher'), ('pubstate'), ('reprinttitle'), ('series'),
  ('shortauthor'), ('shortedition'), ('shorthand'), ('shorthandintro'),
  ('shortjournal'), ('shortseries'), ('shorttitle'), ('subtitle'),
  ('title'), ('translator'), ('type'), ('url'),
  ('venue'), ('version'), ('volume'), ('year')
ON CONFLICT (name) DO NOTHING;

-- Insert default entry fields for each entry type
-- @article: author, title, journaltitle, year
INSERT INTO default_entry_fields (entry_type_id, default_field_id)
SELECT et.id, df.id
FROM entry_types et JOIN default_fields df ON df.name IN ('author','title','journaltitle','year')
WHERE et.name = 'article'
ON CONFLICT (entry_type_id, default_field_id) DO NOTHING;

-- @book: author, title, publisher, year
INSERT INTO default_entry_fields (entry_type_id, default_field_id)
SELECT et.id, df.id
FROM entry_types et JOIN default_fields df ON df.name IN ('author','title','publisher','year')
WHERE et.name = 'book'
ON CONFLICT (entry_type_id, default_field_id) DO NOTHING;

-- @booklet: label (key), title
INSERT INTO default_entry_fields (entry_type_id, default_field_id)
SELECT et.id, df.id
FROM entry_types et JOIN default_fields df ON df.name IN ('label','title')
WHERE et.name = 'booklet'
ON CONFLICT (entry_type_id, default_field_id) DO NOTHING;

-- @conference: author, booktitle, title, year
INSERT INTO default_entry_fields (entry_type_id, default_field_id)
SELECT et.id, df.id
FROM entry_types et JOIN default_fields df ON df.name IN ('author','booktitle','title','year')
WHERE et.name = 'conference'
ON CONFLICT (entry_type_id, default_field_id) DO NOTHING;

-- @inbook: author, title, publisher, year, chapter
INSERT INTO default_entry_fields (entry_type_id, default_field_id)
SELECT et.id, df.id
FROM entry_types et JOIN default_fields df ON df.name IN ('author','title','publisher','year','chapter')
WHERE et.name = 'inbook'
ON CONFLICT (entry_type_id, default_field_id) DO NOTHING;

-- @incollection: author, title, booktitle, publisher, year
INSERT INTO default_entry_fields (entry_type_id, default_field_id)
SELECT et.id, df.id
FROM entry_types et JOIN default_fields df ON df.name IN ('author','title','booktitle','publisher','year')
WHERE et.name = 'incollection'
ON CONFLICT (entry_type_id, default_field_id) DO NOTHING;

-- @inproceedings: author, title, booktitle, year
INSERT INTO default_entry_fields (entry_type_id, default_field_id)
SELECT et.id, df.id
FROM entry_types et JOIN default_fields df ON df.name IN ('author','title','booktitle','year')
WHERE et.name = 'inproceedings'
ON CONFLICT (entry_type_id, default_field_id) DO NOTHING;

-- @manual: label (key), title
INSERT INTO default_entry_fields (entry_type_id, default_field_id)
SELECT et.id, df.id
FROM entry_types et JOIN default_fields df ON df.name IN ('label','title')
WHERE et.name = 'manual'
ON CONFLICT (entry_type_id, default_field_id) DO NOTHING;

-- @mastersthesis: author, title, institution (school), year
INSERT INTO default_entry_fields (entry_type_id, default_field_id)
SELECT et.id, df.id
FROM entry_types et JOIN default_fields df ON df.name IN ('author','title','institution','year')
WHERE et.name = 'masterthesis'
ON CONFLICT (entry_type_id, default_field_id) DO NOTHING;

-- @misc: label (key), note
INSERT INTO default_entry_fields (entry_type_id, default_field_id)
SELECT et.id, df.id
FROM entry_types et JOIN default_fields df ON df.name IN ('label','note')
WHERE et.name = 'misc'
ON CONFLICT (entry_type_id, default_field_id) DO NOTHING;

-- @phdthesis: author, title, institution (school), year
INSERT INTO default_entry_fields (entry_type_id, default_field_id)
SELECT et.id, df.id
FROM entry_types et JOIN default_fields df ON df.name IN ('author','title','institution','year')
WHERE et.name = 'phdthesis'
ON CONFLICT (entry_type_id, default_field_id) DO NOTHING;

-- @proceedings: label (key), title, year
INSERT INTO default_entry_fields (entry_type_id, default_field_id)
SELECT et.id, df.id
FROM entry_types et JOIN default_fields df ON df.name IN ('label','title','year')
WHERE et.name = 'proceedings'
ON CONFLICT (entry_type_id, default_field_id) DO NOTHING;

-- @techreport: author, title, institution, year
INSERT INTO default_entry_fields (entry_type_id, default_field_id)
SELECT et.id, df.id
FROM entry_types et JOIN default_fields df ON df.name IN ('author','title','institution','year')
WHERE et.name = 'techreport'
ON CONFLICT (entry_type_id, default_field_id) DO NOTHING;

-- @unpublished: author, title, note
INSERT INTO default_entry_fields (entry_type_id, default_field_id)
SELECT et.id, df.id
FROM entry_types et JOIN default_fields df ON df.name IN ('author','title','note')
WHERE et.name = 'unpublished'
ON CONFLICT (entry_type_id, default_field_id) DO NOTHING;

COMMIT;
