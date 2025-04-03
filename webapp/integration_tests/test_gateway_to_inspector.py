from fastapi.testclient import TestClient
from webapp.gateway import main
# flake8: noqa

# Create the test client
client = TestClient(main.app)


# Test case to check gateway to static analysis service
def test_gateway_to_static_analysis_no_smell():
    payload = {"code_snippet": "def my_function(): pass"}
    response = client.post(
        "/api/detect_smell_static", json=payload
    )

    assert response.status_code == 200
    assert response.json() == {
        "smells": 'Static analysis returned no data'
    }


# Test case to check gateway to static analysis service
def test_gateway_to_static_analysis_with_smell():
    code_snippet = """
import json
import pandas as pd

def save_as_csv(
    self, train_data, val_data, train_file="train.csv", val_file="val.csv"
):
    pd.DataFrame(train_data).to_csv(train_file, index=False)
    pd.DataFrame(val_data).to_csv(val_file, index=False)
"""

    test_payload = {
        "code_snippet": code_snippet
    }

    # Mocked dataset input for testing
    expected_response = {
        "smells": [
            {
                "function_name": "save_as_csv",
                "line": 8,
                "smell_name": "columns_and_datatype_not_explicitly_set",
                "description": "Pandas' DataFrame or read_csv methods should explicitlyset 'dtype' to avoid unexpected behavior.",
                "additional_info": "Missing explicit 'dtype'in DataFrame call.",
            },
            {
                "function_name": "save_as_csv",
                "line": 9,
                "smell_name": "columns_and_datatype_not_explicitly_set",
                "description": "Pandas' DataFrame or read_csv methods should explicitlyset 'dtype' to avoid unexpected behavior.",
                "additional_info": "Missing explicit 'dtype'in DataFrame call.",
            },
        ]
    }
    response = client.post("/api/detect_smell_static", json=test_payload)
    print(f"Response json: ", response.json())
    assert response.status_code == 200
    assert response.json() == expected_response
