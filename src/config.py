from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    REDIS_URL: str = "redis://localhost:6379/0"

    # location of the env config file
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",  # do not read extra attributes from env file
    )

Config = Settings()
