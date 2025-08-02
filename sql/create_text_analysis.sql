-- Create user_text_analysis table for storing text analysis results
CREATE TABLE IF NOT EXISTS user_text_analysis (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_user_text_analysis_user_id ON user_text_analysis(user_id);
CREATE INDEX IF NOT EXISTS idx_user_text_analysis_created_at ON user_text_analysis(created_at DESC);