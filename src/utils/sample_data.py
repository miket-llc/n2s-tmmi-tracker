"""
Sample data initialization for N2S TMMi Tracker
Automatically creates sample data when no organizations exist
"""

import logging
from datetime import datetime, timedelta
from typing import List

from src.models.database import (
    Assessment,
    AssessmentAnswer,
    TMMiDatabase,
    TMMiQuestion,
    load_tmmi_questions,
)


def create_sample_organization(db: TMMiDatabase) -> int:
    """Create a sample organization"""
    org_data = {
        "name": "Sample Test Organization",
        "contact_person": "Sarah Johnson",
        "email": "sarah.johnson@sampletest.org",
        "status": "Active",
    }
    org_id = db.add_organization(org_data)
    logging.info(f"Created sample organization: {org_data['name']} (ID: {org_id})")
    return org_id


def generate_progressive_answers(
    questions: List[TMMiQuestion],
    target_level: int,
    assessment_number: int,
    total_assessments: int,
) -> List[AssessmentAnswer]:
    """Generate answers that show realistic progression over time"""
    answers = []
    # Calculate progression factor (0.0 to 1.0)
    progression = assessment_number / (total_assessments - 1)
    
    # Sample comments for different question types and levels
    sample_comments = {
        "L2_TPS_001": "Test policy document approved by management and published on intranet",
        "L2_TPS_002": "Risk assessment completed and test strategy aligned with business objectives",
        "L2_TP_001": "Standard test plan template implemented across all projects",
        "L2_TP_002": "Entry/exit criteria defined and documented in test plan template",
        "L2_TMC_001": "Weekly test progress reports implemented with dashboard visibility",
        "L2_TMC_002": "Deviation tracking process established with corrective action workflows",
        "L2_TD_001": "Test design techniques training completed for 80% of team members",
        "L2_TE_001": "Dedicated test environment established with automated provisioning",
        "L3_TLI_001": "Test lifecycle integrated with development process using CI/CD pipeline",
        "L3_PR_001": "Peer review process implemented with mandatory code review requirements",
        "L3_NFTR_001": "Performance testing framework established with baseline metrics",
        "L3_TTO_001": "Test training program launched with quarterly skill assessments",
        "L4_TM_001": "Test metrics dashboard implemented with real-time reporting",
        "L4_TM_002": "Quality gates established with automated measurement collection",
        "L4_SPC_001": "Advanced review techniques implemented including Fagan inspections",
        "L4_QE_001": "Quality evaluation process established with defect trend analysis",
        "L5_TPI_001": "Implementation in progress - Assessment 8",
        "L5_QC_001": "Implementation in progress - Assessment 8",
        "L5_TA_001": "Implementation in progress - Assessment 8",
        "L5_TO_001": "Implementation in progress - Assessment 8"
    }
    
    for question in questions:
        q_level = question.level
        q_id = question.id
        # Determine answer based on progression and level
        if q_level < target_level:
            # Lower levels should be mostly "Yes" as we progress
            if progression > 0.3:  # After 30% progression, lower levels should be solid
                answer = "Yes"
            elif progression > 0.1:  # Some partial implementation
                answer = "Partial" if assessment_number % 3 == 0 else "Yes"
            else:
                answer = "No" if assessment_number < 2 else "Partial"
        elif q_level == target_level:
            # Current target level - gradual improvement
            if progression > 0.8:  # Near end, mostly Yes
                answer = "Yes"
            elif progression > 0.5:  # Middle, mix of Yes and Partial
                answer = "Partial" if assessment_number % 2 == 0 else "Yes"
            elif progression > 0.2:  # Early-middle, mostly Partial
                answer = "Partial"
            else:  # Very early, mostly No
                answer = "No" if assessment_number < 2 else "Partial"
        else:  # q_level > target_level
            # Higher levels - only partial achievement at the end
            if q_level == target_level + 1 and progression > 0.7:
                answer = "Partial"  # Some Level 5 achievement near the end
            else:
                answer = "No"
        
        # Add evidence URLs and comments
        evidence_url = None
        comment = None
        
        # Add evidence for Yes answers (after some progression)
        if answer == "Yes" and assessment_number > 3:
            evidence_url = f"https://docs.sampletest.org/{q_id.lower()}"
        
        # Add comments for most questions (but not all to show variety)
        if q_id in sample_comments:
            comment = sample_comments[q_id]
        elif answer == "Partial":
            comment = f"Implementation in progress - Assessment {assessment_number + 1}"
        elif answer == "No" and assessment_number > 2:
            comment = f"Planned for implementation in Q{((assessment_number % 4) + 1)}"
        elif answer == "Yes" and assessment_number > 4:
            comment = f"Successfully implemented and operational since Assessment {assessment_number - 2}"
        
        answers.append(
            AssessmentAnswer(
                question_id=q_id,
                answer=answer,
                evidence_url=evidence_url,
                comment=comment,
            )
        )
    return answers


def create_sample_assessments(db: TMMiDatabase, org_id: int, questions: List[TMMiQuestion]) -> List[int]:
    """Create 8 sample assessments showing progression from Level 2 to 4+"""
    # Assessment timeline: spread over 18 months
    start_date = datetime.now() - timedelta(days=540)  # 18 months ago
    assessment_scenarios = [
        {"date_offset": 0, "reviewer": "Sarah Johnson", "target_level": 2},
        {"date_offset": 45, "reviewer": "Mike Chen", "target_level": 2},
        {"date_offset": 90, "reviewer": "Sarah Johnson", "target_level": 2},
        {"date_offset": 150, "reviewer": "Dr. Lisa Wang", "target_level": 3},
        {"date_offset": 240, "reviewer": "Mike Chen", "target_level": 3},
        {"date_offset": 330, "reviewer": "Sarah Johnson", "target_level": 4},
        {"date_offset": 420, "reviewer": "Dr. Lisa Wang", "target_level": 4},
        {"date_offset": 510, "reviewer": "Sarah Johnson", "target_level": 4},
    ]
    assessment_ids = []
    for i, scenario in enumerate(assessment_scenarios):
        assessment_date = start_date + timedelta(days=scenario["date_offset"])
        # Generate progressive answers
        answers = generate_progressive_answers(questions, scenario["target_level"], i, len(assessment_scenarios))
        # Create assessment
        assessment = Assessment(
            timestamp=assessment_date.isoformat(),
            reviewer_name=scenario["reviewer"],
            organization="Sample Test Organization",
            answers=answers,
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
        logging.info(
            f"Verification - Organizations: {len(verification_orgs)}, " f"Assessments: {len(verification_assessments)}"
        )
        if verification_orgs and verification_assessments:
            logging.info(
                f"Sample data initialized successfully: "
                f"{len(verification_orgs)} organization(s), {len(verification_assessments)} assessments"
            )
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
            if org["name"] == "Sample Test Organization":
                sample_org = org
                break
        if sample_org:
            assessments = db.get_assessments_by_org(sample_org["id"])
            return {
                "exists": True,
                "organization": sample_org,
                "assessment_count": len(assessments),
                "latest_assessment": assessments[-1]["timestamp"][:10] if assessments else "None",
            }
        else:
            return {"exists": False}
    except Exception as e:
        logging.error(f"Failed to get sample data status: {e}")
        return {"exists": False, "error": str(e)}
