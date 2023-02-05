# Image from dockerhub
FROM python:3.11.1-slim

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# setting a working directory in the container
WORKDIR /code

RUN apt update && apt install -y postgresql-client
    
# Copy requirements from host, to docker container work directory
COPY ./requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy everything from host /app directory to docker container /app directory
COPY ./app ./app
COPY ./alembic.ini .

# Run the application in the port 8000
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8002", "app.main:app"]
