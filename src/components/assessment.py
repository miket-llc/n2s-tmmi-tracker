"""
Streamlit components for TMMi assessment interface
"""
import streamlit as st
from typing import List, Dict, Optional
from src.models.database import (TMMiQuestion, AssessmentAnswer,
                                 Assessment, TMMiDatabase)
from src.utils.scoring import generate_assessment_summary


def render_assessment_form(questions: List[TMMiQuestion]
                           ) -> Optional[Assessment]:
    """Render the main assessment form with organization selection and
    pre-population"""

    st.header("TMMi Assessment")
    st.markdown("Complete the assessment by answering questions across all "
                "TMMi levels and process areas.")

    # Initialize session state for pre-filled data
    if 'prefilled_data' not in st.session_state:
        st.session_state.prefilled_data = {}
    if 'selected_organization' not in st.session_state:
        st.session_state.selected_organization = None
    if 'original_assessment' not in st.session_state:
        st.session_state.original_assessment = None

    # Organization selection
    db = TMMiDatabase()

    with st.expander("Organization Selection", expanded=True):
        # Get organizations for selection
        organizations = db.get_organizations_for_assessment()

        if organizations:
            org_options = ["Select an organization..."] + [org['name'] for org in organizations]

            col1, col2 = st.columns([2, 1])
            with col1:
                selected_org_name = st.selectbox(
                    "Choose Organization",
                    options=org_options,
                    help=("Select an existing organization to pre-fill "
                          "form with their latest assessment data")
                )

            with col2:
                if selected_org_name and selected_org_name != "Select an organization...":
                    org_data = next((org for org in organizations if org['name'] == selected_org_name), None)
                    if org_data:
                        st.info(f"**{org_data['assessment_count']}** previous assessments")
                        st.caption(f"Latest: {org_data['latest_assessment']}")

            # Handle organization selection change
            if selected_org_name != st.session_state.selected_organization:
                st.session_state.selected_organization = selected_org_name
                if selected_org_name and selected_org_name != "Select an organization...":
                    # Load latest assessment for pre-population
                    latest_assessment = db.get_latest_assessment_by_organization(selected_org_name)
                    st.session_state.original_assessment = latest_assessment

                    if latest_assessment:
                        # Pre-populate form data
                        st.session_state.prefilled_data = {
                            'reviewer_name': latest_assessment.reviewer_name,
                            'organization': latest_assessment.organization
                        }

                        # Pre-populate answers
                        prefilled_answers = {}
                        for answer in latest_assessment.answers:
                            prefilled_answers[answer.question_id] = {
                                'answer': answer.answer,
                                'evidence_url': answer.evidence_url or '',
                                'comment': answer.comment or ''
                            }
                        st.session_state.assessment_answers = prefilled_answers.copy()

                        st.success(
                            f"Form pre-filled with data from {selected_org_name}'s most recent "
                            f"assessment from {latest_assessment.timestamp.split('T')[0]}"
                        )
                    else:
                        st.session_state.prefilled_data = {'organization': selected_org_name}
                        st.session_state.assessment_answers = {}
                        st.info(f"No previous assessments found for {selected_org_name}. Starting with a blank form.")
                else:
                    # Clear pre-filled data
                    st.session_state.prefilled_data = {}
                    st.session_state.assessment_answers = {}
                    st.session_state.original_assessment = None
        else:
            st.info(
                "No organizations available. Please add organizations first using the "
                "'Manage Organizations' section."
            )

    # Assessment metadata
    with st.expander("Assessment Information", expanded=True):
        col1, col2 = st.columns(2)

        # Show pre-population status if applicable
        if st.session_state.original_assessment:
            st.markdown(
                f"**Pre-filling form with data from {st.session_state.selected_organization}'s "
                f"most recent assessment.**"
            )
            st.caption(
                f"Previous assessment completed on: "
                f"{st.session_state.original_assessment.timestamp.split('T')[0]}"
            )

        with col1:
            reviewer_name = st.text_input(
                "Reviewer Name *",
                value=st.session_state.prefilled_data.get('reviewer_name', ''),
                help="Person conducting this assessment"
            )

            # Show change indicator for reviewer
            if (st.session_state.original_assessment
                    and reviewer_name != st.session_state.original_assessment.reviewer_name):
                st.markdown(f"**Modified** _(previous: {st.session_state.original_assessment.reviewer_name})_")

        with col2:
            organization = st.text_input(
                "Organization *",
                value=st.session_state.prefilled_data.get('organization', ''),
                help="Organization being assessed"
            )

            # Show change indicator for organization
            if (st.session_state.original_assessment
                    and organization != st.session_state.original_assessment.organization):
                st.markdown(f"**Modified** _(previous: {st.session_state.original_assessment.organization})_")

    if not reviewer_name or not organization:
        st.warning("Please fill in the reviewer name and organization before proceeding.")
        return None

    # Group questions by level and process area
    questions_by_level = {}
    for question in questions:
        if question.level not in questions_by_level:
            questions_by_level[question.level] = {}
        if question.process_area not in questions_by_level[question.level]:
            questions_by_level[question.level][question.process_area] = []
        questions_by_level[question.level][question.process_area].append(question)

    # Store answers in session state
    if 'assessment_answers' not in st.session_state:
        st.session_state.assessment_answers = {}

    # Progress tracking
    total_questions = len(questions)
    answered_questions = len(st.session_state.assessment_answers)
    progress = answered_questions / total_questions if total_questions > 0 else 0

    st.markdown("### Assessment Progress")
    st.progress(progress)
    st.caption(f"{answered_questions}/{total_questions} questions answered ({progress:.1%})")

    # Render questions by level
    st.markdown("### Assessment Questions")

    level_names = {
        2: "Level 2 - Managed",
        3: "Level 3 - Defined",
        4: "Level 4 - Measured",
        5: "Level 5 - Optimized"
    }

    for level in sorted(questions_by_level.keys()):
        with st.expander(f"{level_names.get(level, f'Level {level}')}", expanded=level == 2):

            for process_area in sorted(questions_by_level[level].keys()):
                st.markdown(f"**{process_area}**")

                for question in questions_by_level[level][process_area]:
                    render_question(question)

                st.markdown("---")

    # Assessment submission
    st.markdown("### Submit Assessment")

    if answered_questions == 0:
        st.info("Please answer at least one question before submitting.")
        return None

    # Show change summary if this is a reassessment
    if st.session_state.original_assessment:
        render_change_summary_before_submit(st.session_state.original_assessment,
                                            st.session_state.assessment_answers,
                                            reviewer_name, organization)

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button("Save Assessment", type="primary"):
            # Create assessment object
            answers = [
                AssessmentAnswer(
                    question_id=q_id,
                    answer=answer_data['answer'],
                    evidence_url=answer_data.get('evidence_url'),
                    comment=answer_data.get('comment')
                )
                for q_id, answer_data in st.session_state.assessment_answers.items()
            ]

            assessment = Assessment(
                reviewer_name=reviewer_name,
                organization=organization,
                answers=answers
            )

            return assessment

    with col2:
        if st.button("Clear All"):
            st.session_state.assessment_answers = {}
            st.rerun()

    with col3:
        st.caption(f"Progress: {answered_questions}/{total_questions} questions answered")

    return None


