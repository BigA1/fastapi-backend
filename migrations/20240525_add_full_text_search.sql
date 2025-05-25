-- Add a tsvector column to stories table
ALTER TABLE stories ADD COLUMN IF NOT EXISTS search_vector tsvector GENERATED ALWAYS AS (
    to_tsvector('english', coalesce(title, '') || ' ' || coalesce(content, ''))
) STORED;

-- Create a GIN index for faster full-text search
CREATE INDEX IF NOT EXISTS stories_search_vector_idx ON stories USING GIN (search_vector);

-- Create a function to search stories
CREATE OR REPLACE FUNCTION search_stories(search_query text, user_id uuid)
RETURNS SETOF stories AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM stories
    WHERE stories.user_id = search_stories.user_id
    AND stories.search_vector @@ to_tsquery('english', search_query)
    ORDER BY ts_rank(stories.search_vector, to_tsquery('english', search_query)) DESC;
END;
$$ LANGUAGE plpgsql; 