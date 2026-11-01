# Lightweight base Python image
FROM python:3.11-slim

# Working directory inside container
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirement.txt

# Copy all project code
COPY . .

# Expose port for FastAPI
EXPOSE 8000

# Start server on startup
CMD ["uvicorn", "database_api:app", "--host", "0.0.0.0", "--port", "8000"