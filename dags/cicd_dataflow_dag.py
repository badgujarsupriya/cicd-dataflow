from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.google.cloud.operators.dataflow import DataflowCreatePythonJobOperator
from airflow.operators.python import PythonOperator

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 3, 15),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Create the DAG
dag = DAG(
    'cicd_dataflow_dag',
    default_args=default_args,
    description='CI/CD Pipeline for Dataflow Data Processing',
    schedule_interval=None,  # Only triggered by CI/CD
    catchup=False,
    tags=['dataflow', 'cicd', 'pipeline'],
)

# Hardcoded region as requested
REGION = "us-east1"

# Function to validate setup before running Dataflow
def validate_setup(**context):
    """Validates the setup and parameters for the Dataflow job."""
    
    pipeline_file = context['dag_run'].conf.get('pipeline_file')
    input_file = context['dag_run'].conf.get('input_file')
    output_path = context['dag_run'].conf.get('output_path')
    project_id = context['dag_run'].conf.get('project_id')
    
    if not all([pipeline_file, input_file, output_path, project_id]):
        raise ValueError("Missing required parameters: pipeline_file, input_file, output_path, or project_id")
    
    print(f"Validated pipeline file: {pipeline_file}")
    print(f"Validated input file: {input_file}")
    print(f"Validated output path: {output_path}")
    print(f"Validated project ID: {project_id}")
    
    return {
        'pipeline_file': pipeline_file,
        'input_file': input_file,
        'output_path': output_path,
        'project_id': project_id
    }

# Task to validate setup
validate_setup_task = PythonOperator(
    task_id='validate_setup',
    python_callable=validate_setup,
    provide_context=True,
    dag=dag,
)

# Dataflow job task
run_dataflow_pipeline = DataflowCreatePythonJobOperator(
    task_id='run_dataflow_pipeline',
    py_file='{{ ti.xcom_pull(task_ids="validate_setup")["pipeline_file"] }}',
    job_name='dataflow-pipeline-{{ ds_nodash }}',
    options={
        'project': '{{ ti.xcom_pull(task_ids="validate_setup")["project_id"] }}',
        'input': '{{ ti.xcom_pull(task_ids="validate_setup")["input_file"] }}',
        'output': '{{ ti.xcom_pull(task_ids="validate_setup")["output_path"] }}',
        'temp_location': 'gs://{{ ti.xcom_pull(task_ids="validate_setup")["project_id"] }}-dataflow-temp',
        'staging_location': 'gs://{{ ti.xcom_pull(task_ids="validate_setup")["project_id"] }}-dataflow-staging',
        'region': REGION,
        'max_num_workers': 2,
        'machine_type': 'n1-standard-2'
    },
    location=REGION,
    wait_until_finished=True,
    dag=dag,
)

# Task to verify results
def verify_results(**context):
    """Verifies the results of the Dataflow job."""
    from google.cloud import storage
    
    output_path = context['ti'].xcom_pull(task_ids='validate_setup')['output_path']
    
    # Extract bucket name and prefix from output path
    output_path = output_path.replace('gs://', '')
    bucket_name, prefix = output_path.split('/', 1)
    
    # Create Cloud Storage client
    storage_client = storage.Client()
    
    # Get the bucket
    bucket = storage_client.bucket(bucket_name)
    
    # List output files
    blobs = list(bucket.list_blobs(prefix=prefix))
    
    print(f"Output files found: {len(blobs)}")
    
    # Try to read a sample output file
    for blob in blobs:
        if not blob.name.endswith('/_SUCCESS'):
            content = blob.download_as_text()
            print(f"Sample processed output from {blob.name}:")
            print(content[:500] + "..." if len(content) > 500 else content)
            break
    
    print("Dataflow job completed successfully!")
    return "Results verification completed"

verify_task = PythonOperator(
    task_id='verify_task',
    python_callable=verify_results,
    provide_context=True,
    dag=dag,
)

# Set task dependencies
validate_setup_task >> run_dataflow_pipeline >> verify_task
