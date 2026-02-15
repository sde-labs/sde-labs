"""
Configuration settings loaded from environment variables.
"""
import os

from dotenv import load_dotenv
from pydantic import BaseModel, field_validator


class Settings(BaseModel):
    """
    Application configuration sourced from environment variables.

    TODO (Week 4): Implement the following:
    - from_env classmethod to read required env vars
    - validators for env, database_url, api_token, and log_level
    """
    env: str
    database_url: str
    api_token: str
    log_level: str = "INFO"

    @classmethod
    def from_env(cls):
        """
        Build Settings from environment variables.

        Local development reads from `.env` via python-dotenv.
        CI (GitHub Actions) should provide the same keys as environment variables.

        Required variables:
        - APP_ENV
        - DATABASE_URL
        - API_TOKEN

        Optional variables:
        - LOG_LEVEL (defaults to INFO)

        TODO: Implement reading and missing-variable handling.
        """
        raise NotImplementedError

    # TODO: Add @field_validator for env
    # Valid values: "dev", "test", "prod"

    # TODO: Add @field_validator for database_url
    # Must end with .db and not be empty

    # TODO: Add @field_validator for api_token
    # Must be non-empty

    # TODO: Add @field_validator for log_level
    # Valid values: DEBUG, INFO, WARNING, ERROR, CRITICAL
