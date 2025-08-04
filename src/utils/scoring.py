"""
Scoring logic for TMMi assessment calculations
"""
from typing import List, Dict, Tuple, Set
from src.models.database import TMMiQuestion, AssessmentAnswer, Assessment


def calculate_answer_score(answer: str) -> float:
    """Convert answer to numeric score"""
    score_map = {
        'Yes': 1.0,
        'Partial': 0.5,
        'No': 0.0
    }
    return score_map.get(answer, 0.0)


def calculate_level_compliance(questions: List[TMMiQuestion],
                               answers: List[AssessmentAnswer]) -> Dict[int, Dict]:
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
                
                if answer.answer == 'Yes':
                    yes_count += 1
                elif answer.answer == 'Partial':
                    partial_count += 1
                else:
                    no_count += 1
        
        compliance_percentage = (total_score / max_score * 100) if max_score > 0 else 0
        
        level_compliance[level] = {
            'compliance_percentage': compliance_percentage,
            'total_questions': len(level_questions),
            'answered_questions': answered_questions,
            'yes_count': yes_count,
            'partial_count': partial_count,
            'no_count': no_count,
            'total_score': total_score,
            'max_score': max_score
        }
    
    return level_compliance


def calculate_process_area_compliance(questions: List[TMMiQuestion], 
                                      answers: List[AssessmentAnswer]) -> Dict[str, Dict]:
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
                
                if answer.answer == 'Yes':
                    yes_count += 1
                elif answer.answer == 'Partial':
                    partial_count += 1
                else:
                    no_count += 1
        
        compliance_percentage = (total_score / max_score * 100) if max_score > 0 else 0
        
        area_compliance[area] = {
            'compliance_percentage': compliance_percentage,
            'total_questions': len(area_questions),
            'answered_questions': answered_questions,
            'yes_count': yes_count,
            'partial_count': partial_count,
            'no_count': no_count,
            'total_score': total_score,
            'max_score': max_score
        }
    
    return area_compliance


def determine_current_tmmi_level(level_compliance: Dict[int, Dict], 
                                 threshold: float = 80.0) -> Tuple[int, str]:
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
            compliance = level_compliance[level]['compliance_percentage']
            
            # Check if this level meets threshold
            if compliance >= threshold:
                # Check if all lower levels also meet threshold
                lower_levels_compliant = True
                for lower_level in range(2, level):
                    if lower_level in level_compliance:
                        if level_compliance[lower_level]['compliance_percentage'] < threshold:
                            lower_levels_compliant = False
                            break
                
                if lower_levels_compliant:
                    current_level = level
                    level_names = {
                        2: "Managed",
                        3: "Defined", 
                        4: "Measured",
                        5: "Optimized"
                    }
                    explanation = f"Level {level} ({level_names[level]}) - {compliance:.1f}% compliance"
    
    return current_level, explanation


def get_gap_analysis(questions: List[TMMiQuestion], 
                     answers: List[AssessmentAnswer]) -> List[Dict]:
    """Generate gap analysis for improvement recommendations"""
    # Create answer lookup
    answer_lookup = {ans.question_id: ans for ans in answers}
    
    gaps = []
    
    for question in questions:
        if question.id in answer_lookup:
            answer = answer_lookup[question.id]
            
            # Include gaps for 'No' and 'Partial' answers
            if answer.answer in ['No', 'Partial']:
                gaps.append({
                    'question_id': question.id,
                    'level': question.level,
                    'process_area': question.process_area,
                    'question': question.question,
                    'current_answer': answer.answer,
                    'importance': question.importance,
                    'recommended_activity': question.recommended_activity,
                    'reference_url': question.reference_url,
                    'evidence_url': answer.evidence_url,
                    'comment': answer.comment
                })
        else:
            # Unanswered questions are also gaps
            gaps.append({
                'question_id': question.id,
                'level': question.level,
                'process_area': question.process_area,
                'question': question.question,
                'current_answer': 'Not Answered',
                'importance': question.importance,
                'recommended_activity': question.recommended_activity,
                'reference_url': question.reference_url,
                'evidence_url': None,
                'comment': None
            })
    
    # Sort by importance and level
    importance_order = {'High': 0, 'Medium': 1, 'Low': 2}
    gaps.sort(key=lambda x: (importance_order.get(x['importance'], 3), x['level']))
    
    return gaps


def calculate_evidence_coverage(answers: List[AssessmentAnswer]) -> Dict[str, float]:
    """Calculate percentage of answers that have evidence provided"""
    
    total_answers = len(answers)
    if total_answers == 0:
        return {'percentage': 0.0, 'with_evidence': 0, 'total_answers': 0}
    
    with_evidence = sum(1 for answer in answers if answer.evidence_url and answer.evidence_url.strip())
    percentage = (with_evidence / total_answers) * 100
    
    return {
        'percentage': percentage,
        'with_evidence': with_evidence,
        'total_answers': total_answers
    }


def generate_assessment_summary(questions: List[TMMiQuestion], 
                                assessment: Assessment) -> Dict:
    """Generate comprehensive assessment summary"""
    
    level_compliance = calculate_level_compliance(questions, assessment.answers)
    process_area_compliance = calculate_process_area_compliance(questions, assessment.answers)
    current_level, level_explanation = determine_current_tmmi_level(level_compliance)
    gaps = get_gap_analysis(questions, assessment.answers)
    evidence_coverage = calculate_evidence_coverage(assessment.answers)
    
    # Overall statistics
    total_questions = len(questions)
    answered_questions = len(assessment.answers)
    yes_answers = sum(1 for ans in assessment.answers if ans.answer == 'Yes')
    partial_answers = sum(1 for ans in assessment.answers if ans.answer == 'Partial')
    no_answers = sum(1 for ans in assessment.answers if ans.answer == 'No')
    
    overall_score = sum(calculate_answer_score(ans.answer) for ans in assessment.answers)
    overall_percentage = (overall_score / total_questions * 100) if total_questions > 0 else 0
    
    return {
        'assessment_id': assessment.id,
        'timestamp': assessment.timestamp,
        'reviewer_name': assessment.reviewer_name,
        'organization': assessment.organization,
        'current_level': current_level,
        'level_explanation': level_explanation,
        'overall_percentage': overall_percentage,
        'total_questions': total_questions,
        'answered_questions': answered_questions,
        'yes_answers': yes_answers,
        'partial_answers': partial_answers,
        'no_answers': no_answers,
        'level_compliance': level_compliance,
        'process_area_compliance': process_area_compliance,
        'gaps': gaps,
        'evidence_coverage': evidence_coverage,
        'high_priority_gaps': [gap for gap in gaps if gap['importance'] == 'High'],
        'medium_priority_gaps': [gap for gap in gaps if gap['importance'] == 'Medium'],
        'low_priority_gaps': [gap for gap in gaps if gap['importance'] == 'Low']
    }
