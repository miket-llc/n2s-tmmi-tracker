"""
Unit tests for TMMi progression analysis functionality
"""

import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.models.database import TMMiQuestion, AssessmentAnswer
from src.utils.scoring import (
    calculate_tmmi_band,
    calculate_specific_practice_attainment,
    calculate_specific_goal_attainment,
    calculate_process_area_attainment_enhanced,
    calculate_next_level_readiness,
    extract_gap_analysis_enhanced,
    calculate_generic_goal_compliance,
    generate_progression_dashboard_data,
    calculate_evidence_coverage
)


class TestTMMiBandCalculation:
    """Test TMMi achievement band calculations"""
    
    def test_fully_achieved_band(self):
        """Test F band for 85-100%"""
        assert calculate_tmmi_band(100.0) == "F"
        assert calculate_tmmi_band(85.0) == "F"
        assert calculate_tmmi_band(90.0) == "F"
    
    def test_largely_achieved_band(self):
        """Test L band for 50-85%"""
        assert calculate_tmmi_band(84.9) == "L"
        assert calculate_tmmi_band(50.0) == "L"
        assert calculate_tmmi_band(75.0) == "L"
    
    def test_partially_achieved_band(self):
        """Test P band for 15-50%"""
        assert calculate_tmmi_band(49.9) == "P"
        assert calculate_tmmi_band(15.0) == "P"
        assert calculate_tmmi_band(30.0) == "P"
    
    def test_not_achieved_band(self):
        """Test N band for 0-15%"""
        assert calculate_tmmi_band(14.9) == "N"
        assert calculate_tmmi_band(0.0) == "N"
        assert calculate_tmmi_band(10.0) == "N"


class TestSpecificPracticeAttainment:
    """Test specific practice attainment calculations"""
    
    def setup_method(self):
        """Set up test data"""
        self.questions = [
            TMMiQuestion(
                id="SP1_001",
                level=2,
                process_area="Test Planning",
                question="Test question 1",
                importance="High",
                recommended_activity="Activity 1",
                reference_url="http://example.com",
                specific_practice="SP2.1.1",
                specific_goal="SG2.1",
                generic_goal="GG2.1, GG2.2"
            ),
            TMMiQuestion(
                id="SP1_002",
                level=2,
                process_area="Test Planning",
                question="Test question 2",
                importance="Medium",
                recommended_activity="Activity 2",
                reference_url="http://example.com",
                specific_practice="SP2.1.1",
                specific_goal="SG2.1",
                generic_goal="GG2.1, GG2.2"
            ),
            TMMiQuestion(
                id="SP2_001",
                level=2,
                process_area="Test Planning",
                question="Test question 3",
                importance="High",
                recommended_activity="Activity 3",
                reference_url="http://example.com",
                specific_practice="SP2.2.1",
                specific_goal="SG2.2",
                generic_goal="GG2.1, GG2.2"
            )
        ]
        
        self.answers = [
            AssessmentAnswer(question_id="SP1_001", answer="Yes", evidence_url="http://evidence1.com"),
            AssessmentAnswer(question_id="SP1_002", answer="Partial", evidence_url="http://evidence2.com"),
            AssessmentAnswer(question_id="SP2_001", answer="No", evidence_url=None)
        ]
    
    def test_sp_attainment_calculation(self):
        """Test specific practice attainment calculation"""
        sp_attainment = calculate_specific_practice_attainment(self.questions, self.answers)
        
        # SP2.1.1 should have 2 questions: Yes (1.0) + Partial (0.5) = 1.5 / 2 = 75%
        assert "SP2.1.1" in sp_attainment
        assert sp_attainment["SP2.1.1"]["attainment_percentage"] == 75.0
        assert sp_attainment["SP2.1.1"]["band"] == "L"
        assert sp_attainment["SP2.1.1"]["evidence_coverage"] == 100.0
        
        # SP2.2.1 should have 1 question: No (0.0) = 0%
        assert "SP2.2.1" in sp_attainment
        assert sp_attainment["SP2.2.1"]["attainment_percentage"] == 0.0
        assert sp_attainment["SP2.2.1"]["band"] == "N"
        assert sp_attainment["SP2.2.1"]["evidence_coverage"] == 0.0


