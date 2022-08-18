FROM python:3.10.5-alpine

ENV PYTHONUNBUFFERED=1 
WORKDIR /app
COPY . /app/
RUN apk add --no-cache build-base libffi-dev bash

RUN pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=8000", "--reload"]