def render_change_summary_before_submit(original_assessment: Assessment,
                                        current_answers: Dict,
                                        current_reviewer: str,
                                        current_organization: str):
    """Show summary of changes before submitting reassessment"""

    with st.expander("Change Summary", expanded=False):
        st.markdown("**Summary of changes from previous assessment:**")

        changes = []

        # Check metadata changes
        if current_reviewer != original_assessment.reviewer_name:
            changes.append(f"Reviewer: {original_assessment.reviewer_name} → {current_reviewer}")

        if current_organization != original_assessment.organization:
            changes.append(f"Organization: {original_assessment.organization} → {current_organization}")

        # Check answer changes
        original_answers = {ans.question_id: ans for ans in original_assessment.answers}

        for question_id, current_data in current_answers.items():
            if question_id in original_answers:
                original_ans = original_answers[question_id]

                # Check answer change
                if current_data.get('answer') != original_ans.answer:
                    changes.append(
                        f"Q{question_id.split('_')[-1]} Answer: {original_ans.answer} → "
                        f"{current_data.get('answer')}"
                    )

                # Check evidence change
                original_evidence = original_ans.evidence_url or ''
                current_evidence = current_data.get('evidence_url', '')
                if current_evidence != original_evidence:
                    if original_evidence and current_evidence:
                        changes.append(f"Q{question_id.split('_')[-1]} Evidence: Modified")
                    elif current_evidence:
                        changes.append(f"Q{question_id.split('_')[-1]} Evidence: Added")
                    else:
                        changes.append(f"Q{question_id.split('_')[-1]} Evidence: Removed")

                # Check comment change
                original_comment = original_ans.comment or ''
                current_comment = current_data.get('comment', '')
                if current_comment != original_comment:
                    if original_comment and current_comment:
                        changes.append(f"Q{question_id.split('_')[-1]} Comment: Modified")
                    elif current_comment:
                        changes.append(f"Q{question_id.split('_')[-1]} Comment: Added")
                    else:
                        changes.append(f"Q{question_id.split('_')[-1]} Comment: Removed")
            else:
                # New answer
                changes.append(f"Q{question_id.split('_')[-1]}: New answer added ({current_data.get('answer')})")

        # Check for removed answers
        for question_id in original_answers.keys():
            if question_id not in current_answers:
                changes.append(f"Q{question_id.split('_')[-1]}: Answer removed")

        if changes:
            st.markdown(f"**Total Changes: {len(changes)}**")
            for change in changes:
                st.markdown(f"• {change}")
        else:
            st.info("No changes detected from the previous assessment.")


