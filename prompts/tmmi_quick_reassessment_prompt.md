# TMMi Assessment Tracker - Quick Reassessment Feature

## Context
You're adding functionality to an existing Streamlit app called TMMi Assessment Tracker. The app already supports assessments and organization tracking. Your task is to improve the Assessment flow to support quick reassessment for existing organizations.

## 🎯 Goal:
Enable users to start a new assessment for an existing organization, with the form pre-filled using the data from that org's most recent assessment.

## 👇 Specific Implementation Requirements:

### 1. Organization Selector
In the "Assessment" tab (or a new "New Assessment" tab):
- Add a dropdown (`st.selectbox`) listing all existing organizations by name.
- Fetch this list using `TMMiDatabase.get_organizations()` (implement if missing).

### 2. Form Prepopulation
When an organization is selected:
- Pull the latest assessment for that organization using a method like:

```python
def get_latest_assessment(self, org_id: int) -> dict
```

- Populate the assessment form fields using this data.
- Display a message at the top like:
  "You're starting a new assessment for [Org Name]. The form is pre-filled with data from their most recent assessment."

### 3. Changed Field Indicator
While filling the form:
- Compare the user's current inputs to the pre-filled values.
- If a field is modified, visually highlight it — for example:

```python
if field_value != original_value:
    st.markdown(f"🔁 **{field_label}** _(modified from previous: {original_value})_")
```

- You can also add a small visual tag or background color to show changes.

### 4. Final Submission
When the user submits the form:
- Save the new assessment as a new record (don't overwrite the previous).
- Associate it with the selected organization.

## 🛠 Backend Support:
In `models/database.py`, ensure the following methods exist or implement them:

```python
def get_latest_assessment(self, org_id: int) -> dict
def get_organizations(self) -> List[dict]
def save_assessment(self, org_id: int, responses: dict)
```

## UI Guidelines:
- Be clear, professional, and consistent — no emojis or informal tone.
- Highlight only modified fields from previous assessment.
- Ensure error handling for orgs with no prior assessments — in that case show a message and a blank form.

## Output the required changes to:
- `app.py` (navigation, page logic)
- `components/assessment.py` (form logic, change tracking)
- `models/database.py` (data methods)

Keep it modular and maintainable. Use `st.session_state` as needed.

## Expected Features:
1. **Organization Selection**: Dropdown with existing organizations showing assessment count and latest assessment date
2. **Automatic Pre-population**: Form fields populated with latest assessment data when organization is selected
3. **Visual Change Indicators**: Clear indication of which fields have been modified from the original assessment
4. **Change Summary**: Comprehensive summary of all changes before submission
5. **Error Handling**: Graceful handling of organizations with no previous assessments
6. **Professional UI**: Consistent with existing app design standards