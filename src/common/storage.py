import os
import yaml
import json

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_project_root() -> str:
    """Returns the absolute path to the project root directory."""
    return base_dir

def get_data_path(subfolder: str) -> str:
    """Returns absolute path to a subfolder within the data directory, creating it if needed."""
    path = os.path.join(base_dir, "data", subfolder)
    os.makedirs(path, exist_ok=True)
    return path

def load_yaml_config(config_name: str) -> dict:
    """Loads a YAML configuration file from the config/ directory."""
    path = os.path.join(base_dir, "config", f"{config_name}.yaml")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Configuration file {config_name}.yaml not found at {path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def save_json(data: dict, filepath: str):
    """Saves a dictionary as JSON format to target filepath."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_json(filepath: str) -> dict:
    """Loads a JSON file."""
    if not os.path.exists(filepath):
        return {}
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)
