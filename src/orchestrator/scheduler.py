"""
Pipeline scheduler — runs the full pipeline on a configurable cron interval.

Usage:
    python -m src.orchestrator.scheduler            # uses config/base.yaml schedule
    python -m src.orchestrator.scheduler --interval 24h
    python -m src.orchestrator.scheduler --run-once  # run immediately then exit
"""
import argparse
import time

import schedule

from src.common.logging import get_logger
from src.common.storage import load_yaml_config

logger = get_logger("orchestrator.scheduler")


def _run_pipeline() -> None:
    logger.info("Scheduler triggering pipeline run...")
    try:
        from src.orchestrator.run_pipeline import main
        main(resume=False)
        logger.info("Scheduled pipeline run completed")
    except Exception as e:
        logger.error("Scheduled pipeline run failed: %s", e)


def _parse_interval(interval_str: str) -> int:
    """Parse interval string like '24h', '6h', '30m' into seconds."""
    interval_str = interval_str.strip().lower()
    if interval_str.endswith("h"):
        return int(interval_str[:-1]) * 3600
    if interval_str.endswith("m"):
        return int(interval_str[:-1]) * 60
    if interval_str.endswith("d"):
        return int(interval_str[:-1]) * 86400
    return int(interval_str)


def start(interval_seconds: int = 86400) -> None:
    """Start the scheduler loop. Blocks forever."""
    hours = interval_seconds / 3600
    logger.info("Scheduler started — pipeline will run every %.1f hours", hours)

    schedule.every(interval_seconds).seconds.do(_run_pipeline)

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Africa Giants pipeline scheduler")
    parser.add_argument("--interval", default="24h", help="Run interval e.g. 24h, 6h, 30m")
    parser.add_argument("--run-once", action="store_true", help="Run immediately and exit")
    args = parser.parse_args()

    if args.run_once:
        _run_pipeline()
    else:
        try:
            config = load_yaml_config("base")
            default_interval = config.get("scheduler", {}).get("interval", args.interval)
        except Exception:
            default_interval = args.interval
        start(_parse_interval(default_interval))
