# Viswam EduTech Online Exam

FastAPI + SQLite backend serving a single-page front end (`static/index.html`).

## Run on GitHub (Codespaces)
Repo → **Code → Codespaces → Create codespace on main**. The app starts automatically on port 8000 and opens in a browser tab.
Demo logins (Codespaces only): `admin@school.edu / admin123`, `john@school.edu / student123`.

## Run locally
```bash
pip install -r requirements.txt
JWT_SECRET=$(openssl rand -hex 32) ADMIN_PASSWORD=choose-one SEED_DEMO=0 uvicorn main:app --port 8000
```

## CI/CD (GitHub Actions)
`.github/workflows/ci.yml` runs the tests and a JS syntax check on every push/PR. Pushes to `main` also build and publish a Docker image to
`ghcr.io/<owner>/<repo>:latest`. Run it anywhere with:
```bash
docker run -p 8000:8000 -v exam-data:/data -e JWT_SECRET=... -e ADMIN_PASSWORD=... -e SEED_DEMO=0 ghcr.io/<owner>/<repo>:latest
```
Or deploy that image on Render / Railway / Fly (mount a volume at `/data`).

> GitHub Pages cannot run this app: it only hosts static files and the exam needs the API server.

See `.env.example` for all settings.
