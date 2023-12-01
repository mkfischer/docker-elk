# Dockerfile
FROM python:3.9-slim-buster

# Create app directory
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the python script
COPY metric_sim.py ./

# Expose port
EXPOSE 9123

# Start the application
CMD ["python", "./metric_sim.py"]
