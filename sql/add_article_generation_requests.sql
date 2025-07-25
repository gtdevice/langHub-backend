-- Add to existing schema - just one table
CREATE TABLE IF NOT EXISTS article_generation_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id),
    categories TEXT[] NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Simple index for user queries
CREATE INDEX IF NOT EXISTS idx_user_requests ON article_generation_requests(user_id);