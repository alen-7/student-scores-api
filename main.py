"""Student Scores API (Module B4).

Manage subjects, assessments and student scores.
Run it with:  uvicorn main:app --reload
Then open:    http://127.0.0.1:8000/docs
"""

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Path

import store
from auth import verify_credentials
from models import (
    STUDENT_ID_PATTERN,
    Assessment,
    AssessmentCreate,
    Score,
    ScoreCreate,
    ScoreUpdate,
    StudentAverage,
    StudentResults,
    Subject,
    SubjectCreate,
)

load_dotenv()  # reads API_USERNAME and API_PASSWORD from the .env file

app = FastAPI(
    title="Student Scores API",
    description="Manage subjects, assessments and student scores. "
    "All endpoints except the home page need a username and password.",
    version="1.0.0",
)

# Every endpoint added to this router requires a valid login.
router = APIRouter(dependencies=[Depends(verify_credentials)])

StudentIdPath = Path(min_length=1, max_length=20, pattern=STUDENT_ID_PATTERN)


@app.get("/", tags=["Home"])
def home():
    """Public check that the server is running. Returns no student data."""
    return {"status": "ok", "message": "Student Scores API is running. See /docs."}


# ---------- Subjects ----------


@router.post("/subjects", response_model=Subject, status_code=201, tags=["Subjects"])
def create_subject(subject: SubjectCreate):
    for existing in store.subjects.values():
        if existing["name"].lower() == subject.name.lower():
            raise HTTPException(409, f"Subject '{subject.name}' already exists")
    subject_id = store.next_id("subject")
    record = {"id": subject_id, "name": subject.name}
    store.subjects[subject_id] = record
    return record


@router.get("/subjects", response_model=list[Subject], tags=["Subjects"])
def list_subjects():
    return list(store.subjects.values())


# ---------- Assessments ----------


@router.post(
    "/assessments", response_model=Assessment, status_code=201, tags=["Assessments"]
)
def create_assessment(assessment: AssessmentCreate):
    if assessment.subject_id not in store.subjects:
        raise HTTPException(404, f"Subject {assessment.subject_id} not found")
    assessment_id = store.next_id("assessment")
    record = {
        "id": assessment_id,
        "subject_id": assessment.subject_id,
        "title": assessment.title,
        "max_score": assessment.max_score,
    }
    store.assessments[assessment_id] = record
    return record


@router.get("/assessments", response_model=list[Assessment], tags=["Assessments"])
def list_assessments():
    return list(store.assessments.values())


# ---------- Scores ----------


@router.post("/scores", response_model=Score, status_code=201, tags=["Scores"])
def add_score(new_score: ScoreCreate):
    assessment = store.assessments.get(new_score.assessment_id)
    if assessment is None:
        raise HTTPException(404, f"Assessment {new_score.assessment_id} not found")
    if new_score.score > assessment["max_score"]:
        raise HTTPException(
            422,
            f"Score cannot be higher than the maximum of {assessment['max_score']:g}",
        )
    for existing in store.scores.values():
        if (
            existing["student_id"] == new_score.student_id
            and existing["assessment_id"] == new_score.assessment_id
        ):
            raise HTTPException(
                409,
                "This student already has a score for this assessment. "
                "Use PUT /scores/{score_id} to update it.",
            )
    score_id = store.next_id("score")
    record = {
        "score_id": score_id,
        "student_id": new_score.student_id,
        "assessment_id": new_score.assessment_id,
        "score": new_score.score,
    }
    store.scores[score_id] = record
    return record


@router.put("/scores/{score_id}", response_model=Score, tags=["Scores"])
def update_score(score_id: int, update: ScoreUpdate):
    record = store.scores.get(score_id)
    if record is None:
        raise HTTPException(404, f"Score {score_id} not found")
    assessment = store.assessments[record["assessment_id"]]
    if update.score > assessment["max_score"]:
        raise HTTPException(
            422,
            f"Score cannot be higher than the maximum of {assessment['max_score']:g}",
        )
    record["score"] = update.score
    return record


# ---------- Student results and averages ----------


def _results_for(student_id):
    """Build a readable list of one student's results."""
    results = []
    for record in store.scores.values():
        if record["student_id"] != student_id:
            continue
        assessment = store.assessments[record["assessment_id"]]
        subject = store.subjects[assessment["subject_id"]]
        results.append(
            {
                "score_id": record["score_id"],
                "subject": subject["name"],
                "assessment": assessment["title"],
                "score": record["score"],
                "max_score": assessment["max_score"],
                "percent": round(record["score"] / assessment["max_score"] * 100, 1),
            }
        )
    return results


@router.get(
    "/students/{student_id}/results", response_model=StudentResults, tags=["Students"]
)
def get_results(student_id: str = StudentIdPath):
    results = _results_for(student_id)
    if not results:
        raise HTTPException(404, f"No results found for student {student_id}")
    return {"student_id": student_id, "results": results}


@router.get(
    "/students/{student_id}/average", response_model=StudentAverage, tags=["Students"]
)
def get_average(student_id: str = StudentIdPath):
    results = _results_for(student_id)
    if not results:
        raise HTTPException(404, f"No results found for student {student_id}")

    overall = sum(r["percent"] for r in results) / len(results)

    percents_by_subject = {}
    for r in results:
        percents_by_subject.setdefault(r["subject"], []).append(r["percent"])
    by_subject = [
        {"subject": name, "average_percent": round(sum(p) / len(p), 1)}
        for name, p in percents_by_subject.items()
    ]
    return {
        "student_id": student_id,
        "number_of_scores": len(results),
        "average_percent": round(overall, 1),
        "by_subject": by_subject,
    }


app.include_router(router)
