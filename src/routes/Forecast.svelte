<script lang="ts">
  import { onMount } from "svelte";

  export let wo_centro_prophet;
  let forecast = [];
  let filteredForecast = [];

  onMount(async () => {
    const formatted = wo_centro_prophet.map((row) => ({
      ds: row.ds,
      y: row.y,
    }));

    const res = await fetch("http://localhost:8000/forecast", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ data: formatted }),
    });

    forecast = await res.json();
    plotForecast(forecast);
  });

  function plotForecast(forecast) {
    const startDate = new Date("2025-04-01");

    filteredForecast = forecast.filter((d) => {
      const date = new Date(d.ds);
      return date >= startDate;
    });

    const trace1 = {
      x: filteredForecast.map((d) => d.ds),
      y: filteredForecast.map((d) => d.yhat),
      mode: "lines",
      name: "Forecast",
    };

    const trace2 = {
      x: filteredForecast.map((d) => d.ds),
      y: filteredForecast.map((d) => d.yhat_upper),
      mode: "lines",
      line: { width: 0 },
      name: "Upper Bound",
      showlegend: false,
    };

    const trace3 = {
      x: filteredForecast.map((d) => d.ds),
      y: filteredForecast.map((d) => d.yhat_lower),
      mode: "lines",
      fill: "tonexty",
      line: { width: 0 },
      name: "Lower Bound",
      fillcolor: "rgba(0,100,80,0.2)",
      showlegend: true,
    };

    const trace4 = {
      x: wo_centro_prophet.map((d) => d.ds),
      y: wo_centro_prophet.map((d) => d.y),
      mode: "lines",
      name: "Forecast",
    };

    const layout = {
      title: "Forecast",
      xaxis: { title: "Date" },
      yaxis: { title: "Value" },
    };

    const tableData = {
      type: "table",
      header: {
        values: ["Date", "Forecast (yhat)", "Upper Bound", "Lower Bound"],
        align: "center",
        line: { width: 1, color: "black" },
        fill: { color: "lightgray" },
        font: { family: "Arial", size: 12, color: "black" },
      },
      cells: {
        values: [
          filteredForecast.map((d) => d.ds),
          filteredForecast.map((d) => d.yhat.toFixed(2)),
          filteredForecast.map((d) => d.yhat_upper.toFixed(2)),
          filteredForecast.map((d) => d.yhat_lower.toFixed(2)),
        ],
        align: "center",
        line: { color: "black", width: 1 },
        font: { family: "Arial", size: 11, color: ["black"] },
        height: 24,
      },
    };

    (window as any).Plotly.newPlot(
      "forecast-plot",
      [trace1, trace2, trace3],
      layout,
    );
    (window as any).Plotly.newPlot("actual-plot", [trace4], layout);

    (window as any).Plotly.newPlot("forecast-table", [tableData], {
      margin: { t: 10, b: 10 },
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
    });
  }
</script>

<!-- <div class="grid grid-rows-2 grid-cols-2 gap-1 items-center"> -->
<div class="flex flex-col gap-1 w-full items-center justify-center">
  <div id="actual-plot" class="w-full col-span-2 h-[400px] mt-6 rounded-2xl overflow-hidden shadow-xl"></div>
  
  <div>
    <div id="forecast-plot" class="w-full h-[400px] mt-6 rounded-2xl overflow-hidden shadow-xl"></div>
    
    <div id="forecast-table" class="w-full h-[400px]"></div>
  </div>
  
</div>
