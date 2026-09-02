FROM python:3.12.3

WORKDIR /app

COPY requirements.txt .
COPY *.py .
COPY .env .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "api.py"]
