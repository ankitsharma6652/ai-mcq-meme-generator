# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Create a directory for the database to ensure persistence
RUN mkdir -p /app/data

# Set environment variables
ENV PYTHONPATH=/app/backend
ENV PORT=8000

# Expose port 8000
EXPOSE 8000

# Run main.py when the container launches
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