def render_question(question: TMMiQuestion):
    """Render a single assessment question with change tracking"""

    # Question container
    question_key = f"q_{question.id}"

    st.markdown(f"**Q{question.id.split('_')[-1]}:** {question.question}")

    # Show importance and level
    importance_color = {
        'High': 'High Priority',
        'Medium': 'Medium Priority',
        'Low': 'Low Priority'
    }

    col1, col2 = st.columns([3, 1])

    with col2:
        priority_class = f"status-{question.importance.lower()}"
        st.markdown(
            f'<span class="{priority_class}">'
            f'{importance_color.get(question.importance, question.importance)} Priority</span>',
            unsafe_allow_html=True)

    # Get original answer for comparison
    original_answer = None
    original_evidence = ''
    original_comment = ''

    if st.session_state.original_assessment:
        for ans in st.session_state.original_assessment.answers:
            if ans.question_id == question.id:
                original_answer = ans.answer
                original_evidence = ans.evidence_url or ''
                original_comment = ans.comment or ''
                break

    # Answer selection
    current_answer = st.session_state.assessment_answers.get(question.id, {}).get('answer', None)

    answer = st.radio(
        "Answer",
        options=['Yes', 'Partial', 'No'],
        index=['Yes', 'Partial', 'No'].index(current_answer) if current_answer else None,
        key=f"{question_key}_answer",
        horizontal=True,
        label_visibility="collapsed"
    )

    # Show change indicator for answer
    if original_answer and answer and answer != original_answer:
        st.markdown(f"**Answer Modified** _(previous: {original_answer})_")

    # Evidence URL field
    evidence_url = st.text_input(
        "Evidence/Reference URL (optional)",
        value=st.session_state.assessment_answers.get(question.id, {}).get('evidence_url', ''),
        key=f"{question_key}_evidence",
        help="Link to supporting documentation or evidence"
    )

    # Show change indicator for evidence
    if original_evidence and evidence_url != original_evidence:
        if original_evidence:
            st.markdown(f"**Evidence Modified** _(previous: {original_evidence[:50]}...)_")
        else:
            st.markdown("**Evidence Added**")

    # Comment field
    comment = st.text_area(
        "Comments (optional)",
        value=st.session_state.assessment_answers.get(question.id, {}).get('comment', ''),
        key=f"{question_key}_comment",
        height=80,
        help="Additional notes or context for this answer"
    )

    # Show change indicator for comment
    if original_comment and comment != original_comment:
        if original_comment:
            st.markdown(f"**Comment Modified** _(previous: {original_comment[:50]}...)_")
        else:
            st.markdown("**Comment Added**")

    # Show recommendation if not fully compliant
    if answer in ['Partial', 'No']:
        with st.expander("Improvement Recommendation"):
            st.info(f"**Recommended Activity:** {question.recommended_activity}")
            if question.reference_url:
                st.markdown(f"[Reference Documentation]({question.reference_url})")

    # Update session state
    if answer:
        if question.id not in st.session_state.assessment_answers:
            st.session_state.assessment_answers[question.id] = {}

        st.session_state.assessment_answers[question.id].update({
            'answer': answer,
            'evidence_url': evidence_url,
            'comment': comment
        })

    st.markdown("")  # Add spacing


