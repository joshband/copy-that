import logging
import os
from pathlib import Path

from dotenv import load_dotenv, set_key


class DeploymentConfig:
    _logger = logging.getLogger(__name__)

    @staticmethod
    def _validate_environment(env: str) -> str:
        """
        Validate and normalize the environment string.

        Args:
            env (str): The environment to validate.

        Returns:
            str: A validated environment string.
        """
        valid_envs = {"local", "staging", "production"}
        normalized_env = env.lower()
        return normalized_env if normalized_env in valid_envs else "local"

    @staticmethod
    def detect_environment() -> str:
        """
        Detect the current deployment environment.

        Returns:
            str: One of 'local', 'staging', 'production'
        """
        # Priority order:
        # 1. Explicit environment variable
        # 2. Deployment context
        # 3. Default to local
        env = os.getenv("ENVIRONMENT", "local")

        # GitHub Actions context detection
        if os.getenv("GITHUB_ACTIONS") == "true":
            event_name = os.getenv("GITHUB_EVENT_NAME", "")
            github_ref = os.getenv("GITHUB_REF", "")

            # Pull request scenario
            if event_name == "pull_request":
                return "staging"
            # Main branch push scenario
            elif github_ref == "refs/heads/main":
                return "production"

        return DeploymentConfig._validate_environment(env)

    @staticmethod
    def configure_redis(
        env: str | None = None, env_file_path: str | Path | None = None
    ) -> dict[str, str]:
        """
        Configure Redis connection based on environment.

        Args:
            env (str, optional): Specific environment to configure.
                                 Defaults to auto-detection.
            env_file_path (str or Path, optional): Path to .env file.
                                                   Defaults to auto-detection.

        Returns:
            Dict[str, str]: The Redis configuration for the given environment.
        """
        if env is None:
            env = DeploymentConfig.detect_environment()

        # Validate environment
        env = DeploymentConfig._validate_environment(env)

        # Determine .env file path
        if env_file_path is None:
            env_file_path = Path(".env").resolve()
        else:
            env_file_path = Path(env_file_path)

        # Try to create directory
        try:
            env_file_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            DeploymentConfig._logger.error(f"Failed to create directory for {env_file_path}")
            # Fallback to default .env file
            env_file_path = Path(".env").resolve()

        # Ensure the file exists
        try:
            env_file_path.touch(exist_ok=True)
        except Exception:
            DeploymentConfig._logger.error("Failed to create file")
            # Fallback to default .env file
            env_file_path = Path(".env").resolve()
            env_file_path.touch(exist_ok=True)

        # Load existing environment
        load_dotenv(env_file_path, override=True)

        # Redis configuration mappings with unique configurations
        redis_configs: dict[str, dict[str, str]] = {
            "local": {
                "REDIS_URL": "redis://localhost:6379/0",
                "CELERY_BROKER_URL": "redis://localhost:6379/1",
                "CELERY_RESULT_BACKEND": "redis://localhost:6379/2",
            },
            "staging": {
                "REDIS_URL": "redis://default:AZnUAAIncDI2ZDM0Y2Y1ZTBjYWI0NDBlOGFlNjYwMWE1OTAzZWY1Y3AyMzkzODA@literate-javelin-39380.upstash.io:6379",
                "CELERY_BROKER_URL": "redis://default:AZnUAAIncDI2ZDM0Y2Y1ZTBjYWI0NDBlOGFlNjYwMWE1OTAzZWY1Y3AyMzkzODA@literate-javelin-39380.upstash.io:6379",
                "CELERY_RESULT_BACKEND": "redis://default:AZnUAAIncDI2ZDM0Y2Y1ZTBjYWI0NDBlOGFlNjYwMWE1OTAzZWY1Y3AyMzkzODA@literate-javelin-39380.upstash.io:6379",
            },
            "production": {
                # Use a different Upstash Redis instance for production
                "REDIS_URL": "redis://default:PRODUCTION_TOKEN@production-redis.upstash.io:6379",
                "CELERY_BROKER_URL": "redis://default:PRODUCTION_TOKEN@production-redis.upstash.io:6379",
                "CELERY_RESULT_BACKEND": "redis://default:PRODUCTION_TOKEN@production-redis.upstash.io:6379",
            },
        }

        # Select configuration
        config = redis_configs.get(env, redis_configs["local"])

        # Update .env file
        try:
            for key, value in config.items():
                set_key(str(env_file_path), key, value)
        except Exception:
            DeploymentConfig._logger.error(f"Failed to update key {key}")

        DeploymentConfig._logger.info(f"Configured Redis for {env} environment")
        return config

    @classmethod
    def print_current_config(cls) -> None:
        """Print current environment and Redis configuration."""
        env = cls.detect_environment()
        print(f"Current Environment: {env}")
        print("Redis Configuration:")
        print(f"  REDIS_URL: {os.getenv('REDIS_URL', 'Not set')}")
        print(f"  CELERY_BROKER_URL: {os.getenv('CELERY_BROKER_URL', 'Not set')}")
        print(f"  CELERY_RESULT_BACKEND: {os.getenv('CELERY_RESULT_BACKEND', 'Not set')}")


# If script is run directly, demonstrate configuration
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    DeploymentConfig.configure_redis()
    DeploymentConfig.print_current_config()
