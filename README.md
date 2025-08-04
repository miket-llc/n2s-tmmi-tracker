# TMMi Assessment Tracker

A Streamlit application for evaluating and tracking progress toward TMMi (Test Maturity Model Integration) certification.

## Project Structure

```
n2s-tmmi-tracker/
├── prompts/                    # Original requirements and prompts
├── data/                       # Data files and databases
│   ├── tmmi_questions.json     # TMMi assessment questions
│   └── assessments.db          # SQLite database for results
├── src/                        # Source code
│   ├── models/                 # Data models and database schemas
│   ├── components/             # Streamlit UI components
│   └── utils/                  # Utility functions
├── tests/                      # Test files
├── app.py                      # Main Streamlit application
└── requirements.txt            # Python dependencies
```

## Features

- **Assessment Engine**: Complete assessments organized by TMMi Level and Process Area
- **Historical Tracking**: Store and analyze assessment results over time
- **Dashboard**: Visualize maturity progress and identify gaps
- **Recommendations**: Get specific guidance for improvement
- **Evidence Management**: Track supporting documentation and links

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   streamlit run app.py
   ```

## TMMi Levels

- **Level 2**: Managed - Basic test management processes
- **Level 3**: Defined - Standardized test processes across organization  
- **Level 4**: Measured - Quantitative test process management
- **Level 5**: Optimized - Continuous test process improvement