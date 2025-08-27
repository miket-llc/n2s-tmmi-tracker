import os
import sys

# Ensure the project root is on the import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.scoring import (
    calculate_level_compliance,
    calculate_process_area_compliance,
    calculate_evidence_coverage,
)
from src.models.database import TMMiQuestion, AssessmentAnswer, Assessment
import pytest


def build_sample_data():
    questions = [
        TMMiQuestion(
            id="Q1",
            level=2,
            process_area="PA1",
            question="Question 1",
            importance="High",
            recommended_activity="",
            reference_url="",
        ),
        TMMiQuestion(
            id="Q2",
            level=2,
            process_area="PA2",
            question="Question 2",
            importance="Medium",
            recommended_activity="",
            reference_url="",
        ),
        TMMiQuestion(
            id="Q3",
            level=3,
            process_area="PA1",
            question="Question 3",
            importance="Low",
            recommended_activity="",
            reference_url="",
        ),
        TMMiQuestion(
            id="Q4",
            level=3,
            process_area="PA2",
            question="Question 4",
            importance="Low",
            recommended_activity="",
            reference_url="",
        ),
    ]

    answers = [
        AssessmentAnswer(question_id="Q1", answer="Yes", evidence_url="http://evidence1"),
        AssessmentAnswer(question_id="Q2", answer="Partial"),
        AssessmentAnswer(question_id="Q3", answer="No", evidence_url="http://evidence3"),
    ]

    return questions, answers


def test_calculate_level_compliance():
    questions, answers = build_sample_data()
    result = calculate_level_compliance(questions, answers)

    level2 = result[2]
    assert level2["compliance_percentage"] == pytest.approx(75.0)
    assert level2["yes_count"] == 1
    assert level2["partial_count"] == 1
    assert level2["no_count"] == 0
    assert level2["answered_questions"] == 2

    level3 = result[3]
    assert level3["compliance_percentage"] == pytest.approx(0.0)
    assert level3["yes_count"] == 0
    assert level3["partial_count"] == 0
    assert level3["no_count"] == 1
    assert level3["answered_questions"] == 1


def test_calculate_process_area_compliance():
    questions, answers = build_sample_data()
    result = calculate_process_area_compliance(questions, answers)

    pa1 = result["PA1"]
    assert pa1["compliance_percentage"] == pytest.approx(50.0)
    assert pa1["yes_count"] == 1
    assert pa1["no_count"] == 1
    assert pa1["answered_questions"] == 2

    pa2 = result["PA2"]
    assert pa2["compliance_percentage"] == pytest.approx(25.0)
    assert pa2["partial_count"] == 1
    assert pa2["answered_questions"] == 1


def test_calculate_evidence_coverage():
    _, answers = build_sample_data()
    result = calculate_evidence_coverage(answers)

    assert result["with_evidence"] == 2
    assert result["total_answers"] == 3
    assert result["percentage"] == pytest.approx(66.6666666667)


def test_calculate_answer_score():
    """Test answer score calculation"""
    from src.utils.scoring import calculate_answer_score
    
    assert calculate_answer_score("Yes") == 1.0
    assert calculate_answer_score("Partial") == 0.5
    assert calculate_answer_score("No") == 0.0
    assert calculate_answer_score("Invalid") == 0.0

def test_get_gap_analysis():
    """Test gap analysis generation"""
    from src.utils.scoring import get_gap_analysis
    
    questions = [
        TMMiQuestion(
            id="TEST_001", level=2, process_area="Test Planning",
            question="Test question 1", importance="High",
            recommended_activity="Test activity 1", reference_url="http://example.com"
        ),
        TMMiQuestion(
            id="TEST_002", level=2, process_area="Test Planning",
            question="Test question 2", importance="Medium",
            recommended_activity="Test activity 2", reference_url="http://example.com"
        )
    ]
    
    answers = [
        AssessmentAnswer(question_id="TEST_001", answer="No", evidence_url="http://evidence.com"),
        AssessmentAnswer(question_id="TEST_002", answer="Partial", evidence_url=None)
    ]
    
    gaps = get_gap_analysis(questions, answers)
    
    assert len(gaps) == 2
    assert gaps[0]["question_id"] == "TEST_001"  # High importance first
    assert gaps[0]["current_answer"] == "No"
    assert gaps[1]["question_id"] == "TEST_002"
    assert gaps[1]["current_answer"] == "Partial"

