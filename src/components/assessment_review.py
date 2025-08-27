"""
Assessment Review Component for N2S TMMi Tracker
Displays the most recent completed assessment for a selected organization
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Optional
from src.models.database import TMMiQuestion, AssessmentAnswer, Assessment, TMMiDatabase
from src.utils.scoring import generate_assessment_summary
import base64
from datetime import datetime


def render_assessment_review():
    """Render the main assessment review interface"""
    st.header("Assessment Review")
    st.markdown("Review the most recent completed assessment for a selected organization.")
    
    # Load database and questions
    db = TMMiDatabase()
    questions = load_tmmi_questions()
    
    if not questions:
        st.error("Could not load TMMi questions. Please check the data configuration.")
        return
    
    # Organization selection
    organizations = db.get_organizations_for_assessment()
    if not organizations:
        st.warning("No organizations found. Please add organizations first using the 'Manage Organizations' section.")
        return
    
    # Create organization selector
    org_names = [org["name"] for org in organizations]
    selected_org = st.selectbox(
        "Select Organization",
        options=org_names,
        help="Choose an organization to review their most recent assessment"
    )
    
    if selected_org:
        # Get the latest assessment for the selected organization
        latest_assessment = db.get_latest_assessment_by_organization(selected_org)
        
        if latest_assessment:
            render_assessment_details(latest_assessment, questions, db)
        else:
            st.info(f"No assessments found for {selected_org}. Complete an assessment first to see review data here.")
    else:
        st.info("Please select an organization to view their assessment review.")


def render_assessment_details(assessment: Assessment, questions: List[TMMiQuestion], db: TMMiDatabase):
    """Render detailed assessment information"""
    
    # Assessment header with metadata
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.subheader(f"Assessment Review: {assessment.organization}")
        st.markdown(f"**Reviewer:** {assessment.reviewer_name}")
        st.markdown(f"**Assessment Date:** {format_timestamp(assessment.timestamp)}")
    
    with col2:
        # Generate summary metrics
        summary = generate_assessment_summary(questions, assessment)
        st.metric("Current Level", f"Level {summary['current_level']}")
        st.metric("Compliance", f"{summary['overall_percentage']:.1f}%")
    
    with col3:
        st.metric("Questions", f"{len(assessment.answers)}")
        st.metric("Evidence Items", count_evidence_items(assessment.answers))
    
    # Export options
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("Export to CSV", use_container_width=True):
            export_to_csv(assessment, questions)
    
    with col2:
        if st.button("Export to Markdown", use_container_width=True):
            export_to_markdown(assessment, questions)
    
    with col3:
        if st.button("Print View", use_container_width=True):
            st.info("Use your browser's print function (Ctrl+P / Cmd+P) to print this view")
    
    # Assessment content organized by TMMi levels
    st.markdown("---")
    st.subheader("Assessment Questions by TMMi Level")
    
    # Group questions by level
    questions_by_level = group_questions_by_level(questions)
    
    # Create tabs for each level
    level_tabs = st.tabs([f"Level {level}" for level in sorted(questions_by_level.keys())])
    
    for i, (level, level_questions) in enumerate(sorted(questions_by_level.items())):
        with level_tabs[i]:
            render_level_questions(level, level_questions, assessment, questions)


def render_level_questions(level: int, level_questions: List[TMMiQuestion], 
                          assessment: Assessment, all_questions: List[TMMiQuestion]):
    """Render questions for a specific TMMi level"""
    
    # Calculate level compliance
    level_answers = [ans for ans in assessment.answers 
                    if any(q.id == ans.question_id for q in level_questions)]
    
    level_summary = calculate_level_summary(level_questions, level_answers)
    
    # Level overview
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Questions", len(level_questions))
    with col2:
        st.metric("Answered", len(level_answers))
    with col3:
        st.metric("Compliance", f"{level_summary['compliance']:.1f}%")
    with col4:
        st.metric("Level Status", get_level_status(level_summary['compliance']))
    
    st.markdown("---")
    
    # Process areas within this level
    process_areas = group_questions_by_process_area(level_questions)
    
    for process_area, area_questions in process_areas.items():
        with st.expander(f"**{process_area}** ({len(area_questions)} questions)", expanded=True):
            render_process_area_questions(process_area, area_questions, assessment)


def render_process_area_questions(process_area: str, area_questions: List[TMMiQuestion], 
                                assessment: Assessment):
    """Render questions for a specific process area"""
    
    for i, question in enumerate(area_questions):
        # Find the answer for this question
        answer = next((ans for ans in assessment.answers if ans.question_id == question.id), None)
        
        if answer:
            render_question_with_answer(question, answer, is_first=(i == 0))
        else:
            render_unanswered_question(question, is_first=(i == 0))


def render_question_with_answer(question: TMMiQuestion, answer: AssessmentAnswer, is_first: bool = False):
    """Render a single question with its answer details"""
    
    # Only add separator if not the first question in the category
    if not is_first:
        st.markdown("---")
    
    # Question header with ID and text
    st.markdown(f"**{question.id}:** {question.question}")
    
    # Priority and Answer status on the same line
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Priority indicator - styled as colored text
        priority_colors = {"High": "#dc3545", "Medium": "#fd7e14", "Low": "#28a745"}
        priority_color = priority_colors.get(question.importance, "#6c757d")
        st.markdown(f"""
        <div style="
            color: {priority_color};
            font-weight: 600;
            font-size: 0.9em;
            margin: 8px 0;
        ">
            Priority: {question.importance}
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Answer indicator - styled as colored text
        answer_colors = {"Yes": "#28a745", "Partial": "#ffc107", "No": "#dc3545"}
        answer_color = answer_colors.get(answer.answer, "#6c757d")
        st.markdown(f"""
        <div style="
            color: {answer_color};
            font-weight: 600;
            font-size: 0.9em;
            margin: 8px 0;
        ">
            Answer: {answer.answer}
        </div>
        """, unsafe_allow_html=True)
    
    # Answer details - ensure comments are rendered with clear indicator
    if answer.comment and answer.comment.strip():
        st.info(f"**Comments:** {answer.comment}")
    else:
        st.info("**Comments:** No additional comments provided")
    
    # Evidence/attachments
    if answer.evidence_url and answer.evidence_url.strip():
        st.markdown("**Evidence/Documentation:**")
        if is_valid_url(answer.evidence_url):
            st.markdown(f"[View Evidence]({answer.evidence_url})")
        else:
            st.markdown(f"{answer.evidence_url}")
    
    # Recommendation if not fully compliant
    if answer.answer in ["Partial", "No"]:
        with st.expander("Improvement Recommendation", expanded=False):
            st.info(f"**Recommended Activity:** {question.recommended_activity}")
            if question.reference_url:
                st.markdown(f"""
                <div style="margin-top: 8px;">
                    <a href="{question.reference_url}" target="_blank" style="color: #0056b3;">
                        Reference Documentation
                    </a>
                </div>
                """, unsafe_allow_html=True)


