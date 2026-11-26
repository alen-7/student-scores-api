# How authentication, validation and clear errors protect student results

Student results are sensitive: they affect a student's progress and
reputation, and they are personal data. This API protects them in three ways.

## 1. Authentication protects privacy
Every endpoint that reads or changes results needs a username and password.
Without them the API answers `401` and shows nothing. So only authorised
people (such as teachers) can see or change results.

How it is done safely here:
- The login is stored in **environment variables** (`.env`), not in the code,
  so it never appears on GitHub. `.env` is listed in `.gitignore`.
- Passwords are compared with `secrets.compare_digest`, which prevents
  attackers learning anything from how long the comparison takes.
- The error message is the same whether the username or the password is wrong,
  so it does not reveal which one was correct.

## 2. Validation protects accuracy
Validation rejects bad data **before** it is stored. If wrong data gets in,
every average and report built on it is wrong too. The Pydantic models and
extra checks enforce these rules:
- A score cannot be negative, and cannot be higher than the assessment's maximum.
- A score must belong to a real assessment, and an assessment to a real subject.
- Names cannot be empty, and student IDs may only contain safe characters.
- Numbers must really be numbers (text like "forty" is rejected).
- One student can have only one score per assessment, so a result is not
  accidentally recorded twice. Changes must be made deliberately with `PUT`.
- When an update is rejected, the old score stays unchanged (this is tested).

## 3. Clear error responses protect both accuracy and trust
- The right **status code** tells the caller exactly what went wrong
  (`401`, `404`, `409`, `422`), so mistakes are noticed instead of ignored.
- The `detail` message explains the problem in plain words, so the user can
  fix the input instead of guessing.
- The API never crashes with a confusing page or shows internal details,
  so errors do not leak information about how it works.
- Because wrong requests fail loudly, a typing mistake cannot silently
  become a wrong result in the records.

## Remaining weaknesses
- Basic authentication sends the password with every request, so the API
  must be served over HTTPS in real use.
- There is one shared login. A real system needs separate users and roles
  (for example teachers, students and parents seeing only their own results).
- Data is kept in memory, so it disappears when the server stops.
