from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()

# Middleware for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs for testing/local deployment
AI_ANALYSIS_SERVICE = "http://localhost:8001"
STATIC_ANALYSIS_SERVICE = "http://localhost:8002"
REPORT_SERVICE = "http://localhost:8003"

# Service URLs for docker deployement
""" AI_ANALYSIS_SERVICE = "http://ai_analysis_service:8001"
STATIC_ANALYSIS_SERVICE = "http://static_analysis_service:8002"
REPORT_SERVICE = "http://report_service:8003" """


@app.get("/")
def read_root():
    return {"message": "Welcome to CodeSmile API Gateway"}


# Proxy requests to AI Analysis Service
@app.post("/api/detect_smell_ai")
async def detect_smell_ai(request: dict):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AI_ANALYSIS_SERVICE}/detect_smell_ai",
                json=request,
                timeout=500.0,  # Set a timeout (in seconds)
            )
        return response.json()
    except httpx.RequestError as exc:
        return {
            "success": False,
            "error": f"Request to AI Analysis Service failed: {str(exc)}",
        }
    except httpx.TimeoutException:
        return {"success": False,
                "error": "Request to AI Analysis Service timed out"}


# Proxy requests to Static Analysis Service
@app.post("/api/detect_smell_static")
async def detect_smell_static(request: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{STATIC_ANALYSIS_SERVICE}/detect_smell_static", json=request
        )
    return response.json()


# Proxy requests to Report Service
@app.post("/api/generate_report")
async def generate_report(request: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{REPORT_SERVICE}/generate_report", json=request)
    return response.json()
