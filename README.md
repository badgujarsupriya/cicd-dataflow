# CI/CD Pipeline for Dataflow

This repository demonstrates a complete CI/CD pipeline for Apache Beam Dataflow jobs using Docker, Cloud Build, Cloud Composer (Airflow), and Dataflow.

## Repository Structure

```
cicd-dataflow/
├── src/
│   ├── cicd_pipeline.py       # Main data processing pipeline
│   └── cicd_test_pipeline.py  # Tests for the pipeline
├── dags/
│   └── cicd_dataflow_dag.py   # Airflow DAG file to deploy to Composer
├── Dockerfile                 # Docker config for testing
├── cloudbuild.yaml            # Cloud Build configuration
├── requirements.txt           # Python dependencies
└── README.md                  # Documentation
```

## Architecture

```
GitHub Push → Cloud Build → Docker Test → Deploy Script → Trigger DAG → Run Dataflow
```

### Components

1. **Docker** - Used for consistent test environments and dependency management
2. **Cloud Build** - Automates the CI/CD pipeline 
3. **Cloud Storage** - Stores pipeline scripts and data
4. **Cloud Composer** - Orchestrates the workflow with Airflow
5. **Dataflow** - Executes the data processing pipeline

## Setup Instructions

### 1. Create GCS Buckets

```bash
# Create buckets for scripts, data, and Dataflow temp/staging
gsutil mb -l us-east1 gs://[PROJECT_ID]-dataflow-scripts
gsutil mb -l us-east1 gs://[PROJECT_ID]-data
gsutil mb -l us-east1 gs://[PROJECT_ID]-dataflow-temp
gsutil mb -l us-east1 gs://[PROJECT_ID]-dataflow-staging
```

### 2. Deploy the Airflow DAG to Cloud Composer

```bash
gcloud composer environments storage dags import \
  --environment my-composer-environment \
  --location [COMPOSER_REGION] \
  --source dags/cicd_dataflow_dag.py
```

### 3. Set up Cloud Build Trigger

1. Go to Cloud Build → Triggers
2. Create a new trigger connected to your GitHub repository
3. Use `cloudbuild.yaml` as the configuration file
4. Add substitution variables for your Composer environment:
   - `_COMPOSER_REGION`: Your Composer environment region (default is us-central1)

### 4. Grant Required Permissions

Make sure your Cloud Build service account has:
- Composer User role
- Storage Object Admin role
- Dataflow Admin role

## How It Works

1. When you push code to GitHub, Cloud Build is triggered
2. Cloud Build builds a Docker image and runs tests
3. If tests pass, the pipeline script is uploaded to GCS
4. Cloud Build creates a timestamped input file for tracking
5. Cloud Build triggers the Airflow DAG with appropriate parameters including the timestamp
6. Airflow orchestrates the Dataflow job execution
7. Dataflow runs the data processing pipeline
8. Results are verified and logged with the same timestamp

## How Docker is Used

Docker plays a key role in this CI/CD pipeline:

1. **Testing Environment**: The Docker container provides a consistent environment for running tests, ensuring dependencies are properly installed and configured.

2. **Dependency Management**: All required libraries (Apache Beam, etc.) are specified in the Dockerfile, making it easy to version and track dependencies.

3. **Build Artifact**: The Docker image is stored in Container Registry, providing versioning for your pipeline code and environment.

4. **CI/CD Integration**: Cloud Build uses the Docker container to run tests, ensuring your pipeline code works before triggering the Dataflow job.

## Understanding Key Parameters

- **pipeline-$SHORT_SHA.py**: The pipeline file name with a short version of the commit SHA (hash) appended to it. `$SHORT_SHA` is a built-in variable in Cloud Build containing the first 7 characters of the Git commit hash. This makes each file uniquely identifiable to its source commit.

- **YYYYMMDDHHMMSS timestamp**: A timestamp format added to input and output files, allowing you to trace each execution clearly and avoid file conflicts.