class TestSpecificGoalAttainment:
    """Test specific goal attainment calculations"""
    
    def setup_method(self):
        """Set up test data"""
        self.questions = [
            TMMiQuestion(
                id="SG1_SP1",
                level=2,
                process_area="Test Planning",
                question="SG1 Question 1",
                importance="High",
                recommended_activity="Activity 1",
                reference_url="http://example.com",
                specific_practice="SP2.1.1",
                specific_goal="SG2.1",
                generic_goal="GG2.1"
            ),
            TMMiQuestion(
                id="SG1_SP2",
                level=2,
                process_area="Test Planning",
                question="SG1 Question 2",
                importance="Medium",
                recommended_activity="Activity 2",
                reference_url="http://example.com",
                specific_practice="SP2.1.2",
                specific_goal="SG2.1",
                generic_goal="GG2.1"
            ),
            TMMiQuestion(
                id="SG2_SP1",
                level=2,
                process_area="Test Planning",
                question="SG2 Question 1",
                importance="High",
                recommended_activity="Activity 3",
                reference_url="http://example.com",
                specific_practice="SP2.2.1",
                specific_goal="SG2.2",
                generic_goal="GG2.1"
            )
        ]
        
        self.answers = [
            AssessmentAnswer(question_id="SG1_SP1", answer="Yes"),
            AssessmentAnswer(question_id="SG1_SP2", answer="Partial"),
            AssessmentAnswer(question_id="SG2_SP1", answer="No")
        ]
    
    def test_sg_attainment_calculation(self):
        """Test specific goal attainment calculation"""
        sg_attainment = calculate_specific_goal_attainment(self.questions, self.answers)
        
        # SG2.1 should have 2 SPs: SP2.1.1 (100%) + SP2.1.2 (50%) = 75%
        assert "SG2.1" in sg_attainment
        assert sg_attainment["SG2.1"]["attainment_percentage"] == 75.0
        assert sg_attainment["SG2.1"]["band"] == "L"
        
        # SG2.2 should have 1 SP: SP2.2.1 (0%) = 0%
        assert "SG2.2" in sg_attainment
        assert sg_attainment["SG2.2"]["attainment_percentage"] == 0.0
        assert sg_attainment["SG2.2"]["band"] == "N"


class TestProcessAreaAttainment:
    """Test process area attainment calculations"""
    
    def setup_method(self):
        """Set up test data"""
        self.questions = [
            TMMiQuestion(
                id="PA1_SG1_SP1",
                level=2,
                process_area="Test Planning",
                question="PA1 Question 1",
                importance="High",
                recommended_activity="Activity 1",
                reference_url="http://example.com",
                specific_practice="SP2.1.1",
                specific_goal="SG2.1",
                generic_goal="GG2.1"
            ),
            TMMiQuestion(
                id="PA1_SG2_SP1",
                level=2,
                process_area="Test Planning",
                question="PA1 Question 2",
                importance="Medium",
                recommended_activity="Activity 2",
                reference_url="http://example.com",
                specific_practice="SP2.2.1",
                specific_goal="SG2.2",
                generic_goal="GG2.1"
            ),
            TMMiQuestion(
                id="PA2_SG1_SP1",
                level=3,
                process_area="Test Organization",
                question="PA2 Question 1",
                importance="High",
                recommended_activity="Activity 3",
                reference_url="http://example.com",
                specific_practice="SP3.1.1",
                specific_goal="SG3.1",
                generic_goal="GG3.1"
            )
        ]
        
        self.answers = [
            AssessmentAnswer(question_id="PA1_SG1_SP1", answer="Yes"),
            AssessmentAnswer(question_id="PA1_SG2_SP1", answer="Partial"),
            AssessmentAnswer(question_id="PA2_SG1_SP1", answer="No")
        ]
    
    def test_pa_attainment_calculation(self):
        """Test process area attainment calculation"""
        pa_attainment = calculate_process_area_attainment_enhanced(self.questions, self.answers)
        
        # Test Planning should have 2 SGs: SG2.1 (100%) + SG2.2 (50%) = 75%
        assert "Test Planning" in pa_attainment
        assert pa_attainment["Test Planning"]["attainment_percentage"] == 75.0
        assert pa_attainment["Test Planning"]["band"] == "L"
        assert pa_attainment["Test Planning"]["level"] == 2
        
        # Test Organization should have 1 SG: SG3.1 (0%) = 0%
        assert "Test Organization" in pa_attainment
        assert pa_attainment["Test Organization"]["attainment_percentage"] == 0.0
        assert pa_attainment["Test Organization"]["band"] == "N"
        assert pa_attainment["Test Organization"]["level"] == 3


