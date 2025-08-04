"""
Organization Progress visualization component for TMMi Assessment Tracker
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from typing import List, Dict, Optional
import logging

from src.models.database import TMMiDatabase, load_tmmi_questions
from src.utils.scoring import (
    generate_assessment_summary, 
    calculate_level_compliance,
    calculate_process_area_compliance
)


def render_organization_progress():
    """Render the organization progress tracking page"""
    
    st.header("Organization Progress")
    st.markdown("Track TMMi maturity progression over time for each organization.")
    
    db = TMMiDatabase()
    
    try:
        # Get all organizations for selection
        organizations = db.get_organizations()
        
        if not organizations:
            st.info("No organizations found. Please add organizations first using the 'Manage Organizations' page.")
            return
        
        # Organization selector
        org_options = {
            org['id']: f"{org['name']} ({org['status']})"
            for org in organizations if org['status'] == 'Active'
        }
        
        if not org_options:
            st.info("No active organizations found. Please activate organizations in the 'Manage Organizations' page.")
            return
        
        selected_org_id = st.selectbox(
            "Select Organization",
            options=list(org_options.keys()),
            format_func=lambda x: org_options[x],
            help="Choose an organization to view its TMMi progress over time"
        )
        
        if selected_org_id:
            render_organization_progress_details(db, selected_org_id)
            
    except Exception as e:
        logging.error(f"Error in organization progress: {str(e)}")
        st.error(f"Failed to load organization progress: {str(e)}")


def render_organization_progress_details(db: TMMiDatabase, org_id: int):
    """Render detailed progress information for selected organization"""
    
    # Get organization details
    organizations = db.get_organizations()
    org = next((o for o in organizations if o['id'] == org_id), None)
    if not org:
        st.error("Organization not found.")
        return
    
    # Get assessment history for this organization
    assessments = db.get_assessments_by_org(org_id)
    
    if not assessments:
        st.info(f"No assessments found for {org['name']}. Complete an assessment first to see progress.")
        return
    
    st.markdown(f"### Progress for {org['name']}")
    contact = org['contact_person'] or 'Not specified'
    email = org['email'] or 'Not specified'
    st.markdown(f"**Contact:** {contact} | **Email:** {email}")
    
    # Load TMMi questions for detailed analysis
    questions = load_tmmi_questions()
    
    # Summary metrics
    render_progress_summary(assessments)
    
    # Main visualizations
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_maturity_timeline(assessments)
        
    with col2:
        render_progress_metrics(assessments)
    
    # Detailed analysis tabs
    tab1, tab2, tab3 = st.tabs(["Process Area Analysis", "Assessment Comparison", "Historical Data"])
    
    with tab1:
        if questions and len(assessments) >= 1:
            render_process_area_analysis(db, assessments, questions)
        else:
            st.info("Process area analysis requires TMMi questions data and "
                    "at least one assessment.")
    
    with tab2:
        if len(assessments) >= 2:
            render_assessment_comparison(db, assessments, questions)
        else:
            st.info("Comparison requires at least 2 assessments.")
    
    with tab3:
        render_historical_data_table(assessments)


def render_progress_summary(assessments: List[Dict]):
    """Render high-level progress summary"""
    
    if len(assessments) < 2:
        st.info("Complete at least 2 assessments to see progress trends.")
        return
    
    # Calculate progress metrics
    first_assessment = assessments[0]
    latest_assessment = assessments[-1]
    
    level_change = latest_assessment['maturity_level'] - first_assessment['maturity_level']
    compliance_change = latest_assessment['compliance_percentage'] - first_assessment['compliance_percentage']
    
    # Time span
    first_date = datetime.fromisoformat(
        first_assessment['timestamp'].replace('Z', '+00:00')
    )
    latest_date = datetime.fromisoformat(
        latest_assessment['timestamp'].replace('Z', '+00:00')
    )
    time_span_days = (latest_date - first_date).days
    
    # Progress summary
    st.markdown("#### Progress Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Current TMMi Level",
            latest_assessment['maturity_level'],
            delta=level_change if level_change != 0 else None
        )
    
    with col2:
        st.metric(
            "Compliance %",
            f"{latest_assessment['compliance_percentage']:.1f}%",
            delta=(f"{compliance_change:+.1f}%"
                   if compliance_change != 0 else None)
        )
    
    with col3:
        st.metric(
            "Total Assessments",
            len(assessments)
        )
    
    with col4:
        st.metric(
            "Time Span",
            (f"{time_span_days} days"
             if time_span_days > 0 else "Same day")
        )
    
    # Progress interpretation
    interpretation = generate_progress_interpretation(assessments)
    if interpretation:
        st.markdown("#### Key Insights")
        st.info(interpretation)


def generate_progress_interpretation(assessments: List[Dict]) -> str:
    """Generate human-readable progress interpretation"""
    
    if len(assessments) < 2:
        return ""
    
    first = assessments[0]
    latest = assessments[-1]
    
    level_change = latest['maturity_level'] - first['maturity_level']
    compliance_change = latest['compliance_percentage'] - first['compliance_percentage']
    
    # Time calculation
    first_date = datetime.fromisoformat(
        first['timestamp'].replace('Z', '+00:00')
    )
    latest_date = datetime.fromisoformat(
        latest['timestamp'].replace('Z', '+00:00')
    )
    months = max(1, round((latest_date - first_date).days / 30))
    
    interpretations = []
    
    # Level progression
    if level_change > 0:
        if level_change >= 2:
            interpretations.append(
                f"Significant maturity advancement from Level "
                f"{first['maturity_level']} to Level {latest['maturity_level']} "
                f"over {months} months."
            )
        else:
            interpretations.append(
                f"Steady progression from Level {first['maturity_level']} to "
                f"Level {latest['maturity_level']} over {months} months."
            )
    elif level_change < 0:
        interpretations.append(
            f"Maturity level decreased from {first['maturity_level']} to "
            f"{latest['maturity_level']}, indicating potential process regression."
        )
    else:
        interpretations.append(
            f"Consistent Level {latest['maturity_level']} maturity maintained "
            f"across assessments."
        )
    
    # Compliance trends
    if compliance_change > 10:
        interpretations.append(
            f"Strong improvement in compliance (+{compliance_change:.1f}%), "
            f"showing effective process implementation."
        )
    elif compliance_change > 0:
        interpretations.append(
            f"Gradual compliance improvement (+{compliance_change:.1f}%)."
        )
    elif compliance_change < -10:
        interpretations.append(
            f"Significant compliance decline (-{abs(compliance_change):.1f}%), "
            f"requiring attention."
        )
    
    # Assessment frequency
    if len(assessments) >= 3:
        interpretations.append(
            f"Regular assessment cadence with {len(assessments)} evaluations "
            f"demonstrates commitment to continuous improvement."
        )
    
    return " ".join(interpretations)


def render_maturity_timeline(assessments: List[Dict]):
    """Render maturity level progression over time"""
    
    st.markdown("#### TMMi Maturity Level Over Time")
    
    # Prepare data for plotting
    df = pd.DataFrame(assessments)
    df['date'] = pd.to_datetime(df['timestamp'])
    df['formatted_date'] = df['date'].dt.strftime('%Y-%m-%d')
    
    # Create stepped line chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['maturity_level'],
        mode='lines+markers',
        line=dict(shape='hv', width=3, color='#2E5984'),
        marker=dict(size=8, color='#4A90C2'),
        name='TMMi Level',
        hovertemplate='<b>Date:</b> %{x|%Y-%m-%d}<br>' +
                      '<b>TMMi Level:</b> %{y}<br>' +
                      '<b>Compliance:</b> %{customdata:.1f}%<extra></extra>',
        customdata=df['compliance_percentage']
    ))
    
    fig.update_layout(
        title="TMMi Maturity Level Progression",
        xaxis_title="Assessment Date",
        yaxis_title="TMMi Level",
        yaxis=dict(
            range=[0.5, 5.5],
            tickmode='array',
            tickvals=[1, 2, 3, 4, 5],
            ticktext=['Level 1<br>Initial', 'Level 2<br>Managed',
                      'Level 3<br>Defined', 'Level 4<br>Measured',
                      'Level 5<br>Optimized']
        ),
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_progress_metrics(assessments: List[Dict]):
    """Render key progress metrics"""
    
    st.markdown("#### Key Metrics")
    
    # Latest assessment details
    latest = assessments[-1]
    
    # Compliance breakdown
    st.markdown("**Latest Assessment Breakdown**")
    
    total_answers = latest['total_answers']
    if total_answers > 0:
        yes_pct = (latest['yes_count'] / total_answers) * 100
        partial_pct = (latest['partial_count'] / total_answers) * 100
        no_pct = (latest['no_count'] / total_answers) * 100
        
        # Create a simple bar chart for answer distribution
        answer_data = pd.DataFrame({
            'Answer Type': ['Yes', 'Partial', 'No'],
            'Count': [latest['yes_count'], latest['partial_count'],
                      latest['no_count']],
            'Percentage': [yes_pct, partial_pct, no_pct]
        })
        
        color_map = {
            'Yes': '#27AE60',
            'Partial': '#F39C12',
            'No': '#E74C3C'
        }
        fig = px.bar(
            answer_data,
            x='Answer Type',
            y='Count',
            color='Answer Type',
            color_discrete_map=color_map,
            title="Answer Distribution"
        )
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Trend indicator
    if len(assessments) >= 2:
        prev_assessment = assessments[-2]
        trend = latest['compliance_percentage'] - prev_assessment['compliance_percentage']
        
        if trend > 0:
            st.success(
                f"Upward trend: +{trend:.1f}% from previous assessment"
            )
        elif trend < 0:
            st.error(
                f"Downward trend: {trend:.1f}% from previous assessment"
            )
        else:
            st.info("No change from previous assessment")


def render_process_area_analysis(db: TMMiDatabase, assessments: List[Dict], questions: List):
    """Render process area comparison for recent assessments"""
    
    st.markdown("#### Process Area Analysis")
    
    if len(assessments) < 1:
        st.info("No assessments available for analysis.")
        return
    
    # Get detailed scores for the most recent assessments (up to 3)
    recent_assessments = (assessments[-3:]
                          if len(assessments) >= 3 else assessments)
    
    process_area_data = []
    
    for assessment in recent_assessments:
        assessment_detail = db.get_tmmi_scores_by_assessment(
            assessment['assessment_id']
        )
        if not assessment_detail or not questions:
            continue
        
        # Create Assessment object for scoring
        from src.models.database import Assessment, AssessmentAnswer
        
        answers = []
        for q_id, answer_data in assessment_detail['answers'].items():
            answers.append(AssessmentAnswer(
                question_id=q_id,
                answer=answer_data['answer'],
                evidence_url=answer_data.get('evidence_url'),
                comment=answer_data.get('comment')
            ))
        
        # Calculate process area compliance
        process_compliance = calculate_process_area_compliance(questions, answers)
        
        assessment_date = datetime.fromisoformat(
            assessment['timestamp'].replace('Z', '+00:00')
        ).strftime('%Y-%m-%d')
        
        for area, metrics in process_compliance.items():
            process_area_data.append({
                'Assessment Date': assessment_date,
                'Process Area': area,
                'Compliance %': metrics['compliance_percentage'],
                'Yes Count': metrics['yes_count'],
                'Total Questions': metrics['total_questions']
            })
    
    if process_area_data:
        # Create grouped bar chart
        df_process = pd.DataFrame(process_area_data)
        
        fig = px.bar(
            df_process,
            x='Process Area',
            y='Compliance %',
            color='Assessment Date',
            barmode='group',
            title="Process Area Compliance Comparison"
        )
        fig.update_layout(
            height=400,
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Show detailed table
        with st.expander("Detailed Process Area Scores"):
            st.dataframe(df_process, use_container_width=True)
    else:
        st.info("Process area analysis requires detailed assessment data.")


def render_assessment_comparison(db: TMMiDatabase, assessments: List[Dict], questions: List):
    """Render side-by-side comparison of recent assessments"""
    
    st.markdown("#### Assessment Comparison")
    
    # Let user select which assessments to compare
    assessment_options = {
        i: (f"{a['timestamp'][:10]} - Level {a['maturity_level']} "
            f"({a['compliance_percentage']:.1f}%)")
        for i, a in enumerate(assessments)
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        assessment1_idx = st.selectbox(
            "First Assessment",
            options=list(assessment_options.keys()),
            format_func=lambda x: assessment_options[x],
            index=0 if len(assessments) >= 2 else 0
        )
    
    with col2:
        assessment2_idx = st.selectbox(
            "Second Assessment",
            options=list(assessment_options.keys()),
            format_func=lambda x: assessment_options[x],
            index=len(assessments)-1 if len(assessments) >= 2 else 0
        )
    
    if assessment1_idx != assessment2_idx:
        # Compare the selected assessments
        a1 = assessments[assessment1_idx]
        a2 = assessments[assessment2_idx]
        
        # Create comparison metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "TMMi Level Change",
                a2['maturity_level'],
                delta=a2['maturity_level'] - a1['maturity_level']
            )
        
        with col2:
            compliance_delta = a2['compliance_percentage'] - a1['compliance_percentage']
            st.metric(
                "Compliance Change",
                f"{a2['compliance_percentage']:.1f}%",
                delta=f"{compliance_delta:+.1f}%"
            )
        
        with col3:
            st.metric(
                "Yes Answers Change",
                a2['yes_count'],
                delta=a2['yes_count'] - a1['yes_count']
            )
        
        # Side-by-side comparison table
        comparison_data = {
            'Metric': [
                'Assessment Date', 'TMMi Level', 'Compliance %',
                'Yes Answers', 'Partial Answers', 'No Answers',
                'Total Questions'
            ],
            'First Assessment': [
                a1['timestamp'][:10],
                a1['maturity_level'],
                f"{a1['compliance_percentage']:.1f}%",
                a1['yes_count'],
                a1['partial_count'],
                a1['no_count'],
                a1['total_answers']
            ],
            'Second Assessment': [
                a2['timestamp'][:10],
                a2['maturity_level'],
                f"{a2['compliance_percentage']:.1f}%",
                a2['yes_count'],
                a2['partial_count'],
                a2['no_count'],
                a2['total_answers']
            ]
        }
        
        df_comparison = pd.DataFrame(comparison_data)
        st.dataframe(df_comparison, use_container_width=True,
                     hide_index=True)


def render_historical_data_table(assessments: List[Dict]):
    """Render complete historical data in tabular format"""
    
    st.markdown("#### Complete Assessment History")
    
    # Prepare data for display
    table_data = []
    for i, assessment in enumerate(assessments):
        table_data.append({
            'Assessment #': i + 1,
            'Date': assessment['timestamp'][:10],
            'Reviewer': assessment['reviewer_name'],
            'TMMi Level': assessment['maturity_level'],
            'Compliance %': f"{assessment['compliance_percentage']:.1f}%",
            'Yes': assessment['yes_count'],
            'Partial': assessment['partial_count'],
            'No': assessment['no_count'],
            'Total': assessment['total_answers']
        })
    
    df_history = pd.DataFrame(table_data)
    
    # Display with styling
    st.dataframe(
        df_history,
        use_container_width=True,
        hide_index=True,
        column_config={
            'Assessment #': st.column_config.NumberColumn(
                'Assessment #', width='small'
            ),
            'Date': st.column_config.DateColumn('Date', width='medium'),
            'TMMi Level': st.column_config.NumberColumn(
                'TMMi Level', width='small'
            ),
            'Compliance %': st.column_config.TextColumn(
                'Compliance %', width='small'
            ),
            'Yes': st.column_config.NumberColumn('Yes', width='small'),
            'Partial': st.column_config.NumberColumn('Partial', width='small'),
            'No': st.column_config.NumberColumn('No', width='small'),
            'Total': st.column_config.NumberColumn('Total', width='small')
        }
    )
    
    # Export option
    if st.button("Download Historical Data as CSV"):
        csv = df_history.to_csv(index=False)
        org_name = assessments[0]['organization'].replace(' ', '_')
        filename = f"tmmi_progress_{org_name}.csv"
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=filename,
            mime="text/csv"
        )