def render_assessment_success(assessment_id: int, questions: List[TMMiQuestion]):
    """Render success message after assessment submission"""

    st.success(f"Assessment saved successfully! (ID: {assessment_id})")

    # Load and display summary
    db = TMMiDatabase()
    assessments = db.get_assessments()

    if assessments:
        latest_assessment = assessments[0]  # Most recent
        summary = generate_assessment_summary(questions, latest_assessment)

        # Quick summary
        col1, col2, col3, col4 = st.columns(4)

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
                "Questions Answered",
                f"{summary['answered_questions']}/{summary['total_questions']}"
            )

        with col4:
            st.metric(
                "High Priority Gaps",
                len(summary['high_priority_gaps'])
            )

        # Action buttons
        col1, col2 = st.columns(2)

        with col1:
            if st.button("View Dashboard"):
                st.session_state.page = 'dashboard'
                st.rerun()

        with col2:
            if st.button("New Assessment"):
                st.session_state.assessment_answers = {}
                st.rerun()


def render_assessment_history():
    """Render assessment history table"""

    st.header("Assessment History")

    db = TMMiDatabase()
    assessments = db.get_assessments()

    if not assessments:
        st.info("No assessments found. Complete your first assessment to see history here.")
        return

    # Create summary table
    history_data = []
    for assessment in assessments:
        yes_count = sum(1 for ans in assessment.answers if ans.answer == 'Yes')
        partial_count = sum(1 for ans in assessment.answers if ans.answer == 'Partial')
        no_count = sum(1 for ans in assessment.answers if ans.answer == 'No')
        total_answered = len(assessment.answers)

        compliance = (yes_count / total_answered * 100) if total_answered > 0 else 0

        history_data.append({
            'ID': assessment.id,
            'Date': assessment.timestamp.split('T')[0],  # Just date part
            'Reviewer': assessment.reviewer_name,
            'Organization': assessment.organization,
            'Questions Answered': total_answered,
            'Yes': yes_count,
            'Partial': partial_count,
            'No': no_count,
            'Compliance %': f"{compliance:.1f}%"
        })

    st.dataframe(
        history_data,
        use_container_width=True,
        hide_index=True
    )

    # Assessment details
    if history_data:
        st.markdown("### Assessment Details")

        selected_id = st.selectbox(
            "Select assessment to view details:",
            options=[item['ID'] for item in history_data],
            format_func=lambda x: f"Assessment {x} - {next(item['Date'] for item in history_data if item['ID'] == x)}"
        )

        if selected_id:
            selected_assessment = next(a for a in assessments if a.id == selected_id)
            render_assessment_details(selected_assessment)


def render_assessment_details(assessment: Assessment):
    """Render detailed view of a specific assessment"""

    with st.expander(f"Assessment {assessment.id} Details", expanded=True):

        # Metadata
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**Date:** {assessment.timestamp.split('T')[0]}")
        with col2:
            st.write(f"**Reviewer:** {assessment.reviewer_name}")
        with col3:
            st.write(f"**Organization:** {assessment.organization}")

        # Answers breakdown
        st.markdown("**Answers:**")

        answer_data = []
        for answer in assessment.answers:
            answer_data.append({
                'Question ID': answer.question_id,
                'Answer': answer.answer,
                'Evidence': 'Yes' if answer.evidence_url else 'No',
                'Comments': 'Yes' if answer.comment else 'No'
            })

        st.dataframe(answer_data, use_container_width=True, hide_index=True)
