"""
Scoring logic for TMMi assessment calculations
"""

from typing import List, Dict, Tuple, Set
from src.models.database import TMMiQuestion, AssessmentAnswer, Assessment


def calculate_answer_score(answer: str) -> float:
    """Convert answer to numeric score"""
    score_map = {"Yes": 1.0, "Partial": 0.5, "No": 0.0}
    return score_map.get(answer, 0.0)


def calculate_level_compliance(questions: List[TMMiQuestion], answers: List[AssessmentAnswer]) -> Dict[int, Dict]:
    """Calculate compliance percentage for each TMMi level"""
    # Create answer lookup
    answer_lookup = {ans.question_id: ans for ans in answers}

    # Group questions by level
    questions_by_level = {}
    for question in questions:
        if question.level not in questions_by_level:
            questions_by_level[question.level] = []
        questions_by_level[question.level].append(question)

    level_compliance = {}

    for level, level_questions in questions_by_level.items():
        total_score = 0.0
        max_score = len(level_questions)
        answered_questions = 0

        yes_count = 0
        partial_count = 0
        no_count = 0

        for question in level_questions:
            if question.id in answer_lookup:
                answer = answer_lookup[question.id]
                score = calculate_answer_score(answer.answer)
                total_score += score
                answered_questions += 1

                if answer.answer == "Yes":
                    yes_count += 1
                elif answer.answer == "Partial":
                    partial_count += 1
                else:
                    no_count += 1

        compliance_percentage = (total_score / max_score * 100) if max_score > 0 else 0

        level_compliance[level] = {
            "compliance_percentage": compliance_percentage,
            "total_questions": len(level_questions),
            "answered_questions": answered_questions,
            "yes_count": yes_count,
            "partial_count": partial_count,
            "no_count": no_count,
            "total_score": total_score,
            "max_score": max_score,
        }

    return level_compliance


def calculate_process_area_compliance(
    questions: List[TMMiQuestion], answers: List[AssessmentAnswer]
) -> Dict[str, Dict]:
    """Calculate compliance percentage for each process area"""

    # Create answer lookup
    answer_lookup = {ans.question_id: ans for ans in answers}

    # Group questions by process area
    questions_by_area = {}
    for question in questions:
        if question.process_area not in questions_by_area:
            questions_by_area[question.process_area] = []
        questions_by_area[question.process_area].append(question)

    area_compliance = {}

    for area, area_questions in questions_by_area.items():
        total_score = 0.0
        max_score = len(area_questions)
        answered_questions = 0

        yes_count = 0
        partial_count = 0
        no_count = 0

        for question in area_questions:
            if question.id in answer_lookup:
                answer = answer_lookup[question.id]
                score = calculate_answer_score(answer.answer)
                total_score += score
                answered_questions += 1

                if answer.answer == "Yes":
                    yes_count += 1
                elif answer.answer == "Partial":
                    partial_count += 1
                else:
                    no_count += 1

        compliance_percentage = (total_score / max_score * 100) if max_score > 0 else 0

        area_compliance[area] = {
            "compliance_percentage": compliance_percentage,
            "total_questions": len(area_questions),
            "answered_questions": answered_questions,
            "yes_count": yes_count,
            "partial_count": partial_count,
            "no_count": no_count,
            "total_score": total_score,
            "max_score": max_score,
        }

    return area_compliance


def determine_current_tmmi_level(level_compliance: Dict[int, Dict], threshold: float = 80.0) -> Tuple[int, str]:
    """
    Determine current TMMi level based on compliance scores

    Rules:
    - Must achieve threshold% compliance at current level and all lower levels
    - Returns tuple of (level, explanation)
    """

    current_level = 1  # Start with Level 1 (non-formal)
    explanation = "Level 1 (Initial) - Ad-hoc testing processes"

    # Check levels 2-5 in order
    for level in sorted([2, 3, 4, 5]):
        if level in level_compliance:
            compliance = level_compliance[level]["compliance_percentage"]

            # Check if this level meets threshold
            if compliance >= threshold:
                # Check if all lower levels also meet threshold
                lower_levels_compliant = True
                for lower_level in range(2, level):
                    if lower_level in level_compliance:
                        if level_compliance[lower_level]["compliance_percentage"] < threshold:
                            lower_levels_compliant = False
                            break

                if lower_levels_compliant:
                    current_level = level
                    level_names = {2: "Managed", 3: "Defined", 4: "Measured", 5: "Optimized"}
                    explanation = f"Level {level} ({level_names[level]}) - {compliance:.1f}% compliance"

    return current_level, explanation


