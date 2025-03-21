#!/usr/bin/env python3
"""
Test file for the data processing pipeline
"""
import unittest
import apache_beam as beam
from apache_beam.testing.test_pipeline import TestPipeline
from apache_beam.testing.util import assert_that, equal_to

class PipelineTest(unittest.TestCase):
    def test_transform(self):
        """Test the uppercase transformation"""
        with TestPipeline() as p:
            input_data = ['hello', 'world', 'dataflow']
            expected_output = ['HELLO', 'WORLD', 'DATAFLOW']
            
            output = (
                p 
                | beam.Create(input_data)
                | beam.Map(lambda x: x.upper())
            )
            
            assert_that(output, equal_to(expected_output))

if __name__ == '__main__':
    unittest.main()
