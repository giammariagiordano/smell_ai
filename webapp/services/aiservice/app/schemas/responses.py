from pydantic import BaseModel
from typing import List, Optional, Union


class Smell(BaseModel):
    """
    Represents a detected code smell.
    """
    smell_name: str


class DetectSmellResponse(BaseModel):
    """
    Schema for the AI-based code smell detection response.
    """

    code_snippet: str
    success: bool
    smells: Optional[Union[List[Smell], str]] = []

    class Config:
        json_schema_extra = {
            "example": {
                "success": {"true"},
                "code_snippet": "def example_function():\n"
                                "print('Hello, world!')",
                "smells": [
                    {
                        "smell_name": "Unnecessary DataFrame Operation",
                    }
                ],
            }
        }
