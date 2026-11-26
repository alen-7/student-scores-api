"""In-memory storage. Data is kept in dictionaries and is lost when the
server stops (see the limitations in README.md)."""

subjects = {}  # subject_id -> {"id", "name"}
assessments = {}  # assessment_id -> {"id", "subject_id", "title", "max_score"}
scores = {}  # score_id -> {"score_id", "student_id", "assessment_id", "score"}

_counters = {"subject": 0, "assessment": 0, "score": 0}


def next_id(kind):
    """Give out 1, 2, 3... separately for each kind of record."""
    _counters[kind] += 1
    return _counters[kind]


def reset():
    """Empty everything (used by the tests)."""
    subjects.clear()
    assessments.clear()
    scores.clear()
    for kind in _counters:
        _counters[kind] = 0
