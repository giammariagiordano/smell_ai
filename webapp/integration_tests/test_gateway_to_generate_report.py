from fastapi.testclient import TestClient
from webapp.gateway import main

# flake8: noqa

# Create the test client
client = TestClient(main.app)


# Test case to check the generate_report endpoint with valid data
def test_generate_report_valid_data():
    payload = {
        "projects": [
            {
                "name": "Project",
                "data": {
                    "files": [
                        {
                            "name": "1.py",
                            "size": 1024,
                            "type": "python",
                            "path": "/project/1.py",
                        }
                    ],
                    "message": "Analysis completed.",
                    "result": "Success",
                    "smells": [
                        {
                            "function_name": "function",
                            "line": 5,
                            "smell_name": "Unnecessary DataFrame Operation",
                            "description": "Avoid unnecessary operations on DataFrames.",
                            "additional_info": "Consider simplifying the operation.",
                        }
                    ],
                },
            },
        ]
    }

    expected_response = {
        "report_data": {
            "all_projects_combined": [
                {
                    "smell_name": "Unnecessary DataFrame Operation",
                    "filename": 1,
                },
            ]
        }
    }

    response = client.post("/api/generate_report", json=payload)
    assert response.status_code == 200
    assert response.json() == expected_response