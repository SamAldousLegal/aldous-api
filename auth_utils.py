import json
import os
import requests
import logging
from dotenv import load_dotenv, set_key
from datetime import datetime

# Load environment variables
load_dotenv()

# Create a logger for the authentication process
auth_logger = logging.getLogger("auth_logger")
auth_logger.setLevel(logging.INFO)

# Create a file handler for logging to auth.log
file_handler_auth = logging.FileHandler("logs/auth.log")
file_handler_auth.setLevel(logging.INFO)

# Create a formatter and attach it to the handler
formatter_auth = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
file_handler_auth.setFormatter(formatter_auth)

# Add the handler to the logger
auth_logger.addHandler(file_handler_auth)

def get_api_base_url():
    return os.getenv("API_BASE_URL")

def get_auth_token():
    """Authenticates and retrieves API tokens."""
    api_base_url = get_api_base_url()
    api_username = os.getenv("API_USERNAME")
    api_password = os.getenv("API_PASSWORD")

    if not all([api_base_url, api_username, api_password]):
        auth_logger.error("Missing API environment variables")
        raise ValueError("Missing API environment variables")

    url = f"{api_base_url}/auth/login"
    payload = {"op_id": api_username, "op_password": api_password}

    try:
        response = requests.post(url, json=payload)  # SSL verification enabled by default
        response.raise_for_status()
        tokens = response.json().get("result", {})
        auth_logger.info("Successfully retrieved new auth token.")
        return tokens.get("access_token"), tokens.get("refresh_token")
    except requests.exceptions.RequestException as e:
        auth_logger.error(f"Authentication failed: {e}")
        return None, None

def refresh_auth_token(refresh_token):
    """Uses the refresh token to get a new access token."""
    api_base_url = get_api_base_url()

    if not refresh_token:
        auth_logger.warning("No refresh token available.")
        return None

    url = f"{api_base_url}/auth/refresh"
    headers = {"accept": "*/*", "refresh": refresh_token}

    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        new_token = response.json().get("result", {}).get("access_token")
        auth_logger.info("Successfully refreshed auth token.")
        return new_token
    except requests.exceptions.RequestException as e:
        auth_logger.error(f"Token refresh failed: {e}")
        return None

def save_auth_token(access_token, refresh_token=None):
    """Saves the access and refresh tokens to the .env file."""
    env_path = ".env"

    if access_token:
        set_key(env_path, "AUTH_TOKEN", access_token)
    if refresh_token:
        set_key(env_path, "AUTH_REFRESH_TOKEN", refresh_token)
    
    auth_logger.info("Tokens updated successfully.")

def test_auth_token():
    """Tests the auth token, refreshes if needed, and retrieves a new one if both fail."""
    api_base_url = get_api_base_url()
    access_token = os.getenv("AUTH_TOKEN")
    refresh_token = os.getenv("AUTH_REFRESH_TOKEN")

    headers = {"Authorization": f"Bearer {access_token}"}
    test_url = f"{api_base_url}/auth/profile"

    try:
        response = requests.get(test_url, headers=headers)
        if response.status_code == 200:
            auth_logger.info("Auth token is valid.")
            return access_token

        auth_logger.warning("Auth token invalid, attempting refresh...")
        new_access_token = refresh_auth_token(refresh_token)

        if new_access_token:
            save_auth_token(new_access_token)
            return new_access_token

        auth_logger.warning("Refresh token also failed, getting new auth token...")
        new_access_token, new_refresh_token = get_auth_token()

        if new_access_token and new_refresh_token:
            save_auth_token(new_access_token, new_refresh_token)
            return new_access_token

    except requests.exceptions.RequestException as e:
        auth_logger.error(f"Error testing auth token: {e}")

    auth_logger.error("Failed to authenticate.")
    return None

def get_auth_header():
    """Returns the authorization header with a valid token for API requests."""
    token = test_auth_token()
    if token:
        return {"Authorization": f"Bearer {token}"}
    
    auth_logger.error("Failed to retrieve auth header.")
    return None