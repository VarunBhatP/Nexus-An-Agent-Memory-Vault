FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 10000  # ← Render port
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 10000"]
