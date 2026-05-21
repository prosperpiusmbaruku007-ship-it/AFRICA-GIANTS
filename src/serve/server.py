import os
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from src.serve.inference import InferenceEngine
from src.common.logging import get_logger
from src.common.secrets import get_reload_token

logger = get_logger("server")

app = FastAPI(
    title="AFRICA GIANTS - Inference API",
    description="Serving Swahili/English business insights and regulatory information"
)

# Instantiate inference engine globally
engine = InferenceEngine()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.3
    max_tokens: Optional[int] = 256

class ReloadRequest(BaseModel):
    model_name_or_path: str

def verify_token(x_reload_token: Optional[str] = Header(None)):
    """Secures the reload endpoint using an API key in header."""
    expected_token = get_reload_token()
    if x_reload_token != expected_token:
        raise HTTPException(status_code=403, detail="Invalid or missing X-Reload-Token")

@app.get("/health")
def health_check():
    """Simple health monitoring endpoint."""
    return {
        "status": "healthy",
        "model": engine.model_name,
        "mock_mode": engine.is_mock
    }

@app.post("/v1/chat/completions")
def chat_completions(request: ChatCompletionRequest):
    """OpenAI-compatible chat completion endpoint."""
    logger.info(f"Received request for model {request.model}")
    
    # Reconstruct system and user message
    system_prompt = ""
    user_prompt = ""
    
    for msg in request.messages:
        if msg.role == "system":
            system_prompt = msg.content
        elif msg.role == "user":
            user_prompt = msg.content
            
    if not user_prompt:
        raise HTTPException(status_code=400, detail="Missing user prompt in messages list")
        
    try:
        response_text = engine.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=request.max_tokens
        )
        
        return {
            "id": "chatcmpl-giants",
            "object": "chat.completion",
            "created": 1700000000,
            "model": engine.model_name,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_text
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": len(user_prompt) // 4,
                "completion_tokens": len(response_text) // 4,
                "total_tokens": (len(user_prompt) + len(response_text)) // 4
            }
        }
    except Exception as e:
        logger.error(f"Generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/reload", dependencies=[Depends(verify_token)])
def reload_model(request: ReloadRequest):
    """Triggers in-memory model hot-swapping."""
    logger.info(f"Deployer requested model reload to {request.model_name_or_path}")
    try:
        engine.reload_model(request.model_name_or_path)
        return {
            "status": "success",
            "message": f"Successfully reloaded model to {request.model_name_or_path}",
            "current_model": engine.model_name
        }
    except Exception as e:
        logger.error(f"Reload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Reload failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
