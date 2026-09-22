FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Use 'fastapi dev' for hot-reloading inside the container
CMD ["fastapi", "dev", "app.py", "--host", "0.0.0.0", "--port", "8000"]