def render_unanswered_question(question: TMMiQuestion, is_first: bool = False):
    """Render a question that wasn't answered in the assessment"""
    
    # Only add separator if not the first question in the category
    if not is_first:
        st.markdown("---")
    
    st.markdown(f"**{question.id}:** {question.question}")
    st.warning("Not answered in this assessment")


def export_to_csv(assessment: Assessment, questions: List[TMMiQuestion]):
    """Export assessment data to CSV format"""
    
    # Create export data
    export_data = []
    
    for question in questions:
        answer = next((ans for ans in assessment.answers if ans.question_id == question.id), None)
        
        export_data.append({
            "Question ID": question.id,
            "Level": question.level,
            "Process Area": question.process_area,
            "Question": question.question,
            "Priority": question.importance,
            "Answer": answer.answer if answer else "Not Answered",
            "Comments": answer.comment if answer else "",
            "Evidence URL": answer.evidence_url if answer else "",
            "Recommended Activity": question.recommended_activity,
            "Reference URL": question.reference_url
        })
    
    # Create DataFrame and export
    df = pd.DataFrame(export_data)
    csv = df.to_csv(index=False)
    
    # Create download button
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="tmmi_assessment_{assessment.organization}_{format_timestamp(assessment.timestamp)}.csv">Download CSV</a>'
    st.markdown(href, unsafe_allow_html=True)


