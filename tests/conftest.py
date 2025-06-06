import pytest
import os
import tempfile
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_aws_credentials():
    """Mock AWS credentials for testing"""
    original_values = {}
    
    # Store original values
    for key in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_DEFAULT_REGION']:
        original_values[key] = os.environ.get(key)
    
    # Set mock values
    os.environ['AWS_ACCESS_KEY_ID'] = 'test_access_key'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'test_secret_key'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    
    yield
    
    # Restore original values
    for key, value in original_values.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value