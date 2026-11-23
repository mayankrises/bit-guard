# Demo deployment: frontend + mock backend in ONE container (good for Render/Railway/Fly free tiers)
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY frontend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY frontend ./frontend
COPY mock_backend ./mock_backend
COPY deploy_start.sh ./deploy_start.sh
RUN chmod +x ./deploy_start.sh

# Hosts like Render set $PORT automatically; default to 8000 locally
ENV PORT=8000
EXPOSE 8000

CMD ["./deploy_start.sh"]
