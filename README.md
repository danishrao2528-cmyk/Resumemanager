# Resume Manager AI

Role-based FastAPI + Streamlit resume manager with JWT authentication and AI candidate matching.

## Roles
- **Candidate:** sign up, log in, create exactly one resume, view it, and update only that resume.
- **Admin:** one server-created account, view candidates/resumes, permanently delete a candidate + resume, and run AI Candidate Search.

## Local run
Open two terminals in the project root.

Backend:
```bash
uvicorn main:app --reload
```

Frontend:
```bash
streamlit run app/frontend/streamlit_app.py
```

## Admin
The admin account is created in the included local database. Credentials are configured via `.env` / `create_admin.py`.

## Logs
Local logs are written to `logs/app.log` and also printed to the console.

## Security
`.env`, logs, virtual environments, and the SQLite database are ignored by Git.
