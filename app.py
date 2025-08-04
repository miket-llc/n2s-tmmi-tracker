"""
TMMi Assessment Tracker - Professional Assessment Platform
Updated: 2025-01-04
"""
import streamlit as st
import sys
import os
import logging
# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
# Import modules after adding src to path
from models.database import load_tmmi_questions, TMMiDatabase
from components.assessment import (
    render_assessment_form,
    render_assessment_success,
    render_assessment_history
)
from components.dashboard import (
    render_dashboard,
    render_level_breakdown
)
from components.edit_history import render_edit_history
from components.organizations import render_manage_organizations
from components.progress import render_organization_progress
from components.debug import render_debug_info
from components.manual_sample import render_manual_sample_data
from utils.version import format_version_display, get_deployment_info
from utils.sample_data import initialize_sample_data
# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
# Page configuration - professional, no emojis
st.set_page_config(
    page_title="TMMi Assessment Tracker",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Professional styling - clean and accessible
st.markdown("""
<style>
    /* Professional color scheme */
    :root {
        --primary-color: #2E5984;
        --secondary-color: #4A90C2;
        --success-color: #27AE60;
        --warning-color: #F39C12;
        --error-color: #E74C3C;
        --text-primary: #2C3E50;
        --background-light: #F8F9FA;
        --border-color: #E9ECEF;
    }
    .main-header {
        background: linear-gradient(135deg, var(--primary-color) 0%,
                                     var(--secondary-color) 100%);
        padding: 1.5rem;
        border-radius: 8px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 600;
    }
    .sidebar-info {
        background: var(--background-light);
        color: var(--text-primary);
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
        border: 1px solid var(--border-color);
    }
    /* Professional form styling */
    .stTextInput input, .stTextArea textarea {
        border: 2px solid var(--border-color) !important;
        border-radius: 6px !important;
        padding: 0.5rem !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: var(--secondary-color) !important;
        box-shadow: 0 0 0 2px rgba(74, 144, 194, 0.2) !important;
    }
    .stButton > button {
        border-radius: 6px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button[kind="primary"] {
        background: var(--primary-color) !important;
        color: white !important;
    }
    /* Professional status indicators */
    .status-high { color: var(--error-color); font-weight: 600; }
    .status-medium { color: var(--warning-color); font-weight: 600; }
    .status-low { color: var(--success-color); font-weight: 600; }
    /* Hide Streamlit branding for cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'page' not in st.session_state:
        st.session_state.page = 'dashboard'
    if 'assessment_answers' not in st.session_state:
        st.session_state.assessment_answers = {}
    if 'sample_data_initialized' not in st.session_state:
        st.session_state.sample_data_initialized = False


def show_error_message(message, details=None):
    """Show professional error message"""
    st.markdown(f"""
    <div style="background: #FDEAEA; border: 1px solid #F5B7B1; color: #7F1D1D;
                padding: 1rem; border-radius: 6px; margin: 1rem 0;">
        <strong>⚠️ Error:</strong> {message}
        {f'<br><small>{details}</small>' if details else ''}
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render professional navigation sidebar"""
    with st.sidebar:
        st.markdown("""
        <div class="main-header">
            <h1>TMMi Assessment Tracker</h1>
            <p>Professional Test Maturity Assessment Platform</p>
        </div>
        """, unsafe_allow_html=True)
        # Navigation
        st.markdown("### Navigation")
        pages = {
            'dashboard': 'Dashboard Overview',
            'assessment': 'New Assessment',
            'history': 'Assessment History',
            'progress': 'Organization Progress',
            'edit_history': 'Edit History',
            'organizations': 'Manage Organizations',
            'levels': 'Level Analysis',
            'manual_sample': 'Create Sample Data',
            'about': 'About TMMi'
        }
        selected_page = st.radio(
            "Select Section",
            options=list(pages.keys()),
            format_func=lambda x: pages[x],
            key='page_selector'
        )
        if selected_page != st.session_state.page:
            st.session_state.page = selected_page
            st.rerun()
        st.markdown("---")
        # Quick stats
        st.markdown("### Quick Statistics")
        try:
            db = TMMiDatabase()
            assessments = db.get_assessments()
            if assessments:
                latest = assessments[0]
                from utils.scoring import generate_assessment_summary
                questions = load_tmmi_questions()
                if questions:
                    summary = generate_assessment_summary(questions, latest)
                    st.markdown(f"""
                    <div class="sidebar-info">
                        <strong>Latest Assessment</strong><br>
                        Date: {latest.timestamp.split('T')[0]}<br>
                        Organization: {latest.organization}<br>
                        Level: {summary['current_level']}<br>
                        Compliance: {summary['overall_percentage']:.1f}%
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Complete your first assessment to see statistics")
        except Exception:
            st.error("Unable to load statistics")
        st.markdown("---")
        # TMMi Level Reference - professional, no emojis
        st.markdown("### TMMi Maturity Levels")
        level_info = {
            1: "Level 1: Initial (Ad-hoc)",
            2: "Level 2: Managed (Basic)",
            3: "Level 3: Defined (Standard)",
            4: "Level 4: Measured (Quantitative)",
            5: "Level 5: Optimized (Continuous)"
        }
        for level, description in level_info.items():
            st.caption(f"**{description}**")
        
        st.markdown("---")
        # Version Information
        st.markdown("### Application Info")
        st.markdown(format_version_display(compact=False), unsafe_allow_html=True)
        
        # Deployment environment
        deployment = get_deployment_info()
        if deployment:
            st.caption(f"Environment: {deployment}")
        
        # Debug info (only in development or when needed)
        render_debug_info()


def render_main_content():
    """Render the main content area based on selected page"""
    # Add version header to main content
    col1, col2 = st.columns([4, 1])
    with col2:
        st.markdown(f"""
        <div style="text-align: right; color: #6C757D; font-size: 0.85em; margin-bottom: 1rem;">
            {format_version_display(compact=True)}
        </div>
        """, unsafe_allow_html=True)
    
    try:
        questions = load_tmmi_questions()
        if not questions:
            show_error_message(
                "Could not load TMMi questions",
                "Please check the data/tmmi_questions.json file exists and is valid."
            )
            return
        current_page = st.session_state.page
        if current_page == 'dashboard':
            render_dashboard(questions)
        elif current_page == 'assessment':
            render_assessment_page(questions)
        elif current_page == 'history':
            render_assessment_history()
        elif current_page == 'progress':
            render_organization_progress()
        elif current_page == 'edit_history':
            render_edit_history()
        elif current_page == 'organizations':
            render_manage_organizations()
        elif current_page == 'levels':
            render_level_breakdown()
        elif current_page == 'manual_sample':
            render_manual_sample_data()
        elif current_page == 'about':
            render_about_page()
    except Exception as e:
        logging.error(f"Error rendering page content: {str(e)}")
        show_error_message("Page loading failed",
                           "Please try refreshing the page.")


def render_assessment_page(questions):
    """Render the assessment page with enhanced error handling"""
    try:
        # Check if we just submitted an assessment
        if 'submitted_assessment_id' in st.session_state:
            render_assessment_success(st.session_state.submitted_assessment_id, questions)
            del st.session_state.submitted_assessment_id
            return
        # Render assessment form
        assessment = render_assessment_form(questions)
        if assessment:
            # Validate assessment before saving
            if not assessment.reviewer_name.strip():
                show_error_message("Reviewer name is required")
                return
            if not assessment.organization.strip():
                show_error_message("Organization name is required")
                return
            if not assessment.answers:
                show_error_message("At least one question must be answered")
                return
            # Save assessment to database
            db = TMMiDatabase()
            assessment_id = db.save_assessment(assessment)
            # Clear form and show success
            st.session_state.assessment_answers = {}
            st.session_state.submitted_assessment_id = assessment_id
            st.rerun()
    except Exception as e:
        logging.error(f"Error in assessment page: {str(e)}")
        show_error_message("Assessment processing failed",
                           "Please try again.")


def render_about_page():
    """Render professional information about TMMi"""
    st.header("About TMMi (Test Maturity Model Integration)")
    st.markdown("""
    The **Test Maturity Model Integration (TMMi)** is a staged maturity model for test process improvement.
    It provides a structured approach to assess and improve testing practices within organizations.
    """)
    # TMMi Levels Overview
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("### TMMi Maturity Levels")
        levels = [
            ("Level 1", "Initial", "Ad-hoc testing processes", "#E74C3C"),
            ("Level 2", "Managed", "Basic test management processes", "#F39C12"),
            ("Level 3", "Defined", "Standardized test processes", "#F1C40F"),
            ("Level 4", "Measured", "Quantitative test process management", "#27AE60"),
            ("Level 5", "Optimized", "Continuous test process improvement", "#2ECC71")
        ]
        for level, name, desc, color in levels:
            st.markdown(f"""
            <div style="
                background-color: {color};
                color: white;
                padding: 12px;
                border-radius: 6px;
                margin: 8px 0;
                text-align: center;
                font-weight: 500;
            ">
                <strong>{level}: {name}</strong><br>
                <small>{desc}</small>
            </div>
            """, unsafe_allow_html=True)
    with col2:
        st.markdown("### Process Areas by Level")
        process_areas = {
            "Level 2 (Managed)": [
                "Test Policy and Strategy",
                "Test Planning",
                "Test Monitoring and Control",
                "Test Design and Execution",
                "Test Environment"
            ],
            "Level 3 (Defined)": [
                "Test Organization",
                "Test Training Program",
                "Test Lifecycle and Integration",
                "Non-functional Testing",
                "Peer Reviews"
            ],
            "Level 4 (Measured)": [
                "Test Measurement",
                "Product Quality Evaluation",
                "Advanced Reviews",
                "Software Quality Control"
            ],
            "Level 5 (Optimized)": [
                "Test Process Improvement",
                "Quality Control",
                "Test Automation",
                "Test Optimization"
            ]
        }
        for level, areas in process_areas.items():
            with st.expander(level):
                for area in areas:
                    st.markdown(f"• {area}")
    # Benefits section - professional, no emojis
    st.markdown("### Benefits of TMMi Assessment")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        **Process Improvement**
        - Structured approach to testing
        - Clear improvement roadmap
        - Best practice adoption
        """)
    with col2:
        st.markdown("""
        **Quality Enhancement**
        - Reduced defect rates
        - Improved test coverage
        - Better risk management
        """)
    with col3:
        st.markdown("""
        **Cost Reduction**
        - Lower rework costs
        - Efficient resource utilization
        - Faster time-to-market
        """)
    # Usage instructions
    st.markdown("### How to Use This Assessment Tool")
    st.markdown("""
    1. **Complete Assessment**: Navigate to "New Assessment" and answer questions across all TMMi levels
    2. **Review Dashboard**: View your current maturity level and compliance metrics
    3. **Analyze Gaps**: Identify specific areas for improvement with recommended actions
    4. **Track Progress**: Complete periodic assessments to monitor improvement over time
    5. **Review History**: Compare assessments to measure progress and trends
    """)
    # External resources
    st.markdown("### Additional Resources")
    st.markdown("""
    - [TMMi Foundation Official Website](https://www.tmmi.org/)
    - [TMMi Framework PDF](https://www.tmmi.org/pdf/TMMi_Framework.pdf)
    - [TMMi Assessment Guide](https://www.tmmi.org/assessment/)
    """)


def main():
    """Main application entry point"""
    try:
        # Initialize session state
        initialize_session_state()
        
        # Initialize sample data if needed (only once per session)
        if not st.session_state.sample_data_initialized:
            try:
                if initialize_sample_data():
                    st.success("✅ Sample data initialized! Check the Organization Progress page.", icon="🎉")
                    logging.info("Sample data initialized for demonstration")
                else:
                    logging.info("Sample data already exists or initialization skipped")
            except Exception as e:
                st.error(f"⚠️ Sample data initialization failed: {str(e)}")
                logging.error(f"Sample data initialization error: {e}")
            st.session_state.sample_data_initialized = True
        
        # Create main layout
        render_sidebar()
        render_main_content()
        # Professional footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #7F8C8D; padding: 1rem; font-size: 0.9rem;">
            TMMi Assessment Tracker | Professional Test Maturity Assessment Platform<br>
            <small>For more information about TMMi, visit
            <a href="https://www.tmmi.org/" target="_blank" style="color: #2E5984;">tmmi.org</a></small>
        </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        logging.critical(f"Critical application error: {str(e)}")
        st.error("A critical error occurred. Please refresh the page "
                 "or contact support.")


if __name__ == "__main__":
    main()
