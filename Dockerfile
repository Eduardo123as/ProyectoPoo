FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    imagemagick \
    libmagickwand-dev \
    cabextract \
    wget \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENV FLASK_APP=app.py

CMD ["flask", "run", "--host=0.0.0.0"]