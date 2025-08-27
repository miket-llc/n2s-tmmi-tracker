# TMMi Progression Analysis Feature

## Overview

The TMMi Progression Analysis feature provides comprehensive analysis of an organization's readiness to progress to the next TMMi maturity level. This deterministic, framework-compliant analysis replaces the previous simple percentage-based approach with a structured assessment aligned with official TMMi standards.

## Key Features

### 1. Next Level Readiness Analysis
- **Current Level Assessment**: Determines achieved TMMi level based on compliance thresholds
- **Target Level Identification**: Automatically identifies the next level to achieve
- **Readiness Percentage**: Calculates conservative readiness percentage for next level
- **Gating Status**: Determines eligibility for formal TMMi certification

### 2. TMMi Framework Compliance
- **Specific Practice (SP) Mapping**: Questions mapped to official TMMi practices
- **Specific Goal (SG) Tracking**: Goals derived from practice attainment
- **Generic Goal (GG) Compliance**: Level-appropriate generic goal assessment
- **Process Area Analysis**: Enhanced process area breakdown with bands

### 3. Achievement Bands
Uses official TMMi achievement bands:
- **F (Fully)**: 85-100% - Practice fully implemented
- **L (Largely)**: 50-85% - Practice largely implemented
- **P (Partially)**: 15-50% - Practice partially implemented  
- **N (Not Achieved)**: 0-15% - Practice not implemented

### 4. Enhanced Gap Analysis
- **SP/SG Mapping**: Gaps linked to specific practices and goals
- **Action Recommendations**: Deterministic actions to close gaps
- **Priority Classification**: High/Medium/Low priority based on importance
- **Evidence Coverage**: Tracks evidence availability for assertions

### 5. Evidence Quality Analysis
- **Coverage Metrics**: Percentage of answers with supporting evidence
- **Risk Indicators**: Identifies high-risk assertions (high achievement, low evidence)
- **Process Area Breakdown**: Evidence coverage by process area
- **Quality Recommendations**: Guidance on evidence improvement

## Architecture

### Data Model Enhancements

#### TMMiQuestion Model
```python
@dataclass
class TMMiQuestion:
    id: str
    level: int
    process_area: str
    question: str
    importance: str
    recommended_activity: str
    reference_url: str
    # New fields for framework compliance
    specific_goal: Optional[str] = None
    specific_practice: Optional[str] = None
    generic_goal: Optional[str] = None
    practice_id: Optional[str] = None
```

#### Database Schema
```sql
CREATE TABLE tmmi_framework_mapping (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id TEXT NOT NULL UNIQUE,
    specific_goal TEXT,
    specific_practice TEXT,
    generic_goal TEXT,
    practice_id TEXT,
    process_area_level INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### Scoring Algorithm

#### 1. Specific Practice (SP) Attainment
- Maps questions to specific practices
- Calculates average attainment per practice
- Determines achievement band (N/P/L/F)
- Tracks evidence coverage

#### 2. Specific Goal (SG) Attainment
- Groups practices by specific goals
- Calculates SG attainment as mean of SPs
- Applies achievement bands
- Enables goal-level analysis

#### 3. Process Area (PA) Attainment
- Groups goals by process areas
- Calculates PA attainment as mean of SGs
- Includes level information
- Supports level progression analysis

#### 4. Next Level Readiness
- Identifies target level (current + 1)
- Calculates readiness for target level PAs
- Applies gating logic (all PAs ≥50%)
- Provides conservative readiness estimate

#### 5. Generic Goal Compliance
- Maps questions to generic goals by level
- Calculates GG attainment percentages
- Determines Met/Not Met status (85% threshold)
- Tracks evidence coverage

## Usage

### Accessing the Progression Dashboard

1. **Navigation**: Select "Progression Dashboard" from the main navigation
2. **Organization Selection**: Choose organization to analyze
3. **Assessment Data**: Uses latest assessment for the organization
4. **Comprehensive View**: All progression metrics displayed

### Dashboard Sections

#### Top-Level Metrics
- Current TMMi Level
- Target Level
- Readiness to Next Level
- Total Gaps
- Certification Status

#### Next Level Readiness
- Process area readiness chart
- Achievement bands visualization
- Target level requirements
- Gating status explanation

#### Process Area Progression
- Scatter plot: Attainment vs Evidence
- Risk zone identification
- High-risk assertion warnings
- Level-based organization

#### Gap Analysis
- Filterable gap list
- SP/SG mapping display
- Action recommendations
- Priority classification

#### Generic Goals Panel
- Level-appropriate GG checklist
- Compliance status
- Evidence coverage
- Progress indicators

#### Evidence Coverage
- Overall evidence percentage
- Process area breakdown
- Quality indicators
- Risk assessment

### Download & Export

#### Available Exports
1. **Gap Analysis CSV**: Detailed gap information with actions
2. **Process Area Summary CSV**: PA attainment and evidence data
3. **Summary Report TXT**: Executive summary of progression status

#### Export Fields
- Process Area, Specific Goal, Specific Practice
- Current Answer, Importance, Level
- Attainment Percentage, Achievement Band
- Action to Close, Evidence URL

## Migration & Setup

### 1. Database Migration
```bash
# Run the migration script
python -m src.utils.migration
```

This will:
- Create backup of existing questions
- Add SP/SG/GP mapping fields
- Update question structure
- Preserve existing data

### 2. Question Mapping
The migration script maps existing questions to:
- **Specific Practices**: Based on question IDs and process areas
- **Specific Goals**: Derived from practice mappings
- **Generic Goals**: Level-appropriate generic goal assignments
- **Practice IDs**: Official TMMi practice identifiers

### 3. Validation
After migration:
- Verify question mappings in `data/tmmi_questions.json`
- Check database schema updates
- Run unit tests to validate functionality
- Review sample progression analysis

## Configuration

### Achievement Band Thresholds
```python
# Default TMMi band thresholds
FULLY_ACHIEVED = 85.0      # F band
LARGELY_ACHIEVED = 50.0    # L band
PARTIALLY_ACHIEVED = 15.0  # P band
NOT_ACHIEVED = 0.0         # N band
```

### Gating Logic
```python
# Certification eligibility requirements
MIN_PA_ATTAINMENT = 50.0   # Minimum PA attainment for next level
GG_COMPLIANCE_THRESHOLD = 85.0  # Generic goal compliance threshold
```

### Evidence Risk Thresholds
```python
# Evidence coverage risk indicators
HIGH_RISK_EVIDENCE = 50.0  # Below 50% evidence coverage
MODERATE_RISK_EVIDENCE = 60.0  # Below 60% evidence coverage
```

## Testing

### Unit Tests
```bash
# Run progression tests
pytest tests/test_progression.py -v

