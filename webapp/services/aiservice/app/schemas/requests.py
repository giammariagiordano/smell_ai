from pydantic import BaseModel


class DetectSmellRequest(BaseModel):
    """
    Schema for the request body to detect code smells using AI analysis.
    """

    code_snippet: str

    class Config:
        schema_extra = {
            "example": {
                "code_snippet":
                "def example_function():\n    print('Hello, world!')",
            }
        }
