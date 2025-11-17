FROM python:3.8-slim

RUN apt-get update && apt-get install build-essential -y --fix-missing
RUN apt-get install -y --no-install-recommends \
        build-essential \
        ffmpeg \
    && rm -rf /var/lib/apt/lists/*    

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Сделать entrypoint исполняемым
RUN chmod +x entrypoint.sh

# Использовать entrypoint для автоматической инициализации БД
ENTRYPOINT ["./entrypoint.sh"]
