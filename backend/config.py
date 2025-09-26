import os
import boto3
import json
from botocore.exceptions import ClientError

# --- Configuration --- #

# It's good practice to have a prefix for your parameters/secrets
PARAM_PREFIX = "/n11696630/prod"

# 1. Parameters for AWS Parameter Store (non-sensitive config)
PARAMETER_STORE_MAP = {
    f"{PARAM_PREFIX}/COGNITO_REGION": "COGNITO_REGION",
    f"{PARAM_PREFIX}/COGNITO_USER_POOL_ID": "COGNITO_USER_POOL_ID",
    f"{PARAM_PREFIX}/COGNITO_APP_CLIENT_ID": "COGNITO_APP_CLIENT_ID",
    f"{PARAM_PREFIX}/S3_BUCKET_NAME": "S3_BUCKET_NAME",
    f"{PARAM_PREFIX}/MEMCACHED_ENDPOINT": "MEMCACHED_ENDPOINT",
}

# 2. Secrets for AWS Secrets Manager (API keys, credentials)
SECRETS_MANAGER_MAP = {
    # This is the name of the secret in Secrets Manager
    f"{PARAM_PREFIX}/api_keys": {
        # This is the key within the secret's JSON value
        "PEXELS_API_KEY": "PEXELS_API_KEY"
    }
}

# --- Loading Logic --- #

def load_config():
    """
    Loads all configuration from both Parameter Store and Secrets Manager.
    This should be called once at application startup.
    """
    print("--- Starting Configuration Load ---")
    _load_from_parameter_store()
    _load_from_secrets_manager()
    print("--- Finished Configuration Load ---")

def _load_from_parameter_store():
    """Fetches configuration from AWS Parameter Store and loads them into environment variables."""
    print("Loading from AWS Parameter Store...")
    region = os.getenv("AWS_REGION", "ap-southeast-2")
    ssm_client = boto3.client("ssm", region_name=region)

    for param_name, env_var_name in PARAMETER_STORE_MAP.items():
        if env_var_name in os.environ:
            print(f"Parameter Store: Skipping '{param_name}', as '{env_var_name}' is already set.")
            continue
        try:
            response = ssm_client.get_parameter(Name=param_name)
            param_value = response["Parameter"]["Value"]
            os.environ[env_var_name] = param_value
            print(f"Parameter Store: Loaded '{param_name}' into env var '{env_var_name}'.")
        except ClientError as e:
            if e.response["Error"]["Code"] == "ParameterNotFound":
                print(f"CRITICAL: Parameter '{param_name}' not found in Parameter Store.")
            else:
                print(f"ERROR: Could not fetch parameter '{param_name}': {e}")

def _load_from_secrets_manager():
    """Fetches secrets from AWS Secrets Manager and loads them into environment variables."""
    print("Loading from AWS Secrets Manager...")
    region = os.getenv("AWS_REGION", "ap-southeast-2")
    secrets_client = boto3.client("secretsmanager", region_name=region)

    for secret_name, key_map in SECRETS_MANAGER_MAP.items():
        try:
            response = secrets_client.get_secret_value(SecretId=secret_name)
            secret_string = response['SecretString']
            secrets = json.loads(secret_string)

            for secret_key, env_var_name in key_map.items():
                if env_var_name in os.environ:
                    print(f"Secrets Manager: Skipping '{secret_key}', as '{env_var_name}' is already set.")
                    continue
                if secret_key in secrets:
                    os.environ[env_var_name] = secrets[secret_key]
                    print(f"Secrets Manager: Loaded key '{secret_key}' from secret '{secret_name}' into env var.")
                else:
                    print(f"CRITICAL: Key '{secret_key}' not found in secret '{secret_name}'.")

        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                print(f"CRITICAL: Secret '{secret_name}' not found in Secrets Manager.")
            else:
                print(f"ERROR: Could not fetch secret '{secret_name}': {e}")