def test_get_gap_analysis_unanswered():
    """Test gap analysis with unanswered questions"""
    from src.utils.scoring import get_gap_analysis
    
    questions = [
        TMMiQuestion(
            id="TEST_001", level=2, process_area="Test Planning",
            question="Test question 1", importance="High",
            recommended_activity="Test activity 1", reference_url="http://example.com"
        )
    ]
    
    answers = []  # No answers
    
    gaps = get_gap_analysis(questions, answers)
    
    assert len(gaps) == 1
    assert gaps[0]["current_answer"] == "Not Answered"

def test_calculate_evidence_coverage_edge_cases():
    """Test evidence coverage calculation edge cases"""
    from src.utils.scoring import calculate_evidence_coverage
    
    # Test with no answers
    coverage = calculate_evidence_coverage([])
    assert coverage["percentage"] == 0.0
    assert coverage["with_evidence"] == 0
    assert coverage["total_answers"] == 0
    
    # Test with empty evidence URLs
    answers_empty_evidence = [
        AssessmentAnswer(question_id="TEST_001", answer="Yes", evidence_url=""),
        AssessmentAnswer(question_id="TEST_002", answer="No", evidence_url="   "),
        AssessmentAnswer(question_id="TEST_003", answer="Partial", evidence_url=None)
    ]
    
    coverage = calculate_evidence_coverage(answers_empty_evidence)
    assert coverage["with_evidence"] == 0
    assert coverage["percentage"] == 0.0

def test_generate_assessment_summary():
    """Test assessment summary generation"""
    from src.utils.scoring import generate_assessment_summary
    
    questions = [
        TMMiQuestion(
            id="TEST_001", level=2, process_area="Test Planning",
            question="Test question 1", importance="High",
            recommended_activity="Test activity 1", reference_url="http://example.com"
        ),
        TMMiQuestion(
            id="TEST_002", level=2, process_area="Test Planning",
            question="Test question 2", importance="Medium",
            recommended_activity="Test activity 2", reference_url="http://example.com"
        )
    ]
    
    assessment = Assessment(
        id=1, timestamp="2024-01-01T00:00:00", reviewer_name="Test User",
        organization="Test Org", answers=[
            AssessmentAnswer(question_id="TEST_001", answer="Yes"),
            AssessmentAnswer(question_id="TEST_002", answer="Partial")
        ]
    )
    
    summary = generate_assessment_summary(questions, assessment)
    
    assert "level_compliance" in summary
    assert "process_area_compliance" in summary
    assert "current_level" in summary
    assert "level_explanation" in summary
    assert "gaps" in summary
    assert "evidence_coverage" in summary
    assert "total_questions" in summary
    assert "answered_questions" in summary
    assert "yes_answers" in summary
    assert "partial_answers" in summary
    assert "no_answers" in summary
    assert "overall_percentage" in summary

def test_determine_current_tmmi_level():
    """Test TMMi level determination logic"""
    from src.utils.scoring import determine_current_tmmi_level, calculate_level_compliance
    
    questions = [
        TMMiQuestion(
            id="TEST_001", level=2, process_area="Test Planning",
            question="Test question 1", importance="High",
            recommended_activity="Test activity 1", reference_url="http://example.com"
        ),
        TMMiQuestion(
            id="TEST_002", level=3, process_area="Test Organization",
            question="Test question 2", importance="High",
            recommended_activity="Test activity 2", reference_url="http://example.com"
        )
    ]
    
    # Test case where lower level doesn't meet threshold
    answers_lower_level_fails = [
        AssessmentAnswer(question_id="TEST_001", answer="No"),  # 0% for level 2
        AssessmentAnswer(question_id="TEST_002", answer="Yes")  # 100% for level 3
    ]
    
    level_compliance = calculate_level_compliance(questions, answers_lower_level_fails)
    current_level, explanation = determine_current_tmmi_level(level_compliance)
    
    # Should not reach level 3 because level 2 failed
    assert current_level == 1  # Initial level
    assert "Initial" in explanation
    
    # Test case where all levels meet threshold
    answers_all_levels_pass = [
        AssessmentAnswer(question_id="TEST_001", answer="Yes"),  # 100% for level 2
        AssessmentAnswer(question_id="TEST_002", answer="Yes")  # 100% for level 3
    ]
    
    level_compliance = calculate_level_compliance(questions, answers_all_levels_pass)
    current_level, explanation = determine_current_tmmi_level(level_compliance)
    
    # Should reach level 3 because all levels meet threshold
    assert current_level == 3
    assert "Level 3 (Defined)" in explanation
