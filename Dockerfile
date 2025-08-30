FROM python:3.11-slim
WORKDIR ./app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
COPY ../public ./public
EXPOSE 3000
CMD ["python3", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "3000"]