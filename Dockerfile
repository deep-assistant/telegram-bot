FROM python:3.12-slim

RUN apt-get update && apt-get install build-essential -y --fix-missing

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "__main__.py"]
