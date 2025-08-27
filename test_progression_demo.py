#!/usr/bin/env python3
"""
Demo script for TMMi Progression Analysis Feature

This script demonstrates the enhanced progression analysis capabilities
without requiring the full Streamlit application.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models.database import load_tmmi_questions, AssessmentAnswer
from utils.scoring import (
    calculate_tmmi_band,
    calculate_specific_practice_attainment,
    calculate_specific_goal_attainment,
    calculate_process_area_attainment_enhanced,
    calculate_next_level_readiness,
    extract_gap_analysis_enhanced,
    calculate_generic_goal_compliance,
    generate_progression_dashboard_data
)


def demo_tmmi_bands():
    """Demonstrate TMMi achievement band calculations"""
    print("=== TMMi Achievement Bands ===")
    test_percentages = [0, 10, 25, 60, 80, 90, 100]
    
    for pct in test_percentages:
        band = calculate_tmmi_band(pct)
        print(f"{pct:3.0f}% -> {band} ({get_band_description(band)})")


def get_band_description(band):
    """Get human-readable description of TMMi band"""
    descriptions = {
        'N': 'Not Achieved (0-15%)',
        'P': 'Partially (15-50%)',
        'L': 'Largely (50-85%)',
        'F': 'Fully (85-100%)'
    }
    return descriptions.get(band, 'Unknown')


def demo_progression_analysis():
    """Demonstrate progression analysis with sample data"""
    print("\n=== Progression Analysis Demo ===")
    
    # Load questions
    questions = load_tmmi_questions()
    print(f"Loaded {len(questions)} questions from TMMi framework")
    
    # Create sample assessment answers
    sample_answers = [
        AssessmentAnswer(question_id="L2_TPS_001", answer="Yes", evidence_url="http://example.com/policy.pdf"),
        AssessmentAnswer(question_id="L2_TPS_002", answer="Partial", evidence_url="http://example.com/strategy.pdf"),
        AssessmentAnswer(question_id="L2_TP_001", answer="Yes", evidence_url="http://example.com/plans.pdf"),
        AssessmentAnswer(question_id="L2_TP_002", answer="No", evidence_url=None),
        AssessmentAnswer(question_id="L2_TMC_001", answer="Yes", evidence_url="http://example.com/monitoring.pdf"),
        AssessmentAnswer(question_id="L2_TMC_002", answer="Partial", evidence_url="http://example.com/actions.pdf"),
        AssessmentAnswer(question_id="L2_TD_001", answer="Partial", evidence_url="http://example.com/techniques.pdf"),
        AssessmentAnswer(question_id="L2_TE_001", answer="Yes", evidence_url="http://example.com/environment.pdf"),
        AssessmentAnswer(question_id="L3_TLI_001", answer="Partial", evidence_url="http://example.com/integration.pdf"),
        AssessmentAnswer(question_id="L3_PR_001", answer="No", evidence_url=None),
        AssessmentAnswer(question_id="L3_NFTR_001", answer="Partial", evidence_url="http://example.com/non-functional.pdf"),
        AssessmentAnswer(question_id="L3_TTO_001", answer="No", evidence_url=None),
    ]
    
    print(f"Created sample assessment with {len(sample_answers)} answers")
    
    # Calculate specific practice attainment
    print("\n--- Specific Practice Attainment ---")
    sp_attainment = calculate_specific_practice_attainment(questions, sample_answers)
    
    for sp_id, sp_data in sp_attainment.items():
        if sp_data["question_count"] > 0:
            print(f"{sp_id}: {sp_data['attainment_percentage']:.1f}% ({sp_data['band']}) - "
                  f"{sp_data['evidence_coverage']:.1f}% evidence coverage")
    
    # Calculate specific goal attainment
    print("\n--- Specific Goal Attainment ---")
    sg_attainment = calculate_specific_goal_attainment(questions, sample_answers)
    
    for sg_id, sg_data in sg_attainment.items():
        if sg_data["sp_count"] > 0:
            print(f"{sg_id}: {sg_data['attainment_percentage']:.1f}% ({sg_data['band']})")
    
    # Calculate process area attainment
    print("\n--- Process Area Attainment ---")
    pa_attainment = calculate_process_area_attainment_enhanced(questions, sample_answers)
    
    for pa_name, pa_data in pa_attainment.items():
        print(f"{pa_name} (Level {pa_data['level']}): {pa_data['attainment_percentage']:.1f}% ({pa_data['band']})")
    
    # Calculate next level readiness
    print("\n--- Next Level Readiness ---")
    readiness = calculate_next_level_readiness(questions, sample_answers)
    
    print(f"Current Level: {readiness['current_level']}")
    print(f"Target Level: {readiness['target_level']}")
    print(f"Target Level Readiness: {readiness['target_level_readiness']:.1f}%")
    print(f"Conservative Readiness: {readiness['conservative_readiness']:.1f}%")
    print(f"Gating Status: {readiness['gating_status']}")
    if readiness['gating_reason']:
        print(f"Gating Reason: {readiness['gating_reason']}")
    
    # Gap analysis
    print("\n--- Gap Analysis ---")
    gaps = extract_gap_analysis_enhanced(questions, sample_answers)
    
    print(f"Total gaps identified: {len(gaps)}")
    for i, gap in enumerate(gaps[:5], 1):  # Show first 5 gaps
        print(f"Gap {i}: {gap['process_area']} - {gap['specific_practice']}")
        print(f"  Question: {gap['question'][:60]}...")
        print(f"  Current: {gap['current_answer']} | Priority: {gap['importance']}")
        print(f"  Action: {gap['action_to_close']}")
        if gap['evidence_url']:
            print(f"  Evidence: {gap['evidence_url']}")
        print()
    
    # Generic goal compliance
    print("--- Generic Goal Compliance ---")
    gg_compliance = calculate_generic_goal_compliance(questions, sample_answers)
    
    for gg_name, gg_data in gg_compliance.items():
        status_icon = "✅" if gg_data["status"] == "Met" else "❌"
        print(f"{status_icon} {gg_name}: {gg_data['attainment_percentage']:.1f}% ({gg_data['band']}) - "
              f"{gg_data['evidence_coverage']:.1f}% evidence")
    
    # Generate comprehensive dashboard data
    print("\n--- Progression Dashboard Summary ---")
    dashboard_data = generate_progression_dashboard_data(questions, sample_answers)
    
    print(f"Current Level: {dashboard_data['current_level']}")
    print(f"Next Level: {dashboard_data['next_level']}")
    print(f"Readiness: {dashboard_data['conservative_readiness']:.1f}%")
    print(f"Gating Status: {dashboard_data['gating_status']}")
    print(f"Total Gaps: {dashboard_data['gap_count']}")
    print(f"High Priority Gaps: {len(dashboard_data['high_priority_gaps'])}")
    print(f"Evidence Coverage: {dashboard_data['evidence_coverage']['percentage']:.1f}%")
    
    # High risk assertions
    if dashboard_data['high_risk_assertions']:
        print(f"High Risk Assertions: {', '.join(dashboard_data['high_risk_assertions'])}")


def main():
    """Main demo function"""
    print("TMMi Progression Analysis Feature Demo")
    print("=" * 50)
    
    try:
        demo_tmmi_bands()
        demo_progression_analysis()
        
        print("\n" + "=" * 50)
        print("Demo completed successfully!")
        print("\nTo use the full progression dashboard:")
        print("1. Install Streamlit: pip install streamlit")
        print("2. Run the app: streamlit run app.py")
        print("3. Navigate to 'Progression Dashboard' in the navigation")
        
    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
