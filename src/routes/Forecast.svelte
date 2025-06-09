<script lang="ts">
  import { onMount } from "svelte";

  export let wo_centro_prophet;
  export let total_sales;
  export let total_revenue;
  export let total_parties;
  export let chupps_items;

  let forecast = [];
  let filteredForecast = [];
  let dataToPlot = [];

  // Dropdown & calendar variables
  let selectedItem = "";
  let startDate = "2024-04-01";
  let endDate = "2025-02-01";
  let monthly_avg_sales = 0;
  let weekly_avg_sales = 0;
  let maxEntry = 0;
  let max_sales_day = 0;

  $: filteredForecast = filterForecast();
  // Total forecast sales
  $: forecast_total_sales = filteredForecast.reduce(
    (sum, d) => sum + d.yhat,
    0,
  );
  // Time range (in ms, days, weeks, months)
  $: {
    const msDiff = new Date(endDate).getTime() - new Date(startDate).getTime();
    const daysDiff = msDiff / (1000 * 60 * 60 * 24);
    const weeksDiff = daysDiff / 7;
    const monthsDiff = daysDiff / 30.44; // Average month duration

    monthly_avg_sales = monthsDiff > 0 ? forecast_total_sales / monthsDiff : 0;
    weekly_avg_sales = weeksDiff > 0 ? forecast_total_sales / weeksDiff : 0;
  }

  $: stats = [
    {
      title: "Expected Total Sales",
      value: forecast_total_sales.toFixed(0),
    },
    {
      title: "Monthly Avg. Sales",
      value: monthly_avg_sales.toFixed(0),
    },
    {
      title: "Weekly Avg. Sales",
      value: weekly_avg_sales.toFixed(0),
    },
  ];

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
    filteredForecast = filterForecast(); // ← Make sure to populate
    plotForecast(filteredForecast);
  });

  function filterForecast() {
    if (!forecast.length) return [];

    return forecast.filter((d) => {
      const date = new Date(d.ds);
      const inRange =
        (!startDate || date >= new Date(startDate)) &&
        (!endDate || date <= new Date(endDate));

      // const itemMatch = selectedItem ? d.item === selectedItem : true; // If forecast contains item info

      return inRange;
    });
  }

  function applyFilters() {
    const filtered = filterForecast();
    if (filtered.length) {
      plotForecast(filtered);
    }
  }

  function resetDate() {
    startDate = "2024-04-01";
    endDate = "2026-02-01";

    const filtered = filterForecast();
    if (filtered.length) {
      plotForecast(filtered);
    }
  }

  function plotForecast(dataToPlot) {
    filteredForecast = dataToPlot;

    const trace1 = {
      x: dataToPlot.map((d) => d.ds),
      y: dataToPlot.map((d) => d.yhat),
      mode: "lines",
      name: "Forecast",
    };

    const trace2 = {
      x: dataToPlot.map((d) => d.ds),
      y: dataToPlot.map((d) => d.yhat_upper),
      mode: "lines",
      line: { width: 1 },
      name: "Max. Sales",
      // fillcolor: "rgba(0,100,80,0.2)",
      showlegend: true,
    };

    const trace3 = {
      x: dataToPlot.map((d) => d.ds),
      y: dataToPlot.map((d) => d.yhat_lower),
      mode: "lines",
      fill: "tonexty",
      line: { width: 1 },
      name: "Min. Sales",
      // fillcolor: "rgba(0,100,80,0.2)",
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
      yaxis: { title: "Sales" },
    };

    const tableData = {
      type: "table",
      header: {
        values: ["Date", "Forecasted Sales", "Max. Sales", "Min. Sales"],
        align: "center",
        line: { width: 1, color: "black" },
        fill: { color: "lightgray" },
        font: { family: "Arial", size: 12, color: "black" },
      },
      cells: {
        values: [
          dataToPlot.map((d) => d.ds.split("T")[0]),
          dataToPlot.map((d) => d.yhat.toFixed(2)),
          dataToPlot.map((d) => d.yhat_upper.toFixed(2)),
          dataToPlot.map((d) => d.yhat_lower.toFixed(2)),
        ],
        align: "center",
        line: { color: "black", width: 1 },
        font: { family: "Arial", size: 11, color: ["black"] },
        height: 24,
      },
    };

    (window as any).Plotly.newPlot("forecast-plot", [trace1, trace2], layout, {
      displayModeBar: false,
      responsive: true,
    });

    (window as any).Plotly.newPlot("actual-plot", [trace4], layout, {
      displayModeBar: false,
      responsive: true,
    });

    (window as any).Plotly.newPlot(
      "forecast-table",
      [tableData],
      {
        margin: { t: 10, b: 10, l: 20, r: 20 },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
      },
      {
        displayModeBar: false,
        responsive: true,
      },
    );
  }
</script>

