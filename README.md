# cicd-dataflow

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
