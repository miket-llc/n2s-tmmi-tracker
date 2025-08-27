"""
Migration script for TMMi framework compliance

This script updates existing questions with specific goal, specific practice,
and generic goal mappings to enable enhanced progression analysis.
"""

import json
import os
from typing import Dict, List


def load_questions(file_path: str = "data/tmmi_questions.json") -> List[Dict]:
    """Load existing questions from JSON file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Questions file not found: {file_path}")
        return []


def save_questions(questions: List[Dict], file_path: str = "data/tmmi_questions.json"):
    """Save updated questions to JSON file"""
    try:
        # Create backup
        backup_path = file_path.replace('.json', '_backup.json')
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                backup_data = f.read()
            with open(backup_path, 'w') as f:
                f.write(backup_data)
            print(f"Backup created: {backup_path}")
        
        # Save updated questions
        with open(file_path, 'w') as f:
            json.dump(questions, f, indent=2)
        print(f"Questions updated: {file_path}")
        
    except Exception as e:
        print(f"Error saving questions: {e}")


def update_questions_with_tmmi_mapping(questions: List[Dict]) -> List[Dict]:
    """
    Update questions with TMMi framework mapping
    
    Maps questions to:
    - Specific Goals (SG)
    - Specific Practices (SP) 
    - Generic Goals (GG)
    - Practice IDs
    """
    
    # TMMi framework mapping based on official documentation
    tmmi_mapping = {
        # Level 2 Process Areas
        "Test Policy and Strategy": {
            "level": 2,
            "specific_goals": {
                "SG2.1": "Establish Test Policy and Strategy",
                "SG2.2": "Align Testing with Business Objectives"
            },
            "specific_practices": {
                "L2_TPS_001": "SP2.1.1 - Document Test Policy",
                "L2_TPS_002": "SP2.2.1 - Align with Business Objectives"
            },
            "generic_goals": ["GG2.1", "GG2.2"]
        },
        
        "Test Planning": {
            "level": 2,
            "specific_goals": {
                "SG2.3": "Plan Test Activities",
                "SG2.4": "Define Test Entry/Exit Criteria"
            },
            "specific_practices": {
                "L2_TP_001": "SP2.3.1 - Create Test Plans",
                "L2_TP_002": "SP2.4.1 - Define Entry/Exit Criteria"
            },
            "generic_goals": ["GG2.1", "GG2.2"]
        },
        
        "Test Monitoring and Control": {
            "level": 2,
            "specific_goals": {
                "SG2.5": "Monitor Test Progress",
                "SG2.6": "Control Test Activities"
            },
            "specific_practices": {
                "L2_TMC_001": "SP2.5.1 - Monitor Progress",
                "L2_TMC_002": "SP2.6.1 - Take Corrective Actions"
            },
            "generic_goals": ["GG2.1", "GG2.2"]
        },
        
        "Test Design and Execution": {
            "level": 2,
            "specific_goals": {
                "SG2.7": "Design Test Cases",
                "SG2.8": "Execute Test Cases"
            },
            "specific_practices": {
                "L2_TD_001": "SP2.7.1 - Use Test Design Techniques"
            },
            "generic_goals": ["GG2.1", "GG2.2"]
        },
        
        "Test Environment": {
            "level": 2,
            "specific_goals": {
                "SG2.9": "Establish Test Environment"
            },
            "specific_practices": {
                "L2_TE_001": "SP2.9.1 - Set Up Test Environment"
            },
            "generic_goals": ["GG2.1", "GG2.2"]
        },
        
        # Level 3 Process Areas
        "Test Lifecycle Integration": {
            "level": 3,
            "specific_goals": {
                "SG3.1": "Integrate Testing in SDLC"
            },
            "specific_practices": {
                "L3_TLI_001": "SP3.1.1 - Integrate Throughout SDLC"
            },
            "generic_goals": ["GG3.1", "GG3.2", "GG3.3"]
        },
        
        "Peer Reviews": {
            "level": 3,
            "specific_goals": {
                "SG3.2": "Perform Peer Reviews"
            },
            "specific_practices": {
                "L3_PR_001": "SP3.2.1 - Conduct Peer Reviews"
            },
            "generic_goals": ["GG3.1", "GG3.2", "GG3.3"]
        },
        
        "Non-functional Testing": {
            "level": 3,
            "specific_goals": {
                "SG3.3": "Test Non-functional Requirements"
            },
            "specific_practices": {
                "L3_NFTR_001": "SP3.3.1 - Test Non-functional Requirements"
            },
            "generic_goals": ["GG3.1", "GG3.2", "GG3.3"]
        },
        
        "Test Training": {
            "level": 3,
            "specific_goals": {
                "SG3.4": "Provide Test Training"
            },
            "specific_practices": {
                "L3_TTO_001": "SP3.4.1 - Train Test Personnel"
            },
            "generic_goals": ["GG3.1", "GG3.2", "GG3.3"]
        },
        
        # Level 4 Process Areas
        "Test Measurement": {
            "level": 4,
            "specific_goals": {
                "SG4.1": "Collect Test Metrics",
                "SG4.2": "Analyze Test Data"
            },
            "specific_practices": {
                "L4_TM_001": "SP4.1.1 - Collect Process Metrics",
                "L4_TM_002": "SP4.2.1 - Establish Quality Goals"
            },
            "generic_goals": ["GG4.1", "GG4.2", "GG4.3", "GG4.4"]
        },
        
        "Software Quality Control": {
            "level": 4,
            "specific_goals": {
                "SG4.3": "Apply Statistical Process Control"
            },
            "specific_practices": {
                "L4_SPC_001": "SP4.3.1 - Use SPC Techniques"
            },
            "generic_goals": ["GG4.1", "GG4.2", "GG4.3", "GG4.4"]
        },
        
        "Quality Evaluation": {
            "level": 4,
            "specific_goals": {
                "SG4.4": "Evaluate Product Quality"
            },
            "specific_practices": {
                "L4_QE_001": "SP4.4.1 - Use Quantitative Measures"
            },
            "generic_goals": ["GG4.1", "GG4.2", "GG4.3", "GG4.4"]
        },
        
        # Level 5 Process Areas
        "Test Process Improvement": {
            "level": 5,
            "specific_goals": {
                "SG5.1": "Improve Test Processes"
            },
            "specific_practices": {
                "L5_TPI_001": "SP5.1.1 - Continuous Improvement"
            },
            "generic_goals": ["GG5.1", "GG5.2", "GG5.3", "GG5.4", "GG5.5"]
        },
        
        "Quality Control": {
            "level": 5,
            "specific_goals": {
                "SG5.2": "Implement Defect Prevention"
            },
            "specific_practices": {
                "L5_QC_001": "SP5.2.1 - Defect Prevention Activities"
            },
            "generic_goals": ["GG5.1", "GG5.2", "GG5.3", "GG5.4", "GG5.5"]
        },
        
        "Test Automation": {
            "level": 5,
            "specific_goals": {
                "SG5.3": "Optimize Test Automation"
            },
            "specific_practices": {
                "L5_TA_001": "SP5.3.1 - Optimize Automation"
            },
            "generic_goals": ["GG5.1", "GG5.2", "GG5.3", "GG5.4", "GG5.5"]
        },
        
        "Test Optimization": {
            "level": 5,
            "specific_goals": {
                "SG5.4": "Optimize Testing Activities"
            },
            "specific_practices": {
                "L5_TO_001": "SP5.4.1 - Advanced Techniques"
            },
            "generic_goals": ["GG5.1", "GG5.2", "GG5.3", "GG5.4", "GG5.5"]
        }
    }
    
    updated_questions = []
    
    for question in questions:
        updated_question = question.copy()
        process_area = question.get("process_area", "")
        
        if process_area in tmmi_mapping:
            mapping = tmmi_mapping[process_area]
            
            # Add new fields
            updated_question["specific_goal"] = None
            updated_question["specific_practice"] = None
            updated_question["generic_goal"] = None
            updated_question["practice_id"] = None
            
            # Map specific practice if question ID matches
            question_id = question.get("id", "")
            if question_id in mapping["specific_practices"]:
                updated_question["specific_practice"] = mapping["specific_practices"][question_id]
                # Extract SG from SP mapping
                for sg_id, sg_name in mapping["specific_goals"].items():
                    if sg_id in mapping["specific_practices"][question_id]:
                        updated_question["specific_goal"] = f"{sg_id}: {sg_name}"
                        break
            
            # Add generic goals
            if mapping["generic_goals"]:
                updated_question["generic_goal"] = ", ".join(mapping["generic_goals"])
            
            # Add practice ID
            if question_id in mapping["specific_practices"]:
                updated_question["practice_id"] = question_id
        
        updated_questions.append(updated_question)
    
    return updated_questions


def main():
    """Main migration function"""
    print("Starting TMMi framework migration...")
    
    # Load existing questions
    questions = load_questions()
    if not questions:
        print("No questions found to migrate.")
        return
    
    print(f"Loaded {len(questions)} questions for migration.")
    
    # Update questions with TMMi mapping
    updated_questions = update_questions_with_tmmi_mapping(questions)
    
    # Save updated questions
    save_questions(updated_questions)
    
    print("Migration completed successfully!")
    
    # Print summary
    mapped_count = sum(1 for q in updated_questions if q.get("specific_practice"))
    print(f"Questions mapped to specific practices: {mapped_count}/{len(updated_questions)}")
    
    # Show sample of mapped questions
    print("\nSample mapped questions:")
    for i, q in enumerate(updated_questions[:3]):
        if q.get("specific_practice"):
            print(f"  {q['id']}: {q['specific_practice']}")


if __name__ == "__main__":
    main()
