
"""
Supabase database adapter for TMMi Assessment Tracker
"""
import streamlit as st
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

# Import existing models
from src.models.database import TMMiQuestion, AssessmentAnswer, Assessment


class SupabaseTMMiDatabase:
    """Supabase-compatible database manager for TMMi assessments"""

    def __init__(self):
        # Initialize Supabase connection using st.connection
        self.conn = st.connection("supabase", type="sql")

    def get_organizations(self) -> List[dict]:
        """Retrieve all organizations"""
        try:
            result = self.conn.query("""
                SELECT id, name, contact_person, email, status, 
                       created_at, updated_at
                FROM organizations
                ORDER BY name
            """, ttl="1m")
            
            return [dict(row) for row in result.itertuples(index=False, name=None)]
        except Exception as e:
            logging.error(f"Error fetching organizations: {e}")
            return []

    def add_organization(self, org_data: dict) -> int:
        """Add a new organization"""
        try:
            result = self.conn.query("""
                INSERT INTO organizations (name, contact_person, email, status)
                VALUES (%(name)s, %(contact_person)s, %(email)s, %(status)s)
                RETURNING id
            """, params=org_data, ttl=0)
            
            return result.iloc[0]['id']
        except Exception as e:
            logging.error(f"Error adding organization: {e}")
            raise

    def update_organization(self, org_id: int, updated_fields: dict):
        """Update organization with new field values"""
        if not updated_fields:
            return
        
        try:
            # Build dynamic update query
            set_clauses = []
            params = {'id': org_id}
            
            for field, value in updated_fields.items():
                if field in ['name', 'contact_person', 'email', 'status']:
                    set_clauses.append(f"{field} = %({field})s")
                    params[field] = value
            
            if set_clauses:
                set_clauses.append("updated_at = NOW()")
                
                query = f"""
                    UPDATE organizations 
                    SET {', '.join(set_clauses)}
                    WHERE id = %(id)s
                """
                
                self.conn.query(query, params=params, ttl=0)
        except Exception as e:
            logging.error(f"Error updating organization: {e}")
            raise

    def delete_organization(self, org_id: int):
        """Delete an organization"""
        try:
            self.conn.query(
                "DELETE FROM organizations WHERE id = %(id)s",
                params={'id': org_id},
                ttl=0
            )
        except Exception as e:
            logging.error(f"Error deleting organization: {e}")
            raise

    def save_assessment(self, assessment: Assessment) -> int:
        """Save a complete assessment to the database"""
        try:
            # Insert assessment record
            result = self.conn.query("""
                INSERT INTO assessments (timestamp, reviewer_name, organization)
                VALUES (%(timestamp)s, %(reviewer_name)s, %(organization)s)
                RETURNING id
            """, params={
                'timestamp': assessment.timestamp,
                'reviewer_name': assessment.reviewer_name,
                'organization': assessment.organization
            }, ttl=0)
            
            assessment_id = result.iloc[0]['id']
            
            # Insert all answers
            for answer in assessment.answers:
                self.conn.query("""
                    INSERT INTO assessment_answers 
                    (assessment_id, question_id, answer, evidence_url, comment)
                    VALUES (%(assessment_id)s, %(question_id)s, %(answer)s, 
                           %(evidence_url)s, %(comment)s)
                """, params={
                    'assessment_id': assessment_id,
                    'question_id': answer.question_id,
                    'answer': answer.answer,
                    'evidence_url': answer.evidence_url,
                    'comment': answer.comment
                }, ttl=0)
            
            return assessment_id
        except Exception as e:
            logging.error(f"Error saving assessment: {e}")
            raise

    def get_assessments(self) -> List[Assessment]:
        """Retrieve all assessments from the database"""
        try:
            # Get all assessments
            assessments_result = self.conn.query("""
                SELECT id, timestamp, reviewer_name, organization
                FROM assessments
                ORDER BY timestamp DESC
            """, ttl="5m")
            
            assessments = []
            
            for _, row in assessments_result.iterrows():
                assessment_id = row['id']
                
                # Get answers for this assessment
                answers_result = self.conn.query("""
                    SELECT question_id, answer, evidence_url, comment
                    FROM assessment_answers
                    WHERE assessment_id = %(assessment_id)s
                """, params={'assessment_id': assessment_id}, ttl="5m")
                
                answers = [
                    AssessmentAnswer(
                        question_id=answer_row['question_id'],
                        answer=answer_row['answer'],
                        evidence_url=answer_row['evidence_url'],
                        comment=answer_row['comment']
                    )
                    for _, answer_row in answers_result.iterrows()
                ]
                
                assessments.append(Assessment(
                    id=assessment_id,
                    timestamp=row['timestamp'].isoformat() if hasattr(row['timestamp'], 'isoformat') else str(row['timestamp']),
                    reviewer_name=row['reviewer_name'],
                    organization=row['organization'],
                    answers=answers
                ))
            
            return assessments
        except Exception as e:
            logging.error(f"Error fetching assessments: {e}")
            return []

    def get_assessments_by_org(self, org_id: int) -> List[dict]:
        """Get all assessments for a specific organization"""
        try:
            # First get the organization name
            org_result = self.conn.query(
                "SELECT name FROM organizations WHERE id = %(id)s",
                params={'id': org_id},
                ttl="5m"
            )
            
            if org_result.empty:
                return []
            
            org_name = org_result.iloc[0]['name']
            
            # Get assessments for this organization
            result = self.conn.query("""
                SELECT 
                    a.id as assessment_id,
                    a.timestamp,
                    a.reviewer_name,
                    a.organization,
                    COUNT(aa.id) as total_answers,
                    COUNT(CASE WHEN aa.answer = 'Yes' THEN 1 END) as yes_count,
                    COUNT(CASE WHEN aa.answer = 'Partial' THEN 1 END) as partial_count,
                    COUNT(CASE WHEN aa.answer = 'No' THEN 1 END) as no_count
                FROM assessments a
                LEFT JOIN assessment_answers aa ON a.id = aa.assessment_id
                WHERE LOWER(a.organization) = LOWER(%(org_name)s)
                GROUP BY a.id, a.timestamp, a.reviewer_name, a.organization
                ORDER BY a.timestamp ASC
            """, params={'org_name': org_name}, ttl="5m")
            
            assessments = []
            for _, row in result.iterrows():
                total = row['total_answers'] or 0
                yes = row['yes_count'] or 0
                compliance_pct = (yes / total * 100) if total > 0 else 0
                
                # Determine maturity level based on compliance
                if compliance_pct >= 90:
                    maturity_level = 5
                elif compliance_pct >= 80:
                    maturity_level = 4
                elif compliance_pct >= 60:
                    maturity_level = 3
                elif compliance_pct >= 40:
                    maturity_level = 2
                else:
                    maturity_level = 1
                
                assessments.append({
                    'assessment_id': row['assessment_id'],
                    'timestamp': row['timestamp'].isoformat() if hasattr(row['timestamp'], 'isoformat') else str(row['timestamp']),
                    'reviewer_name': row['reviewer_name'],
                    'organization': row['organization'],
                    'total_answers': total,
                    'yes_count': yes,
                    'partial_count': row['partial_count'] or 0,
                    'no_count': row['no_count'] or 0,
                    'compliance_percentage': compliance_pct,
                    'maturity_level': maturity_level
                })
            
            return assessments
        except Exception as e:
            logging.error(f"Error fetching org assessments: {e}")
            return []

    def get_tmmi_scores_by_assessment(self, assessment_id: int) -> dict:
        """Get detailed TMMi scores and process area breakdown for an assessment"""
        try:
            # Get assessment details
            assessment_result = self.conn.query("""
                SELECT timestamp, reviewer_name, organization
                FROM assessments WHERE id = %(id)s
            """, params={'id': assessment_id}, ttl="5m")
            
            if assessment_result.empty:
                return {}
            
            assessment_row = assessment_result.iloc[0]
            
            # Get all answers for this assessment
            answers_result = self.conn.query("""
                SELECT question_id, answer, evidence_url, comment
                FROM assessment_answers
                WHERE assessment_id = %(id)s
            """, params={'id': assessment_id}, ttl="5m")
            
            answers = {}
            for _, row in answers_result.iterrows():
                answers[row['question_id']] = {
                    'answer': row['answer'],
                    'evidence_url': row['evidence_url'],
                    'comment': row['comment']
                }
            
            return {
                'assessment_id': assessment_id,
                'timestamp': assessment_row['timestamp'].isoformat() if hasattr(assessment_row['timestamp'], 'isoformat') else str(assessment_row['timestamp']),
                'reviewer_name': assessment_row['reviewer_name'],
                'organization': assessment_row['organization'],
                'answers': answers
            }
        except Exception as e:
            logging.error(f"Error fetching assessment scores: {e}")
            return {}

    def delete_assessment(self, assessment_id: int):
        """Delete an assessment and all its answers"""
        try:
            # Due to CASCADE, deleting assessment will also delete answers
            self.conn.query(
                "DELETE FROM assessments WHERE id = %(id)s",
                params={'id': assessment_id},
                ttl=0
            )
        except Exception as e:
            logging.error(f"Error deleting assessment: {e}")
            raise
