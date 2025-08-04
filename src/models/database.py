"""
Database models and schema for TMMi Assessment Tracker
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
import os


@dataclass
class TMMiQuestion:
    """Data model for TMMi assessment questions"""
    id: str
    level: int
    process_area: str
    question: str
    importance: str
    recommended_activity: str
    reference_url: str


@dataclass
class AssessmentAnswer:
    """Data model for individual question answers"""
    question_id: str
    answer: str  # 'Yes', 'No', 'Partial'
    evidence_url: Optional[str] = None
    comment: Optional[str] = None


@dataclass
class Assessment:
    """Data model for complete assessment"""
    id: Optional[int] = None
    timestamp: Optional[str] = None
    reviewer_name: str = ""
    organization: str = ""
    answers: List[AssessmentAnswer] = None

    def __post_init__(self):
        if self.answers is None:
            self.answers = []
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class TMMiDatabase:
    """Database manager for TMMi assessments"""

    def __init__(self, db_path: str = "data/assessments.db"):
        self.db_path = db_path
        self.ensure_db_directory()
        self.init_database()

    def ensure_db_directory(self):
        """Ensure the data directory exists"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create assessments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS assessments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    reviewer_name TEXT NOT NULL,
                    organization TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create assessment_answers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS assessment_answers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    assessment_id INTEGER NOT NULL,
                    question_id TEXT NOT NULL,
                    answer TEXT NOT NULL CHECK (answer IN ('Yes', 'No',
                                                       'Partial')),
                    evidence_url TEXT,
                    comment TEXT,
                    FOREIGN KEY (assessment_id) REFERENCES assessments (id)
                )
            """)

            # Create organizations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS organizations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    contact_person TEXT,
                    email TEXT,
                    status TEXT DEFAULT 'Active' CHECK (status IN ('Active',
                                                          'Inactive')),
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

    def save_assessment(self, assessment: Assessment) -> int:
        """Save a complete assessment to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Insert assessment record
            cursor.execute("""
                INSERT INTO assessments (timestamp, reviewer_name,
                                         organization)
                VALUES (?, ?, ?)
            """, (assessment.timestamp, assessment.reviewer_name,
                  assessment.organization))

            assessment_id = cursor.lastrowid

            # Insert all answers
            for answer in assessment.answers:
                cursor.execute("""
                    INSERT INTO assessment_answers
                    (assessment_id, question_id, answer, evidence_url,
                     comment)
                    VALUES (?, ?, ?, ?, ?)
                """, (assessment_id, answer.question_id, answer.answer,
                      answer.evidence_url, answer.comment))

            conn.commit()
            return assessment_id

    def get_assessments(self) -> List[Assessment]:
        """Retrieve all assessments from the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get all assessments
            cursor.execute("""
                SELECT id, timestamp, reviewer_name, organization
                FROM assessments
                ORDER BY timestamp DESC
            """)

            assessments = []
            for row in cursor.fetchall():
                assessment_id, timestamp, reviewer_name, organization = row

                # Get answers for this assessment
                cursor.execute("""
                    SELECT question_id, answer, evidence_url, comment
                    FROM assessment_answers
                    WHERE assessment_id = ?
                """, (assessment_id,))

                answers = [
                    AssessmentAnswer(
                        question_id=answer_row[0],
                        answer=answer_row[1],
                        evidence_url=answer_row[2],
                        comment=answer_row[3]
                    )
                    for answer_row in cursor.fetchall()
                ]

                assessments.append(Assessment(
                    id=assessment_id,
                    timestamp=timestamp,
                    reviewer_name=reviewer_name,
                    organization=organization,
                    answers=answers
                ))

            return assessments

    def get_latest_assessment(self) -> Optional[Assessment]:
        """Get the most recent assessment"""
        assessments = self.get_assessments()
        return assessments[0] if assessments else None

    def get_assessment_history(self) -> List[Dict]:
        """Get assessment history for trend analysis"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    a.timestamp,
                    a.reviewer_name,
                    a.organization,
                    COUNT(CASE WHEN aa.answer = 'Yes' THEN 1 END)
                        as yes_count,
                    COUNT(CASE WHEN aa.answer = 'Partial' THEN 1 END)
                        as partial_count,
                    COUNT(CASE WHEN aa.answer = 'No' THEN 1 END)
                        as no_count,
                    COUNT(*) as total_questions
                FROM assessments a
                LEFT JOIN assessment_answers aa ON a.id = aa.assessment_id
                GROUP BY a.id
                ORDER BY a.timestamp
            """)

            history = []
            for row in cursor.fetchall():
                (timestamp, reviewer, org, yes_count, partial_count,
                 no_count, total) = row
                history.append({
                    'timestamp': timestamp,
                    'reviewer_name': reviewer,
                    'organization': org,
                    'yes_count': yes_count or 0,
                    'partial_count': partial_count or 0,
                    'no_count': no_count or 0,
                    'total_questions': total or 0,
                    'compliance_percentage': (yes_count / total * 100
                                              if total > 0 else 0)
                })

            return history

    def update_assessment_entry(self, entry_id: int, updated_data: dict):
        """Update assessment entry with new data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Update main assessment data
            if any(key in updated_data
                   for key in ['reviewer_name', 'organization']):
                cursor.execute("""
                    UPDATE assessments
                    SET reviewer_name = COALESCE(?, reviewer_name),
                        organization = COALESCE(?, organization)
                    WHERE id = ?
                """, (
                    updated_data.get('reviewer_name'),
                    updated_data.get('organization'),
                    entry_id
                ))

            conn.commit()

    def get_assessments_for_editing(self) -> List[Dict]:
        """Get assessments in a format suitable for data editor"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    a.id,
                    a.timestamp,
                    a.reviewer_name,
                    a.organization,
                    COUNT(aa.id) as answer_count,
                    COUNT(CASE WHEN aa.answer = 'Yes' THEN 1 END)
                        as yes_count,
                    COUNT(CASE WHEN aa.answer = 'Partial' THEN 1 END)
                        as partial_count,
                    COUNT(CASE WHEN aa.answer = 'No' THEN 1 END)
                        as no_count
                FROM assessments a
                LEFT JOIN assessment_answers aa ON a.id = aa.assessment_id
                GROUP BY a.id
                ORDER BY a.timestamp DESC
            """)

            assessments = []
            for row in cursor.fetchall():
                id_val, timestamp, reviewer, org, total, yes, partial, no = row
                compliance = (yes / total * 100) if total > 0 else 0

                assessments.append({
                    'ID': id_val,
                    'Date': timestamp.split('T')[0] if timestamp else '',
                    'Reviewer': reviewer,
                    'Organization': org,
                    'Total Questions': total,
                    'Yes': yes or 0,
                    'Partial': partial or 0,
                    'No': no or 0,
                    'Compliance %': round(compliance, 1)
                })

            return assessments

    def delete_assessment(self, assessment_id: int):
        """Delete an assessment and all its answers"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Delete answers first (foreign key constraint)
            cursor.execute(
                "DELETE FROM assessment_answers WHERE assessment_id = ?",
                (assessment_id,))

            # Delete assessment
            cursor.execute("DELETE FROM assessments WHERE id = ?",
                           (assessment_id,))

            conn.commit()

    # Organization management methods
    def get_organizations(self) -> List[dict]:
        """Retrieve all organizations"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, name, contact_person, email, status,
                       created_at, updated_at
                FROM organizations
                ORDER BY name
            """)

            organizations = []
            for row in cursor.fetchall():
                organizations.append({
                    'id': row[0],
                    'name': row[1],
                    'contact_person': row[2],
                    'email': row[3],
                    'status': row[4],
                    'created_at': row[5],
                    'updated_at': row[6]
                })

            return organizations

    def update_organization(self, org_id: int, updated_fields: dict):
        """Update organization with new field values"""
        if not updated_fields:
            return

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Build dynamic update query
            set_clauses = []
            values = []

            for field, value in updated_fields.items():
                if field in ['name', 'contact_person', 'email', 'status']:
                    set_clauses.append(f"{field} = ?")
                    values.append(value)

            if set_clauses:
                set_clauses.append("updated_at = CURRENT_TIMESTAMP")
                values.append(org_id)

                query = (f"UPDATE organizations SET {', '.join(set_clauses)} "
                         f"WHERE id = ?")
                cursor.execute(query, values)
                conn.commit()

    def add_organization(self, new_org_data: dict):
        """Add a new organization"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO organizations (name, contact_person, email, status)
                VALUES (?, ?, ?, ?)
            """, (
                new_org_data.get('name', ''),
                new_org_data.get('contact_person', ''),
                new_org_data.get('email', ''),
                new_org_data.get('status', 'Active')
            ))

            conn.commit()
            return cursor.lastrowid

    def delete_organization(self, org_id: int):
        """Delete an organization"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM organizations WHERE id = ?", (org_id,))
            conn.commit()

    def get_latest_assessment_by_organization(self,
                                              organization_name: str
                                              ) -> Optional[Assessment]:
        """Get the most recent assessment for a specific
        organization"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get the latest assessment for the organization
            cursor.execute("""
                SELECT id, timestamp, reviewer_name, organization
                FROM assessments
                WHERE LOWER(organization) = LOWER(?)
                ORDER BY timestamp DESC
                LIMIT 1
            """, (organization_name,))

            row = cursor.fetchone()
            if not row:
                return None

            assessment_id, timestamp, reviewer_name, organization = row

            # Get answers for this assessment
            cursor.execute("""
                SELECT question_id, answer, evidence_url, comment
                FROM assessment_answers
                WHERE assessment_id = ?
            """, (assessment_id,))

            answers = [
                AssessmentAnswer(
                    question_id=answer_row[0],
                    answer=answer_row[1],
                    evidence_url=answer_row[2],
                    comment=answer_row[3]
                )
                for answer_row in cursor.fetchall()
            ]

            return Assessment(
                id=assessment_id,
                timestamp=timestamp,
                reviewer_name=reviewer_name,
                organization=organization,
                answers=answers
            )

    def get_organizations_for_assessment(self) -> List[dict]:
        """Get organizations suitable for assessment selection"""
        organizations = self.get_organizations()

        # Add assessment count for each organization
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            enhanced_orgs = []
            for org in organizations:
                # Count assessments for this organization
                cursor.execute("""
                    SELECT COUNT(*) FROM assessments
                    WHERE LOWER(organization) = LOWER(?)
                """, (org['name'],))

                assessment_count = cursor.fetchone()[0]

                # Get latest assessment date
                cursor.execute("""
                    SELECT MAX(timestamp) FROM assessments
                    WHERE LOWER(organization) = LOWER(?)
                """, (org['name'],))

                latest_date = cursor.fetchone()[0]

                enhanced_orgs.append({
                    **org,
                    'assessment_count': assessment_count,
                    'latest_assessment': (latest_date.split('T')[0]
                                          if latest_date else 'Never')
                })

            return enhanced_orgs

    def get_assessments_by_org(self, org_id: int) -> List[dict]:
        """Get all assessments for a specific organization"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # First get the organization name
            cursor.execute("SELECT name FROM organizations WHERE id = ?", (org_id,))
            org_result = cursor.fetchone()
            if not org_result:
                return []
            
            org_name = org_result[0]

            # Get all assessments for this organization
            cursor.execute("""
                SELECT 
                    a.id,
                    a.timestamp,
                    a.reviewer_name,
                    a.organization,
                    COUNT(aa.id) as total_answers,
                    COUNT(CASE WHEN aa.answer = 'Yes' THEN 1 END) as yes_count,
                    COUNT(CASE WHEN aa.answer = 'Partial' THEN 1 END) as partial_count,
                    COUNT(CASE WHEN aa.answer = 'No' THEN 1 END) as no_count
                FROM assessments a
                LEFT JOIN assessment_answers aa ON a.id = aa.assessment_id
                WHERE LOWER(a.organization) = LOWER(?)
                GROUP BY a.id
                ORDER BY a.timestamp ASC
            """, (org_name,))

            assessments = []
            for row in cursor.fetchall():
                assessment_id, timestamp, reviewer, org, total, yes, partial, no = row
                
                # Calculate compliance percentage and maturity level
                compliance_pct = (yes / total * 100) if total > 0 else 0
                
                # Determine maturity level based on compliance (simplified logic)
                if compliance_pct >= 90:
                    maturity_level = 5
                elif compliance_pct >= 80:
                    maturity_level = 4
                elif compliance_pct >= 60:
                    maturity_level = 3
                elif compliance_pct >= 40:
                    maturity_level = 2
                else:
                    maturity_level = 1

                assessments.append({
                    'assessment_id': assessment_id,
                    'timestamp': timestamp,
                    'reviewer_name': reviewer,
                    'organization': org,
                    'total_answers': total,
                    'yes_count': yes or 0,
                    'partial_count': partial or 0,
                    'no_count': no or 0,
                    'compliance_percentage': compliance_pct,
                    'maturity_level': maturity_level
                })

            return assessments

    def get_tmmi_scores_by_assessment(self, assessment_id: int) -> dict:
        """Get detailed TMMi scores and process area breakdown for an assessment"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get assessment details
            cursor.execute("""
                SELECT timestamp, reviewer_name, organization
                FROM assessments WHERE id = ?
            """, (assessment_id,))
            
            assessment_row = cursor.fetchone()
            if not assessment_row:
                return {}

            timestamp, reviewer, organization = assessment_row

            # Get all answers for this assessment
            cursor.execute("""
                SELECT question_id, answer, evidence_url, comment
                FROM assessment_answers
                WHERE assessment_id = ?
            """, (assessment_id,))

            answers = {}
            for row in cursor.fetchall():
                question_id, answer, evidence_url, comment = row
                answers[question_id] = {
                    'answer': answer,
                    'evidence_url': evidence_url,
                    'comment': comment
                }

            return {
                'assessment_id': assessment_id,
                'timestamp': timestamp,
                'reviewer_name': reviewer,
                'organization': organization,
                'answers': answers
            }


def load_tmmi_questions(file_path: str = "data/tmmi_questions.json"
                        ) -> List[TMMiQuestion]:
    """Load TMMi questions from JSON file"""
    try:
        with open(file_path, 'r') as f:
            questions_data = json.load(f)

        return [TMMiQuestion(**q) for q in questions_data]
    except FileNotFoundError:
        print(f"Questions file not found: {file_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing questions file: {e}")
        return []


def get_questions_by_level(questions: List[TMMiQuestion]
                           ) -> Dict[int, List[TMMiQuestion]]:
    """Group questions by TMMi level"""
    questions_by_level = {}
    for question in questions:
        if question.level not in questions_by_level:
            questions_by_level[question.level] = []
        questions_by_level[question.level].append(question)
    return questions_by_level


def get_questions_by_process_area(questions: List[TMMiQuestion]
                                  ) -> Dict[str, List[TMMiQuestion]]:
    """Group questions by process area"""
    questions_by_area = {}
    for question in questions:
        if question.process_area not in questions_by_area:
            questions_by_area[question.process_area] = []
        questions_by_area[question.process_area].append(question)
    return questions_by_area
