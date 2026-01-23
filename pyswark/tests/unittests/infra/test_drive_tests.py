import unittest
from unittest.mock import patch, MagicMock, Mock
import sys

from pyswark.infra.drive_tests import Driver, drive_tests


class TestDriver(unittest.TestCase):
    """Tests for the Driver class."""

    def test_init_with_valid_engine(self):
        """Test Driver initialization with a valid engine."""
        driver = Driver('unittests')
        self.assertEqual(driver.engine, 'unittests')

    def test_init_with_invalid_engine(self):
        """Test Driver initialization raises ValueError for invalid engine."""
        with self.assertRaises(ValueError) as ctx:
            Driver('invalid_engine')
        
        self.assertIn('invalid_engine', str(ctx.exception))

    def test_call_dispatches_to_engine_method(self):
        """Test that __call__ dispatches to the correct engine method."""
        driver = Driver('unittests')
        
        # Mock the unittests method
        mock_result = Mock()
        mock_return = (False, mock_result, None)
        with patch.object(Driver, 'unittests', return_value=mock_return) as mock_unittests:
            mock_package = MagicMock()
            result = driver(mock_package)
            
            mock_unittests.assert_called_once_with(mock_package)
            # Verify the result structure and values
            self.assertEqual(len(result), 3)
            self.assertFalse(result[0])  # isFailure
            self.assertEqual(result[1], mock_result)  # result object
            self.assertIsNone(result[2])  # report

    @patch('pyswark.infra.drive_tests.coverage.Coverage')
    @patch('pyswark.infra.drive_tests.unittest.TextTestRunner')
    @patch('pyswark.infra.drive_tests.unittest.TestLoader')
    @patch('pyswark.infra.drive_tests.os.path.join')
    @patch('pyswark.infra.drive_tests.os.path.dirname')
    def test_unittests_success(self, mock_dirname, mock_join, mock_loader_class, mock_runner_class, mock_coverage_class):
        """Test unittests method with successful test run."""
        # Setup mocks
        mock_package = MagicMock()
        mock_package.__file__ = '/path/to/package/__init__.py'
        
        mock_dirname.return_value = '/path/to/package'
        mock_join.side_effect = lambda *args: '/'.join(args)
        
        # Mock coverage
        mock_cov = MagicMock()
        mock_coverage_class.return_value = mock_cov
        
        # Mock unittest
        mock_loader = MagicMock()
        mock_suite = MagicMock()
        mock_loader.discover.return_value = mock_suite
        mock_loader_class.return_value = mock_loader
        
        mock_runner = MagicMock()
        mock_result = MagicMock()
        mock_result.errors = []
        mock_result.failures = []
        mock_runner.run.return_value = mock_result
        mock_runner_class.return_value = mock_runner
        
        # Call the method
        isFailure, result, report = Driver.unittests(mock_package)
        
        # Verify coverage was used correctly
        mock_coverage_class.assert_called_once_with(source=['/path/to/package'])
        mock_cov.start.assert_called_once()
        mock_cov.stop.assert_called_once()
        mock_cov.save.assert_called_once()
        mock_cov.report.assert_called_once()
        mock_cov.html_report.assert_called_once()
        mock_cov.xml_report.assert_called_once()
        
        # Verify unittest was used correctly
        mock_loader.discover.assert_called_once_with(start_dir='/path/to/package/tests/unittests')
        mock_runner.run.assert_called_once_with(mock_suite)
        
        # Verify return values
        self.assertFalse(isFailure)
        self.assertEqual(result, mock_result)
        self.assertIsNotNone(report)

    @patch('pyswark.infra.drive_tests.coverage.Coverage')
    @patch('pyswark.infra.drive_tests.unittest.TextTestRunner')
    @patch('pyswark.infra.drive_tests.unittest.TestLoader')
    @patch('pyswark.infra.drive_tests.os.path.join')
    @patch('pyswark.infra.drive_tests.os.path.dirname')
    def test_unittests_with_errors(self, mock_dirname, mock_join, mock_loader_class, mock_runner_class, mock_coverage_class):
        """Test unittests method with test errors."""
        # Setup mocks
        mock_package = MagicMock()
        mock_package.__file__ = '/path/to/package/__init__.py'
        
        mock_dirname.return_value = '/path/to/package'
        mock_join.side_effect = lambda *args: '/'.join(args)
        
        # Mock coverage
        mock_cov = MagicMock()
        mock_coverage_class.return_value = mock_cov
        
        # Mock unittest with errors
        mock_loader = MagicMock()
        mock_suite = MagicMock()
        mock_loader.discover.return_value = mock_suite
        mock_loader_class.return_value = mock_loader
        
        mock_runner = MagicMock()
        mock_result = MagicMock()
        mock_result.errors = [('test', 'error')]
        mock_result.failures = []
        mock_runner.run.return_value = mock_result
        mock_runner_class.return_value = mock_runner
        
        # Call the method
        isFailure, result, report = Driver.unittests(mock_package)
        
        # Verify coverage was stopped but not saved/reported
        mock_cov.start.assert_called_once()
        mock_cov.stop.assert_called_once()
        mock_cov.save.assert_not_called()
        mock_cov.report.assert_not_called()
        
        # Verify return values
        self.assertTrue(isFailure)
        self.assertEqual(result, mock_result)
        self.assertIsNone(report)

    @patch('pyswark.infra.drive_tests.coverage.Coverage')
    @patch('pyswark.infra.drive_tests.unittest.TextTestRunner')
    @patch('pyswark.infra.drive_tests.unittest.TestLoader')
    @patch('pyswark.infra.drive_tests.os.path.join')
    @patch('pyswark.infra.drive_tests.os.path.dirname')
    def test_unittests_with_failures(self, mock_dirname, mock_join, mock_loader_class, mock_runner_class, mock_coverage_class):
        """Test unittests method with test failures."""
        # Setup mocks
        mock_package = MagicMock()
        mock_package.__file__ = '/path/to/package/__init__.py'
        
        mock_dirname.return_value = '/path/to/package'
        mock_join.side_effect = lambda *args: '/'.join(args)
        
        # Mock coverage
        mock_cov = MagicMock()
        mock_coverage_class.return_value = mock_cov
        
        # Mock unittest with failures
        mock_loader = MagicMock()
        mock_suite = MagicMock()
        mock_loader.discover.return_value = mock_suite
        mock_loader_class.return_value = mock_loader
        
        mock_runner = MagicMock()
        mock_result = MagicMock()
        mock_result.errors = []
        mock_result.failures = [('test', 'failure')]
        mock_runner.run.return_value = mock_result
        mock_runner_class.return_value = mock_runner
        
        # Call the method
        isFailure, result, report = Driver.unittests(mock_package)
        
        # Verify coverage was stopped but not saved/reported
        mock_cov.start.assert_called_once()
        mock_cov.stop.assert_called_once()
        mock_cov.save.assert_not_called()
        mock_cov.report.assert_not_called()
        
        # Verify return values
        self.assertTrue(isFailure)
        self.assertEqual(result, mock_result)
        self.assertIsNone(report)


