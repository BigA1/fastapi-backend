-- Drop old RLS policies first
DROP POLICY IF EXISTS "Users can view their own stories" ON stories;
DROP POLICY IF EXISTS "Users can insert their own stories" ON stories;
DROP POLICY IF EXISTS "Users can update their own stories" ON stories;
DROP POLICY IF EXISTS "Users can delete their own stories" ON stories;

-- Drop old media_attachments RLS policies
DROP POLICY IF EXISTS "Users can view their own story media" ON media_attachments;
DROP POLICY IF EXISTS "Users can insert their own story media" ON media_attachments;
DROP POLICY IF EXISTS "Users can update their own story media" ON media_attachments;
DROP POLICY IF EXISTS "Users can delete their own story media" ON media_attachments;

-- Rename stories table to memories
ALTER TABLE stories RENAME TO memories;

-- Rename the search vector index
ALTER INDEX stories_search_vector_idx RENAME TO memories_search_vector_idx;

-- Rename the search function
DROP FUNCTION IF EXISTS search_stories;
CREATE OR REPLACE FUNCTION search_memories(search_query text, user_id uuid)
RETURNS SETOF memories AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM memories
    WHERE memories.user_id = search_memories.user_id
    AND memories.search_vector @@ to_tsquery('english', search_query)
    ORDER BY ts_rank(memories.search_vector, to_tsquery('english', search_query)) DESC;
END;
$$ LANGUAGE plpgsql;

-- Create function to get all memories for a user
CREATE OR REPLACE FUNCTION get_memories_for_user(user_id uuid)
RETURNS SETOF memories AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM memories
    WHERE memories.user_id = get_memories_for_user.user_id
    ORDER BY memories.date DESC;
END;
$$ LANGUAGE plpgsql;

-- Update media_attachments table to reference memories instead of stories
ALTER TABLE media_attachments DROP CONSTRAINT IF EXISTS media_attachments_story_id_fkey;
ALTER TABLE media_attachments RENAME COLUMN story_id TO memory_id;

-- Add new foreign key constraint
ALTER TABLE media_attachments
    ADD CONSTRAINT media_attachments_memory_id_fkey
    FOREIGN KEY (memory_id)
    REFERENCES memories(id)
    ON DELETE CASCADE;

-- Create new RLS policies for memories
CREATE POLICY "Users can view their own memories"
    ON memories FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own memories"
    ON memories FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own memories"
    ON memories FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own memories"
    ON memories FOR DELETE
    USING (auth.uid() = user_id);

-- Create new RLS policies for media_attachments
CREATE POLICY "Users can view their own memory media"
    ON media_attachments FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own memory media"
    ON media_attachments FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own memory media"
    ON media_attachments FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own memory media"
    ON media_attachments FOR DELETE
    USING (auth.uid() = user_id); 