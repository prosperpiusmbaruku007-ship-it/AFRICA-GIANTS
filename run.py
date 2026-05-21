import sys
import argparse
from src.common.logging import get_logger
from src.orchestrator.run_pipeline import run_local_data_pipeline

logger = get_logger("cli")

def main():
    parser = argparse.ArgumentParser(
        description="AFRICA GIANTS - LLM Pipeline CLI Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available pipeline sub-commands")
    
    # Scrape command
    subparsers.add_parser("scrape", help="Run Tanzanian websites scraper and format datasets")
    
    # Train command
    subparsers.add_parser("train", help="Run the full orchestrator (data ingestion -> push HF -> run Kaggle)")
    
    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Start the local FastAPI inference API server")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port to run FastAPI server on")
    serve_parser.add_argument("--host", type=str, default="0.0.0.0", help="Host address for FastAPI")
    
    # Deploy command
    subparsers.add_parser("deploy", help="Send reload instruction to local API server")

    # RAG command
    subparsers.add_parser("build-rag", help="Build the local RAG index from processed/eval data")

    # Evaluation command
    eval_parser = subparsers.add_parser("evaluate", help="Run benchmarks and evaluation gate")
    eval_parser.add_argument("--model", type=str, default="", help="Optional model name/path to evaluate")

    # Smoke test command
    smoke_parser = subparsers.add_parser("smoke", help="Run smoke tests against a running API server")
    smoke_parser.add_argument("--port", type=str, default="8000", help="Server port to test")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
        
    if args.command == "scrape":
        logger.info("Executing Scraper and Processing pipeline...")
        success = run_local_data_pipeline()
        if success:
            logger.info("Scrape and data preparation step completed.")
        else:
            logger.error("Scraper step failed.")
            sys.exit(1)
            
    elif args.command == "train":
        logger.info("Triggering full training orchestrator...")
        from src.orchestrator.run_pipeline import main as run_orch
        run_orch()
        
    elif args.command == "serve":
        logger.info(f"Starting server on {args.host}:{args.port}...")
        import uvicorn
        from src.serve.server import app
        uvicorn.run(app, host=args.host, port=args.port)
        
    elif args.command == "deploy":
        logger.info("Triggering hot-reload deployer...")
        from src.deploy.deploy_hf_model import trigger_reload
        trigger_reload()

    elif args.command == "build-rag":
        logger.info("Building local RAG index...")
        from src.rag.retriever import Retriever
        count = Retriever().rebuild()
        logger.info(f"RAG index built with {count} chunks.")

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

if __name__ == "__main__":
    main()
