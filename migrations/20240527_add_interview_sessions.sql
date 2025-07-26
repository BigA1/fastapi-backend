-- Create interview_sessions table
CREATE TABLE IF NOT EXISTS interview_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    initial_context TEXT,
    conversation JSONB DEFAULT '[]'::jsonb,
    current_question TEXT,
    summary TEXT,
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'abandoned')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT fk_user
        FOREIGN KEY (user_id)
        REFERENCES auth.users(id)
        ON DELETE CASCADE
);

-- Create index on user_id for faster queries
CREATE INDEX IF NOT EXISTS idx_interview_sessions_user_id ON interview_sessions(user_id);

-- Create index on session_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_interview_sessions_session_id ON interview_sessions(session_id);

-- Create index on status for filtering
CREATE INDEX IF NOT EXISTS idx_interview_sessions_status ON interview_sessions(status);

-- Create index on created_at for sorting
CREATE INDEX IF NOT EXISTS idx_interview_sessions_created_at ON interview_sessions(created_at);

-- Add RLS (Row Level Security) policies
ALTER TABLE interview_sessions ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own interview sessions
CREATE POLICY "Users can view own interview sessions" ON interview_sessions
    FOR SELECT USING (auth.uid() = user_id);

-- Policy: Users can insert their own interview sessions
CREATE POLICY "Users can insert own interview sessions" ON interview_sessions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Policy: Users can update their own interview sessions
CREATE POLICY "Users can update own interview sessions" ON interview_sessions
    FOR UPDATE USING (auth.uid() = user_id);

-- Policy: Users can delete their own interview sessions
CREATE POLICY "Users can delete own interview sessions" ON interview_sessions
    FOR DELETE USING (auth.uid() = user_id);

-- Create function to automatically update last_updated timestamp
CREATE OR REPLACE FUNCTION update_interview_session_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update last_updated
CREATE TRIGGER update_interview_session_timestamp
    BEFORE UPDATE ON interview_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_interview_session_timestamp();

-- Create function to get interview sessions for a user
CREATE OR REPLACE FUNCTION get_interview_sessions_for_user(user_uuid UUID)
RETURNS SETOF interview_sessions AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM interview_sessions
    WHERE user_id = user_uuid
    ORDER BY created_at DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to create interview session for a user (bypasses RLS)
CREATE OR REPLACE FUNCTION create_interview_session_for_user(
    p_session_id VARCHAR(255),
    p_user_id UUID,
    p_initial_context TEXT DEFAULT NULL,
    p_conversation JSONB DEFAULT '[]'::jsonb,
    p_current_question TEXT DEFAULT NULL,
    p_status VARCHAR(50) DEFAULT 'active'
)
RETURNS interview_sessions AS $$
DECLARE
    new_session interview_sessions;
BEGIN
    INSERT INTO interview_sessions (
        session_id,
        user_id,
        initial_context,
        conversation,
        current_question,
        status
    ) VALUES (
        p_session_id,
        p_user_id,
        p_initial_context,
        p_conversation,
        p_current_question,
        p_status
    )
    RETURNING * INTO new_session;
    
    RETURN new_session;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to update interview session for a user (bypasses RLS)
CREATE OR REPLACE FUNCTION update_interview_session_for_user(
    p_session_id VARCHAR(255),
    p_user_id UUID,
    p_conversation JSONB DEFAULT NULL,
    p_current_question TEXT DEFAULT NULL,
    p_summary TEXT DEFAULT NULL,
    p_status VARCHAR(50) DEFAULT NULL,
    p_ended_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
)
RETURNS interview_sessions AS $$
DECLARE
    updated_session interview_sessions;
BEGIN
    UPDATE interview_sessions
    SET 
        conversation = COALESCE(p_conversation, conversation),
        current_question = COALESCE(p_current_question, current_question),
        summary = COALESCE(p_summary, summary),
        status = COALESCE(p_status, status),
        ended_at = COALESCE(p_ended_at, ended_at),
        last_updated = NOW()
    WHERE session_id = p_session_id AND user_id = p_user_id
    RETURNING * INTO updated_session;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Interview session not found or access denied';
    END IF;
    
    RETURN updated_session;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to get interview session for a user (bypasses RLS)
CREATE OR REPLACE FUNCTION get_interview_session_for_user(
    p_session_id VARCHAR(255),
    p_user_id UUID
)
RETURNS interview_sessions AS $$
DECLARE
    session_record interview_sessions;
BEGIN
    SELECT * INTO session_record
    FROM interview_sessions
    WHERE session_id = p_session_id AND user_id = p_user_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Interview session not found or access denied';
    END IF;
    
    RETURN session_record;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permission on the functions
GRANT EXECUTE ON FUNCTION get_interview_sessions_for_user(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION create_interview_session_for_user(VARCHAR, UUID, TEXT, JSONB, TEXT, VARCHAR) TO authenticated;
GRANT EXECUTE ON FUNCTION update_interview_session_for_user(VARCHAR, UUID, JSONB, TEXT, TEXT, VARCHAR, TIMESTAMP WITH TIME ZONE) TO authenticated;
GRANT EXECUTE ON FUNCTION get_interview_session_for_user(VARCHAR, UUID) TO authenticated; 