def get_gap_analysis(questions: List[TMMiQuestion], answers: List[AssessmentAnswer]) -> List[Dict]:
    """Generate gap analysis for improvement recommendations"""
    # Create answer lookup
    answer_lookup = {ans.question_id: ans for ans in answers}

    gaps = []

    for question in questions:
        if question.id in answer_lookup:
            answer = answer_lookup[question.id]

            # Include gaps for 'No' and 'Partial' answers
            if answer.answer in ["No", "Partial"]:
                gaps.append(
                    {
                        "question_id": question.id,
                        "level": question.level,
                        "process_area": question.process_area,
                        "question": question.question,
                        "current_answer": answer.answer,
                        "importance": question.importance,
                        "recommended_activity": question.recommended_activity,
                        "reference_url": question.reference_url,
                        "evidence_url": answer.evidence_url,
                        "comment": answer.comment,
                    }
                )
        else:
            # Unanswered questions are also gaps
            gaps.append(
                {
                    "question_id": question.id,
                    "level": question.level,
                    "process_area": question.process_area,
                    "question": question.question,
                    "current_answer": "Not Answered",
                    "importance": question.importance,
                    "recommended_activity": question.recommended_activity,
                    "reference_url": question.reference_url,
                    "evidence_url": None,
                    "comment": None,
                }
            )

    # Sort by importance and level
    importance_order = {"High": 0, "Medium": 1, "Low": 2}
    gaps.sort(key=lambda x: (importance_order.get(x["importance"], 3), x["level"]))

    return gaps


def calculate_evidence_coverage(answers: List[AssessmentAnswer]) -> Dict[str, float]:
    """Calculate percentage of answers that have evidence provided"""

    total_answers = len(answers)
    if total_answers == 0:
        return {"percentage": 0.0, "with_evidence": 0, "total_answers": 0}

    with_evidence = sum(1 for answer in answers if answer.evidence_url and answer.evidence_url.strip())
    percentage = (with_evidence / total_answers) * 100

    return {"percentage": percentage, "with_evidence": with_evidence, "total_answers": total_answers}


def generate_assessment_summary(questions: List[TMMiQuestion], assessment: Assessment) -> Dict:
    """Generate comprehensive assessment summary"""

    level_compliance = calculate_level_compliance(questions, assessment.answers)
    process_area_compliance = calculate_process_area_compliance(questions, assessment.answers)
    current_level, level_explanation = determine_current_tmmi_level(level_compliance)
    gaps = get_gap_analysis(questions, assessment.answers)
    evidence_coverage = calculate_evidence_coverage(assessment.answers)

    # Overall statistics
    total_questions = len(questions)
    answered_questions = len(assessment.answers)
    yes_answers = sum(1 for ans in assessment.answers if ans.answer == "Yes")
    partial_answers = sum(1 for ans in assessment.answers if ans.answer == "Partial")
    no_answers = sum(1 for ans in assessment.answers if ans.answer == "No")

    overall_score = sum(calculate_answer_score(ans.answer) for ans in assessment.answers)
    overall_percentage = (overall_score / total_questions * 100) if total_questions > 0 else 0

    return {
        "assessment_id": assessment.id,
        "timestamp": assessment.timestamp,
        "reviewer_name": assessment.reviewer_name,
        "organization": assessment.organization,
        "current_level": current_level,
        "level_explanation": level_explanation,
        "overall_percentage": overall_percentage,
        "total_questions": total_questions,
        "answered_questions": answered_questions,
        "yes_answers": yes_answers,
        "partial_answers": partial_answers,
        "no_answers": no_answers,
        "level_compliance": level_compliance,
        "process_area_compliance": process_area_compliance,
        "gaps": gaps,
        "evidence_coverage": evidence_coverage,
        "high_priority_gaps": [gap for gap in gaps if gap["importance"] == "High"],
        "medium_priority_gaps": [gap for gap in gaps if gap["importance"] == "Medium"],
        "low_priority_gaps": [gap for gap in gaps if gap["importance"] == "Low"],
    }


