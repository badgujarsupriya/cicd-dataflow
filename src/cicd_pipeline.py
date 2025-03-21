#!/usr/bin/env python3
"""
Data Processing Pipeline for Dataflow
This script transforms data by converting text to uppercase.
"""
import argparse
import logging
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions, SetupOptions
from apache_beam.options.pipeline_options import GoogleCloudOptions

def run_pipeline(argv=None):
    """Runs the data processing pipeline with the provided arguments."""
    parser = argparse.ArgumentParser(description='Data Processing Pipeline')
    
    # Add pipeline-specific arguments
    parser.add_argument('--input', required=True, help='Input file pattern')
    parser.add_argument('--output', required=True, help='Output location')
    parser.add_argument('--project', required=True, help='Google Cloud Project ID')
    parser.add_argument('--temp_location', required=True, help='Temp location')
    parser.add_argument('--staging_location', required=True, help='Staging location')
    parser.add_argument('--region', required=True, help='GCP Region')
    
    # Parse known arguments
    known_args, pipeline_args = parser.parse_known_args(argv)
    
    # Create pipeline options
    pipeline_options = PipelineOptions(pipeline_args)
    
    # Set up various pipeline options
    pipeline_options.view_as(StandardOptions)
    pipeline_options.view_as(SetupOptions).save_main_session = True
    
    # Explicitly set required options
    google_cloud_options = pipeline_options.view_as(GoogleCloudOptions)
    google_cloud_options.project = known_args.project
    google_cloud_options.region = known_args.region
    google_cloud_options.temp_location = known_args.temp_location
    google_cloud_options.staging_location = known_args.staging_location
    
    # Log the configured options
    logging.info(f"Running pipeline with input: {known_args.input}")
    logging.info(f"Output path: {known_args.output}")
    logging.info(f"Project ID: {known_args.project}")
    logging.info(f"Region: {known_args.region}")
    logging.info(f"Temp location: {known_args.temp_location}")
    logging.info(f"Staging location: {known_args.staging_location}")
    logging.info(f"Pipeline options: {pipeline_options.get_all_options()}")
    
    # Run the pipeline
    with beam.Pipeline(options=pipeline_options) as p:
        (p 
         | 'ReadData' >> beam.io.ReadFromText(known_args.input)
         | 'ProcessData' >> beam.Map(lambda x: x.upper())
         | 'WriteData' >> beam.io.WriteToText(known_args.output)
        )
    
    logging.info("Pipeline execution completed successfully")

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    logging.info("Starting the data processing pipeline")
    run_pipeline()