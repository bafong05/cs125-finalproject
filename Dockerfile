###############################################################################
# CS 125 FastAPI Server (Youth Group API)
#
# Instructions:
#
# 1) Build this image (from the directory containing this Dockerfile):
#       docker build -t youthgroup-api .
#
# 2) Run the container (mapping port 5000):
#       docker run --name youthgroup-api -p 8000:5000 --env-file .env youthgroup-api
#
# 3) View API docs:
#       http://localhost:8000/docs
#
# 4) Stop the container:
#       docker stop youthgroup-api
#
# 5) Start the container again:
#       docker start youthgroup-api
###############################################################################

############################
# Base Image: Python 3.11
############################

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy secrets folder into container
COPY secrets/ ./secrets/

# Copy source code
COPY . .

EXPOSE 5000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
