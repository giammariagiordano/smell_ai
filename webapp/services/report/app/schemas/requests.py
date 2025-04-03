from pydantic import BaseModel
from typing import List


class SmellInfo(BaseModel):
    function_name: str
    line: int
    smell_name: str
    description: str
    additional_info: str


class FileInfo(BaseModel):
    name: str
    size: int
    type: str
    path: str


class ProjectData(BaseModel):
    files: List[FileInfo]
    message: str
    result: str
    smells: List[SmellInfo]


class Project(BaseModel):
    name: str
    data: ProjectData


class GenerateReportRequest(BaseModel):
    """
    Request model for generating reports.
    """

    projects: List[Project]
