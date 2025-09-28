from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    app_name: str = Field(default="Server Controller", env="APP_NAME")
    secret_key: str = Field(default="change-me", env="SECRET_KEY")
    database_url: str = Field(default="sqlite:////data/app.db", env="DATABASE_URL")

    # Initial admin bootstrap (optional)
    admin_email: str | None = Field(default=None, env="ADMIN_EMAIL")
    admin_password: str | None = Field(default=None, env="ADMIN_PASSWORD")

    # Managed container configuration
    managed_image: str = Field(default="nginx:alpine", env="MANAGED_IMAGE")
    managed_name: str = Field(default="managed-server", env="MANAGED_NAME")
    # Comma-separated list of host:container port mappings, e.g. "8080:80,8443:443"
    managed_ports: str = Field(default="8080:80", env="MANAGED_PORTS")
    # Comma-separated KEY=VALUE pairs
    managed_env: str | None = Field(default=None, env="MANAGED_ENV")
    # Comma-separated host_path:container_path[:ro|rw]
    managed_volumes: str | None = Field(default=None, env="MANAGED_VOLUMES")

    class Config:
        env_file = ".env"


settings = Settings()

