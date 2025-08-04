"""
Streamlit dashboard components for TMMi assessment visualization
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import List, Dict
from src.models.database import TMMiQuestion, TMMiDatabase
from src.utils.scoring import generate_assessment_summary


def render_dashboard(questions: List[TMMiQuestion]):
    """Render the main TMMi dashboard"""
    
    st.header("TMMi Assessment Dashboard")
    
    db = TMMiDatabase()
    
    # Get all organizations for selection
    organizations = db.get_organizations()
    
    if not organizations:
        st.info("No organizations found. Please add an organization first.")
        if st.button("Manage Organizations"):
            st.session_state.page = 'organizations'
            st.rerun()
        return
    
    # Organization selector
    org_options = {
        org['id']: f"{org['name']} ({org['status']})"
        for org in organizations
    }
    
    selected_org_id = st.selectbox(
        "Select Organization",
        options=list(org_options.keys()),
        format_func=lambda x: org_options[x],
        help="Choose an organization to view dashboard data"
    )
    
    if not selected_org_id:
        return
    
    # Get assessments for selected organization
    org_assessments = db.get_assessments_by_org(selected_org_id)
    
    if not org_assessments:
        selected_org_name = org_options[selected_org_id]
        st.info(f"No assessment data available for {selected_org_name}. Complete an assessment first.")
        if st.button("Start Assessment"):
            st.session_state.page = 'assessment'
            st.rerun()
        return
    
    # Get latest assessment for selected organization
    # Convert org assessment data to Assessment object for compatibility
    latest_org_assessment = org_assessments[-1]  # Most recent
    
    # Get the full Assessment object
    all_assessments = db.get_assessments()
    latest_assessment = None
    for assessment in all_assessments:
        if assessment.id == latest_org_assessment['assessment_id']:
            latest_assessment = assessment
            break
    
    if not latest_assessment:
        st.error("Could not load assessment details.")
        return
    
    summary = generate_assessment_summary(questions, latest_assessment)
    
    # Show organization info
    selected_org = next(org for org in organizations if org['id'] == selected_org_id)
    st.markdown(f"**Organization:** {selected_org['name']} | **Assessments:** {len(org_assessments)}")
    st.markdown("---")
    
    # Dashboard header metrics
    render_header_metrics(summary)
    
    # Main dashboard content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_maturity_trend(all_assessments, questions, selected_org_id)
        render_process_area_compliance(summary)
    
    with col2:
        render_current_level_indicator(summary)
        render_evidence_coverage(summary)
    
    # Gap analysis and recommendations
    render_gap_analysis(summary)


def render_header_metrics(summary: Dict):
    """Render top-level dashboard metrics"""
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Current TMMi Level",
            f"Level {summary['current_level']}",
            help=summary['level_explanation']
        )
    
    with col2:
        st.metric(
            "Overall Compliance",
            f"{summary['overall_percentage']:.1f}%"
        )
    
    with col3:
        st.metric(
            "Assessment Progress",
            f"{summary['answered_questions']}/{summary['total_questions']}",
            f"{(summary['answered_questions'] / summary['total_questions'] * 100):.0f}% complete"
        )
    
    with col4:
        st.metric(
            "High Priority Gaps",
            len(summary['high_priority_gaps']),
            help="Number of high-priority items requiring attention"
        )
    
    with col5:
        st.metric(
            "Evidence Coverage",
            f"{summary['evidence_coverage']['percentage']:.1f}%",
            help="Percentage of answers with supporting evidence"
        )


def render_maturity_trend(assessments: List, questions: List[TMMiQuestion], selected_org_id: int = None):
    """Render maturity progression over time"""
    
    st.markdown("### Maturity Progression Over Time")
    
    # Filter assessments for selected organization if specified
    if selected_org_id:
        db = TMMiDatabase()
        org_assessments = db.get_assessments_by_org(selected_org_id)
        
        if len(org_assessments) < 2:
            st.info("Complete multiple assessments for this organization to see progression trends.")
            return
        
        # Get full assessment objects for the organization
        org_assessment_ids = [a['assessment_id'] for a in org_assessments]
        filtered_assessments = [a for a in assessments if a.id in org_assessment_ids]
    else:
        filtered_assessments = assessments
        
    if len(filtered_assessments) < 2:
        st.info("Complete multiple assessments to see progression trends.")
        return
    
    # Prepare trend data
    trend_data = []
    for assessment in reversed(filtered_assessments):  # Chronological order
        summary = generate_assessment_summary(questions, assessment)
        
        trend_data.append({
            'Date': datetime.fromisoformat(assessment.timestamp).date(),
            'TMMi Level': summary['current_level'],
            'Overall Compliance': summary['overall_percentage'],
            'Assessment ID': assessment.id,
            'Reviewer': assessment.reviewer_name
        })
    
    df = pd.DataFrame(trend_data)
    
    # Create dual-axis chart
    fig = go.Figure()
    
    # Add compliance percentage line
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Overall Compliance'],
        mode='lines+markers',
        name='Overall Compliance %',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8),
        yaxis='y1'
    ))
    
    # Add TMMi level as bars
    fig.add_trace(go.Bar(
        x=df['Date'],
        y=df['TMMi Level'],
        name='TMMi Level',
        marker_color='#ff7f0e',
        opacity=0.6,
        yaxis='y2'
    ))
    
    # Update layout for dual y-axis
    fig.update_layout(
        title="TMMi Maturity Progression",
        xaxis_title="Assessment Date",
        yaxis=dict(
            title="Compliance Percentage",
            side="left",
            range=[0, 100]
        ),
        yaxis2=dict(
            title="TMMi Level",
            side="right",
            overlaying="y",
            range=[1, 6],
            dtick=1
        ),
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_current_level_indicator(summary: Dict):
    """Render current TMMi level with visual indicator"""
    
    st.markdown("### Current TMMi Level")
    
    current_level = summary['current_level']
    
    # Level definitions
    level_info = {
        1: {"name": "Initial", "color": "#ff4444", "description": "Ad-hoc testing processes"},
        2: {"name": "Managed", "color": "#ff8800", "description": "Basic test management"},
        3: {"name": "Defined", "color": "#ffcc00", "description": "Standardized processes"},
        4: {"name": "Measured", "color": "#88cc00", "description": "Quantitative management"},
        5: {"name": "Optimized", "color": "#00cc44", "description": "Continuous improvement"}
    }
    
    # Visual level indicator
    for level in range(1, 6):
        is_current = (level == current_level)
        is_achieved = (level <= current_level)
        
        level_data = level_info[level]
        
        if is_current:
            st.markdown(f"""
            <div style="
                background-color: {level_data['color']}; 
                color: white; 
                padding: 10px; 
                border-radius: 5px; 
                margin: 2px 0;
                font-weight: bold;
                border: 3px solid #333;
            ">
                CURRENT: Level {level}: {level_data['name']}
            </div>
            """, unsafe_allow_html=True)
        elif is_achieved:
            st.markdown(f"""
            <div style="
                background-color: {level_data['color']}; 
                color: white; 
                padding: 8px; 
                border-radius: 5px; 
                margin: 2px 0;
                opacity: 0.7;
            ">
                ACHIEVED: Level {level}: {level_data['name']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="
                background-color: #e0e0e0; 
                color: #666; 
                padding: 8px; 
                border-radius: 5px; 
                margin: 2px 0;
            ">
                TARGET: Level {level}: {level_data['name']}
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown(f"**Current Status:** {summary['level_explanation']}")


def render_process_area_compliance(summary: Dict):
    """Render process area compliance chart"""
    
    st.markdown("### Process Area Compliance")
    
    process_data = summary['process_area_compliance']
    
    if not process_data:
        st.info("No process area data available.")
        return
    
    # Prepare data for visualization
    areas = list(process_data.keys())
    compliance_percentages = [process_data[area]['compliance_percentage'] for area in areas]
    answered_questions = [process_data[area]['answered_questions'] for area in areas]
    total_questions = [process_data[area]['total_questions'] for area in areas]
    
    # Create horizontal bar chart
    df = pd.DataFrame({
        'Process Area': areas,
        'Compliance %': compliance_percentages,
        'Answered': answered_questions,
        'Total': total_questions
    })
    
    # Sort by compliance percentage
    df = df.sort_values('Compliance %', ascending=True)
    
    fig = px.bar(
        df, 
        x='Compliance %', 
        y='Process Area',
        orientation='h',
        title="Compliance by Process Area",
        color='Compliance %',
        color_continuous_scale='RdYlGn',
        range_color=[0, 100],
        text='Compliance %'
    )
    
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(
        height=max(300, len(areas) * 40),
        xaxis=dict(range=[0, 100]),
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_evidence_coverage(summary: Dict):
    """Render evidence coverage visualization"""
    
    st.markdown("### Evidence Coverage")
    
    evidence_data = summary['evidence_coverage']
    
    # Donut chart for evidence coverage
    fig = go.Figure(data=[go.Pie(
        labels=['With Evidence', 'Without Evidence'],
        values=[evidence_data['with_evidence'], 
                evidence_data['total_answers'] - evidence_data['with_evidence']],
        hole=0.6,
        marker_colors=['#00cc44', '#ff4444']
    )])
    
    fig.update_layout(
        title="Evidence Documentation",
        height=300,
        showlegend=True,
        annotations=[dict(text=f"{evidence_data['percentage']:.1f}%", 
                          x=0.5, y=0.5, font_size=20, showarrow=False)]
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.caption(
        f"{evidence_data['with_evidence']} out of {evidence_data['total_answers']} "
        f"answers have supporting evidence"
    )


def render_gap_analysis(summary: Dict):
    """Render comprehensive gap analysis"""
    
    st.markdown("### Gap Analysis & Recommendations")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        priority_filter = st.selectbox(
            "Priority Filter",
            options=['All', 'High', 'Medium', 'Low'],
            index=0
        )
    
    with col2:
        level_filter = st.selectbox(
            "Level Filter",
            options=['All'] + [f'Level {i}' for i in range(2, 6)],
            index=0
        )
    
    with col3:
        answer_filter = st.selectbox(
            "Answer Filter",
            options=['All', 'No', 'Partial', 'Not Answered'],
            index=0
        )
    
    # Apply filters
    gaps = summary['gaps'].copy()
    
    if priority_filter != 'All':
        gaps = [gap for gap in gaps if gap['importance'] == priority_filter]
    
    if level_filter != 'All':
        level_num = int(level_filter.split()[1])
        gaps = [gap for gap in gaps if gap['level'] == level_num]
    
    if answer_filter != 'All':
        gaps = [gap for gap in gaps if gap['current_answer'] == answer_filter]
    
    # Display gaps
    if not gaps:
        st.success("No gaps found with the current filters!")
        return
    
    st.markdown(f"**Found {len(gaps)} gap(s) requiring attention:**")
    
    for i, gap in enumerate(gaps, 1):
        with st.expander(f"Gap {i}: {gap['process_area']} - Level {gap['level']}"):
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Question:** {gap['question']}")
                st.markdown(f"**Current Answer:** {gap['current_answer']}")
                
                if gap['comment']:
                    st.markdown(f"**Comment:** {gap['comment']}")
                
                if gap['evidence_url']:
                    st.markdown(f"**Evidence:** [Link]({gap['evidence_url']})")
            
            with col2:
                priority_class = f"status-{gap['importance'].lower()}"
                st.markdown(f'<span class="{priority_class}">Priority: {gap["importance"]}</span>', 
                            unsafe_allow_html=True)
                st.markdown(f"**Level:** {gap['level']}")
            
            # Recommendation
            st.markdown("**Recommended Action:**")
            st.info(gap['recommended_activity'])
            
            if gap['reference_url']:
                st.markdown(f"[Reference Documentation]({gap['reference_url']})")


def render_level_breakdown():
    """Render detailed breakdown by TMMi level"""
    
    st.header("Level-by-Level Analysis")
    
    db = TMMiDatabase()
    assessments = db.get_assessments()
    
    if not assessments:
        st.info("No assessment data available.")
        return
    
    latest_assessment = assessments[0]
    
    # Load questions for context
    from src.models.database import load_tmmi_questions
    questions = load_tmmi_questions()
    summary = generate_assessment_summary(questions, latest_assessment)
    
    level_compliance = summary['level_compliance']
    
    # Level breakdown
    for level in sorted([2, 3, 4, 5]):
        if level in level_compliance:
            data = level_compliance[level]
            
            level_names = {
                2: "Managed",
                3: "Defined",
                4: "Measured",
                5: "Optimized"
            }
            
            with st.expander(f"Level {level} - {level_names[level]}", 
                             expanded=(level == summary['current_level'])):
                
                # Metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Compliance", f"{data['compliance_percentage']:.1f}%")
                
                with col2:
                    st.metric("Yes Answers", data['yes_count'])
                
                with col3:
                    st.metric("Partial Answers", data['partial_count'])
                
                with col4:
                    st.metric("No Answers", data['no_count'])
                
                # Progress bar
                progress = data['compliance_percentage'] / 100
                st.progress(progress)
                st.caption(f"{data['answered_questions']}/{data['total_questions']} questions answered")
                
                # Status indicator
                if data['compliance_percentage'] >= 80:
                    st.success(f"Level {level} requirements met!")
                elif data['compliance_percentage'] >= 60:
                    st.warning(f"Level {level} partially compliant")
                else:
                    st.error(f"Level {level} requires significant improvement")
