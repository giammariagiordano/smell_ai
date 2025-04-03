import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { useProjectContext } from "../../context/ProjectContext";
import Project from "../../components/ProjectComponent";
import "@testing-library/jest-dom";

// Mocking the context hook
jest.mock("../../context/ProjectContext", () => ({
  ...jest.requireActual("../../context/ProjectContext"),
  useProjectContext: jest.fn(),
}));

describe("Project Component", () => {
  const mockRemoveProject = jest.fn();
  const mockAddProject = jest.fn();

  let mockProjects: { name: string; files: File[] }[] = [
    { name: "Test Project 1", files: [] },
  ];

  beforeEach(() => {
    // Mock the `webkitRelativePath` using the real `File` constructor.
    const fileMock = new File(["content"], "example.py", {
      type: "text/plain",
      lastModified: Date.now(),
    });

    // Mock the `webkitRelativePath` for the file to simulate directory structure
    Object.defineProperty(fileMock, "webkitRelativePath", {
      value: "test_folder/example.py", // Simulate directory structure
    });

    // Return the mocked context and the mock file
    (useProjectContext as jest.Mock).mockReturnValue({
      projects: mockProjects,
      addProject: mockAddProject,
      removeProject: mockRemoveProject,
      updateProject: (index: number, project: { files: File[]; name: string }) => {
        // Handle file upload and project name update
        mockProjects[index].files = project.files;
        mockProjects[index].name = project.name;
      },
    });
  });

  it("should render project name", () => {
    render(<Project index={0} />);
    expect(screen.getByText("Test Project 1")).toBeInTheDocument();
  });

  it("should update folder name and files on file upload", async () => {
    render(<Project index={0} />);

    // Use getByTestId to find the file input element
    const fileInput = screen.getByTestId("file-input");
    
    // Create a mock file with a path simulating a folder structure
    const file = new File(["content"], "example.py", { type: "text/plain" });
    Object.defineProperty(file, "webkitRelativePath", {
      value: "test_folder/example.py", // Simulate directory structure
    });

    // Mock the change event for file upload
    fireEvent.change(fileInput, {
      target: { files: [file] },
    });

    // Ensure the folder name is updated in the project name
    expect(mockProjects[0].name).toBe("test_folder");
  });

  it("should call removeProject on button click", () => {
    render(<Project index={0} />);

    const removeButton = screen.getByRole("button", { name: /Remove Project/i });
    fireEvent.click(removeButton);

    // Check if removeProject is called with the correct argument
    expect(mockRemoveProject).toHaveBeenCalledWith(0);
  });
});