# Enhanced TMMi Progression Analysis Functions

def calculate_tmmi_band(percentage: float) -> str:
    """
    Calculate TMMi achievement band based on percentage
    
    N (Not Achieved) = 0–15%
    P (Partially) = 15–50% 
    L (Largely) = 50–85%
    F (Fully) = 85–100%
    """
    if percentage >= 85:
        return "F"
    elif percentage >= 50:
        return "L"
    elif percentage >= 15:
        return "P"
    else:
        return "N"


def calculate_specific_practice_attainment(questions: List[TMMiQuestion], answers: List[AssessmentAnswer]) -> Dict[str, Dict]:
    """
    Calculate attainment for each Specific Practice (SP)
    
    Returns: Dict[sp_id, {attainment_pct, band, question_count, evidence_count}]
    """
    sp_attainment = {}
    answer_lookup = {ans.question_id: ans for ans in answers}
    
    # Group questions by specific practice
    for question in questions:
        if question.specific_practice:
            sp_id = question.specific_practice
            if sp_id not in sp_attainment:
                sp_attainment[sp_id] = {
                    "questions": [],
                    "total_score": 0.0,
                    "question_count": 0,
                    "evidence_count": 0
                }
            
            sp_attainment[sp_id]["questions"].append(question.id)
            sp_attainment[sp_id]["question_count"] += 1
            
            if question.id in answer_lookup:
                answer = answer_lookup[question.id]
                score = calculate_answer_score(answer.answer)
                sp_attainment[sp_id]["total_score"] += score
                
                if answer.evidence_url and answer.evidence_url.strip():
                    sp_attainment[sp_id]["evidence_count"] += 1
    
    # Calculate percentages and bands
    for sp_id, data in sp_attainment.items():
        if data["question_count"] > 0:
            attainment_pct = (data["total_score"] / data["question_count"]) * 100
            data["attainment_percentage"] = attainment_pct
            data["band"] = calculate_tmmi_band(attainment_pct)
            data["evidence_coverage"] = (data["evidence_count"] / data["question_count"]) * 100
        else:
            data["attainment_percentage"] = 0.0
            data["band"] = "N"
            data["evidence_coverage"] = 0.0
    
    return sp_attainment


def calculate_specific_goal_attainment(questions: List[TMMiQuestion], answers: List[AssessmentAnswer]) -> Dict[str, Dict]:
    """
    Calculate attainment for each Specific Goal (SG) based on its SPs
    """
    sp_attainment = calculate_specific_practice_attainment(questions, answers)
    sg_attainment = {}
    
    # Group SPs by SG
    for question in questions:
        if question.specific_goal:
            sg_id = question.specific_goal
            if sg_id not in sg_attainment:
                sg_attainment[sg_id] = {
                    "specific_practices": [],
                    "total_attainment": 0.0,
                    "sp_count": 0
                }
            
            if question.specific_practice in sp_attainment:
                sg_attainment[sg_id]["specific_practices"].append(question.specific_practice)
                sg_attainment[sg_id]["total_attainment"] += sp_attainment[question.specific_practice]["attainment_percentage"]
                sg_attainment[sg_id]["sp_count"] += 1
    
    # Calculate SG attainment as mean of SPs
    for sg_id, data in sg_attainment.items():
        if data["sp_count"] > 0:
            data["attainment_percentage"] = data["total_attainment"] / data["sp_count"]
            data["band"] = calculate_tmmi_band(data["attainment_percentage"])
        else:
            data["attainment_percentage"] = 0.0
            data["band"] = "N"
    
    return sg_attainment


