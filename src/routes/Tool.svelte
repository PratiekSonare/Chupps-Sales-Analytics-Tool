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
      plot_bgcolor: "rgba(0,0,0,0)", // background color inside the plotting area
      paper_bgcolor: "rgba(0,0,0,0)",
    };

    (window as any).Plotly.newPlot("forecast-plot", [trace1, trace2, trace3], layout);
    (window as any).Plotly.newPlot("actual-plot", [trace4], layout);
  }
</script>

<div class="grid grid-rows-2 grid-cols-2 gap-1">
  <!-- First row: actual plot spanning 2 columns -->
  <div id="actual-plot" class="col-span-2 h-[400px] mt-6"></div>

  <!-- Second row, first column: forecast plot -->
  <div id="forecast-plot" class="h-[400px] mt-6"></div>

  <!-- Second row, second column: scrollable table -->
  <div class="h-[400px] overflow-y-auto border rounded">
    <table class="min-w-full text-sm text-left">
      <thead class="sticky top-0 bg-gray-100">
        <tr>
          <th class="px-3 py-2">Date</th>
          <th class="px-3 py-2">Forecast (yhat)</th>
          <th class="px-3 py-2">Upper Bound</th>
          <th class="px-3 py-2">Lower Bound</th>
        </tr>
      </thead>
      <tbody>
        {#each filteredForecast as row}
          <tr class="border-b">
            <td class="px-3 py-2">{row.ds}</td>
            <td class="px-3 py-2">{row.yhat.toFixed(2)}</td>
            <td class="px-3 py-2">{row.yhat_upper.toFixed(2)}</td>
            <td class="px-3 py-2">{row.yhat_lower.toFixed(2)}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
</div>

