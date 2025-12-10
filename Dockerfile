###############################################################################
# CS 125 FastAPI Server (Youth Group API)
###############################################################################

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy secrets folder into container
COPY secrets/ ./secrets/

# Copy source code
COPY . .

EXPOSE 5000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
