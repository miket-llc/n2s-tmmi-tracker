"""
Streamlit component for managing organizations
"""
import streamlit as st
import pandas as pd
import logging
from typing import List, Dict
from src.models.database import TMMiDatabase


def render_manage_organizations():
    """Render the organizations management interface"""
    
    st.header("Manage Organizations")
    st.markdown("Add, edit, and manage organizations that undergo TMMi assessments.")
    
    db = TMMiDatabase()
    
    try:
        # Load current organizations
        organizations = db.get_organizations()
        
        # Create tabs for different organization operations
        tab1, tab2 = st.tabs(["Current Organizations", "Add New Organization"])
        
        with tab1:
            render_organization_editor(db, organizations)
        
        with tab2:
            render_add_organization(db)
            
    except Exception as e:
        logging.error(f"Error in manage_organizations: {str(e)}")
        st.error(f"Failed to load organizations: {str(e)}")


def render_organization_editor(db: TMMiDatabase, organizations: List[Dict]):
    """Render the organization editing interface"""
    
    if not organizations:
        st.info("No organizations found. Add your first organization using the 'Add New Organization' tab.")
        return
    
    # Prepare data for data editor
    df_data = []
    for org in organizations:
        df_data.append({
            'ID': org['id'],
            'Name': org['name'],
            'Contact Person': org['contact_person'] or '',
            'Email': org['email'] or '',
            'Status': org['status']
        })
    
    df = pd.DataFrame(df_data)
    
    st.markdown(f"### Current Organizations ({len(organizations)})")
    st.caption(
        "Edit organization details directly in the table below. Changes are saved when you "
        "click 'Save Changes'."
    )
    
    # Data editor with proper configuration
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        hide_index=True,
        disabled=['ID'],
        column_config={
            'ID': st.column_config.NumberColumn(
                'ID',
                help='Unique organization identifier',
                width='small'
            ),
            'Name': st.column_config.TextColumn(
                'Organization Name',
                help='Full name of the organization',
                width='medium',
                max_chars=100,
                validate=r'^.{1,100}$'
            ),
            'Contact Person': st.column_config.TextColumn(
                'Contact Person',
                help='Primary contact person for assessments',
                width='medium',
                max_chars=100
            ),
            'Email': st.column_config.TextColumn(
                'Email Address',
                help='Contact email address',
                width='medium',
                max_chars=100,
                validate=r'^[a-zA-Z0-9._%+-]*@[a-zA-Z0-9.-]*\.[a-zA-Z]{2,}$|^$'
            ),
            'Status': st.column_config.SelectboxColumn(
                'Status',
                help='Organization status',
                width='small',
                options=['Active', 'Inactive']
            )
        }
    )
    
    # Track changes
    changes_detected = False
    if not df.equals(edited_df):
        changes_detected = True
        
        # Validate required fields
        validation_errors = validate_organization_data(edited_df)
        if validation_errors:
            st.error("Please fix the following validation errors:")
            for error in validation_errors:
                st.error(f"• {error}")
            changes_detected = False
        else:
            st.info("Changes detected. Click 'Save Changes' to apply them.")
    
    # Action buttons
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.button("Save Changes", type="primary", disabled=not changes_detected):
            save_organization_changes(db, df, edited_df)
    
    with col2:
        if st.button("Refresh Data"):
            st.rerun()
    
    with col3:
        show_delete_mode = st.checkbox("Delete Mode")
    
    # Delete functionality
    if show_delete_mode:
        render_delete_organizations(db, organizations)
    
    # Show change summary
    if changes_detected and not validate_organization_data(edited_df):
        render_organization_change_summary(df, edited_df)


def validate_organization_data(df: pd.DataFrame) -> List[str]:
    """Validate organization data and return list of errors"""
    errors = []
    
    for idx, row in df.iterrows():
        row_num = idx + 1
        
        # Name is required
        if not row['Name'] or not row['Name'].strip():
            errors.append(f"Row {row_num}: Organization name is required")
        
        # Email validation (if provided)
        if row['Email'] and row['Email'].strip():
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, row['Email'].strip()):
                errors.append(f"Row {row_num}: Invalid email format")
        
        # Check for duplicate names (excluding current row)
        other_rows = df.drop(idx)
        if row['Name'] and row['Name'].strip() in other_rows['Name'].values:
            errors.append(f"Row {row_num}: Organization name must be unique")
    
    return errors


def save_organization_changes(db: TMMiDatabase, original_df: pd.DataFrame, edited_df: pd.DataFrame):
    """Save changes made to organization data"""
    
    try:
        changes_made = 0
        
        # Compare rows to find changes
        for idx in range(len(original_df)):
            original_row = original_df.iloc[idx]
            edited_row = edited_df.iloc[idx]
            
            # Check for changes in each field
            changes = {}
            fields_to_check = ['Name', 'Contact Person', 'Email', 'Status']
            
            for field in fields_to_check:
                original_val = original_row[field] if pd.notna(original_row[field]) else ''
                edited_val = edited_row[field] if pd.notna(edited_row[field]) else ''
                
                if original_val != edited_val:
                    # Map display names to database field names
                    field_mapping = {
                        'Name': 'name',
                        'Contact Person': 'contact_person',
                        'Email': 'email',
                        'Status': 'status'
                    }
                    changes[field_mapping[field]] = edited_val.strip() if edited_val else None
            
            # Apply changes if any
            if changes:
                org_id = int(original_row['ID'])
                db.update_organization(org_id, changes)
                changes_made += 1
                
                # Log the change
                logging.info(f"Updated organization {org_id}: {changes}")
        
        if changes_made > 0:
            st.success(f"Successfully saved changes to {changes_made} organization(s).")
            st.rerun()
        else:
            st.info("No changes detected to save.")
            
    except Exception as e:
        logging.error(f"Error saving organization changes: {str(e)}")
        st.error(f"Failed to save changes: {str(e)}")