class TestNextLevelReadiness:
    """Test next level readiness calculations"""
    
    def setup_method(self):
        """Set up test data for level 2 organization"""
        self.questions = [
            # Level 2 questions (current level)
            TMMiQuestion(
                id="L2_PA1_1",
                level=2,
                process_area="Test Planning",
                question="L2 Question 1",
                importance="High",
                recommended_activity="Activity 1",
                reference_url="http://example.com",
                specific_practice="SP2.1.1",
                specific_goal="SG2.1",
                generic_goal="GG2.1"
            ),
            TMMiQuestion(
                id="L2_PA1_2",
                level=2,
                process_area="Test Planning",
                question="L2 Question 2",
                importance="Medium",
                recommended_activity="Activity 2",
                reference_url="http://example.com",
                specific_practice="SP2.1.2",
                specific_goal="SG2.1",
                generic_goal="GG2.1"
            ),
            # Level 3 questions (target level)
            TMMiQuestion(
                id="L3_PA1_1",
                level=3,
                process_area="Test Organization",
                question="L3 Question 1",
                importance="High",
                recommended_activity="Activity 3",
                reference_url="http://example.com",
                specific_practice="SP3.1.1",
                specific_goal="SG3.1",
                generic_goal="GG3.1"
            ),
            TMMiQuestion(
                id="L3_PA1_2",
                level=3,
                process_area="Test Organization",
                question="L3 Question 2",
                importance="Medium",
                recommended_activity="Activity 4",
                reference_url="http://example.com",
                specific_practice="SP3.1.2",
                specific_goal="SG3.1",
                generic_goal="GG3.1"
            )
        ]
        
        # Level 2 fully achieved (100%), Level 3 partially achieved (50%)
        self.answers = [
            AssessmentAnswer(question_id="L2_PA1_1", answer="Yes"),
            AssessmentAnswer(question_id="L2_PA1_2", answer="Yes"),
            AssessmentAnswer(question_id="L3_PA1_1", answer="Yes"),
            AssessmentAnswer(question_id="L3_PA1_2", answer="No")
        ]
    
    def test_next_level_readiness_calculation(self):
        """Test next level readiness calculation"""
        readiness = calculate_next_level_readiness(self.questions, self.answers)
        
        # Should be at level 2, targeting level 3
        assert readiness["current_level"] == 2
        assert readiness["target_level"] == 3
        
        # Level 3 readiness should be 50% (1 Yes + 1 No)
        assert readiness["target_level_readiness"] == 50.0
        
        # Should be eligible since PA meets 50% threshold
        assert readiness["gating_status"] == "Eligible"
        assert readiness["gating_reason"] == ""
        
        # Conservative readiness should match target level readiness
        assert readiness["conservative_readiness"] == 50.0


class TestGapAnalysis:
    """Test enhanced gap analysis"""
    
    def setup_method(self):
        """Set up test data"""
        self.questions = [
            TMMiQuestion(
                id="GAP_TEST_1",
                level=2,
                process_area="Test Planning",
                question="Gap question 1",
                importance="High",
                recommended_activity="Fix this gap",
                reference_url="http://example.com",
                specific_practice="SP2.1.1",
                specific_goal="SG2.1",
                generic_goal="GG2.1"
            ),
            TMMiQuestion(
                id="GAP_TEST_2",
                level=3,
                process_area="Test Organization",
                question="Gap question 2",
                importance="Medium",
                recommended_activity="Improve this area",
                reference_url="http://example.com",
                specific_practice="SP3.1.1",
                specific_goal="SG3.1",
                generic_goal="GG3.1"
            )
        ]
        
        self.answers = [
            AssessmentAnswer(question_id="GAP_TEST_1", answer="No", evidence_url=None),
            AssessmentAnswer(question_id="GAP_TEST_2", answer="Partial", evidence_url="http://evidence.com")
        ]
    
    def test_gap_analysis_extraction(self):
        """Test gap analysis extraction"""
        gaps = extract_gap_analysis_enhanced(self.questions, self.answers)
        
        assert len(gaps) == 2
        
        # Check first gap
        gap1 = gaps[0]  # High priority first
        assert gap1["question_id"] == "GAP_TEST_1"
        assert gap1["importance"] == "High"
        assert gap1["current_answer"] == "No"
        assert gap1["specific_practice"] == "SP2.1.1"
        assert gap1["specific_goal"] == "SG2.1"
        assert "Implement" in gap1["action_to_close"]
        
        # Check second gap
        gap2 = gaps[1]
        assert gap2["question_id"] == "GAP_TEST_2"
        assert gap2["importance"] == "Medium"
        assert gap2["current_answer"] == "Partial"
        assert gap2["evidence_url"] == "http://evidence.com"


