import { useInView } from "react-intersection-observer";
import Plot from "react-plotly.js";

type ChartData = { smell_name: string; filename: string };

interface ChartSectionProps {
  chartData: ChartData[];
}

const ChartSection: React.FC<ChartSectionProps> = ({ chartData }) => {
  const { ref, inView } = useInView({
    triggerOnce: true,
    threshold: 0.5,
  });

  return (
    <div data-testid="chart" ref={ref}>
      {inView && chartData ? (
        <Plot
          data={[
            {
              type: "bar",
              x: chartData.map((item) => item.smell_name),
              y: chartData.map((item) => item.filename),
              marker: { color: "rgb(31, 119, 180)" },
            },
          ]}
          layout={{
            title: "Smell Occurrences for All Projects",
            xaxis: { title: "Smell Type" },
            yaxis: { title: "Number of Occurrences" },
          }}
        />
      ) : (
        <div>Loading chart...</div>
      )}
    </div>
  );
};

export default ChartSection;