<div class="w-screen h-screen">
  <div class="grid grid-cols-4 grid-rows-[1fr_3fr_3fr] gap-5 h-full p-2">
    <div class="card flex flex-col p-0">
      <span>Total Pairs Sold</span>
      <span class="text-4xl text-black">{total_sales}</span>
    </div>

    <div class="card flex flex-col p-2">
      <span>Total Revenue Generated</span>
      <span class="text-4xl text-black">{total_revenue}</span>
    </div>

    <div class="card flex flex-col p-2">
      <span>Total Parties Served</span>
      <span class="text-4xl text-black">{total_parties}</span>
    </div>

    <!-- <span>Settings</span> -->
    <div class="flex flex-col gap-1 p-2 w-full">
      <!-- Start date picker -->
      <div class="flex flex-row justify-between w-full">
        <!-- svelte-ignore a11y_consider_explicit_label -->
        <button 
          class="border p-2 h-fit rounded-xl mt-auto border-red-500 hover:bg-red-500 hover:text-white transition-all duration-300 ease-in-out"
          on:click={resetDate}>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            x="0px"
            y="0px"
            width="20"
            height="20"
            viewBox="0 0 30 30"
            class="fill-current"
          >
            <path
              d="M 15 3 C 12.031398 3 9.3028202 4.0834384 7.2070312 5.875 A 1.0001 1.0001 0 1 0 8.5058594 7.3945312 C 10.25407 5.9000929 12.516602 5 15 5 C 20.19656 5 24.450989 8.9379267 24.951172 14 L 22 14 L 26 20 L 30 14 L 26.949219 14 C 26.437925 7.8516588 21.277839 3 15 3 z M 4 10 L 0 16 L 3.0507812 16 C 3.562075 22.148341 8.7221607 27 15 27 C 17.968602 27 20.69718 25.916562 22.792969 24.125 A 1.0001 1.0001 0 1 0 21.494141 22.605469 C 19.74593 24.099907 17.483398 25 15 25 C 9.80344 25 5.5490109 21.062074 5.0488281 16 L 8 16 L 4 10 z"
            ></path>
          </svg>
        </button>
        <div class="flex flex-col items-start">
          <span class="text-xs">From</span>
          <input
            type="date"
            bind:value={startDate}
            max={endDate}
            class="border rounded px-2 py-1"
          />
        </div>

        <!-- End date picker -->
        <div class="flex flex-col items-start">
          <span class="text-xs">To</span>
          <input
            type="date"
            bind:value={endDate}
            min={startDate}
            class="border rounded px-2 py-1"
          />
        </div>
      </div>

      <!-- Dropdown for items -->
      <div class="flex flex-col items-center w-full">
        <span class="text-xs">Choose Item</span>
        <select
          bind:value={selectedItem}
          class="border rounded px-1 py-1 w-full"
        >
          {#each chupps_items as i}
            <option value={i.item}>{i.item}</option>
          {/each}
        </select>
      </div>

      <button
        class="p-0 mt-1 border border-blue-500 rounded py-0 px-2 h-full hover:bg-blue-500 hover:text-white transition-all duration-300 ease-out"
        on:click={applyFilters}
      >
        Enter
      </button>
    </div>

    <div class="card col-start-3 row-start-2 row-end-3 flex flex-col py-2">
      <span>Data Input</span>
      <div id="forecast-table" class="w-full h-full"></div>
    </div>

    <div
      class="card-alt2 col-start-3 row-start-3 row-end-4 flex-col w-full h-full"
    >
      <div class="flex flex-col justify-center items-center my-5">
        <span class="">Data Statistics</span>
        <span class="text-gray-400 text-xs -mt-1"
          >(in the selected timeframe)</span
        >
      </div>
      {#each stats as stat}
        <div
          class="flex flex-row justify-between items-center py-1 border-b w-11/12"
        >
          <span class="text-base text-gray-500">{stat.title}</span>
          <span class="text-xl font-medium text-right">{stat.value}</span>
        </div>
      {/each}
    </div>

    <div class="col-span-2 card flex flex-col">
      <span class="mt-5">Daily Sales</span>
      <div
        id="actual-plot"
        class="w-full h-full rounded-2xl overflow-hidden"
      ></div>
    </div>

    <div class="col-span-2 card flex flex-col">
      <span class="mt-5">Forecasted Sales</span>
      <div
        id="forecast-plot"
        class="w-full h-full rounded-2xl overflow-hidden"
      ></div>
    </div>

    <div class="card row-start-2 row-end-4 col-start-4">
      <span>AI Insights</span>
    </div>
  </div>
</div>

<style>
  @reference "tailwindcss";

  .card {
    @apply bg-white w-full h-full rounded-lg flex items-center justify-center shadow-xl;
  }
  .card-alt {
    @apply bg-transparent w-full h-full rounded-lg flex items-center justify-center;
  }
  .card-alt2 {
    @apply bg-white w-full h-full rounded-lg flex items-center justify-start shadow-xl;
  }
</style>