def render_organization_change_summary(original_df: pd.DataFrame, edited_df: pd.DataFrame):
    """Show summary of detected changes"""
    
    st.markdown("### Change Summary")
    
    with st.expander("View Detailed Changes", expanded=False):
        changes_found = False
        
        for idx in range(len(original_df)):
            original_row = original_df.iloc[idx]
            edited_row = edited_df.iloc[idx]
            
            row_changes = []
            fields_to_check = ['Name', 'Contact Person', 'Email', 'Status']
            
            for field in fields_to_check:
                original_val = original_row[field] if pd.notna(original_row[field]) else ''
                edited_val = edited_row[field] if pd.notna(edited_row[field]) else ''
                
                if original_val != edited_val:
                    row_changes.append(f"{field}: '{original_val}' → '{edited_val}'")
            
            if row_changes:
                changes_found = True
                st.markdown(f"**Organization {original_row['ID']} ({original_row['Name']}):**")
                for change in row_changes:
                    st.markdown(f"  • {change}")
        
        if not changes_found:
            st.info("No changes detected.")


def render_add_organization(db: TMMiDatabase):
    """Render interface for adding new organizations"""
    
    st.markdown("### Add New Organization")
    
    with st.form("add_organization_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            org_name = st.text_input(
                "Organization Name *",
                help="Full name of the organization"
            )
            contact_person = st.text_input(
                "Contact Person",
                help="Primary contact for assessments"
            )
        
        with col2:
            email = st.text_input(
                "Email Address",
                help="Contact email address"
            )
            status = st.selectbox(
                "Status",
                options=['Active', 'Inactive'],
                index=0,
                help="Current status of the organization"
            )
        
        submitted = st.form_submit_button("Add Organization", type="primary")
        
        if submitted:
            # Validate input
            errors = []
            
            if not org_name or not org_name.strip():
                errors.append("Organization name is required")
            
            if email and email.strip():
                import re
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, email.strip()):
                    errors.append("Invalid email format")
            
            # Check for duplicate names
            existing_orgs = db.get_organizations()
            if any(org['name'].lower() == org_name.strip().lower() for org in existing_orgs):
                errors.append("An organization with this name already exists")
            
            if errors:
                for error in errors:
                    st.error(f"• {error}")
            else:
                # Add the organization
                try:
                    new_org_data = {
                        'name': org_name.strip(),
                        'contact_person': contact_person.strip() if contact_person else None,
                        'email': email.strip() if email else None,
                        'status': status
                    }
                    
                    org_id = db.add_organization(new_org_data)
                    logging.info(f"Added new organization: {new_org_data}")
                    
                    st.success(f"Successfully added organization '{org_name}' (ID: {org_id})")
                    st.rerun()
                    
                except Exception as e:
                    logging.error(f"Error adding organization: {str(e)}")
                    st.error(f"Failed to add organization: {str(e)}")


def render_delete_organizations(db: TMMiDatabase, organizations: List[Dict]):
    """Render organization deletion interface"""
    
    st.markdown("### Delete Organizations")
    st.warning("⚠️ Deleting organizations will permanently remove their data and cannot be undone.")
    
    # Selection interface
    org_options = [
        f"{org['name']} (ID: {org['id']}) - {org['status']}"
        for org in organizations
    ]
    
    selected_orgs = st.multiselect(
        "Select organizations to delete:",
        options=org_options,
        help="Hold Ctrl/Cmd to select multiple organizations"
    )
    
    if selected_orgs:
        # Extract IDs from selections
        selected_ids = []
        for selection in selected_orgs:
            org_id = int(selection.split('(ID: ')[1].split(')')[0])
            selected_ids.append(org_id)
        
        st.markdown(f"**Selected {len(selected_ids)} organization(s) for deletion:**")
        for org_id in selected_ids:
            org = next(o for o in organizations if o['id'] == org_id)
            st.markdown(f"• {org['name']} (ID: {org_id})")
        
        # Confirmation and delete
        col1, col2 = st.columns([1, 3])
        
        with col1:
            confirm_delete = st.checkbox("I understand this action cannot be undone")
        
        with col2:
            if st.button("Delete Selected", type="secondary", disabled=not confirm_delete):
                delete_selected_organizations(db, selected_ids)


def delete_selected_organizations(db: TMMiDatabase, org_ids: List[int]):
    """Delete selected organizations"""
    
    try:
        deleted_count = 0
        
        for org_id in org_ids:
            db.delete_organization(org_id)
            deleted_count += 1
            logging.info(f"Deleted organization {org_id}")
        
        st.success(f"Successfully deleted {deleted_count} organization(s).")
        st.rerun()
        
    except Exception as e:
        logging.error(f"Error deleting organizations: {str(e)}")
        st.error(f"Failed to delete organizations: {str(e)}")
