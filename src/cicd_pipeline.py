#!/usr/bin/env python3
"""
Data Processing Pipeline for Dataflow
This script transforms data by converting text to uppercase.
"""
import argparse
import logging
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions, SetupOptions

def run_pipeline(argv=None):
    """Runs the data processing pipeline with the provided arguments."""
    parser = argparse.ArgumentParser(description='Data Processing Pipeline')
    
    # Add pipeline-specific arguments
    parser.add_argument('--input', required=True, help='Input file pattern')
    parser.add_argument('--output', required=True, help='Output location')
    parser.add_argument('--project', required=True, help='Google Cloud Project ID')
    
    # Parse known arguments
    known_args, pipeline_args = parser.parse_known_args(argv)
    
    # Create pipeline options
    pipeline_options = PipelineOptions(pipeline_args)
    
    # Set up various pipeline options
    pipeline_options.view_as(StandardOptions)
    pipeline_options.view_as(SetupOptions).save_main_session = True
    
    # Log the configured options
    logging.info(f"Running pipeline with input: {known_args.input}")
    logging.info(f"Output path: {known_args.output}")
    logging.info(f"Project ID: {known_args.project}")
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
