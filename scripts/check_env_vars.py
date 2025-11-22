#!/usr/bin/env python3
"""
Check environment variables in local environment and GCP.

Usage:
    python scripts/check_env_vars.py [--service SERVICE_NAME] [--project PROJECT_ID]

Examples:
    python scripts/check_env_vars.py
    python scripts/check_env_vars.py --service copy-that --project copy-that-platform
"""

import argparse
import os
import subprocess

# Required environment variables for Copy That
REQUIRED_VARS = {
    "SECRET_KEY": {
        "required": True,
        "description": "JWT signing key (min 32 chars)",
        "sensitive": True,
    },
    "DATABASE_URL": {
        "required": True,
        "description": "PostgreSQL connection string",
        "sensitive": True,
    },
    "ANTHROPIC_API_KEY": {
        "required": True,
        "description": "Claude API key",
        "sensitive": True,
    },
}

OPTIONAL_VARS = {
    "ACCESS_TOKEN_EXPIRE_MINUTES": {
        "required": False,
        "description": "Access token lifetime",
        "default": "30",
        "sensitive": False,
    },
    "REFRESH_TOKEN_EXPIRE_DAYS": {
        "required": False,
        "description": "Refresh token lifetime",
        "default": "7",
        "sensitive": False,
    },
    "REDIS_URL": {
        "required": False,
        "description": "Redis connection (caching/rate limiting)",
        "sensitive": True,
    },
    "ENVIRONMENT": {
        "required": False,
        "description": "Deployment environment",
        "default": "local",
        "sensitive": False,
    },
    "GCP_PROJECT_ID": {
        "required": False,
        "description": "GCP project identifier",
        "default": "copy-that-platform",
        "sensitive": False,
    },
    "CORS_ORIGINS": {
        "required": False,
        "description": "Allowed CORS origins",
        "sensitive": False,
    },
    "PORT": {
        "required": False,
        "description": "Server port",
        "default": "8000",
        "sensitive": False,
    },
}

ALL_VARS = {**REQUIRED_VARS, **OPTIONAL_VARS}


def check_local_env():
    """Check environment variables in local environment."""
    print("\n" + "=" * 60)
    print("LOCAL ENVIRONMENT")
    print("=" * 60)

    missing_required = []

    for var_name, config in ALL_VARS.items():
        value = os.getenv(var_name)
        required = config.get("required", False)
        default = config.get("default")
        sensitive = config.get("sensitive", False)

        if value:
            if sensitive:
                # Mask sensitive values
                display = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "****"
            else:
                display = value
            status = "\033[92m[SET]\033[0m"
            print(f"  {status} {var_name}: {display}")
        elif default:
            status = "\033[93m[DEFAULT]\033[0m"
            print(f"  {status} {var_name}: {default} (using default)")
        else:
            if required:
                status = "\033[91m[MISSING]\033[0m"
                missing_required.append(var_name)
            else:
                status = "\033[90m[NOT SET]\033[0m"
            print(f"  {status} {var_name}: - ({config['description']})")

    if missing_required:
        print(f"\n\033[91mWARNING: Missing required variables: {', '.join(missing_required)}\033[0m")
    else:
        print("\n\033[92mAll required variables are set.\033[0m")

    return len(missing_required) == 0


def run_gcloud(args: list) -> tuple[bool, str]:
    """Run a gcloud command and return success status and output."""
    try:
        result = subprocess.run(
            ["gcloud"] + args,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout.strip()
    except FileNotFoundError:
        return False, "gcloud CLI not found"
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)


