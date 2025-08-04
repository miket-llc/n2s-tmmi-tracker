# Organization Progress Feature Implementation

You're working on the TMMi Assessment Tracker Streamlit app. Your task is to implement a progress visualization feature that shows how each organization's TMMi maturity has changed over time across multiple assessments.

🧭 Feature Name:
"Organization Progress" – add this as a new page in the sidebar.

✅ Functional Requirements:
1. Organization Selector
At the top of the page, provide a st.selectbox listing all tracked organizations.

On org selection, load all historical assessments for that organization (from earliest to most recent).

2. Assessment History Loader
In models/database.py, implement or ensure availability of:

```python
def get_assessments_by_org(self, org_id: int) -> List[dict]
```

Each record must include:
- Timestamp
- Maturity level
- Scores or ratings for all assessed criteria/domains (if available)

3. Visualizations
You must create meaningful, multi-dimensional visual feedback using Plotly or Streamlit native charts.

a. Maturity Level Over Time (Line Chart)
- X-axis: Timestamp of assessment
- Y-axis: TMMi Level (1–5)
- Show as a stepped line or markers for clarity

b. Radar or Bar Chart for Criteria Breakdown
For the most recent 2–3 assessments:
- Show a radar or grouped bar chart comparing ratings across key TMMi domains.
- If domains or processes have subcategories, include those in tooltips or hover text.

c. Optional Table View
Include a st.dataframe() showing all assessments in tabular form for easy comparison.

🧠 Interpretive Elements
Add context cues such as:
- A text summary of observed improvements (e.g., "This organization has advanced from Level 2 to Level 4 over the last 18 months.")
- Highlight significant jumps (≥1 level)
- Optionally: show which specific process areas improved most (if data supports that)

⚙ Backend Support
Update or create in models/database.py:

```python
def get_assessments_by_org(self, org_id: int) -> List[dict]
def get_tmmi_scores_by_assessment(self, assessment_id: int) -> dict
```

🖼 UI Design Notes
- Use clean layout (st.columns(), st.expander() where needed)
- No emojis, no gamification
- Ensure charts are professional, accessible, and resize well on smaller screens
- Label axes clearly, avoid technical jargon

Output:
- All code additions to a new module: components/progress.py
- Updates to app.py to include the new page
- Supporting DB queries in models/database.py
- Use mock data if needed, but build as if working with real longitudinal assessment data

Save this prompt in the prompts directory.