class TestGenericGoalCompliance:
    """Test generic goal compliance calculations"""
    
    def setup_method(self):
        """Set up test data"""
        self.questions = [
            TMMiQuestion(
                id="GG2_1",
                level=2,
                process_area="Test Planning",
                question="GG2 Question 1",
                importance="High",
                recommended_activity="Activity 1",
                reference_url="http://example.com",
                specific_practice="SP2.1.1",
                specific_goal="SG2.1",
                generic_goal="GG2.1"
            ),
            TMMiQuestion(
                id="GG2_2",
                level=2,
                process_area="Test Planning",
                question="GG2 Question 2",
                importance="Medium",
                recommended_activity="Activity 2",
                reference_url="http://example.com",
                specific_practice="SP2.1.2",
                specific_goal="SG2.1",
                generic_goal="GG2.1"
            ),
            TMMiQuestion(
                id="GG3_1",
                level=3,
                process_area="Test Organization",
                question="GG3 Question 1",
                importance="High",
                recommended_activity="Activity 3",
                reference_url="http://example.com",
                specific_practice="SP3.1.1",
                specific_goal="SG3.1",
                generic_goal="GG3.1"
            )
        ]
        
        self.answers = [
            AssessmentAnswer(question_id="GG2_1", answer="Yes", evidence_url="http://evidence1.com"),
            AssessmentAnswer(question_id="GG2_2", answer="Partial", evidence_url="http://evidence2.com"),
            AssessmentAnswer(question_id="GG3_1", answer="No", evidence_url=None)
        ]
    
    def test_generic_goal_compliance(self):
        """Test generic goal compliance calculation"""
        gg_compliance = calculate_generic_goal_compliance(self.questions, self.answers)
        
        # GG2 should be 75% (Yes + Partial) and met
        assert "GG2 - Managed" in gg_compliance
        gg2_data = gg_compliance["GG2 - Managed"]
        assert gg2_data["attainment_percentage"] == 75.0
        assert gg2_data["band"] == "L"
        assert gg2_data["status"] == "Not Met"  # Below 85% threshold
        assert gg2_data["evidence_coverage"] == 100.0
        
        # GG3 should be 0% and not met
        assert "GG3 - Defined" in gg_compliance
        gg3_data = gg_compliance["GG3 - Defined"]
        assert gg3_data["attainment_percentage"] == 0.0
        assert gg3_data["band"] == "N"
        assert gg3_data["status"] == "Not Met"
        assert gg3_data["evidence_coverage"] == 0.0


