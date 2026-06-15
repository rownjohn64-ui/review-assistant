FROM python:3.11-slim

WORKDIR /worker

RUN pip install httpx pydantic python-dotenv

COPY main.py .

CMD ["python", "main.py"]