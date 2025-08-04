# TMMi Assessment Tracker - New Features Implementation

## Context
You're working on a Streamlit app called TMMi Assessment Tracker. The app is already modular and uses components like assessment.py, dashboard.py, and database.py. Your task is to implement two new features with full functionality:

## 🔧 Feature 1: Editable Evaluation History

### Requirements:
- Create a new component file: `components/edit_history.py`.
- Add a new tab/page in the app called "Edit History" (e.g., add it to the st.sidebar.radio() navigation).
- Load historical assessments from the database using the existing TMMiDatabase class.
- Display history using `st.data_editor()` so users can directly edit the entries.
- Add a "Save Changes" button to commit edits to the database.
- Update the database model (`models/database.py`) with a method:

```python
def update_assessment_entry(self, entry_id: int, updated_data: dict):
    # Update logic using SQLite or existing persistence
```

- Ensure proper validation and error handling.

## 🏢 Feature 2: Manage Organizations

### Requirements:
- Add a new tab/page in the sidebar: "Manage Organizations".
- Display a list of current organizations using `st.data_editor()`:
  - Columns: id, name, contact_person, email, status
- Allow users to edit, add, and delete rows inline.
- Provide "Save Changes" and "Delete Selected" buttons.
- In `models/database.py`, implement:

```python
def get_organizations(self) -> List[dict]
def update_organization(self, org_id: int, updated_fields: dict)
def add_organization(self, new_org_data: dict)
def delete_organization(self, org_id: int)
```

- Ensure that updates persist (e.g., via SQLite).
- Validate required fields (e.g., name and email must not be empty).

## Additional Notes:
- Maintain the app's existing professional style — no emojis or informal elements.
- Use Streamlit 1.32+ features (`st.data_editor`, layout blocks, session state).
- Keep logging (already in app.py) for all database write operations.
- Keep all UI interactions responsive and error-tolerant.
- Output the full code changes required, including updates to app.py, the new component files, and any necessary updates in models/database.py.

## Expected Deliverables:
1. New component file: `src/components/edit_history.py`
2. New component file: `src/components/organizations.py`
3. Updated database model: `src/models/database.py` (with new methods)
4. Updated main app: `app.py` (with navigation integration)
5. Database schema updates for organizations table
6. Comprehensive error handling and validation
7. Professional UI consistent with existing design standards