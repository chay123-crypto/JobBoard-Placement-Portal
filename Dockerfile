FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["sh", "-c", "python -m backend.init_db --seed-demo && exec gunicorn --bind 0.0.0.0:5000 app:app"]