class TestProgressionDashboardData:
    """Test progression dashboard data generation"""

    def setup_method(self):
        self.questions = [
            TMMiQuestion(
                id="L2_TPS_001", level=2, process_area="Test Policy and Strategy",
                question="Is a documented test policy established and maintained?",
                importance="High", recommended_activity="Define and publish a company-wide test policy.",
                reference_url="https://example.com", specific_goal="SG2.1", specific_practice="SP2.1.1",
                generic_goal="GG2.1", practice_id="L2_TPS_001"
            ),
            TMMiQuestion(
                id="L2_TPS_002", level=2, process_area="Test Policy and Strategy",
                question="Is the test policy aligned with business objectives?",
                importance="High", recommended_activity="Review and align test policy with business goals.",
                reference_url="https://example.com", specific_goal="SG2.2", specific_practice="SP2.2.1",
                generic_goal="GG2.2", practice_id="L2_TPS_002"
            )
        ]
        self.answers = [
            AssessmentAnswer(question_id="L2_TPS_001", answer="Yes", evidence_url="https://example.com/doc1"),
            AssessmentAnswer(question_id="L2_TPS_002", answer="Partial", evidence_url="https://example.com/doc2")
        ]

    def test_progression_dashboard_data_generation(self):
        """Test that progression dashboard data is generated correctly"""
        data = generate_progression_dashboard_data(self.questions, self.answers)
        
        assert "current_level" in data
        assert "next_level" in data
        assert "conservative_readiness" in data
        assert "gating_status" in data
        assert "process_areas" in data
        assert "gaps" in data
        assert "generic_goals" in data
        assert "evidence_coverage" in data

    def test_gap_analysis_extraction(self):
        """Test gap analysis extraction with enhanced data"""
        gaps = extract_gap_analysis_enhanced(self.questions, self.answers)
        
        assert len(gaps) > 0
        gap1 = gaps[0]
        assert "process_area" in gap1
        assert "specific_goal" in gap1
        assert "specific_practice" in gap1
        assert "current_answer" in gap1
        assert "action_to_close" in gap1

    def test_evidence_coverage_enhanced(self):
        """Test enhanced evidence coverage calculation"""
        coverage = calculate_evidence_coverage(self.answers)
        
        assert "percentage" in coverage
        assert "with_evidence" in coverage
        assert "total_answers" in coverage

    def test_generic_goal_compliance(self):
        """Test generic goal compliance calculation"""
        compliance = calculate_generic_goal_compliance(self.questions, self.answers)
        
        # Check that we have generic goal compliance data
        assert len(compliance) > 0
        # Check that we have the expected structure for at least one generic goal
        first_gg = list(compliance.keys())[0]
        assert "attainment_percentage" in compliance[first_gg]
        assert "band" in compliance[first_gg]
        assert "status" in compliance[first_gg]

    def test_specific_practice_attainment_edge_cases(self):
        """Test specific practice attainment with edge cases"""
        # Test with no answers - should still return SPs but with 0% attainment
        no_answers = []
        sp_attainment = calculate_specific_practice_attainment(self.questions, no_answers)
        assert len(sp_attainment) > 0  # Should return SPs even with no answers
        # Check that first SP has 0% attainment
        first_sp = list(sp_attainment.keys())[0]
        assert sp_attainment[first_sp]["attainment_percentage"] == 0.0
        
        # Test with single answer
        single_answer = [AssessmentAnswer(question_id="L2_TPS_001", answer="Yes")]
        sp_attainment = calculate_specific_practice_attainment(self.questions, single_answer)
        assert "SP2.1.1" in sp_attainment
        assert sp_attainment["SP2.1.1"]["attainment_percentage"] == 100.0

    def test_process_area_attainment_edge_cases(self):
        """Test process area attainment with edge cases"""
        # Test with no specific goals
        questions_no_sg = [
            TMMiQuestion(
                id="L2_TPS_001", level=2, process_area="Test Policy and Strategy",
                question="Test question", importance="High", recommended_activity="Test activity",
                reference_url="https://example.com", specific_goal=None, specific_practice=None,
                generic_goal=None, practice_id="L2_TPS_001"
            )
        ]
        pa_attainment = calculate_process_area_attainment_enhanced(questions_no_sg, self.answers)
        assert "Test Policy and Strategy" in pa_attainment

    def test_next_level_readiness_edge_cases(self):
        """Test next level readiness with edge cases"""
        # Test with no process areas at target level
        questions_l2_only = [
            TMMiQuestion(
                id="L2_TPS_001", level=2, process_area="Test Policy and Strategy",
                question="Test question", importance="High", recommended_activity="Test activity",
                reference_url="https://example.com", specific_goal="SG2.1", specific_practice="SP2.1.1",
                generic_goal="GG2.1", practice_id="L2_TPS_001"
            )
        ]
        readiness = calculate_next_level_readiness(questions_l2_only, self.answers)
        assert readiness["current_level"] == 2
        assert readiness["target_level"] == 3
        # If no process areas at target level, readiness should be 0
        assert readiness["conservative_readiness"] == 0.0
        # Since there are no process areas at level 3, it can't gate against them
        # The status will depend on the actual logic, but we should have a reason
        assert "gating_status" in readiness
        assert "gating_reason" in readiness

    def test_tmmi_band_calculation_edge_cases(self):
        """Test TMMi band calculation with edge cases"""
        assert calculate_tmmi_band(0.0) == "N"
        assert calculate_tmmi_band(15.0) == "P"
        assert calculate_tmmi_band(50.0) == "L"
        assert calculate_tmmi_band(85.0) == "F"
        assert calculate_tmmi_band(100.0) == "F"
        
        # Test boundary conditions
        assert calculate_tmmi_band(14.9) == "N"
        assert calculate_tmmi_band(15.1) == "P"
        assert calculate_tmmi_band(49.9) == "P"
        assert calculate_tmmi_band(50.1) == "L"
        assert calculate_tmmi_band(84.9) == "L"
        assert calculate_tmmi_band(85.1) == "F"


if __name__ == "__main__":
    pytest.main([__file__])
