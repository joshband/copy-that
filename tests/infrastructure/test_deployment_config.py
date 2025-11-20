import os
import pytest
import tempfile
import logging
from pathlib import Path
from unittest.mock import patch, mock_open
from src.copy_that.infrastructure.deployment_config import DeploymentConfig

@pytest.fixture
def temp_env_file():
    """Create a temporary .env file for testing."""
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.env') as temp_file:
        temp_file.write("""
# Test environment configuration
ENVIRONMENT=local
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
""")
        temp_file.flush()
    yield temp_file.name
    os.unlink(temp_file.name)

def test_validate_environment():
    """Test environment validation method."""
    test_cases = [
        ('local', 'local'),
        ('STAGING', 'staging'),
        ('Production', 'production'),
        ('invalid', 'local')
    ]

    for input_env, expected in test_cases:
        result = DeploymentConfig._validate_environment(input_env)
        assert result == expected

def test_environment_detection_default():
    """Test default environment detection."""
    with patch.dict(os.environ, clear=True):
        assert DeploymentConfig.detect_environment() == 'local'

def test_environment_detection_explicit():
    """Test explicit environment detection."""
    test_cases = [
        ('local', 'local'),
        ('staging', 'staging'),
        ('production', 'production'),
        ('invalid', 'local')
    ]

    for env_value, expected in test_cases:
        with patch.dict(os.environ, {'ENVIRONMENT': env_value}):
            assert DeploymentConfig.detect_environment() == expected

def test_github_actions_environment_detection():
    """Test environment detection in GitHub Actions context."""
    github_action_cases = [
        # Pull Request scenario
        {
            'GITHUB_ACTIONS': 'true',
            'GITHUB_EVENT_NAME': 'pull_request',
            'expected': 'staging'
        },
        # Main branch push scenario
        {
            'GITHUB_ACTIONS': 'true',
            'GITHUB_EVENT_NAME': 'push',
            'GITHUB_REF': 'refs/heads/main',
            'expected': 'production'
        }
    ]

    for case in github_action_cases:
        with patch.dict(os.environ, {k: str(v) for k, v in case.items() if k != 'expected'}):
            detected_env = DeploymentConfig.detect_environment()
            assert detected_env == case['expected']

def test_redis_configuration(temp_env_file):
    """Test Redis configuration for different environments."""
    # Test local configuration
    local_config = DeploymentConfig.configure_redis('local', env_file_path=temp_env_file)
    assert local_config['REDIS_URL'] == 'redis://localhost:6379/0'
    assert local_config['CELERY_BROKER_URL'] == 'redis://localhost:6379/1'
    assert local_config['CELERY_RESULT_BACKEND'] == 'redis://localhost:6379/2'

    # Test staging configuration
    staging_config = DeploymentConfig.configure_redis('staging', env_file_path=temp_env_file)
    assert staging_config['REDIS_URL'].startswith('redis://default')
    assert 'upstash.io' in staging_config['REDIS_URL']

    # Test production configuration
    production_config = DeploymentConfig.configure_redis('production', env_file_path=temp_env_file)
    assert production_config['REDIS_URL'].startswith('redis://default')
    assert 'production-redis' in production_config['REDIS_URL']

def test_configuration_error_handling(caplog):
    """Test error handling during configuration."""
    # Ensure error logging works with various failures
    error_scenarios = [
        # Scenario 1: Failed to create directory
        {
            'mock_path': '/nonexistent/path',
            'expected_log': 'Failed to create directory'
        },
        # Scenario 2: Failed to create file
        {
            'mock_path': '/nonexistent/unreachable.env',
            'expected_log': 'Failed to create file'
        }
    ]

    for scenario in error_scenarios:
        # Reset caplog before each test
        caplog.clear()
        caplog.set_level(logging.ERROR)

        # Configure with problematic path
        config = DeploymentConfig.configure_redis(env_file_path=scenario['mock_path'])

        # Verify error was logged
        assert len(caplog.records) > 0
        assert scenario['expected_log'] in caplog.text

def test_print_current_config(capfd):
    """Test current configuration printing."""
    # Temporarily set some environment variables
    with patch.dict(os.environ, {
        'REDIS_URL': 'redis://testhost:6379/0',
        'CELERY_BROKER_URL': 'redis://testhost:6379/1',
        'CELERY_RESULT_BACKEND': 'redis://testhost:6379/2'
    }):
        DeploymentConfig.print_current_config()

        # Capture the output
        out, _ = capfd.readouterr()

        # Verify the output contains the expected configuration
        assert 'Current Environment:' in out
        assert 'REDIS_URL: redis://testhost:6379/0' in out
        assert 'CELERY_BROKER_URL: redis://testhost:6379/1' in out
        assert 'CELERY_RESULT_BACKEND: redis://testhost:6379/2' in out

def test_environment_specific_configuration():
    """Test that different environments have distinct configurations."""
    environments = ['local', 'staging', 'production']

    configs = {}
    for env in environments:
        configs[env] = DeploymentConfig.configure_redis(env)

    # Ensure no two environments have the same Redis configuration
    for i, env1 in enumerate(environments):
        for env2 in environments[i+1:]:
            assert configs[env1]['REDIS_URL'] != configs[env2]['REDIS_URL'], \
                f"Configurations for {env1} and {env2} should be different"