def calculate_process_area_attainment_enhanced(questions: List[TMMiQuestion], answers: List[AssessmentAnswer]) -> Dict[str, Dict]:
    """
    Enhanced process area calculation using SG attainment
    """
    sg_attainment = calculate_specific_goal_attainment(questions, answers)
    pa_attainment = {}
    
    # Group SGs by Process Area
    for question in questions:
        if question.process_area:
            pa_name = question.process_area
            if pa_name not in pa_attainment:
                pa_attainment[pa_name] = {
                    "specific_goals": [],
                    "total_attainment": 0.0,
                    "sg_count": 0,
                    "level": question.level
                }
            
            if question.specific_goal in sg_attainment:
                sg_id = question.specific_goal
                if sg_id not in pa_attainment[pa_name]["specific_goals"]:
                    pa_attainment[pa_name]["specific_goals"].append(sg_id)
                    pa_attainment[pa_name]["total_attainment"] += sg_attainment[sg_id]["attainment_percentage"]
                    pa_attainment[pa_name]["sg_count"] += 1
    
    # Calculate PA attainment as mean of SGs
    for pa_name, data in pa_attainment.items():
        if data["sg_count"] > 0:
            data["attainment_percentage"] = data["total_attainment"] / data["sg_count"]
            data["band"] = calculate_tmmi_band(data["attainment_percentage"])
        else:
            data["attainment_percentage"] = 0.0
            data["band"] = "N"
    
    return pa_attainment


def calculate_next_level_readiness(questions: List[TMMiQuestion], answers: List[AssessmentAnswer]) -> Dict:
    """
    Calculate readiness for the next TMMi level
    
    Returns comprehensive readiness analysis including:
    - Current achieved level
    - Target level (next level)
    - Readiness percentage
    - Gating status
    - Process area breakdown
    - Specific gaps
    """
    # Get current level
    level_compliance = calculate_level_compliance(questions, answers)
    current_level, _ = determine_current_tmmi_level(level_compliance)
    
    # Target level is next level
    target_level = min(current_level + 1, 5)
    
    # Get process areas for target level
    target_level_questions = [q for q in questions if q.level == target_level]
    target_process_areas = list(set(q.process_area for q in target_level_questions))
    
    # Calculate enhanced PA attainment
    pa_attainment = calculate_process_area_attainment_enhanced(questions, answers)
    
    # Filter for target level PAs
    target_pa_data = {}
    target_level_readiness = 0.0
    target_pa_count = 0
    
    for pa_name, pa_data in pa_attainment.items():
        if pa_data["level"] == target_level:
            target_pa_data[pa_name] = pa_data
            target_level_readiness += pa_data["attainment_percentage"]
            target_pa_count += 1
    
    if target_pa_count > 0:
        target_level_readiness = target_level_readiness / target_pa_count
    
    # Gating logic: require all PAs at target level to be at least L (≥50%)
    gating_status = "Eligible"
    gating_reason = ""
    
    for pa_name, pa_data in target_pa_data.items():
        if pa_data["attainment_percentage"] < 50:
            gating_status = "Not Eligible"
            gating_reason = f"Process Area '{pa_name}' below 50% (currently {pa_data['attainment_percentage']:.1f}%)"
            break
    
    # Conservative readiness calculation
    if gating_status == "Not Eligible":
        # Clamp readiness to just above lowest PA percentage
        min_pa_attainment = min(pa_data["attainment_percentage"] for pa_data in target_pa_data.values())
        conservative_readiness = min_pa_attainment + 5  # Add small buffer
    else:
        conservative_readiness = target_level_readiness
    
    return {
        "current_level": current_level,
        "target_level": target_level,
        "target_level_readiness": target_level_readiness,
        "conservative_readiness": conservative_readiness,
        "gating_status": gating_status,
        "gating_reason": gating_reason,
        "target_process_areas": target_pa_data,
        "target_pa_count": target_pa_count,
        "overall_pa_attainment": pa_attainment
    }


