FROM python:3.10

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD python startup.py && uvicorn app:app --host 0.0.0.0 --port 8000
