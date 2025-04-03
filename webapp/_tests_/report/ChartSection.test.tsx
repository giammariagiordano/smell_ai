import { render, screen, waitFor } from "@testing-library/react";
import ChartSection from "../../components/ChartSection";

// Mock `useInView` to always return `inView: true`
jest.mock("react-intersection-observer", () => ({
  useInView: jest.fn().mockReturnValue({ ref: jest.fn(), inView: true }),
}));

// Mock `Plot` component from `react-plotly.js`
jest.mock("react-plotly.js", () => ({
  __esModule: true,
  default: jest.fn(() => <div>Mocked Plot</div>),
}));

describe("ChartSection", () => {
  it("renders the chart when in view", async () => {
    const chartData = [
      { smell_name: "Code Smell 1", filename: "file1.py" },
      { smell_name: "Code Smell 2", filename: "file2.py" },
    ];

    render(<ChartSection chartData={chartData} />);

    // Check that the chart is rendered after `inView` becomes true
    await waitFor(() => {
      expect(screen.getByText("Mocked Plot")).toBeInTheDocument();
    });

    // Check that loading message is not displayed
    expect(screen.queryByText("Loading chart...")).toBeNull();
  });

});
