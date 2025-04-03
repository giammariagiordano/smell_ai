import pandas as pd


def generate_report_data(projects: list) -> dict:
    """
    Generate aggregated report data for the given projects.
    Args:
        projects (list): List of project data containing smells and files.
    Returns:
        dict: Aggregated report data for charting.
    """
    combined_smells = []

    for project in projects:
        project_data = project.data

        # Add smells from the project to the combined list
        for smell, file in zip(project_data.smells, project_data.files):
            if smell:
                combined_smells.append(
                    {
                        "smell_name": smell.smell_name,
                        "filename": file.name,
                    }
                )

    # Create a DataFrame for analysis
    df = pd.DataFrame(combined_smells)
    if df.empty:
        return {}

    # Aggregate data for charting
    chart_data = df.groupby("smell_name")["filename"].count().reset_index()
    return {"all_projects_combined": chart_data.to_dict(orient="records")}