def export_to_markdown(assessment: Assessment, questions: List[TMMiQuestion]):
    """Export assessment data to Markdown format"""
    
    # Create markdown content
    md_content = f"""# TMMi Assessment Review - {assessment.organization}

**Assessment Date:** {format_timestamp(assessment.timestamp)}  
**Reviewer:** {assessment.reviewer_name}  
**Total Questions:** {len(questions)}  
**Questions Answered:** {len(assessment.answers)}

---

"""
    
    # Group by level and process area
    questions_by_level = group_questions_by_level(questions)
    
    for level in sorted(questions_by_level.keys()):
        level_questions = questions_by_level[level]
        md_content += f"## Level {level}\n\n"
        
        process_areas = group_questions_by_process_area(level_questions)
        for process_area, area_questions in process_areas.items():
            md_content += f"### {process_area}\n\n"
            
            for question in area_questions:
                answer = next((ans for ans in assessment.answers if ans.question_id == question.id), None)
                
                md_content += f"#### {question.id}: {question.question}\n\n"
                md_content += f"- **Priority:** {question.importance}\n"
                md_content += f"- **Answer:** {answer.answer if answer else 'Not Answered'}\n"
                
                if answer and answer.comment:
                    md_content += f"- **Comments:** {answer.comment}\n"
                else:
                    md_content += f"- **Comments:** No additional comments provided\n"
                
                if answer and answer.evidence_url:
                    md_content += f"- **Evidence:** {answer.evidence_url}\n"
                
                if answer and answer.answer in ["Partial", "No"]:
                    md_content += f"- **Recommendation:** {question.recommended_activity}\n"
                
                md_content += "\n"
    
    # Create download button
    b64 = base64.b64encode(md_content.encode()).decode()
    href = f'<a href="data:file/markdown;base64,{b64}" download="tmmi_assessment_{assessment.organization}_{format_timestamp(assessment.timestamp)}.md">Download Markdown</a>'
    st.markdown(href, unsafe_allow_html=True)


def group_questions_by_level(questions: List[TMMiQuestion]) -> Dict[int, List[TMMiQuestion]]:
    """Group questions by TMMi level"""
    questions_by_level = {}
    for question in questions:
        if question.level not in questions_by_level:
            questions_by_level[question.level] = []
        questions_by_level[question.level].append(question)
    return questions_by_level


def group_questions_by_process_area(questions: List[TMMiQuestion]) -> Dict[str, List[TMMiQuestion]]:
    """Group questions by process area"""
    questions_by_area = {}
    for question in questions:
        if question.process_area not in questions_by_area:
            questions_by_area[question.process_area] = []
        questions_by_area[question.process_area].append(question)
    return questions_by_area


def calculate_level_summary(level_questions: List[TMMiQuestion], level_answers: List[AssessmentAnswer]) -> Dict:
    """Calculate summary statistics for a specific level"""
    
    if not level_questions:
        return {"compliance": 0.0, "answered": 0, "total": 0}
    
    total_score = 0.0
    for answer in level_answers:
        if answer.answer == "Yes":
            total_score += 1.0
        elif answer.answer == "Partial":
            total_score += 0.5
    
    compliance = (total_score / len(level_questions)) * 100 if level_questions else 0
    
    return {
        "compliance": compliance,
        "answered": len(level_answers),
        "total": len(level_questions)
    }


def get_level_status(compliance: float) -> str:
    """Get human-readable level status based on compliance percentage"""
    if compliance >= 90:
        return "Optimized"
    elif compliance >= 80:
        return "Measured"
    elif compliance >= 60:
        return "Defined"
    elif compliance >= 40:
        return "Managed"
    else:
        return "Initial"


def count_evidence_items(answers: List[AssessmentAnswer]) -> int:
    """Count the number of answers with evidence URLs"""
    return sum(1 for ans in answers if ans.evidence_url)


def format_timestamp(timestamp: str) -> str:
    """Format timestamp for display"""
    try:
        if 'T' in timestamp:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime("%B %d, %Y")
        else:
            return timestamp
    except:
        return timestamp


def is_valid_url(url: str) -> bool:
    """Check if a string is a valid URL"""
    return url.startswith(('http://', 'https://', 'ftp://'))


def load_tmmi_questions(file_path: str = None) -> List[TMMiQuestion]:
    """Load TMMi questions from JSON file"""
    import json
    import os
    
    if file_path is None:
        file_path = os.environ.get("TMMI_QUESTIONS_PATH", "data/tmmi_questions.json")

    try:
        with open(file_path, "r") as f:
            questions_data = json.load(f)
        return [TMMiQuestion(**q) for q in questions_data]
    except FileNotFoundError:
        st.error(f"Questions file not found: {file_path}")
        return []
    except json.JSONDecodeError as e:
        st.error(f"Error parsing questions file: {e}")
        return []
