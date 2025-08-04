"""
Manual sample data creation component
"""
import streamlit as st
from datetime import datetime, timedelta
from src.models.database import TMMiDatabase, Assessment, AssessmentAnswer, load_tmmi_questions


def render_manual_sample_data():
    """Render manual sample data creation interface"""
    
    st.header("Manual Sample Data Creation")
    st.markdown("If automatic sample data creation isn't working, you can manually create it here.")
    
    # Check current state
    db = TMMiDatabase()
    orgs = db.get_organizations()
    assessments = db.get_assessments()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Organizations", len(orgs))
    
    with col2:
        st.metric("Assessments", len(assessments))
    
    with col3:
        questions = load_tmmi_questions()
        st.metric("TMMi Questions", len(questions) if questions else 0)
    
    # Show existing organizations
    if orgs:
        st.subheader("Existing Organizations")
        for org in orgs:
            st.write(f"• {org['name']} (ID: {org['id']}, Status: {org['status']})")
    
    # Create sample data button
    if st.button("🚀 Create Complete Sample Dataset", type="primary"):
        create_complete_sample_data()
    
    # Emergency reset
    st.markdown("---")
    st.subheader("⚠️ Emergency Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear All Data", help="Removes ALL organizations and assessments"):
            if st.session_state.get('confirm_clear', False):
                clear_all_data()
                st.session_state.confirm_clear = False
                st.success("All data cleared!")
                st.rerun()
            else:
                st.session_state.confirm_clear = True
                st.warning("Click again to confirm deletion of ALL data!")
    
    with col2:
        if st.button("🔄 Reset Session"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("Session reset! Page will refresh.")
            st.rerun()


def create_complete_sample_data():
    """Create a complete sample dataset"""
    
    try:
        db = TMMiDatabase()
        
        # Load questions first
        questions = load_tmmi_questions()
        if not questions:
            st.error("❌ Cannot load TMMi questions file!")
            return
        
        st.info(f"✅ Loaded {len(questions)} TMMi questions")
        
        # Create organization
        org_data = {
            'name': 'Sample Test Organization',
            'contact_person': 'Sarah Johnson',
            'email': 'sarah.johnson@sampletest.org',
            'status': 'Active'
        }
        
        # Check if org already exists
        existing_orgs = db.get_organizations()
        sample_org = None
        for org in existing_orgs:
            if org['name'] == 'Sample Test Organization':
                sample_org = org
                break
        
        if sample_org:
            org_id = sample_org['id']
            st.info(f"✅ Using existing Sample Test Organization (ID: {org_id})")
        else:
            org_id = db.add_organization(org_data)
            st.success(f"✅ Created Sample Test Organization (ID: {org_id})")
        
        # Create 8 progressive assessments
        start_date = datetime.now() - timedelta(days=540)  # 18 months ago
        
        scenarios = [
            {'days': 0, 'reviewer': 'Sarah Johnson', 'target_level': 2, 'desc': 'Initial baseline'},
            {'days': 45, 'reviewer': 'Mike Chen', 'target_level': 2, 'desc': 'First improvement'},
            {'days': 90, 'reviewer': 'Sarah Johnson', 'target_level': 2, 'desc': 'Level 2 consolidation'},
            {'days': 150, 'reviewer': 'Dr. Lisa Wang', 'target_level': 3, 'desc': 'Level 3 transition'},
            {'days': 240, 'reviewer': 'Mike Chen', 'target_level': 3, 'desc': 'Level 3 maturation'},
            {'days': 330, 'reviewer': 'Sarah Johnson', 'target_level': 4, 'desc': 'Level 4 initial'},
            {'days': 420, 'reviewer': 'Dr. Lisa Wang', 'target_level': 4, 'desc': 'Level 4 advancement'},
            {'days': 510, 'reviewer': 'Sarah Johnson', 'target_level': 4, 'desc': 'Current state - partial Level 5'}
        ]
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, scenario in enumerate(scenarios):
            progress_bar.progress((i + 1) / len(scenarios))
            status_text.text(f"Creating assessment {i+1}: {scenario['desc']}")
            
            assessment_date = start_date + timedelta(days=scenario['days'])
            
            # Generate progressive answers
            answers = []
            progression = i / (len(scenarios) - 1)  # 0.0 to 1.0
            
            for question in questions:
                q_level = question.level
                target = scenario['target_level']
                
                if q_level < target:
                    # Lower levels - should be mostly Yes as we progress
                    if progression > 0.4:
                        answer = 'Yes'
                    elif progression > 0.2:
                        answer = 'Partial'
                    else:
                        answer = 'No'
                elif q_level == target:
                    # Current target level
                    if progression > 0.7:
                        answer = 'Yes'
                    elif progression > 0.3:
                        answer = 'Partial'
                    else:
                        answer = 'No'
                else:
                    # Higher levels
                    if q_level == target + 1 and progression > 0.8:
                        answer = 'Partial'  # Some Level 5 at the end
                    else:
                        answer = 'No'
                
                answers.append(AssessmentAnswer(
                    question_id=question.id,
                    answer=answer,
                    evidence_url=(f"https://docs.sampletest.org/{question.id.lower()}" 
                                 if answer == 'Yes' and i > 3 else None),
                    comment=(f"Implementation in progress - Assessment {i+1}" 
                            if answer == 'Partial' else None)
                ))
            
            # Create assessment
            assessment = Assessment(
                timestamp=assessment_date.isoformat(),
                reviewer_name=scenario['reviewer'],
                organization='Sample Test Organization',
                answers=answers
            )
            
            assessment_id = db.save_assessment(assessment)
            
        progress_bar.progress(1.0)
        status_text.text("Sample data creation complete!")
        
        # Verify results
        final_assessments = db.get_assessments()
        st.success(f"🎉 Successfully created {len(final_assessments)} assessments!")
        
        st.info("✅ Sample data is ready! Go to 'Organization Progress' to see the visualizations.")
        
    except Exception as e:
        st.error(f"❌ Error creating sample data: {str(e)}")
        import traceback
        st.text(traceback.format_exc())


def clear_all_data():
    """Clear all data from the database"""
    try:
        db = TMMiDatabase()
        
        # Get all assessments and delete them
        assessments = db.get_assessments()
        for assessment in assessments:
            db.delete_assessment(assessment.id)
        
        # Get all organizations and delete them
        organizations = db.get_organizations()
        for org in organizations:
            db.delete_organization(org['id'])
            
        st.success(f"Deleted {len(assessments)} assessments and {len(organizations)} organizations")
        
    except Exception as e:
        st.error(f"Error clearing data: {str(e)}")