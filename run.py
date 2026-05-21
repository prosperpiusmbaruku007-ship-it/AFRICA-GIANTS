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

if __name__ == "__main__":
    main()
