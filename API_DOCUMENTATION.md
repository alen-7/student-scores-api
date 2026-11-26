# API documentation

Base URL when running locally: `http://127.0.0.1:8000`

FastAPI also builds interactive documentation automatically:
- Swagger UI: `http://127.0.0.1:8000/docs` (click **Authorize** to log in, then **Try it out**)
- ReDoc: `http://127.0.0.1:8000/redoc`

## Authentication
Every endpoint except `GET /` needs **HTTP Basic authentication**: a username
and password sent with each request. The correct values are set in the `.env`
file (`API_USERNAME`, `API_PASSWORD`). Without valid details the API replies
`401 Unauthorized`.

## Endpoints

| Method | Path | Purpose | Success |
|--------|------|---------|---------|
| GET | `/` | Check the server is running (public) | 200 |
| POST | `/subjects` | Create a subject | 201 |
| GET | `/subjects` | List subjects | 200 |
| POST | `/assessments` | Create an assessment for a subject | 201 |
| GET | `/assessments` | List assessments | 200 |
| POST | `/scores` | Add a student's score | 201 |
| PUT | `/scores/{score_id}` | Update a result | 200 |
| GET | `/students/{student_id}/results` | Retrieve a student's results | 200 |
| GET | `/students/{student_id}/average` | Calculate a student's average | 200 |

## Request bodies

**Create subject**: `{"name": "Mathematics"}`
- `name`: text, 1 to 50 characters (spaces at the ends are removed)

**Create assessment**: `{"subject_id": 1, "title": "Mid-term Test", "max_score": 50}`
- `subject_id`: must be an existing subject
- `title`: text, 1 to 80 characters
- `max_score`: number above 0, up to 1000

**Add score**: `{"student_id": "S001", "assessment_id": 1, "score": 40}`
- `student_id`: 1 to 20 characters: letters, numbers, `-` and `_` only
- `assessment_id`: must be an existing assessment
- `score`: number from 0 up to the assessment's `max_score`

**Update score**: `{"score": 45}`, same rule for `score`.

## How averages are calculated
Each score is turned into a percentage (`score / max_score x 100`). The overall
average is the mean of those percentages, and the average is also given for
each subject. Percentages make scores out of different maximums comparable.

## Status codes

| Code | Meaning | When it happens |
|------|---------|-----------------|
| 200 | OK | A read or update worked |
| 201 | Created | A subject, assessment or score was created |
| 401 | Unauthorized | Login missing or wrong |
| 404 | Not found | Unknown subject, assessment, score or student |
| 409 | Conflict | Duplicate subject name, or a second score for the same student and assessment |
| 422 | Unprocessable | Invalid data: wrong type, empty name, score below 0 or above the maximum, bad student ID |
| 500 | Server error | Server login is not configured (`.env` missing) |

Errors always come back as JSON with a `detail` message, for example:
```json
{"detail": "Score cannot be higher than the maximum of 50"}
```
Real examples are in [SAMPLE_REQUESTS.md](SAMPLE_REQUESTS.md).
