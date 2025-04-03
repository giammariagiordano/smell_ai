import tempfile
import os
import pandas as pd
# when running locally/testing
from webapp.services.staticanalysis.app.schemas.responses import Smell
# when deploying in docker
""" from app.schemas.responses import Smell """
from components.inspector import Inspector

OUTPUT_DIR = "output"
inspector = Inspector(output_path=OUTPUT_DIR)


def detect_static(code_snippet: str) -> dict:
    try:
        # Create a temporary file to analyze the code snippet
        with tempfile.NamedTemporaryFile(
            suffix=".py", delete=False, mode="w"
        ) as temp_file:
            temp_file.write(code_snippet)
            temp_file_path = temp_file.name

        smells_df: pd.DataFrame = inspector.inspect(temp_file_path)

        # Handle cases with no results
        if smells_df.empty:
            return {"success": True,
                    "response": "Static analysis returned no data"}

        smells = [
            Smell(
                function_name=row["function_name"],
                line=row["line"],
                smell_name=row["smell_name"],
                description=row["description"],
                additional_info=row["additional_info"],
            )
            for _, row in smells_df.iterrows()
        ]

        # Clean up the temporary file
        os.remove(temp_file_path)

        return {"success": True, "response": smells}

    except Exception as e:
        return {"success": False, "response": str(e)}
