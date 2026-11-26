# Sample requests and responses

These were produced by running the API on a fresh server, in this order.
Every request except the home page needs Basic authentication
(username `teacher`, password `change-this-password` from `.env.example`).
The IDs below (1, 2, ...) assume the server was just started, because data is kept in memory.

## 1. Home page (public)

`GET /`  (no login sent)

Response: **200**

```json
{
  "status": "ok",
  "message": "Student Scores API is running. See /docs."
}
```

## 2. Create a subject

`POST /subjects`

Request body:
```json
{
  "name": "Mathematics"
}
```

Response: **201**

```json
{
  "id": 1,
  "name": "Mathematics"
}
```

## 3. Create an assessment

`POST /assessments`

Request body:
```json
{
  "subject_id": 1,
  "title": "Mid-term Test",
  "max_score": 50
}
```

Response: **201**

```json
{
  "id": 1,
  "subject_id": 1,
  "title": "Mid-term Test",
  "max_score": 50.0
}
```

## 4. Create a second assessment

`POST /assessments`

Request body:
```json
{
  "subject_id": 1,
  "title": "Final Exam",
  "max_score": 100
}
```

Response: **201**

```json
{
  "id": 2,
  "subject_id": 1,
  "title": "Final Exam",
  "max_score": 100.0
}
```

## 5. Add a score

`POST /scores`

Request body:
```json
{
  "student_id": "S001",
  "assessment_id": 1,
  "score": 40
}
```

Response: **201**

```json
{
  "score_id": 1,
  "student_id": "S001",
  "assessment_id": 1,
  "score": 40.0
}
```

## 6. Add another score

`POST /scores`

Request body:
```json
{
  "student_id": "S001",
  "assessment_id": 2,
  "score": 90
}
```

Response: **201**

```json
{
  "score_id": 2,
  "student_id": "S001",
  "assessment_id": 2,
  "score": 90.0
}
```

## 7. Update a score

`PUT /scores/1`

Request body:
```json
{
  "score": 45
}
```

Response: **200**

```json
{
  "score_id": 1,
  "student_id": "S001",
  "assessment_id": 1,
  "score": 45.0
}
```

## 8. Get a student's results

`GET /students/S001/results`

Response: **200**

```json
{
  "student_id": "S001",
  "results": [
    {
      "score_id": 1,
      "subject": "Mathematics",
      "assessment": "Mid-term Test",
      "score": 45.0,
      "max_score": 50.0,
      "percent": 90.0
    },
    {
      "score_id": 2,
      "subject": "Mathematics",
      "assessment": "Final Exam",
      "score": 90.0,
      "max_score": 100.0,
      "percent": 90.0
    }
  ]
}
```

## 9. Get a student's average

`GET /students/S001/average`

Response: **200**

```json
{
  "student_id": "S001",
  "number_of_scores": 2,
  "average_percent": 90.0,
  "by_subject": [
    {
      "subject": "Mathematics",
      "average_percent": 90.0
    }
  ]
}
```

# Error examples

## Score above the maximum

`POST /scores`

Request body:
```json
{
  "student_id": "S002",
  "assessment_id": 1,
  "score": 80
}
```

Response: **422**

```json
{
  "detail": "Score cannot be higher than the maximum of 50"
}
```

## Duplicate score for the same assessment

`POST /scores`

Request body:
```json
{
  "student_id": "S001",
  "assessment_id": 1,
  "score": 30
}
```

Response: **409**

```json
{
  "detail": "This student already has a score for this assessment. Use PUT /scores/{score_id} to update it."
}
```

## Unknown student

`GET /students/S999/results`

Response: **404**

```json
{
  "detail": "No results found for student S999"
}
```

## Invalid data (empty subject name)

`POST /subjects`

Request body:
```json
{
  "name": ""
}
```

Response: **422**

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": [
        "body",
        "name"
      ],
      "msg": "String should have at least 1 character",
      "input": "",
      "ctx": {
        "min_length": 1
      }
    }
  ]
}
```

## No login sent

`GET /students/S001/results`  (no login sent)

Response: **401**

```json
{
  "detail": "Not authenticated"
}
```

## Wrong password

`GET /students/S001/results`

Response: **401**

```json
{
  "detail": "Incorrect username or password"
}
```
