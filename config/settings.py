import os
from dotenv import load_dotenv

# Load environment variables from .env at application startup
load_dotenv()


class Settings:
    """
    Centralized configuration management.

    This class loads environment variables and exposes them
    as typed, read-only configuration values across the system.
    """

    # ------------------ Environment ------------------ #
    ENV: str = os.getenv("ENV", "development")

    # ------------------ Secrets ------------------ #
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")

    # ------------------ LLM Configuration ------------------ #
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-3.5-turbo")

    try:
        LLM_TEMPERATURE_DEFAULT: float = float(
            os.getenv("LLM_TEMPERATURE_DEFAULT", "0.7")
        )
    except ValueError:
        LLM_TEMPERATURE_DEFAULT = 0.7

    # ------------------ Feature Flags ------------------ #
    ENABLE_TELEMETRY: bool = (
        os.getenv("ENABLE_TELEMETRY", "true").strip().lower() == "true"
    )


# Singleton instance to be imported by other modules
settings = Settings()
