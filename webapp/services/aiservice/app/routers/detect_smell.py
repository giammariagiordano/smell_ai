import ast
import logging
from fastapi import APIRouter, HTTPException
# When running locally
from webapp.services.aiservice.app.schemas.requests import DetectSmellRequest
from webapp.services.aiservice.app.schemas.responses import DetectSmellResponse
from webapp.services.aiservice.app.utils.model import Model
# When running with Docker
"""from app.schemas.requests import DetectSmellRequest
from app.schemas.responses import DetectSmellResponse
from app.utils.model import Model"""

router = APIRouter()

# Initialize the AI model instance
model_instance = Model()

# Logging setup
logger = logging.getLogger("ModelLoader")
logging.basicConfig(level=logging.INFO)


@router.post("/detect_smell_ai", response_model=DetectSmellResponse)
async def detect_smell_ai(payload: DetectSmellRequest):
    """
    Endpoint for detecting code smells using AI-based analysis.
    """
    code_snippet = payload.code_snippet

    if not validate_code_snippet(code_snippet):
        raise HTTPException(
            status_code=400,
            detail="Invalid Python syntax in the code snippet.",
        )

    # Perform AI-based analysis
    analysis_result = model_instance.detect_code_smell(code_snippet)

    if not analysis_result["success"]:
        raise HTTPException(
            status_code=500,
            detail="Error during AI analysis",
        )

    return DetectSmellResponse(
        code_snippet=code_snippet,
        success=analysis_result["success"],
        smells=analysis_result["smells"],
    )


def validate_code_snippet(code_snippet: str) -> bool:
    """
    Validate the input code snippet for syntax correctness.
    """
    try:
        ast.parse(code_snippet)
        return True
    except SyntaxError as e:
        logger.error(f"Syntax error in the code snippet: {e}")
        return False
