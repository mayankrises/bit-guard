# Deploying BitGuard (demo version)

This runs the website + the mock risk API in one container. Scores are demo data
(derived from the address), so no Neo4j, model files or Bitcoin node are needed.

## Test locally with Docker
    docker build -t bitguard .
    docker run -p 8000:8000 bitguard
    # open http://localhost:8000

## Deploy on Render (free)
1. Put this project on GitHub (private repo is fine).
2. Render dashboard -> New -> Blueprint (or Web Service) -> pick the repo.
3. It reads `render.yaml` / `Dockerfile` automatically. Click Deploy.
4. Open the `https://<name>.onrender.com` URL when the build finishes.
Free instances sleep after ~15 min idle; the first visit then takes ~30-60 s.

## Before you deploy
Make sure `frontend/static/img/bitguard2.png` (your logo) is in the repo.
