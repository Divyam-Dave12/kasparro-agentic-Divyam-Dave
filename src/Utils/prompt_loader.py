import os
import yaml
from typing import Dict, Any

def load_prompts(config_path: str = "config/prompts.yaml") -> Dict[str, Any]:
    """Loads system prompts from a YAML configuration file."""
    if not os.path.exists(config_path):
        print(f"⚠️ Warning: Config file not found at {config_path}")
        return {}

    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file) or {}
    except Exception as e:
        print(f"❌ Error loading prompts: {e}")
        return {}