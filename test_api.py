from fastapi.testclient import TestClient

from main import app

client = TestClient(app)
AUTH = ("teacher", "test-password")


def make_subject(name="Mathematics"):
    return client.post("/subjects", json={"name": name}, auth=AUTH).json()


def make_assessment(subject_id, title="Mid-term Test", max_score=50):
    body = {"subject_id": subject_id, "title": title, "max_score": max_score}
    return client.post("/assessments", json=body, auth=AUTH).json()


def add_score(student_id, assessment_id, score):
    body = {"student_id": student_id, "assessment_id": assessment_id, "score": score}
    return client.post("/scores", json=body, auth=AUTH)


# ----- home and authentication -----


def test_home_is_public():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_missing_login_is_rejected():
    assert client.get("/subjects").status_code == 401


def test_wrong_password_is_rejected():
    response = client.get("/subjects", auth=("teacher", "wrong"))
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


def test_wrong_username_is_rejected():
    assert client.get("/subjects", auth=("someone", "test-password")).status_code == 401


# ----- subjects and assessments -----


def test_create_subject():
    response = client.post("/subjects", json={"name": "  Mathematics "}, auth=AUTH)
    assert response.status_code == 201
    assert response.json() == {"id": 1, "name": "Mathematics"}


def test_duplicate_subject_is_rejected():
    make_subject("Mathematics")
    response = client.post("/subjects", json={"name": "mathematics"}, auth=AUTH)
    assert response.status_code == 409


def test_empty_subject_name_is_rejected():
    response = client.post("/subjects", json={"name": "   "}, auth=AUTH)
    assert response.status_code == 422


def test_assessment_needs_existing_subject():
    body = {"subject_id": 99, "title": "Quiz", "max_score": 20}
    assert client.post("/assessments", json=body, auth=AUTH).status_code == 404


def test_assessment_max_score_must_be_positive():
    make_subject()
    body = {"subject_id": 1, "title": "Quiz", "max_score": 0}
    assert client.post("/assessments", json=body, auth=AUTH).status_code == 422


# ----- adding scores -----


def test_add_score():
    make_assessment(make_subject()["id"])
    response = add_score("S001", 1, 40)
    assert response.status_code == 201
    assert response.json() == {
        "score_id": 1,
        "student_id": "S001",
        "assessment_id": 1,
        "score": 40.0,
    }


def test_score_above_maximum_is_rejected():
    make_assessment(make_subject()["id"], max_score=50)
    response = add_score("S001", 1, 51)
    assert response.status_code == 422
    assert "maximum" in response.json()["detail"]


def test_negative_score_is_rejected():
    make_assessment(make_subject()["id"])
    assert add_score("S001", 1, -5).status_code == 422


def test_score_for_unknown_assessment_is_rejected():
    assert add_score("S001", 99, 10).status_code == 404


def test_bad_student_id_is_rejected():
    make_assessment(make_subject()["id"])
    assert add_score("S 001!", 1, 10).status_code == 422


def test_duplicate_score_is_rejected():
    make_assessment(make_subject()["id"])
    add_score("S001", 1, 40)
    assert add_score("S001", 1, 45).status_code == 409


# ----- updating scores -----


def test_update_score():
    make_assessment(make_subject()["id"])
    add_score("S001", 1, 40)
    response = client.put("/scores/1", json={"score": 45}, auth=AUTH)
    assert response.status_code == 200
    assert response.json()["score"] == 45.0


def test_update_above_maximum_is_rejected():
    make_assessment(make_subject()["id"], max_score=50)
    add_score("S001", 1, 40)
    assert client.put("/scores/1", json={"score": 60}, auth=AUTH).status_code == 422
    # the old value must be unchanged
    results = client.get("/students/S001/results", auth=AUTH).json()
    assert results["results"][0]["score"] == 40.0


def test_update_unknown_score_is_rejected():
    assert client.put("/scores/99", json={"score": 10}, auth=AUTH).status_code == 404


# ----- results and averages -----


def test_get_student_results():
    make_assessment(make_subject()["id"], "Mid-term Test", 50)
    add_score("S001", 1, 40)
    response = client.get("/students/S001/results", auth=AUTH)
    assert response.status_code == 200
    item = response.json()["results"][0]
    assert item["subject"] == "Mathematics"
    assert item["assessment"] == "Mid-term Test"
    assert item["percent"] == 80.0


def test_results_for_unknown_student_return_404():
    assert client.get("/students/S999/results", auth=AUTH).status_code == 404


def test_average_overall_and_by_subject():
    maths = make_subject("Mathematics")["id"]
    english = make_subject("English")["id"]
    make_assessment(maths, "Mid-term Test", 50)  # assessment 1
    make_assessment(maths, "Final Exam", 100)  # assessment 2
    make_assessment(english, "Essay", 20)  # assessment 3
    add_score("S001", 1, 40)  # 80%
    add_score("S001", 2, 90)  # 90%
    add_score("S001", 3, 10)  # 50%
    data = client.get("/students/S001/average", auth=AUTH).json()
    assert data["number_of_scores"] == 3
    assert data["average_percent"] == 73.3  # (80 + 90 + 50) / 3
    by_subject = {
        item["subject"]: item["average_percent"] for item in data["by_subject"]
    }
    assert by_subject == {"Mathematics": 85.0, "English": 50.0}


def test_results_require_login():
    assert client.get("/students/S001/results").status_code == 401
    assert client.get("/students/S001/average").status_code == 401
