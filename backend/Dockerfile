FROM python:3.13-slim

WORKDIR /app

# Сначала библиотеки: Docker запомнит этот шаг, пересборка будет быстрой
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
# Сертификат Минцифры для GigaChat
COPY certs ./certs

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]