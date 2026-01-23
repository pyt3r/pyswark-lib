"""
Tests for pyswark.gluedb.models
=================================

IoModel provides ETL (Extract, Transform, Load) capabilities for GlueDb records.
It defines how data is read from and written to external sources using URIs.

Key Features
------------
- Extract: Read data from any URI (file, HTTP, etc.)
- Load: Write data to any URI with separate write configuration
- Flexible: Different datahandlers and options for read vs write operations

Example Usage
-------------
>>> from pyswark.gluedb.models.iomodel import IoModel
>>> import pandas
>>>
>>> # Create a model pointing to a CSV file
>>> model = IoModel.fromArgs('file:./data.csv')
>>> df = model.extract()  # Read the CSV
>>>
>>> # Modify and write back
>>> df['new_col'] = 1
>>> model.load(df)  # Write to same file
"""

import unittest
import tempfile
import pathlib
import shutil
import json

import pandas

from pyswark.gluedb.models.iomodel import IoModel


class TestIoModel(unittest.TestCase):
    """
    Tests for IoModel - ETL operations for GlueDb records.
    
    IoModel enables reading from and writing to external data sources
    using a unified URI interface. This is the foundation of the GlueDb
    "data as configuration" pattern.
    """

    def setUp(self):
        """Create a temporary directory for test files."""
        self.tempdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tempdir)

    def test_extract_reads_data_from_file(self):
        """
        IoModel.extract() reads data from a URI.
        
        This is the "E" in ETL - extracting data from an external source.
        The URI can point to files, HTTP endpoints, or any supported data source.
        """
        # Create a test CSV file
        csv_path = pathlib.Path(self.tempdir) / 'data.csv'
        df = pandas.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
        df.to_csv(csv_path, index=True)
        
        # Create IoModel and extract
        model = IoModel.fromArgs(str(csv_path))
        extracted = model.extract()
        
        # Verify data matches
        pandas.testing.assert_frame_equal(extracted, df)

    def test_load_writes_data_to_file(self):
        """
        IoModel.load() writes data to a URI.
        
        This is the "L" in ETL - loading data into an external system.
        The write operation uses the same URI as read by default.
        """
        # Create initial CSV
        csv_path = pathlib.Path(self.tempdir) / 'output.csv'
        initial_df = pandas.DataFrame({'x': [1, 2]})
        initial_df.to_csv(csv_path, index=False)
        
        # Create IoModel and modify data
        model = IoModel.fromArgs(str(csv_path), kwWrite={'overwrite': True})
        new_df = pandas.DataFrame({'x': [1, 2], 'y': [3, 4]})
        
        # Load (write) the new data
        model.load(new_df)
        
        # Verify it was written
        written = model.extract()
        pandas.testing.assert_frame_equal(written, new_df)

    def test_separate_read_write_configurations(self):
        """
        IoModel supports different configurations for read vs write.
        
        This enables scenarios like:
        - Reading from a CSV but writing to JSON
        - Different options for read (e.g., no header) vs write (e.g., with header)
        - Reading from one source, writing to another
        """
        # Create source and destination files
        source_path = pathlib.Path(self.tempdir) / 'source.csv'
        dest_path = pathlib.Path(self.tempdir) / 'dest.json'
        
        # Write initial CSV
        df = pandas.DataFrame({'name': ['Alice', 'Bob'], 'age': [30, 25]})
        df.to_csv(source_path, index=False)
        
        # Create model: read from CSV, write to JSON
        model = IoModel.fromArgs(
            uri=str(source_path),
            datahandler='',  # Auto-detect CSV for read
            uriWrite=str(dest_path),
            datahandlerWrite='json',  # Explicitly use JSON for write
            kwWrite={'indent': 2}  # Pretty-print JSON
        )
        
        # Extract from CSV
        extracted = model.extract()
        self.assertIsInstance(extracted, pandas.DataFrame)
        
        # Load to JSON (convert DataFrame to dict first)
        data_dict = extracted.to_dict('records')
        model.load(data_dict)
        
        # Verify JSON was written
        with open(dest_path) as f:
            written = json.load(f)
        self.assertEqual(written, data_dict)


if __name__ == '__main__':
    unittest.main()
