import os
import logging
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# -------------------------------------------------
# Base paths
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------------------------------
# Logging
# -------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------------------------
# Load base 
# -------------------------------------------------
base_env_file = BASE_DIR / ".env"
print(base_env_file)
if base_env_file.exists():
    load_dotenv(base_env_file)
    logger.info("Loaded base .env file")
else:
    logger.warning(".env not found, using system environment variables")

# -------------------------------------------------
# Environment selection
# -------------------------------------------------
ENV = os.getenv("ENV", "dev").lower()

env_file_map = {
    "dev": BASE_DIR / ".env_dev",
    "prod": BASE_DIR / ".env_prod",
}

env_file = env_file_map.get(ENV)

if env_file and env_file.exists():
    load_dotenv(env_file, override=True)
    logger.info(f"Loaded environment file: {env_file.name}")
else:
    logger.warning(f"No environment-specific .env file found for ENV={ENV}")


# -------------------------------------------------
# Helpers
# -------------------------------------------------
def str_to_bool(value: str) -> bool:
    return value.lower() in {"1", "true", "yes", "on"}


# -------------------------------------------------
# Configuration Dataclass
# -------------------------------------------------
@dataclass(frozen=True)
class Configuration:
    """Application configuration loaded from environment variables"""

    ENV: str
    DEBUG: bool
    APP_NAME: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ACCESS_TOKEN_SLIDE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_NAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_DRIVER: str
    DATABASE_URL: str
    DATABASE_URL_SYNC: str

    FRONTEND_URL: str

    EMAIL_BACKEND: str
    SMTP_SERVER: str
    SMTP_PORT: int
    USE_TLS: bool
    SMTP_USERNAME: str
    SMTP_PASSWORD: str

    LOG_LEVEL: str

    # Redis
    REDIS_HOST: str
    REDIS_ACCESS_TYPE: str
    REDIS_PORT: str
    REDIS_PWD: str
    REDIS_DB: int

    @classmethod
    def load(cls) -> "Configuration":
        database_host = os.getenv("DATABASE_HOST")
        database_port = int(os.getenv("DATABASE_PORT"))
        database_name = os.getenv("DATABASE_NAME")
        database_user = os.getenv("DATABASE_USER")
        database_password = os.getenv("DATABASE_PASSWORD")
        database_driver = os.getenv("DATABASE_DRIVER")

        # Build DATABASE_URL dynamically
        database_url = os.getenv(
            "DATABASE_URL",
            f"{database_driver}://"
            f"{database_user}:{database_password}@"
            f"{database_host}:{database_port}/"
            f"{database_name}",
        )
        database_url_sync = os.getenv(
            "DATABASE_URL",
            f"postgresql+psycopg2://"
            f"{database_user}:{database_password}@"
            f"{database_host}:{database_port}/"
            f"{database_name}",
        )
        return cls(
            ENV=os.getenv("ENV", "dev"),
            DEBUG=str_to_bool(os.getenv("DEBUG", "false")),
            APP_NAME=os.getenv("APP_NAME", "Fit Finance API"),

            # JWT Authentication configuration
            SECRET_KEY=os.getenv("SECRET_KEY"),
            ALGORITHM=os.getenv("ALGORITHM"),
            ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")),
            ACCESS_TOKEN_SLIDE_MINUTES=int(os.getenv("ACCESS_TOKEN_SLIDE_MINUTES")),
            REFRESH_TOKEN_EXPIRE_DAYS=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")),

            # Google Oauth
            GOOGLE_CLIENT_ID=os.getenv("CLIENT_ID"),
            GOOGLE_CLIENT_SECRET=os.getenv("CLIENT_SECRET"),

            DATABASE_HOST=database_host,
            DATABASE_PORT=database_port,
            DATABASE_NAME=database_name,
            DATABASE_USER=database_user,
            DATABASE_PASSWORD=database_password,
            DATABASE_DRIVER=database_driver,
            DATABASE_URL=database_url,
            DATABASE_URL_SYNC=database_url_sync,

            FRONTEND_URL=os.getenv("FRONTEND_URL"),

            EMAIL_BACKEND=os.getenv("EMAIL_BACKEND"),
            SMTP_SERVER=os.getenv("SMTP_SERVER"),
            SMTP_PORT=int(os.getenv("SMTP_PORT")),
            USE_TLS=bool(os.getenv("USE_TLS")),
            SMTP_USERNAME=os.getenv("SMTP_USERNAME"),
            SMTP_PASSWORD=os.getenv("SMTP_PASSWORD"),

            # Redis
            REDIS_HOST=os.getenv("REDIS_HOST"),
            REDIS_ACCESS_TYPE=os.getenv("REDIS_ACCESS_TYPE"),
            REDIS_PORT=os.getenv("REDIS_PORT"),
            REDIS_PWD=os.getenv("REDIS_PWD"),
            REDIS_DB=int(os.getenv("REDIS_DB")),

            LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO"),

        )
