from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: str = Field(default="development", alias="ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    service_name: str = "inventory-service"
    inventory_service_host: str = Field(default="0.0.0.0", alias="INVENTORY_SERVICE_HOST")
    inventory_service_port: int = Field(default=8002, alias="INVENTORY_SERVICE_PORT")

    inventory_service_db_url: str = Field(..., alias="INVENTORY_SERVICE_DB_URL")

    inventory_sqs_queue_url: str = Field(..., alias="INVENTORY_SQS_QUEUE_URL")
    inventory_event_queue_url: str = Field(..., alias="INVENTORY_EVENT_QUEUE_URL")
    aws_region: str = Field(default="ap-south-1", alias="AWS_REGION")
    aws_access_key_id: str = Field(default="test", alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(default="test", alias="AWS_SECRET_ACCESS_KEY")
    aws_endpoint_url: str = Field(default="http://localhost:4566", alias="AWS_ENDPOINT_URL")


@lru_cache
def get_settings() -> Settings:
    return Settings()
