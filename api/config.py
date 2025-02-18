from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    LOG_LEVEL: str
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str

    TRAVEL_API_KEY: str
    TRAVEL_API_SECRET: str

    REDIS_HOST: str
    REDIS_PORT: int

    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = True

    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    DOMAIN: str
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


Config = Settings()

broker_url = f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}/0"
result_backend = f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}/0"
broker_connection_retry_on_startup = True
