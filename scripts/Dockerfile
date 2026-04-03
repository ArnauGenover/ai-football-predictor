FROM python:3.11-slim

WORKDIR /scripts

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir sqlalchemy==2.0.36 psycopg2-binary==2.9.10 python-dotenv==1.0.1

COPY . .

CMD ["python", "clean_seed_data.py"]
