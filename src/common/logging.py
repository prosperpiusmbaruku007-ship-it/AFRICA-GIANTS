import logging
import os
import yaml

def get_logger(name: str) -> logging.Logger:
    """Configures and returns a logger instance based on configuration."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    # Load configuration
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    config_path = os.path.join(base_dir, "config", "base.yaml")
    
    level = "INFO"
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file = os.path.join(base_dir, "logs", "pipeline.log")

    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
                level = config.get("logging", {}).get("level", "INFO")
                log_format = config.get("logging", {}).get("format", log_format)
                log_file_rel = config.get("logging", {}).get("file", "logs/pipeline.log")
                log_file = os.path.join(base_dir, log_file_rel)
        except Exception:
            pass

    # Create log directory if not exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Set log level
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)

    # Console Handler
    c_handler = logging.StreamHandler()
    c_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(c_handler)

    # File Handler
    try:
        f_handler = logging.FileHandler(log_file, encoding="utf-8")
        f_handler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(f_handler)
    except Exception as e:
        print(f"Failed to initialize file logger: {e}")

    return logger
