"""
Sample data initialization for TMMi Assessment Tracker
Automatically creates sample data when no organizations exist
"""
from datetime import datetime, timedelta
from typing import List
import logging

from src.models.database import TMMiDatabase, Assessment, AssessmentAnswer, load_tmmi_questions


def create_sample_organization(db: TMMiDatabase) -> int:
    """Create a sample organization"""
    org_data = {
        'name': 'Sample Test Organization',
        'contact_person': 'Sarah Johnson',
        'email': 'sarah.johnson@sampletest.org',
        'status': 'Active'
    }
    
    org_id = db.add_organization(org_data)
    logging.info(f"Created sample organization: {org_data['name']} (ID: {org_id})")
    return org_id


def generate_progressive_answers(questions: List[dict], target_level: int, 
                                assessment_number: int, total_assessments: int) -> List[AssessmentAnswer]:
    """Generate answers that show realistic progression over time"""
    answers = []
    
    # Calculate progression factor (0.0 to 1.0)
    progression = assessment_number / (total_assessments - 1)
    
    for question in questions:
        q_level = question['level']
        q_id = question['id']
        
        # Determine answer based on progression and level
        if q_level < target_level:
            # Lower levels should be mostly "Yes" as we progress
            if progression > 0.3:  # After 30% progression, lower levels should be solid
                answer = 'Yes'
            elif progression > 0.1:  # Some partial implementation
                answer = 'Partial' if assessment_number % 3 == 0 else 'Yes'
            else:
                answer = 'No' if assessment_number < 2 else 'Partial'
                
        elif q_level == target_level:
            # Current target level - gradual improvement
            if progression > 0.8:  # Near end, mostly Yes
                answer = 'Yes'
            elif progression > 0.5:  # Middle, mix of Yes and Partial
                answer = 'Partial' if assessment_number % 2 == 0 else 'Yes'
            elif progression > 0.2:  # Early-middle, mostly Partial
                answer = 'Partial'
            else:  # Very early, mostly No
                answer = 'No' if assessment_number < 2 else 'Partial'
                
        else:  # q_level > target_level
            # Higher levels - only partial achievement at the end
            if q_level == target_level + 1 and progression > 0.7:
                answer = 'Partial'  # Some Level 5 achievement near the end
            else:
                answer = 'No'
        
        # Add some realistic evidence URLs and comments
        evidence_url = None
        comment = None
        
        if answer == 'Yes' and assessment_number > 3:
            evidence_url = f"https://docs.sampletest.org/{q_id.lower()}"
            
        if answer == 'Partial':
            comment = f"Implementation in progress - Assessment {assessment_number + 1}"
            
        answers.append(AssessmentAnswer(
            question_id=q_id,
            answer=answer,
            evidence_url=evidence_url,
            comment=comment
        ))
    
    return answers


def create_sample_assessments(db: TMMiDatabase, org_id: int, questions: List[dict]) -> List[int]:
    """Create 8 sample assessments showing progression from Level 2 to 4+"""
    
    # Assessment timeline: spread over 18 months
    start_date = datetime.now() - timedelta(days=540)  # 18 months ago
    
    assessment_scenarios = [
        {'date_offset': 0, 'reviewer': 'Sarah Johnson', 'target_level': 2},
        {'date_offset': 45, 'reviewer': 'Mike Chen', 'target_level': 2},
        {'date_offset': 90, 'reviewer': 'Sarah Johnson', 'target_level': 2},
        {'date_offset': 150, 'reviewer': 'Dr. Lisa Wang', 'target_level': 3},
        {'date_offset': 240, 'reviewer': 'Mike Chen', 'target_level': 3},
        {'date_offset': 330, 'reviewer': 'Sarah Johnson', 'target_level': 4},
        {'date_offset': 420, 'reviewer': 'Dr. Lisa Wang', 'target_level': 4},
        {'date_offset': 510, 'reviewer': 'Sarah Johnson', 'target_level': 4}
    ]
    
    assessment_ids = []
    
    for i, scenario in enumerate(assessment_scenarios):
        assessment_date = start_date + timedelta(days=scenario['date_offset'])
        
        # Generate progressive answers
        answers = generate_progressive_answers(
            questions, 
            scenario['target_level'], 
            i, 
            len(assessment_scenarios)
        )
        
        # Create assessment
        assessment = Assessment(
            timestamp=assessment_date.isoformat(),
            reviewer_name=scenario['reviewer'],
            organization='Sample Test Organization',
            answers=answers
        )
        
        assessment_id = db.save_assessment(assessment)
        assessment_ids.append(assessment_id)
    
    logging.info(f"Created {len(assessment_ids)} sample assessments")
    return assessment_ids


def initialize_sample_data() -> bool:
    """Initialize sample data if no organizations exist"""
    try:
        db = TMMiDatabase()
        
        # Check if any organizations exist
        existing_orgs = db.get_organizations()
        if existing_orgs:
            # Sample data already exists or real data is present
            logging.info(f"Found {len(existing_orgs)} existing organizations, skipping sample data")
            return False
        
        # Load TMMi questions
        questions = load_tmmi_questions()
        if not questions:
            logging.warning("No TMMi questions available, skipping sample data creation")
            return False
        
        logging.info(f"Loaded {len(questions)} TMMi questions for sample data")
        
        # Create sample organization
        org_id = create_sample_organization(db)
        logging.info(f"Created sample organization with ID: {org_id}")
        
        # Create sample assessments
        assessment_ids = create_sample_assessments(db, org_id, questions)
        logging.info(f"Created {len(assessment_ids)} sample assessments")
        
        # Verify the data was created
        verification_orgs = db.get_organizations()
        verification_assessments = db.get_assessments()
        
        logging.info(f"Verification - Organizations: {len(verification_orgs)}, Assessments: {len(verification_assessments)}")
        
        if verification_orgs and verification_assessments:
            logging.info(f"Sample data initialized successfully: "
                        f"{len(verification_orgs)} organization(s), {len(verification_assessments)} assessments")
            return True
        else:
            logging.error("Sample data verification failed - no data found after creation")
            return False
        
    except Exception as e:
        import traceback
        logging.error(f"Failed to initialize sample data: {e}")
        logging.error(f"Traceback: {traceback.format_exc()}")
        return False


def get_sample_data_status() -> dict:
    """Get status of sample data for display purposes"""
    try:
        db = TMMiDatabase()
        organizations = db.get_organizations()
        
        sample_org = None
        for org in organizations:
            if org['name'] == 'Sample Test Organization':
                sample_org = org
                break
        
        if sample_org:
            assessments = db.get_assessments_by_org(sample_org['id'])
            return {
                'exists': True,
                'organization': sample_org,
                'assessment_count': len(assessments),
                'latest_assessment': assessments[-1]['timestamp'][:10] if assessments else 'None'
            }
        else:
            return {'exists': False}
            
    except Exception as e:
        logging.error(f"Failed to get sample data status: {e}")
        return {'exists': False, 'error': str(e)}