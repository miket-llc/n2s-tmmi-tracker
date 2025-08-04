"""
Debug component for troubleshooting TMMi Assessment Tracker
"""
import streamlit as st
import logging
from src.models.database import TMMiDatabase, load_tmmi_questions
from src.utils.sample_data import initialize_sample_data, get_sample_data_status


def render_debug_info():
    """Render debug information for troubleshooting"""
    
    st.sidebar.markdown("---")
    
    with st.sidebar.expander("🔧 Debug Info", expanded=False):
        if st.button("Check Database Status"):
            try:
                db = TMMiDatabase()
                
                # Check organizations
                orgs = db.get_organizations()
                st.write(f"**Organizations:** {len(orgs)}")
                for org in orgs:
                    st.write(f"  - {org['name']} (ID: {org['id']})")
                
                # Check assessments
                assessments = db.get_assessments()
                st.write(f"**Assessments:** {len(assessments)}")
                
                # Check TMMi questions
                questions = load_tmmi_questions()
                st.write(f"**TMMi Questions:** {len(questions) if questions else 0}")
                
                # Sample data status
                sample_status = get_sample_data_status()
                st.write(f"**Sample Data:** {'✅ Exists' if sample_status['exists'] else '❌ Missing'}")
                
            except Exception as e:
                st.error(f"Debug check failed: {e}")
        
        if st.button("Force Initialize Sample Data"):
            try:
                # Import the direct creation function
                import sys
                import os
                sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                
                from create_sample_data_direct import create_sample_data_now
                
                with st.spinner("Creating sample data..."):
                    success, message = create_sample_data_now()
                
                if success:
                    st.success(f"✅ {message}")
                    st.info("Refresh the page to see the new data!")
                else:
                    st.error(f"❌ {message}")
                    
            except Exception as e:
                st.error(f"Sample data creation failed: {e}")
                import traceback
                st.text(traceback.format_exc())
        
        if st.button("Clear Session State"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("Session state cleared - page will refresh")
            st.rerun()