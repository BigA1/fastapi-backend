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
GRANT EXECUTE ON FUNCTION create_interview_session_for_user(VARCHAR, UUID, TEXT, JSONB, TEXT, VARCHAR) TO authenticated;
GRANT EXECUTE ON FUNCTION update_interview_session_for_user(VARCHAR, UUID, JSONB, TEXT, TEXT, VARCHAR, TIMESTAMP WITH TIME ZONE) TO authenticated;
GRANT EXECUTE ON FUNCTION get_interview_session_for_user(VARCHAR, UUID) TO authenticated; 