def check_cloud_run(service: str, project: str, region: str = "us-central1"):
    """Check environment variables in Cloud Run service."""
    print("\n" + "=" * 60)
    print(f"CLOUD RUN SERVICE: {service}")
    print(f"Project: {project}, Region: {region}")
    print("=" * 60)

    # Get service configuration
    success, output = run_gcloud([
        "run", "services", "describe", service,
        "--project", project,
        "--region", region,
        "--format", "yaml"
    ])

    if not success:
        print(f"\033[91mFailed to get Cloud Run service: {output}\033[0m")
        print("\nMake sure:")
        print("  1. gcloud CLI is installed and authenticated")
        print("  2. Service name and project are correct")
        print("  3. Run: gcloud auth login")
        return False

    # Parse environment variables from output
    env_vars_found = set()
    secrets_found = set()

    in_env_section = False
    for line in output.split("\n"):
        line = line.strip()

        if "env:" in line:
            in_env_section = True
            continue

        if in_env_section:
            if line.startswith("- name:"):
                var_name = line.replace("- name:", "").strip()
                env_vars_found.add(var_name)
            elif line.startswith("name:"):
                var_name = line.replace("name:", "").strip()
                env_vars_found.add(var_name)
            elif "secretKeyRef:" in line:
                # Mark previous var as a secret
                if env_vars_found:
                    secrets_found.add(list(env_vars_found)[-1])
            elif line and not line.startswith("-") and not line.startswith("value"):
                in_env_section = False

    # Display results
    for var_name in ALL_VARS:
        config = ALL_VARS[var_name]
        required = config.get("required", False)

        if var_name in env_vars_found:
            if var_name in secrets_found:
                status = "\033[92m[SECRET]\033[0m"
                print(f"  {status} {var_name}: (from Secret Manager)")
            else:
                status = "\033[92m[SET]\033[0m"
                print(f"  {status} {var_name}")
        else:
            if required:
                status = "\033[91m[MISSING]\033[0m"
            else:
                status = "\033[90m[NOT SET]\033[0m"
            print(f"  {status} {var_name}")

    return True


def check_secret_manager(project: str):
    """Check secrets in GCP Secret Manager."""
    print("\n" + "=" * 60)
    print(f"SECRET MANAGER: {project}")
    print("=" * 60)

    # List all secrets
    success, output = run_gcloud([
        "secrets", "list",
        "--project", project,
        "--format", "value(name)"
    ])

    if not success:
        print(f"\033[91mFailed to list secrets: {output}\033[0m")
        return False

    secrets = set(output.split("\n")) if output else set()

    print("\nFound secrets:")
    for secret in sorted(secrets):
        if secret:
            print(f"  \033[92m[EXISTS]\033[0m {secret}")

    # Check which expected secrets are missing
    missing = []
    for var_name, config in ALL_VARS.items():
        if config.get("sensitive", False):
            # Check various naming conventions
            found = any(
                s in secrets for s in [
                    var_name,
                    var_name.lower(),
                    var_name.lower().replace("_", "-"),
                ]
            )
            if not found and config.get("required", False):
                missing.append(var_name)

    if missing:
        print(f"\n\033[93mSuggested secrets to create: {', '.join(missing)}\033[0m")

    return True


def check_env_file():
    """Check for .env files in the project."""
    print("\n" + "=" * 60)
    print("LOCAL .env FILES")
    print("=" * 60)

    env_files = [".env", ".env.local", ".env.development", ".env.staging", ".env.production"]
    found_files = []

    for env_file in env_files:
        if os.path.exists(env_file):
            found_files.append(env_file)
            print(f"  \033[92m[FOUND]\033[0m {env_file}")

            # Check which vars are defined
            with open(env_file) as f:
                defined = set()
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        var_name = line.split("=")[0].strip()
                        defined.add(var_name)

                if defined:
                    print(f"           Defines: {', '.join(sorted(defined))}")
        else:
            print(f"  \033[90m[NOT FOUND]\033[0m {env_file}")

    if not found_files:
        print("\n\033[93mNo .env files found. Create one for local development.\033[0m")

    return len(found_files) > 0


def main():
    parser = argparse.ArgumentParser(
        description="Check environment variables for Copy That platform"
    )
    parser.add_argument(
        "--service",
        default="copy-that",
        help="Cloud Run service name (default: copy-that)"
    )
    parser.add_argument(
        "--project",
        default=os.getenv("GCP_PROJECT_ID", "copy-that-platform"),
        help="GCP project ID"
    )
    parser.add_argument(
        "--region",
        default="us-central1",
        help="GCP region (default: us-central1)"
    )
    parser.add_argument(
        "--skip-gcp",
        action="store_true",
        help="Skip GCP checks (local only)"
    )

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("COPY THAT - ENVIRONMENT VARIABLE CHECK")
    print("=" * 60)

    # Check local environment
    check_env_file()
    local_ok = check_local_env()

    # Check GCP if not skipped
    if not args.skip_gcp:
        check_cloud_run(args.service, args.project, args.region)
        check_secret_manager(args.project)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    if local_ok:
        print("\033[92mLocal environment is properly configured.\033[0m")
    else:
        print("\033[91mLocal environment is missing required variables.\033[0m")
        print("\nTo fix, create a .env file with:")
        print("  SECRET_KEY=your-secret-key-at-least-32-characters")
        print("  DATABASE_URL=postgresql+asyncpg://...")
        print("  ANTHROPIC_API_KEY=sk-ant-...")

    print()


if __name__ == "__main__":
    main()
