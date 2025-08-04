# TMMi Tracker Application - Original Prompt

You are helping me build a Streamlit application to evaluate and track progress toward TMMi (Test Maturity Model Integration) certification. This tool will be used by QA and consulting teams to conduct structured assessments, monitor progress over time, and identify specific gaps and recommended actions to advance maturity.

⸻

✅ App Purpose

Build a Streamlit app that does the following:
	1.	Assess maturity across the five TMMi levels
	2.	Store historical results over time (SQLite or CSV is fine for now)
	3.	Display dashboards showing current level, trend over time, and process-area-level insights
	4.	Provide recommendations based on gaps in compliance
	5.	Track evidence with links or files for each question

⸻

📂 Key Features

1. Assessment Engine
	•	Users complete assessments organized by TMMi Level and Process Area
	•	Each question includes:
	•	Text of the question
	•	TMMi level (2–5 only; Level 1 is non-formal)
	•	Process Area (e.g., Test Policy and Strategy, Test Planning, Test Monitoring and Control, etc.)
	•	Answer type: Yes / No / Partial
	•	Evidence URL field (optional)
	•	Comment field

2. Storage
	•	Store each completed assessment with:
	•	Timestamp
	•	User/reviewer name
	•	All answers, comments, and evidence
	•	Auto-computed metrics (see below)

3. Computation
	•	Determine the current TMMi Level based on a predefined scoring threshold (e.g., 80% or more "Yes" per level and all lower levels complete)
	•	Calculate per–process area coverage (e.g., % complete for "Test Planning")

4. Recommendations
	•	For each "No" or "Partial," suggest:
	•	Why the item is important
	•	What activities will help
	•	Link to external resource (can be stubbed)

5. Visualization
	•	Line graph: maturity over time
	•	Table of open gaps and suggested activities
	•	% of answered questions with evidence
	•	Filters by date, level, or process area

⸻

🔢 Seed Data – Sample TMMi Questions

Seed the system with at least 3–5 sample questions per level, with metadata. Example format below:
[
  {
    "level": 2,
    "process_area": "Test Policy and Strategy",
    "question": "Is a documented test policy established and maintained?",
    "importance": "High",
    "recommended_activity": "Define and publish a company-wide test policy. Include scope, objectives, and organizational responsibility.",
    "reference_url": "https://www.tmmi.org/pdf/TMMi_Framework.pdf"
  },
  {
    "level": 2,
    "process_area": "Test Planning",
    "question": "Are test plans created for all software development projects?",
    "importance": "High",
    "recommended_activity": "Introduce a test planning template that includes objectives, scope, resources, and schedule.",
    "reference_url": "https://www.tmmi.org/pdf/TMMi_Framework.pdf"
  },
  {
    "level": 3,
    "process_area": "Peer Reviews",
    "question": "Are peer reviews systematically performed on test designs?",
    "importance": "Medium",
    "recommended_activity": "Implement mandatory peer review checklists and track completion.",
    "reference_url": "https://www.tmmi.org/pdf/TMMi_Framework.pdf"
  },
  {
    "level": 4,
    "process_area": "Test Measurement",
    "question": "Are test process metrics collected and analyzed over time?",
    "importance": "High",
    "recommended_activity": "Establish a KPI dashboard for test execution, defect rates, and rework costs.",
    "reference_url": "https://www.tmmi.org/pdf/TMMi_Framework.pdf"
  }
]

If you don't have full TMMi coverage, generate a sample JSON/YAML/CSV file with ~20 questions spanning all levels and process areas to help me get started.

⸻

📦 Your Tasks

Start by doing the following:
	1.	Propose a folder/file structure for the Streamlit app
	2.	Generate a Streamlit app scaffold that:
	•	Loads the questions
	•	Presents them in a clean UI grouped by TMMi Level and Process Area
	•	Captures user answers, evidence, and comments
	•	Stores results with timestamp
	3.	Implement scoring logic and recommendations
	4.	Create a simple dashboard (use Streamlit's built-in charts)

⸻

Once we have this scaffold running, we'll iterate to improve UX, evidence linking, and export features. Let's begin with the data model and assessment UI.

I also need you to create a directory for prompts and to store this prompt verbatim in that directory.