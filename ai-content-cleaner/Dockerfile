# ---- Base image ----
FROM python:3.12-slim

# ---- Set working directory ----
WORKDIR /app

# ---- Install system dependencies (curl for health‑check) ----
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
    && rm -rf /var/lib/apt/lists/*

# ---- Copy requirements and install Python packages ----
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Copy application code ----
COPY app/ ./app/
COPY static/ ./static/

# ---- Expose port used by FastAPI (Uvicorn) ----
EXPOSE 8000

# ---- Run the app ----
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]