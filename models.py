"""Pydantic models: they describe what valid data looks like.

FastAPI checks every incoming request against these models and
automatically replies with a 422 error if the data is invalid.
"""

from typing import List

from pydantic import BaseModel, ConfigDict, Field

# Student IDs: letters, numbers, dash and underscore only (e.g. S001).
STUDENT_ID_PATTERN = r"^[A-Za-z0-9_-]+$"


class SubjectCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(min_length=1, max_length=50, examples=["Mathematics"])


class Subject(BaseModel):
    id: int
    name: str


class AssessmentCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    subject_id: int = Field(gt=0, examples=[1])
    title: str = Field(min_length=1, max_length=80, examples=["Mid-term Test"])
    max_score: float = Field(gt=0, le=1000, allow_inf_nan=False, examples=[50])


class Assessment(BaseModel):
    id: int
    subject_id: int
    title: str
    max_score: float


class ScoreCreate(BaseModel):
    student_id: str = Field(
        min_length=1, max_length=20, pattern=STUDENT_ID_PATTERN, examples=["S001"]
    )
    assessment_id: int = Field(gt=0, examples=[1])
    score: float = Field(ge=0, allow_inf_nan=False, examples=[40])


class ScoreUpdate(BaseModel):
    score: float = Field(ge=0, allow_inf_nan=False, examples=[45])


class Score(BaseModel):
    score_id: int
    student_id: str
    assessment_id: int
    score: float


class ResultItem(BaseModel):
    score_id: int
    subject: str
    assessment: str
    score: float
    max_score: float
    percent: float


class StudentResults(BaseModel):
    student_id: str
    results: List[ResultItem]


class SubjectAverage(BaseModel):
    subject: str
    average_percent: float


class StudentAverage(BaseModel):
    student_id: str
    number_of_scores: int
    average_percent: float
    by_subject: List[SubjectAverage]
