# TMMi Assessment Form Improvements


## 1. 🚫 Stop Asking for Manual Org Name Entry
Replace:
Any st.text_input() or freeform field for organization name

With:
A dropdown selector:

```python
org_names = [org["name"] for org in db.get_organizations()]
selected_org_name = st.selectbox("Select Organization", org_names)

```

Store the selected org in st.session_state.selected_organization.

Use this as the org_id when saving assessment data.


## 2. 🧭 Fix Priority Label Formatting
Problem:
Labels currently appear as "High Priority Priority" or "Low Priority Priority"

Also, they are misaligned visually with the question text

Fix:
Update rendering logic to:

Display priority once (e.g., "Priority: High")

Left-align the priority badge or label so it sits with the question header or label

If using st.markdown() or HTML for styling, wrap everything in a flex container or a single horizontal layout block

Avoid floating the priority in a separate line or awkward margin


## 3. 🧼 General Cleanup
Ensure the organization selector is required.

Clearly indicate when a form is being prefilled based on previous assessment data (if applicable).

Keep styling consistent, clean, and professional (no emojis or UI gimmicks).


## Output
Update render_assessment_form() in components/assessment.py

If necessary, adjust any helper methods or database calls in models/database.py

Do not introduce regressions in how answers are collected or assessments saved

Save this prompt in the prompts directory for later reference.
