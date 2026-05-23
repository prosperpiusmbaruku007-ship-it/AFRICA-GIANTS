import sys
import argparse
from src.common.logging import get_logger
from src.orchestrator.run_pipeline import run_local_data_pipeline

logger = get_logger("cli")


def main():
    parser = argparse.ArgumentParser(
        description="AFRICA GIANTS - LLM Pipeline CLI Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available pipeline sub-commands")

    subparsers.add_parser("scrape", help="Scrape Tanzanian websites and prepare datasets")
    subparsers.add_parser("train", help="Full orchestrator: data → HF upload → Kaggle → evaluate → deploy")

    serve_parser = subparsers.add_parser("serve", help="Start FastAPI inference server")
    serve_parser.add_argument("--port", type=int, default=8000)
    serve_parser.add_argument("--host", type=str, default="0.0.0.0")

    subparsers.add_parser("deploy", help="Hot-reload model weights on running server")
    subparsers.add_parser("build-rag", help="Rebuild RAG vector index from processed/eval data")

    eval_parser = subparsers.add_parser("evaluate", help="Run benchmarks and evaluation gate")
    eval_parser.add_argument("--model", type=str, default="", help="Model name/path to evaluate")

    smoke_parser = subparsers.add_parser("smoke", help="Smoke test a running API server")
    smoke_parser.add_argument("--port", type=str, default="8000")

    subparsers.add_parser("build-dataset", help="Build clean instruction dataset for fine-tuning")

    subparsers.add_parser("feedback-loop", help="Convert collected feedback into training examples")

    sched_parser = subparsers.add_parser("schedule", help="Start the pipeline scheduler (runs on interval)")
    sched_parser.add_argument("--interval", type=str, default="24h", help="Run interval e.g. 24h, 6h, 30m")
    sched_parser.add_argument("--run-once", action="store_true", help="Run immediately then exit")

    registry_parser = subparsers.add_parser("registry", help="Show model registry")
    registry_parser.add_argument("--status", type=str, default=None, help="Filter by status (production/candidate/archived)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "scrape":
        logger.info("Running scrape and data preparation pipeline...")
        success = run_local_data_pipeline()
        if not success:
            sys.exit(1)

    elif args.command == "train":
        logger.info("Triggering full training orchestrator...")
        from src.orchestrator.run_pipeline import main as run_orch
        run_orch(resume=True)

    elif args.command == "serve":
        logger.info("Starting server on %s:%d...", args.host, args.port)
        import uvicorn
        from src.serve.server import app
        uvicorn.run(app, host=args.host, port=args.port)

    elif args.command == "deploy":
        logger.info("Triggering hot-reload deployer...")
        from src.deploy.deploy_hf_model import trigger_reload
        trigger_reload()

    elif args.command == "build-rag":
        logger.info("Building RAG index...")
        from src.rag.retriever import Retriever
        count = Retriever().rebuild()
        logger.info("RAG index built with %d chunks", count)

    elif args.command == "evaluate":
        logger.info("Running evaluation gate...")
        from src.evaluate.eval_gate import evaluate_gate
        passed = evaluate_gate(model_name=args.model)
        if not passed:
            sys.exit(1)

    elif args.command == "smoke":
        logger.info("Running smoke tests...")
        from src.deploy.smoke_test import run_smoke_tests
        success = run_smoke_tests(port=args.port)
        if not success:
            sys.exit(1)

    elif args.command == "build-dataset":
        logger.info("Building clean instruction dataset...")
        from src.process.build_instruction_dataset import build_instruction_dataset
        examples = build_instruction_dataset(include_forums=True)
        logger.info("Built %d instruction examples", len(examples))

    elif args.command == "feedback-loop":
        logger.info("Running feedback loop...")
        from src.orchestrator.feedback_loop import merge_feedback_into_dataset
        added = merge_feedback_into_dataset()
        logger.info("Added %d feedback examples to training dataset", added)

    elif args.command == "schedule":
        if args.run_once:
            from src.orchestrator.scheduler import _run_pipeline
            _run_pipeline()
        else:
            from src.orchestrator.scheduler import start, _parse_interval
            start(_parse_interval(args.interval))

    elif args.command == "registry":
        import json
        from src.registry.model_registry import list_models, get_current
        current = get_current()
        models = list_models(status_filter=args.status)
        print(json.dumps({"current": current, "models": models}, indent=2))


if __name__ == "__main__":
    main()
