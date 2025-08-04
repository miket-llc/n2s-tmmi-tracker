"""
Streamlit component for editing assessment history
"""
import streamlit as st
import pandas as pd
import logging
from typing import List, Dict
from src.models.database import TMMiDatabase


def render_edit_history():
    """Render the assessment history editing interface"""

    st.header("Edit Assessment History")
    st.markdown("Review and modify historical assessment records using "
                "the interactive data editor below.")

    db = TMMiDatabase()

    try:
        # Load assessment data for editing
        assessments = db.get_assessments_for_editing()

        if not assessments:
            st.info("No assessment history found. Complete your first assessment to see data here.")
            if st.button("Start New Assessment"):
                st.session_state.page = 'assessment'
                st.rerun()
            return

        # Convert to DataFrame for data editor
        df = pd.DataFrame(assessments)

        # Make ID column non-editable in data editor configuration

        st.markdown("### Assessment History")
        st.caption(f"Found {len(assessments)} assessment(s). You can edit "
                   f"the Reviewer and Organization fields.")

        # Display data editor
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            hide_index=True,
            disabled=['ID', 'Date', 'Total Questions', 'Yes', 'Partial', 'No', 'Compliance %'],
            column_config={
                'ID': st.column_config.NumberColumn(
                    'Assessment ID',
                    help='Unique identifier for this assessment',
                    width='small'
                ),
                'Date': st.column_config.DateColumn(
                    'Assessment Date',
                    help='Date when assessment was completed',
                    width='medium'
                ),
                'Reviewer': st.column_config.TextColumn(
                    'Reviewer Name',
                    help='Person who conducted the assessment',
                    width='medium',
                    validate=r'^.{1,100}$'
                ),
                'Organization': st.column_config.TextColumn(
                    'Organization',
                    help='Organization that was assessed',
                    width='medium',
                    validate=r'^.{1,100}$'
                ),
                'Total Questions': st.column_config.NumberColumn(
                    'Total Questions',
                    help='Number of questions answered',
                    width='small'
                ),
                'Compliance %': st.column_config.NumberColumn(
                    'Compliance %',
                    help='Overall compliance percentage',
                    width='small',
                    format='%.1f%%'
                )
            }
        )

        # Track changes
        changes_detected = False
        if not df.equals(edited_df):
            changes_detected = True
            st.info("Changes detected in the assessment data.")

        # Action buttons
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            if st.button("Save Changes", type="primary",
                         disabled=not changes_detected):
                save_assessment_changes(db, df, edited_df)

        with col2:
            if st.button("Refresh Data"):
                st.rerun()

        with col3:
            show_delete_mode = st.checkbox("Delete Mode")

        # Delete functionality
        if show_delete_mode:
            render_delete_assessments(db, assessments)

        # Show detailed change summary if there are changes
        if changes_detected:
            render_change_summary(df, edited_df)

    except Exception as e:
        logging.error(f"Error in edit_history: {str(e)}")
        st.error(f"Failed to load assessment history: {str(e)}")


def save_assessment_changes(db: TMMiDatabase, original_df: pd.DataFrame, edited_df: pd.DataFrame):
    """Save changes made to assessment data"""

    try:
        changes_made = 0

        # Compare rows to find changes
        for idx in range(len(original_df)):
            original_row = original_df.iloc[idx]
            edited_row = edited_df.iloc[idx]

            # Check if reviewer or organization changed
            changes = {}
            if original_row['Reviewer'] != edited_row['Reviewer']:
                changes['reviewer_name'] = edited_row['Reviewer']

            if original_row['Organization'] != edited_row['Organization']:
                changes['organization'] = edited_row['Organization']

            # Apply changes if any
            if changes:
                assessment_id = int(original_row['ID'])
                db.update_assessment_entry(assessment_id,
                                           changes)
                changes_made += 1

                # Log the change
                logging.info(f"Updated assessment {assessment_id}: {changes}")

        if changes_made > 0:
            st.success(f"Successfully saved changes to {changes_made} assessment(s).")
            st.rerun()
        else:
            st.info("No changes detected to save.")

    except Exception as e:
        logging.error(f"Error saving assessment changes: {str(e)}")
        st.error(f"Failed to save changes: {str(e)}")


def render_change_summary(original_df: pd.DataFrame, edited_df: pd.DataFrame):
    """Show summary of detected changes"""

    st.markdown("### Change Summary")

    with st.expander("View Detailed Changes", expanded=False):
        changes_found = False

        for idx in range(len(original_df)):
            original_row = original_df.iloc[idx]
            edited_row = edited_df.iloc[idx]

            row_changes = []
            if original_row['Reviewer'] != edited_row['Reviewer']:
                row_changes.append(f"Reviewer: '{original_row['Reviewer']}' → '{edited_row['Reviewer']}'")

            if original_row['Organization'] != edited_row['Organization']:
                row_changes.append(f"Organization: '{original_row['Organization']}' → '{edited_row['Organization']}'")

            if row_changes:
                changes_found = True
                st.markdown(f"**Assessment {original_row['ID']}:**")
                for change in row_changes:
                    st.markdown(f"  • {change}")

        if not changes_found:
            st.info("No changes detected.")


def render_delete_assessments(db: TMMiDatabase, assessments: List[Dict]):
    """Render assessment deletion interface"""

    st.markdown("### Delete Assessments")
    st.warning("⚠️ Deleting assessments will permanently remove all "
               "associated data including answers and cannot be undone.")

    # Selection interface
    assessment_options = [
        f"Assessment {a['ID']} - {a['Date']} "
        f"({a['Organization']})"
        for a in assessments
    ]

    selected_assessments = st.multiselect(
        "Select assessments to delete:",
        options=assessment_options,
        help="Hold Ctrl/Cmd to select multiple assessments"
    )

    if selected_assessments:
        # Extract IDs from selections
        selected_ids = []
        for selection in selected_assessments:
            assessment_id = int(selection.split(' - ')[0].replace('Assessment ', ''))
            selected_ids.append(assessment_id)

        st.markdown(f"**Selected {len(selected_ids)} assessment(s) for deletion:**")
        for assessment_id in selected_ids:
            assessment = next(a for a in assessments if a['ID'] == assessment_id)
            st.markdown(f"• Assessment {assessment_id}: {assessment['Date']} - {assessment['Organization']}")

        # Confirmation and delete
        col1, col2 = st.columns([1, 3])

        with col1:
            confirm_delete = st.checkbox("I understand this action cannot be undone")

        with col2:
            if st.button("Delete Selected", type="secondary", disabled=not confirm_delete):
                delete_selected_assessments(db, selected_ids)


def delete_selected_assessments(db: TMMiDatabase, assessment_ids: List[int]):
    """Delete selected assessments"""

    try:
        deleted_count = 0

        for assessment_id in assessment_ids:
            db.delete_assessment(assessment_id)
            deleted_count += 1
            logging.info(f"Deleted assessment {assessment_id}")

        st.success(f"Successfully deleted {deleted_count} assessment(s).")
        st.rerun()

    except Exception as e:
        logging.error(f"Error deleting assessments: {str(e)}")
        st.error(f"Failed to delete assessments: {str(e)}")