class TestDriveTestsFunction(unittest.TestCase):
    """Tests for the drive_tests function."""

    @patch('pyswark.infra.drive_tests.sys.exit')
    @patch('pyswark.infra.drive_tests.Driver')
    def test_drive_tests_success(self, mock_driver_class, mock_exit):
        """Test drive_tests function with successful test run."""
        # Setup mocks
        mock_driver = MagicMock()
        mock_driver.return_value = (False, MagicMock(), MagicMock())
        mock_driver_class.return_value = mock_driver
        
        mock_package = MagicMock()
        
        # Call the function
        drive_tests('unittests', mock_package)
        
        # Verify Driver was created and called
        mock_driver_class.assert_called_once_with('unittests')
        mock_driver.assert_called_once_with(mock_package)
        
        # Verify sys.exit was called with code 0
        mock_exit.assert_called_once_with(0)

    @patch('pyswark.infra.drive_tests.sys.exit')
    @patch('pyswark.infra.drive_tests.Driver')
    def test_drive_tests_failure(self, mock_driver_class, mock_exit):
        """Test drive_tests function with failed test run."""
        # Setup mocks
        mock_driver = MagicMock()
        mock_driver.return_value = (True, MagicMock(), None)
        mock_driver_class.return_value = mock_driver
        
        mock_package = MagicMock()
        
        # Call the function
        drive_tests('unittests', mock_package)
        
        # Verify Driver was created and called
        mock_driver_class.assert_called_once_with('unittests')
        mock_driver.assert_called_once_with(mock_package)
        
        # Verify sys.exit was called with code 1
        mock_exit.assert_called_once_with(1)


if __name__ == '__main__':
    unittest.main()