def extract_gap_analysis_enhanced(questions: List[TMMiQuestion], answers: List[AssessmentAnswer]) -> List[Dict]:
    """
    Enhanced gap analysis with SP/SG mapping and action recommendations
    """
    sp_attainment = calculate_specific_practice_attainment(questions, answers)
    sg_attainment = calculate_specific_goal_attainment(questions, answers)
    pa_attainment = calculate_process_area_attainment_enhanced(questions, answers)
    
    gaps = []
    answer_lookup = {ans.question_id: ans for ans in answers}
    
    for question in questions:
        if question.id in answer_lookup:
            answer = answer_lookup[question.id]
            
            # Include gaps for 'No' and 'Partial' answers, or if SP attainment < 85%
            if (answer.answer in ["No", "Partial"] or 
                (question.specific_practice and 
                 sp_attainment.get(question.specific_practice, {}).get("attainment_percentage", 0) < 85)):
                
                # Get SP and SG data
                sp_data = sp_attainment.get(question.specific_practice, {}) if question.specific_practice else {}
                sg_data = sg_attainment.get(question.specific_goal, {}) if question.specific_goal else {}
                
                gap = {
                    "question_id": question.id,
                    "level": question.level,
                    "process_area": question.process_area,
                    "specific_goal": question.specific_goal,
                    "specific_practice": question.specific_practice,
                    "question": question.question,
                    "current_answer": answer.answer,
                    "importance": question.importance,
                    "recommended_activity": question.recommended_activity,
                    "reference_url": question.reference_url,
                    "evidence_url": answer.evidence_url,
                    "comment": answer.comment,
                    "sp_attainment": sp_data.get("attainment_percentage", 0),
                    "sp_band": sp_data.get("band", "N"),
                    "sg_attainment": sg_data.get("attainment_percentage", 0),
                    "sg_band": sg_data.get("band", "N"),
                    "action_to_close": _generate_action_recommendation(
                        question, answer, sp_data, sg_data
                    )
                }
                
                gaps.append(gap)
    
    # Sort by importance, level, and attainment
    importance_order = {"High": 0, "Medium": 1, "Low": 2}
    gaps.sort(key=lambda x: (
        importance_order.get(x["importance"], 3),
        x["level"],
        x["sp_attainment"]
    ))
    
    return gaps


def _generate_action_recommendation(question: TMMiQuestion, answer: AssessmentAnswer, 
                                  sp_data: Dict, sg_data: Dict) -> str:
    """Generate specific action recommendation for closing a gap"""
    
    if answer.answer == "Not Answered":
        return f"Complete assessment for {question.process_area} - {question.question}"
    
    elif answer.answer == "No":
        if question.importance == "High":
            return f"Implement {question.recommended_activity} - Critical for level {question.level}"
        else:
            return f"Establish {question.recommended_activity}"
    
    elif answer.answer == "Partial":
        if sp_data.get("attainment_percentage", 0) < 50:
            return f"Strengthen implementation of {question.recommended_activity}"
        else:
            return f"Complete implementation of {question.recommended_activity}"
    
    else:
        return "Review and validate current implementation"


