#!/usr/bin/env python3
"""
Direct sample data creation that bypasses automatic initialization
This will be called from a Streamlit button to manually create sample data
"""
import sys
import os
from datetime import datetime, timedelta

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def create_sample_data_now():
    """Create sample data immediately with full error reporting"""
    try:
        from src.models.database import TMMiDatabase, Assessment, AssessmentAnswer, load_tmmi_questions
        
        # Initialize database
        db = TMMiDatabase()
        print("✓ Database initialized")
        
        # Check existing data
        existing_orgs = db.get_organizations()
        existing_assessments = db.get_assessments()
        
        print(f"Current state: {len(existing_orgs)} organizations, {len(existing_assessments)} assessments")
        
        # Load questions
        questions = load_tmmi_questions()
        if not questions:
            return False, "Failed to load TMMi questions"
        
        print(f"✓ Loaded {len(questions)} TMMi questions")
        
        # Create organization if it doesn't exist
        sample_org = None
        for org in existing_orgs:
            if org['name'] == 'Sample Test Organization':
                sample_org = org
                break
        
        if not sample_org:
            org_data = {
                'name': 'Sample Test Organization',
                'contact_person': 'Sarah Johnson',
                'email': 'sarah.johnson@sampletest.org',
                'status': 'Active'
            }
            org_id = db.add_organization(org_data)
            print(f"✓ Created Sample Test Organization (ID: {org_id})")
        else:
            org_id = sample_org['id']
            print(f"✓ Using existing Sample Test Organization (ID: {org_id})")
        
        # Create assessments
        start_date = datetime.now() - timedelta(days=540)  # 18 months ago
        
        assessment_scenarios = [
            {'offset': 0, 'reviewer': 'Sarah Johnson', 'level': 2},
            {'offset': 45, 'reviewer': 'Mike Chen', 'level': 2},
            {'offset': 90, 'reviewer': 'Sarah Johnson', 'level': 2},
            {'offset': 150, 'reviewer': 'Dr. Lisa Wang', 'level': 3},
            {'offset': 240, 'reviewer': 'Mike Chen', 'level': 3},
            {'offset': 330, 'reviewer': 'Sarah Johnson', 'level': 4},
            {'offset': 420, 'reviewer': 'Dr. Lisa Wang', 'level': 4},
            {'offset': 510, 'reviewer': 'Sarah Johnson', 'level': 4}
        ]
        
        created_assessments = 0
        for i, scenario in enumerate(assessment_scenarios):
            assessment_date = start_date + timedelta(days=scenario['offset'])
            
            # Create simple answers for demonstration
            answers = []
            for j, question in enumerate(questions):
                # Simple progression logic
                if question['level'] <= scenario['level']:
                    if i >= 5:  # Later assessments
                        answer = 'Yes'
                    elif i >= 3:
                        answer = 'Partial' if j % 2 == 0 else 'Yes'
                    else:
                        answer = 'Partial' if j % 3 == 0 else 'No'
                else:
                    answer = 'Partial' if question['level'] == scenario['level'] + 1 and i >= 6 else 'No'
                
                answers.append(AssessmentAnswer(
                    question_id=question['id'],
                    answer=answer,
                    evidence_url=f"https://docs.sampletest.org/{question['id'].lower()}" if answer == 'Yes' and i > 3 else None,
                    comment=f"Assessment {i+1} response" if answer == 'Partial' else None
                ))
            
            # Create assessment
            assessment = Assessment(
                timestamp=assessment_date.isoformat(),
                reviewer_name=scenario['reviewer'],
                organization='Sample Test Organization',
                answers=answers
            )
            
            assessment_id = db.save_assessment(assessment)
            created_assessments += 1
            print(f"✓ Created assessment {i+1}: {scenario['reviewer']} - {assessment_date.strftime('%Y-%m-%d')}")
        
        # Verify final state
        final_orgs = db.get_organizations()
        final_assessments = db.get_assessments()
        
        print(f"Final state: {len(final_orgs)} organizations, {len(final_assessments)} assessments")
        
        return True, f"Successfully created {created_assessments} sample assessments for Sample Test Organization"
        
    except Exception as e:
        import traceback
        error_msg = f"Error: {str(e)}\nTraceback: {traceback.format_exc()}"
        print(error_msg)
        return False, error_msg

if __name__ == "__main__":
    success, message = create_sample_data_now()
    print(f"\nResult: {'SUCCESS' if success else 'FAILED'}")
    print(f"Message: {message}")