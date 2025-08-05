import pytest
import sys
from pathlib import Path

# Ensure src package is importable
sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.models.database import TMMiDatabase, Assessment, AssessmentAnswer


def test_assessment_history_counts_partial(tmp_path):
    db_path = tmp_path / "test.db"
    db = TMMiDatabase(db_path=str(db_path))
    assessment = Assessment(
        reviewer_name="tester",
        organization="Org",
        answers=[
            AssessmentAnswer(question_id="q1", answer="Yes"),
            AssessmentAnswer(question_id="q2", answer="Partial"),
            AssessmentAnswer(question_id="q3", answer="No"),
        ],
    )
    db.save_assessment(assessment)
    history = db.get_assessment_history()
    assert len(history) == 1
    entry = history[0]
    assert entry["yes_count"] == 1
    assert entry["partial_count"] == 1
    assert entry["no_count"] == 1
    assert entry["total_questions"] == 3
    assert entry["compliance_percentage"] == pytest.approx(50.0)


def test_assessments_for_editing_compliance(tmp_path):
    db_path = tmp_path / "test.db"
    db = TMMiDatabase(db_path=str(db_path))
    assessment = Assessment(
        reviewer_name="tester",
        organization="Org",
        answers=[
            AssessmentAnswer(question_id="q1", answer="Yes"),
            AssessmentAnswer(question_id="q2", answer="Partial"),
        ],
    )
    db.save_assessment(assessment)
    rows = db.get_assessments_for_editing()
    assert len(rows) == 1
    assert rows[0]["Compliance %"] == pytest.approx(75.0)
