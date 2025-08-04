
-- TMMi Assessment Tracker Database Schema for Supabase
-- Copy and paste this into Supabase SQL Editor

-- Organizations table
CREATE TABLE organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    contact_person VARCHAR(255),
    email VARCHAR(255),
    status VARCHAR(20) DEFAULT 'Active' CHECK (status IN ('Active', 'Inactive')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Assessments table
CREATE TABLE assessments (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    reviewer_name VARCHAR(255) NOT NULL,
    organization VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Assessment answers table
CREATE TABLE assessment_answers (
    id SERIAL PRIMARY KEY,
    assessment_id INTEGER NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
    question_id VARCHAR(50) NOT NULL,
    answer VARCHAR(20) NOT NULL CHECK (answer IN ('Yes', 'No', 'Partial')),
    evidence_url TEXT,
    comment TEXT
);

-- Indexes for better performance
CREATE INDEX idx_assessments_org ON assessments(organization);
CREATE INDEX idx_assessments_timestamp ON assessments(timestamp DESC);
CREATE INDEX idx_answers_assessment_id ON assessment_answers(assessment_id);
CREATE INDEX idx_answers_question_id ON assessment_answers(question_id);

-- Insert sample organization
INSERT INTO organizations (name, contact_person, email, status) 
VALUES ('Sample Test Organization', 'Sarah Johnson', 'sarah.johnson@sampletest.org', 'Active');

-- You can also insert sample assessments here if needed
