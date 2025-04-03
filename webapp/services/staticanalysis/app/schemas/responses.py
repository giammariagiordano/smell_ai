from typing import List, Optional, Union
from pydantic import BaseModel


class Smell(BaseModel):
    """
    Represents a detected code smell.
    """

    function_name: str
    line: int
    smell_name: str
    description: str
    additional_info: str


class DetectSmellStaticResponse(BaseModel):
    """
    Schema for the static analysis code smell detection response.
    """
    success: bool
    smells: Optional[Union[List[Smell], str]] = []

    class Config:
        schema_extra = {
            "example": {
                "success": {"true"},
                "smells": [
                    {
                        "function_name": "example_function",
                        "smell_name": "Unnecessary DataFrame Operation",
                        "line": 2,
                        "description":
                        "The column 'b' is created but not used further.",
                        "additional_info":
                        "Consider removing or optimizing the operation.",
                    }
                ],
            }
        }
