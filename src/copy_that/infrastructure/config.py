import logging
import os

from decouple import Config, RepositoryEmpty, RepositoryEnv

logger = logging.getLogger(__name__)


class AppConfig:
    _VALID_ENVIRONMENTS = {"local", "staging", "production"}

    def __init__(self, env_file=None):
        """
        Initialize configuration with optional env file.

        Args:
            env_file (str, optional): Path to .env file.
                                      Defaults to searching for .env in project root.
        """
        try:
            # Try to load from specific env file if provided
            if env_file and os.path.exists(env_file):
                self._config = Config(RepositoryEnv(env_file))
                # Explicitly set environment if file is provided
                try:
                    environment = self._config("ENVIRONMENT", default="local")
                    os.environ["ENVIRONMENT"] = environment
                except Exception as e:
                    logger.debug(f"Could not set ENVIRONMENT from env file: {e}")
            else:
                # Search for .env file in common locations
                possible_paths = [".env", ".env.local", "~/.env", "/etc/copy_that/.env"]

                for path in possible_paths:
                    try:
                        expanded_path = os.path.expanduser(path)
                        if os.path.exists(expanded_path):
                            self._config = Config(RepositoryEnv(expanded_path))
                            logger.debug(f"Loaded configuration from {expanded_path}")
                            break
                    except Exception as e:
                        logger.debug(f"Could not load config from {path}: {e}")
                        continue
                else:
                    # Fallback to empty config if no env file found
                    logger.debug("No .env file found, using empty configuration")
                    self._config = Config(RepositoryEmpty())
        except Exception as e:
            # Ultimate fallback
            logger.warning(f"Configuration initialization failed, using empty config: {e}")
            self._config = Config(RepositoryEmpty())

    def _validate_environment(self, env):
        """
        Validate and normalize environment.

        Args:
            env (str): Environment to validate.

        Returns:
            str: Validated environment or 'local' if invalid.
        """
        normalized_env = env.lower()
        return normalized_env if normalized_env in self._VALID_ENVIRONMENTS else "local"

    def __call__(self, key, default=None):
        """
        Proxy method to access config values directly.

        Args:
            key (str): Configuration key
            default (Any, optional): Default value if key not found

        Returns:
            Any: Configuration value or default
        """
        # Special handling for environment
        if key == "ENVIRONMENT":
            env = os.getenv(key, default or "local").lower()
            return self._validate_environment(env)

        return self._config(key, default=default)

    def get_redis_config(self, env=None):
        """
        Get Redis configuration for a specific environment.

        Args:
            env (str, optional): Environment name.
                                 Defaults to environment variable or 'local'.

        Returns:
            dict: Redis configuration dictionary
        """
        # Determine environment
        if env is None:
            env = self("ENVIRONMENT", default="local")

        # Validate environment
        env = self._validate_environment(env)

        # Redis configurations - only local has defaults, others require env vars
        configs = {
            "local": {
                "REDIS_URL": "redis://localhost:6379/0",
                "CELERY_BROKER_URL": "redis://localhost:6379/1",
                "CELERY_RESULT_BACKEND": "redis://localhost:6379/2",
            },
            "staging": {
                # Staging credentials must be set via environment variables
                "REDIS_URL": os.getenv("REDIS_URL", ""),
                "CELERY_BROKER_URL": os.getenv("CELERY_BROKER_URL", ""),
                "CELERY_RESULT_BACKEND": os.getenv("CELERY_RESULT_BACKEND", ""),
            },
            "production": {
                # Production credentials must be set via environment variables
                "REDIS_URL": os.getenv("REDIS_URL", ""),
                "CELERY_BROKER_URL": os.getenv("CELERY_BROKER_URL", ""),
                "CELERY_RESULT_BACKEND": os.getenv("CELERY_RESULT_BACKEND", ""),
            },
        }

        # Warn if credentials are missing for non-local environments
        if env != "local":
            env_config = configs.get(env, configs["local"])
            if not env_config.get("REDIS_URL"):
                logger.warning(
                    f"REDIS_URL not set for {env} environment. Set via environment variable."
                )

        # Override with environment-specific variables if they exist
        env_config = configs.get(env, configs["local"])

        # Allow manual override via environment variables
        env_config["REDIS_URL"] = self._config(
            f"{env.upper()}_REDIS_URL", default=env_config["REDIS_URL"]
        )
        env_config["CELERY_BROKER_URL"] = self._config(
            f"{env.upper()}_CELERY_BROKER_URL", default=env_config["CELERY_BROKER_URL"]
        )
        env_config["CELERY_RESULT_BACKEND"] = self._config(
            f"{env.upper()}_CELERY_RESULT_BACKEND", default=env_config["CELERY_RESULT_BACKEND"]
        )

        return env_config


# Global configuration instance
config = AppConfig()


# Easy access function for Redis config
def get_redis_config(env=None):
    """Convenience function to get Redis configuration."""
    return config.get_redis_config(env)


# If script is run directly, demonstrate configuration
if __name__ == "__main__":
    print("Current Environment:", config("ENVIRONMENT", "local"))
    print("Redis Configuration:", get_redis_config())
