# Student Scores API (Module B4)

A FastAPI service for managing subjects, assessments and student scores.
Built for the FlexiSAF Internship Program, AI Engineering pathway,
Module B4: Web foundations and APIs.

Author: Chinecherem Ude

## Features
- Add scores, update results, calculate averages, retrieve a student's results
- Pydantic validation models (reject bad data automatically)
- Basic authentication (username and password from environment variables)
- Clear JSON error responses with the right status codes
- Automatic interactive documentation at `/docs`

## Requirements
- Python 3.11 or newer
- Git
- Postman (optional, to try the requests)

## Setup
```bash
git clone https://github.com/alen-7/student-scores-api.git
cd student-scores-api
python -m venv .venv
```

Activate the environment:
- Windows (Command Prompt): `.venv\Scripts\activate.bat`
- Windows (PowerShell): `.venv\Scripts\Activate.ps1`
- Mac/Linux: `source .venv/bin/activate`

Install the requirements:
```bash
python -m pip install -r requirements.txt
```

Create your login file. Copy `.env.example` to `.env`, then choose your own values:
- Windows: `copy .env.example .env`
- Mac/Linux: `cp .env.example .env`

## Run the server
```bash
uvicorn main:app --reload
```
Open http://127.0.0.1:8000/docs in your browser. Click **Authorize**, enter the
username and password from your `.env`, then use **Try it out** on any endpoint.
Stop the server with **Ctrl + C**.

## Try it with Postman
1. Import `postman_collection.json` (Import button).
2. The collection already contains the login and `base_url` variables. Change
   `username` and `password` if you changed them in `.env`.
3. Start the server, then run requests 1 to 9 in order. Requests marked
   `ERROR` show the error responses.

Data is kept in memory, so restart the server to start fresh.

## Run the tests
```bash
python -m pytest
```

## Files
| File | Purpose |
|------|---------|
| `main.py` | The endpoints |
| `models.py` | Pydantic validation models |
| `auth.py` | Basic authentication |
| `store.py` | In-memory storage |
| `test_api.py`, `conftest.py` | Automated tests |
| `postman_collection.json` | Postman collection |
| `SAMPLE_REQUESTS.md` | Example JSON requests and responses |
| `API_DOCUMENTATION.md` | Endpoint, rule and status code reference |
| `EXPLANATION.md` | How authentication, validation and errors protect results |
| `.env.example` | Example login settings (no real secrets) |

## Limitations
- Data is stored in memory and lost when the server stops
- One shared login, with no separate users or roles
- Basic authentication needs HTTPS before real use
- No pagination for long lists
