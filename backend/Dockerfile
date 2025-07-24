# Use Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend files
COPY . .

# Expose port
EXPOSE 8080

# Start FastAPI with uvicorn (adjust if using Flask)
CMD ["uvicorn", "cloud_main:app", "--host", "0.0.0.0", "--port", "8080"]