# Run all tests
pytest tests/ -v
```

### Test Coverage
- TMMi band calculations
- SP/SG/PA attainment
- Next level readiness
- Gap analysis extraction
- Generic goal compliance
- Dashboard data generation

### Test Fixtures
- Level 2 organization targeting Level 3
- Mixed attainment scenarios
- Evidence coverage variations
- Gap identification validation

## Troubleshooting

### Common Issues

#### 1. Missing SP/SG Mapping
**Symptoms**: Questions show "None" for specific practices/goals
**Solution**: Run migration script, verify question data structure

#### 2. Incorrect Achievement Bands
**Symptoms**: Bands don't match expected percentages
**Solution**: Check band threshold constants, validate percentage calculations

#### 3. Gating Status Errors
**Symptoms**: Incorrect eligibility determination
**Solution**: Verify PA attainment calculations, check gating logic

#### 4. Evidence Coverage Issues
**Symptoms**: Incorrect evidence percentages
**Solution**: Validate evidence URL fields, check coverage calculations

### Debug Information
- Check application logs for calculation details
- Use debug mode for detailed metric breakdown
- Validate question mapping in migration output
- Review test results for expected vs actual values

## Performance Considerations

### Optimization Strategies
1. **Database Indexing**: Indexes on question_id and process_area_level
2. **Caching**: Progression data cached during session
3. **Lazy Loading**: Calculations performed on-demand
4. **Batch Processing**: Multiple calculations grouped for efficiency

### Scalability
- Supports organizations with multiple assessments
- Handles large question banks efficiently
- Optimized for real-time dashboard updates
- Minimal memory footprint for calculations

## Future Enhancements

### Planned Features
1. **Historical Progression**: Track readiness changes over time
2. **Benchmarking**: Compare against industry standards
3. **Roadmap Planning**: Automated improvement recommendations
4. **Audit Trail**: Track assessment changes and impact

### Integration Opportunities
1. **External TMMi Tools**: API integration with official tools
2. **Reporting Systems**: Export to enterprise reporting platforms
3. **Workflow Integration**: Connect with improvement tracking systems
4. **Compliance Monitoring**: Automated compliance reporting

## Support & Documentation

### Additional Resources
- [TMMi Foundation Official Website](https://www.tmmi.org/)
- [TMMi Framework Documentation](https://www.tmmi.org/pdf/TMMi_Framework.pdf)
- [Assessment Guidelines](https://www.tmmi.org/assessment/)

### Technical Support
- Review unit tests for implementation examples
- Check migration script for data structure
- Validate against official TMMi documentation
- Use debug mode for detailed analysis

---

**Note**: This feature implements deterministic TMMi progression analysis based on official framework requirements. All calculations are rule-based and do not use AI/LLM scoring. The system provides actionable insights for organizations seeking to improve their test maturity and progress through TMMi levels.
