FROM python:3.9-slim

# Set up working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the code
COPY src/cicd_pipeline.py pipeline.py
COPY src/cicd_test_pipeline.py test_pipeline.py

# Run tests by default when the container is started for CI/CD
CMD ["python", "-m", "pytest", "test_pipeline.py", "-v"]
