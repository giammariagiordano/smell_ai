from pydantic import BaseModel
from typing import Dict, List, Union


class GenerateReportResponse(BaseModel):
    """
    Response model for generating reports that returns data for charting.
    """

    report_data: Dict[str, List[Dict[str, Union[str, int]]]]

    class Config:
        schema_extra = {
            "example": {
                "all_projects_combined": [
                    {
                        "smell_name": "Unnecessary DataFrame Operation",
                        "filename": "file1.py",
                        "count": 5,
                    },
                    {
                        "smell_name": "Code Duplication",
                        "filename": "file2.py",
                        "count": 3,
                    },
                ]
            }
        }
