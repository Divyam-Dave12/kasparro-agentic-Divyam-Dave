import json
import time
from typing import Dict, Optional, Any

from config.settings import settings


class Telemetry:
    """
    Lightweight telemetry service for the Agentic Content System.

    Responsibilities:
    - Record structured system events and errors
    - Respect ENABLE_TELEMETRY configuration flag
    - Default output backend: console (stdout)

    This is intentionally minimal and deterministic.
    """

    def __init__(self):
        """
        Initialize telemetry based on centralized configuration.
        """
        self.enabled: bool = settings.ENABLE_TELEMETRY

    def log_event(self, name: str, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Records a structured system event.

        Args:
            name: Event identifier (e.g., 'AgentStart', 'LLMCall')
            data: Optional structured payload
        """
        if not self.enabled:
            return

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        payload = ""

        if data:
            try:
                payload = f" | {json.dumps(data, default=str)}"
            except Exception:
                payload = " | <unserializable data>"

        print(f"[TELEMETRY] [{timestamp}] {name}{payload}")

    def log_error(self, message: str) -> None:
        """
        Records an error event.

        Args:
            message: Error description
        """
        if not self.enabled:
            return

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[ERROR] [{timestamp}] {message}")
