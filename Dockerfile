FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    BUDGET_DEPLOYMENT=production \
    BUDGET_DB_PATH=/var/data/smart_budget_tracker.db \
    TZ=Asia/Kuala_Lumpur

WORKDIR /app
RUN apt-get update \
    && apt-get install -y --no-install-recommends tesseract-ocr tesseract-ocr-eng tzdata \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY Smart_Budget_Tracker_Professional.py budget_assistant.py deployment_config.py receipt_scanner.py receipt_ui.py ./
COPY .streamlit/config.toml .streamlit/config.toml
COPY assets/ assets/

EXPOSE 8501
CMD ["sh", "-c", "exec python -m streamlit run Smart_Budget_Tracker_Professional.py --server.address=0.0.0.0 --server.port=${PORT:-8501} --server.headless=true"]
