import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import UploadPythonPage from "../../app/upload-python/page";
import { detectAi, detectStatic } from "../../utils/api";
import { toast } from "react-toastify";
import { act } from "react";

// Mock the API functions
jest.mock("../../utils/api", () => ({
  detectAi: jest.fn(),
  detectStatic: jest.fn(),
}));

// Mock toast notifications
jest.mock("react-toastify", () => ({
  toast: {
    error: jest.fn(),
    success: jest.fn(),
    info: jest.fn(),
  },
}));

describe("UploadPythonPage Component", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders all components correctly", () => {
    render(<UploadPythonPage />);

    expect(screen.getByText(/Upload and Analyze Python Code/i)).toBeInTheDocument();
    expect(screen.getByText(/Select Analysis Mode/i)).toBeInTheDocument();
    expect(screen.getByText(/Select a Python File/i)).toBeInTheDocument();
  });

  it("defaults to AI mode and toggles to Static mode", () => {
    render(<UploadPythonPage />);

    const aiButton = screen.getByText(/AI-Based/i);
    const staticButton = screen.getByText(/Static Tool/i);

    expect(aiButton).toHaveClass("bg-red-500");
    expect(staticButton).toHaveClass("bg-gray-200");

    fireEvent.click(staticButton);
    expect(staticButton).toHaveClass("bg-blue-500");
    expect(aiButton).toHaveClass("bg-gray-200");
  });
  
  it("handles file upload correctly", async () => {
    render(<UploadPythonPage />);

    const fileInput = screen.getByLabelText(/Select a Python File/i);
    const file = new File(["print('hello world')"], "test.py", { type: "text/x-python" });

    await act(async () => {
      fireEvent.change(fileInput, { target: { files: [file] } });
    });

    expect(screen.getByTestId("filename")).toHaveTextContent("test.py");
  });

  it("shows an error when submitting without a file", async () => {
    render(<UploadPythonPage />);

    const submitButton = screen.getByText(/Upload Code/i);
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith("No file available. Please add a file before submitting.");
    });
  });


  it("analyzes code using AI mode", async () => {
    (detectAi as jest.Mock).mockResolvedValueOnce({
      success: true,
      smells: [
        {
          description: "Example smell",
          function_name: "exampleFunction",
          line: 10,
          additional_info: "This is a test smell",
        },
      ],
    });

    render(<UploadPythonPage />);

    const fileInput = screen.getByLabelText(/Select a Python File/i);
    const file = new File(["mock file content"], "test.py", { type: "text/x-python" });

    Object.defineProperty(file, "text", {
      value: jest.fn().mockResolvedValueOnce("mock file content"),
    });

    fireEvent.change(fileInput, { target: { files: [file] } });

    const submitButton = screen.getByText(/Upload Code/i);

    await act(async () => {
      fireEvent.click(submitButton);
    });

    await waitFor(() => {
      expect(detectAi).toHaveBeenCalledWith("mock file content");
      expect(toast.success).toHaveBeenCalledWith("Code uploaded and analyzed successfully!");
    });

    expect(screen.getByText(/Smell #1/i)).toBeInTheDocument();
    expect(screen.getByText(/Example smell/i)).toBeInTheDocument();
  });


  it("hides the progress bar after loading", async () => {
    (detectAi as jest.Mock).mockResolvedValueOnce({
      success: true,
      smells: [],
    });

    render(<UploadPythonPage />);

    const fileInput = screen.getByLabelText(/Select a Python File/i);
    const file = new File(["mock file content"], "test.py", { type: "text/x-python" });

    Object.defineProperty(file, "text", {
      value: jest.fn().mockResolvedValueOnce("mock file content"),
    });

    await act(async () => {
      fireEvent.change(fileInput, { target: { files: [file] } });
    });

    const submitButton = screen.getByText(/Upload Code/i);

    await act(async () => {
      fireEvent.click(submitButton);
    });

    await waitFor(() => {
      expect(screen.queryByTestId("progress")).not.toBeInTheDocument();
    });
  });

});