def calculate_generic_goal_compliance(questions: List[TMMiQuestion], answers: List[AssessmentAnswer]) -> Dict[str, Dict]:
    """
    Calculate compliance with Generic Goals (GG) for current and target levels
    
    GG2: Managed (Level 2+)
    GG3: Defined (Level 3+)
    GG4: Quantitatively Managed (Level 4+)
    GG5: Optimizing (Level 5)
    """
    generic_goals = {}
    answer_lookup = {ans.question_id: ans for ans in answers}
    
    # Define Generic Goals by level
    gg_by_level = {
        2: "GG2 - Managed",
        3: "GG3 - Defined", 
        4: "GG4 - Quantitatively Managed",
        5: "GG5 - Optimizing"
    }
    
    for level in range(2, 6):
        gg_name = gg_by_level[level]
        level_questions = [q for q in questions if q.level == level and q.generic_goal]
        
        if level_questions:
            total_score = 0.0
            question_count = 0
            evidence_count = 0
            
            for question in level_questions:
                if question.id in answer_lookup:
                    answer = answer_lookup[question.id]
                    score = calculate_answer_score(answer.answer)
                    total_score += score
                    question_count += 1
                    
                    if answer.evidence_url and answer.evidence_url.strip():
                        evidence_count += 1
            
            if question_count > 0:
                attainment_pct = (total_score / question_count) * 100
                generic_goals[gg_name] = {
                    "level": level,
                    "attainment_percentage": attainment_pct,
                    "band": calculate_tmmi_band(attainment_pct),
                    "question_count": question_count,
                    "evidence_count": evidence_count,
                    "evidence_coverage": (evidence_count / question_count) * 100,
                    "status": "Met" if attainment_pct >= 85 else "Not Met"
                }
    
    return generic_goals


def generate_progression_dashboard_data(questions: List[TMMiQuestion], answers: List[AssessmentAnswer]) -> Dict:
    """
    Generate comprehensive data for the progression dashboard
    
    This is the main function that aggregates all progression metrics
    """
    # Basic assessment summary
    basic_summary = generate_assessment_summary(questions, Assessment(
        answers=answers,
        reviewer_name="",
        organization=""
    ))
    
    # Enhanced progression analysis
    next_level_readiness = calculate_next_level_readiness(questions, answers)
    enhanced_gaps = extract_gap_analysis_enhanced(questions, answers)
    generic_goals = calculate_generic_goal_compliance(questions, answers)
    
    # Process area breakdown with bands
    pa_attainment = next_level_readiness["overall_pa_attainment"]
    
    # Evidence coverage by process area
    evidence_coverage_by_pa = {}
    for pa_name, pa_data in pa_attainment.items():
        pa_questions = [q for q in questions if q.process_area == pa_name]
        pa_answers = [a for a in answers if a.question_id in [q.id for q in pa_questions]]
        
        if pa_answers:
            with_evidence = sum(1 for a in pa_answers if a.evidence_url and a.evidence_url.strip())
            evidence_coverage_by_pa[pa_name] = {
                "percentage": (with_evidence / len(pa_answers)) * 100,
                "with_evidence": with_evidence,
                "total_answers": len(pa_answers)
            }
    
    return {
        # Basic metrics
        "current_level": basic_summary["current_level"],
        "overall_compliance": basic_summary["overall_percentage"],
        "total_questions": basic_summary["total_questions"],
        "answered_questions": basic_summary["answered_questions"],
        
        # Next level progression
        "next_level": next_level_readiness["target_level"],
        "next_level_readiness": next_level_readiness["target_level_readiness"],
        "conservative_readiness": next_level_readiness["conservative_readiness"],
        "gating_status": next_level_readiness["gating_status"],
        "gating_reason": next_level_readiness["gating_reason"],
        
        # Process area breakdown
        "process_areas": pa_attainment,
        "target_process_areas": next_level_readiness["target_process_areas"],
        
        # Gap analysis
        "gaps": enhanced_gaps,
        "gap_count": len(enhanced_gaps),
        "high_priority_gaps": [g for g in enhanced_gaps if g["importance"] == "High"],
        
        # Generic goals
        "generic_goals": generic_goals,
        
        # Evidence coverage
        "evidence_coverage": basic_summary["evidence_coverage"],
        "evidence_coverage_by_pa": evidence_coverage_by_pa,
        
        # Risk indicators
        "high_risk_assertions": [
            pa_name for pa_name, pa_data in pa_attainment.items()
            if pa_data["band"] == "F" and 
            evidence_coverage_by_pa.get(pa_name, {}).get("percentage", 0) < 50
        ]
    }
