import os

import pytest

from src.copy_that.infrastructure.config import AppConfig, get_redis_config


@pytest.fixture
def clean_env():
    """Ensure a clean environment for testing."""
    original_env = dict(os.environ)
    try:
        os.environ.clear()
        yield
    finally:
        os.environ.clear()
        os.environ.update(original_env)

def test_default_environment(clean_env):
    """Test that default environment is local."""
    config = AppConfig()
    assert config('ENVIRONMENT', default='local') == 'local'

def test_environment_detection(clean_env):
    """Test environment detection and switching."""
    test_environments = ['local', 'staging', 'production']

    for env in test_environments:
        # Set environment variable
        os.environ['ENVIRONMENT'] = env

        # Create new config instance
        config = AppConfig()

        # Verify environment is correctly detected
        assert config('ENVIRONMENT', default='local') == env

def test_redis_config_per_environment(clean_env):
    """Test Redis configurations for different environments."""
    test_cases = {
        'local': {
            'REDIS_URL': 'redis://localhost:6379/0',
            'CELERY_BROKER_URL': 'redis://localhost:6379/1',
            'CELERY_RESULT_BACKEND': 'redis://localhost:6379/2'
        },
        'staging': {
            'REDIS_URL': 'redis://default:AZnUAAIncDI2ZDM0Y2Y1ZTBjYWI0NDBlOGFlNjYwMWE1OTAzZWY1Y3AyMzkzODA@literate-javelin-39380.upstash.io:6379',
            'CELERY_BROKER_URL': 'redis://default:AZnUAAIncDI2ZDM0Y2Y1ZTBjYWI0NDBlOGFlNjYwMWE1OTAzZWY1Y3AyMzkzODA@literate-javelin-39380.upstash.io:6379',
            'CELERY_RESULT_BACKEND': 'redis://default:AZnUAAIncDI2ZDM0Y2Y1ZTBjYWI0NDBlOGFlNjYwMWE1OTAzZWY1Y3AyMzkzODA@literate-javelin-39380.upstash.io:6379'
        },
        'production': {
            'REDIS_URL': 'redis://default:PRODUCTION_TOKEN@production-redis.upstash.io:6379',
            'CELERY_BROKER_URL': 'redis://default:PRODUCTION_TOKEN@production-redis.upstash.io:6379',
            'CELERY_RESULT_BACKEND': 'redis://default:PRODUCTION_TOKEN@production-redis.upstash.io:6379'
        }
    }

    for env, expected_config in test_cases.items():
        # Set environment
        os.environ['ENVIRONMENT'] = env

        # Get configuration
        config = AppConfig()
        current_config = config.get_redis_config()

        # Verify each config parameter
        for key, value in expected_config.items():
            assert current_config[key] == value, f"Mismatch in {key} for {env} environment"

def test_environment_variable_override(clean_env):
    """Test that environment variables can override default configurations."""
    # Set base environment
    os.environ['ENVIRONMENT'] = 'local'

    # Override Redis URL
    custom_redis_url = 'redis://custom-host:6379/0'
    os.environ['LOCAL_REDIS_URL'] = custom_redis_url

    # Get configuration
    config = AppConfig()
    current_config = config.get_redis_config()

    # Verify override
    assert current_config['REDIS_URL'] == custom_redis_url

def test_unknown_environment(clean_env):
    """Test behavior with unknown environment."""
    # Set an unknown environment
    os.environ['ENVIRONMENT'] = 'unknown'

    # Create config
    config = AppConfig()
    current_config = config.get_redis_config()

    # Verify fallback to local configuration
    local_config = {
        'REDIS_URL': 'redis://localhost:6379/0',
        'CELERY_BROKER_URL': 'redis://localhost:6379/1',
        'CELERY_RESULT_BACKEND': 'redis://localhost:6379/2'
    }

    # Check that all config matches local
    for key, value in local_config.items():
        assert current_config[key] == value

def test_file_based_configuration(tmp_path):
    """Test loading configuration from a specific file."""
    # Create a temporary .env file
    env_file_path = tmp_path / ".env"
    env_file_path.write_text("""
ENVIRONMENT=staging
STAGING_REDIS_URL=redis://custom-staging-host:6379/0
""")

    # Load configuration from the specific file
    config = AppConfig(str(env_file_path))

    # Get configuration
    current_config = config.get_redis_config()

    # Verify custom staging configuration
    assert current_config['REDIS_URL'] == 'redis://custom-staging-host:6379/0'

def test_config_call_method(clean_env):
    """Test the __call__ method for accessing configuration."""
    config = AppConfig()

    # Test default values
    assert config('NON_EXISTENT_KEY', default='test_default') == 'test_default'

    # Set an environment variable
    os.environ['TEST_CONFIG_KEY'] = 'test_value'
    assert config('TEST_CONFIG_KEY') == 'test_value'

def test_get_redis_config_convenience_function(clean_env):
    """Test the global get_redis_config function."""
    # Set environment
    os.environ['ENVIRONMENT'] = 'staging'

    # Get configuration using convenience function
    config = get_redis_config()

    # Verify configuration matches staging
    staging_config = {
        'REDIS_URL': 'redis://default:AZnUAAIncDI2ZDM0Y2Y1ZTBjYWI0NDBlOGFlNjYwMWE1OTAzZWY1Y3AyMzkzODA@literate-javelin-39380.upstash.io:6379',
        'CELERY_BROKER_URL': 'redis://default:AZnUAAIncDI2ZDM0Y2Y1ZTBjYWI0NDBlOGFlNjYwMWE1OTAzZWY1Y3AyMzkzODA@literate-javelin-39380.upstash.io:6379',
        'CELERY_RESULT_BACKEND': 'redis://default:AZnUAAIncDI2ZDM0Y2Y1ZTBjYWI0NDBlOGFlNjYwMWE1OTAzZWY1Y3AyMzkzODA@literate-javelin-39380.upstash.io:6379'
    }

    for key, value in staging_config.items():
        assert config[key] == value
