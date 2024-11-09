FROM python:3.12.4-slim

WORKDIR /app
COPY ./app /app

RUN pip install flask pymongo

EXPOSE 80

CMD ["python", "main.py"]