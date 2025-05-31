-- Add a tsvector column to memories table
ALTER TABLE memories ADD COLUMN IF NOT EXISTS search_vector tsvector GENERATED ALWAYS AS (
    to_tsvector('english', coalesce(title, '') || ' ' || coalesce(content, ''))
) STORED;

-- Create a GIN index for faster full-text search
CREATE INDEX IF NOT EXISTS memories_search_vector_idx ON memories USING GIN (search_vector);

-- Create a function to search memories
CREATE OR REPLACE FUNCTION search_memories(search_query text, user_id uuid)
RETURNS SETOF memories AS $$
DECLARE
    formatted_query text;
BEGIN
    -- Format the search query for better matching
    -- 1. Convert to lowercase
    -- 2. Split into words
    -- 3. Add :* to each word for prefix matching
    -- 4. Join with & for AND operation
    formatted_query := (
        SELECT string_agg(word || ':*', ' & ')
        FROM regexp_split_to_table(lower(search_query), '\s+') AS word
        WHERE word != ''
    );

    RETURN QUERY
    SELECT *
    FROM memories
    WHERE memories.user_id = search_memories.user_id
    AND memories.search_vector @@ to_tsquery('english', formatted_query)
    ORDER BY ts_rank(memories.search_vector, to_tsquery('english', formatted_query)) DESC;
END;
$$ LANGUAGE plpgsql; 