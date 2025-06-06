<script lang="ts">
  import { onMount } from 'svelte';
  import Plotly from 'plotly.js-dist-min';

  export let data;
  const { wo_centro_prophet } = data;

  let forecast = [];

  onMount(async () => {
    // Transform table to Prophet input
    const formatted = wo_centro_prophet.map(row => ({
      ds: row.ds,
      y: row.y,
    }));

    const res = await fetch('http://localhost:8000/forecast', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ data: formatted })
    });

    forecast = await res.json();
    plotForecast(forecast);
  });

  function plotForecast(forecast) {
    const trace1 = {
      x: forecast.map(d => d.ds),
      y: forecast.map(d => d.yhat),
      mode: 'lines',
      name: 'Forecast',
    };

    const trace2 = {
      x: forecast.map(d => d.ds),
      y: forecast.map(d => d.yhat_upper),
      mode: 'lines',
      line: { width: 0 },
      name: 'Upper Bound',
      showlegend: false,
    };

    const trace3 = {
      x: forecast.map(d => d.ds),
      y: forecast.map(d => d.yhat_lower),
      mode: 'lines',
      fill: 'tonexty',
      line: { width: 0 },
      name: 'Lower Bound',
      fillcolor: 'rgba(0,100,80,0.2)',
      showlegend: true,
    };

    const layout = {
      title: 'Forecast',
      xaxis: { title: 'Date' },
      yaxis: { title: 'Value' },
    };

    Plotly.newPlot('forecast-plot', [trace1, trace2, trace3], layout);
  }
</script>

<div id="forecast-plot" class="w-full h-[400px] mt-6"></div>
