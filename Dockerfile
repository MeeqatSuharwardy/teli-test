# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Install git and ssh
RUN apt-get update && apt-get install

# Set your working directory
WORKDIR /app

COPY . /app



# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run app.py when the container launches using uvicorn
CMD ["gunicorn","-k", "uvicorn.workers.UvicornWorker","-b", "0.0.0.0:8000", "main:app"]
