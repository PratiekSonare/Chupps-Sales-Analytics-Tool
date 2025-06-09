<script lang="ts">
  import { onMount } from "svelte";
  import { slide } from "svelte/transition";
  import { format } from "d3-format";
  const formatNumber = format(",");

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
  let maxEntry = 0;
  let max_sales_day = 0;
  let firstTrend = 0;
  let lastTrend = 0;
  let forecast_trend = "";

  //from 2024-04-01 to 2025-02-01
  let forecast_total_sales = 156596;
  let monthly_avg_sales = 15578;
  let weekly_avg_sales = 3582;

  // $: filteredForecast = filterForecast();

  // $: forecast_total_sales = filteredForecast.reduce(
  //   (sum, d) => sum + d.yhat,
  //   0,
  // );

  $: formatted_total_sales = formatNumber(total_sales.toFixed(0));
  $: formatted_forecast_total_sales = formatNumber(
    forecast_total_sales.toFixed(0),
  );
  $: formatted_total_revenue = formatNumber(total_revenue.toFixed(0));
  $: formatted_monthly_avg_sales = formatNumber(monthly_avg_sales.toFixed(0));
  $: formatted_weekly_avg_sales = formatNumber(weekly_avg_sales.toFixed(0));

  // Time range (in ms, days, weeks, months)
  $: {
    // const msDiff = new Date(endDate).getTime() - new Date(startDate).getTime();
    // const daysDiff = msDiff / (1000 * 60 * 60 * 24);
    // const weeksDiff = daysDiff / 7;
    // const monthsDiff = daysDiff / 30.44; // Average month duration
    // monthly_avg_sales = monthsDiff > 0 ? total_sales / monthsDiff : 0;
    // weekly_avg_sales = weeksDiff > 0 ? total_sales / weeksDiff : 0;
  }

  $: stats = [
    {
      title: "Expected Total Sales",
      value: formatted_forecast_total_sales,
    },
    {
      title: "Monthly Avg. Sales",
      value: formatted_monthly_avg_sales,
    },
    {
      title: "Weekly Avg. Sales",
      value: formatted_weekly_avg_sales,
    },
    {
      title: "Trend",
      value: forecast_trend,
    },
  ];

  onMount(async () => {
    console.log("Component is inside mount");
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
    console.log("result: ", forecast.trend);
    // Check trend direction
    const firstTrend = forecast[0]?.trend ?? 0;
    const lastTrend = forecast[forecast.length - 1]?.trend ?? 0;
    forecast_trend = lastTrend > firstTrend ? "Upward" : "Downward";

    console.log("trend:", forecast_trend);

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

    filteredForecast = filterForecast();

    forecast_total_sales = filteredForecast.reduce((sum, d) => sum + d.yhat, 0);

    const msDiff = new Date(endDate).getTime() - new Date(startDate).getTime();
    const daysDiff = msDiff / (1000 * 60 * 60 * 24);
    const weeksDiff = daysDiff / 7;
    const monthsDiff = daysDiff / 30.44; // Average month duration

    monthly_avg_sales = monthsDiff > 0 ? forecast_total_sales / monthsDiff : 0;
    weekly_avg_sales = weeksDiff > 0 ? forecast_total_sales / weeksDiff : 0;

    if (filtered.length) {
      plotForecast(filtered);
    }
  }

  function resetDate() {
    startDate = "2025-03-01";
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

  let setOpen = false;

  function openSet() {
    setOpen = !setOpen;
  }
</script>

<div class="w-screen h-screen">
  <div class="grid grid-cols-4 grid-rows-[1fr_3fr_3fr] gap-5 h-full p-2">
    <div class="card flex flex-col p-0">
      <span>Total Pairs Sold</span>
      <span class="text-4xl text-black">{formatted_total_sales}</span>
    </div>

    <div class="card flex flex-col p-2">
      <span>Total Revenue Generated</span>
      <span class="text-4xl text-black">{formatted_total_revenue}</span>
    </div>

    <div class="card flex flex-col p-2">
      <span>Total Parties Served</span>
      <span class="text-4xl text-black">{total_parties}</span>
    </div>

    <!-- <span>Settings</span> -->
    {#if setOpen}
      <div
        class="col-start-4 row-start-1 transition-all duration-500 ease-in-out"
        transition:slide
      >
        <div class="flex flex-col gap-1 p-2 w-full">
          <!-- Start date picker -->
          <div class="flex flex-row justify-between w-full">
            <!-- svelte-ignore a11y_consider_explicit_label -->
            <button
              class="border p-2 h-fit rounded-xl mt-auto border-red-500 hover:bg-red-500 hover:text-white transition-all duration-300 ease-in-out"
              on:click={resetDate}
            >
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
      </div>
    {/if}

    <!-- //if setOpen = true, then change row-start-2 to row-start-1 -->
    <div class={`card col-start-3 row-start-2 row-end-3 flex flex-col py-2`}>
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
          <span
            class={`text-xl font-medium text-right
        ${
          stat.title === "Trend"
            ? stat.value === "Upward"
              ? "text-green-500"
              : "text-red-500"
            : ""
        }
      `}
          >
            {stat.value}
          </span>
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
      <div class="flex flex-col items-center justify-center w-full gap-0">
        <span class="mt-5 text-center">Forecasted Sales</span>
        <button
          class="border h-fit rounded-lg px-1 py-1 text-xs flex flex-row gap-1 mt-auto hover:bg-gray-500 hover:text-white transition-all duration-300 ease-in-out"
          on:click={openSet}
        >
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
              d="M 15 2 C 14.448 2 14 2.448 14 3 L 14 3.171875 C 14 3.649875 13.663406 4.0763437 13.191406 4.1523438 C 12.962406 4.1893437 12.735719 4.2322031 12.511719 4.2832031 C 12.047719 4.3892031 11.578484 4.1265 11.396484 3.6875 L 11.330078 3.53125 C 11.119078 3.02125 10.534437 2.7782344 10.023438 2.9902344 C 9.5134375 3.2012344 9.2704219 3.785875 9.4824219 4.296875 L 9.5488281 4.4570312 C 9.7328281 4.8970313 9.5856875 5.4179219 9.1796875 5.6699219 C 8.9836875 5.7919219 8.7924688 5.9197344 8.6054688 6.0527344 C 8.2174688 6.3297344 7.68075 6.2666875 7.34375 5.9296875 L 7.2226562 5.8085938 C 6.8316562 5.4175937 6.1985937 5.4175938 5.8085938 5.8085938 C 5.4185938 6.1995938 5.4185938 6.8326563 5.8085938 7.2226562 L 5.9296875 7.34375 C 6.2666875 7.68075 6.3297344 8.2164688 6.0527344 8.6054688 C 5.9197344 8.7924687 5.7919219 8.9836875 5.6699219 9.1796875 C 5.4179219 9.5856875 4.8960781 9.7337812 4.4550781 9.5507812 L 4.296875 9.484375 C 3.786875 9.273375 3.2002813 9.5153906 2.9882812 10.025391 C 2.7772813 10.535391 3.0192969 11.120031 3.5292969 11.332031 L 3.6855469 11.396484 C 4.1245469 11.578484 4.3892031 12.047719 4.2832031 12.511719 C 4.2322031 12.735719 4.1873906 12.962406 4.1503906 13.191406 C 4.0753906 13.662406 3.649875 14 3.171875 14 L 3 14 C 2.448 14 2 14.448 2 15 C 2 15.552 2.448 16 3 16 L 3.171875 16 C 3.649875 16 4.0763437 16.336594 4.1523438 16.808594 C 4.1893437 17.037594 4.2322031 17.264281 4.2832031 17.488281 C 4.3892031 17.952281 4.1265 18.421516 3.6875 18.603516 L 3.53125 18.669922 C 3.02125 18.880922 2.7782344 19.465563 2.9902344 19.976562 C 3.2012344 20.486563 3.785875 20.729578 4.296875 20.517578 L 4.4570312 20.451172 C 4.8980312 20.268172 5.418875 20.415312 5.671875 20.820312 C 5.793875 21.016313 5.9206875 21.208484 6.0546875 21.396484 C 6.3316875 21.784484 6.2686406 22.321203 5.9316406 22.658203 L 5.8085938 22.779297 C 5.4175937 23.170297 5.4175938 23.803359 5.8085938 24.193359 C 6.1995938 24.583359 6.8326562 24.584359 7.2226562 24.193359 L 7.3457031 24.072266 C 7.6827031 23.735266 8.2174688 23.670266 8.6054688 23.947266 C 8.7934688 24.081266 8.9856406 24.210031 9.1816406 24.332031 C 9.5866406 24.584031 9.7357344 25.105875 9.5527344 25.546875 L 9.4863281 25.705078 C 9.2753281 26.215078 9.5173438 26.801672 10.027344 27.013672 C 10.537344 27.224672 11.121984 26.982656 11.333984 26.472656 L 11.398438 26.316406 C 11.580438 25.877406 12.049672 25.61275 12.513672 25.71875 C 12.737672 25.76975 12.964359 25.814562 13.193359 25.851562 C 13.662359 25.924562 14 26.350125 14 26.828125 L 14 27 C 14 27.552 14.448 28 15 28 C 15.552 28 16 27.552 16 27 L 16 26.828125 C 16 26.350125 16.336594 25.923656 16.808594 25.847656 C 17.037594 25.810656 17.264281 25.767797 17.488281 25.716797 C 17.952281 25.610797 18.421516 25.8735 18.603516 26.3125 L 18.669922 26.46875 C 18.880922 26.97875 19.465563 27.221766 19.976562 27.009766 C 20.486563 26.798766 20.729578 26.214125 20.517578 25.703125 L 20.451172 25.542969 C 20.268172 25.101969 20.415312 24.581125 20.820312 24.328125 C 21.016313 24.206125 21.208484 24.079312 21.396484 23.945312 C 21.784484 23.668312 22.321203 23.731359 22.658203 24.068359 L 22.779297 24.191406 C 23.170297 24.582406 23.803359 24.582406 24.193359 24.191406 C 24.583359 23.800406 24.584359 23.167344 24.193359 22.777344 L 24.072266 22.654297 C 23.735266 22.317297 23.670266 21.782531 23.947266 21.394531 C 24.081266 21.206531 24.210031 21.014359 24.332031 20.818359 C 24.584031 20.413359 25.105875 20.264266 25.546875 20.447266 L 25.705078 20.513672 C 26.215078 20.724672 26.801672 20.482656 27.013672 19.972656 C 27.224672 19.462656 26.982656 18.878016 26.472656 18.666016 L 26.316406 18.601562 C 25.877406 18.419563 25.61275 17.950328 25.71875 17.486328 C 25.76975 17.262328 25.814562 17.035641 25.851562 16.806641 C 25.924562 16.337641 26.350125 16 26.828125 16 L 27 16 C 27.552 16 28 15.552 28 15 C 28 14.448 27.552 14 27 14 L 26.828125 14 C 26.350125 14 25.923656 13.663406 25.847656 13.191406 C 25.810656 12.962406 25.767797 12.735719 25.716797 12.511719 C 25.610797 12.047719 25.8735 11.578484 26.3125 11.396484 L 26.46875 11.330078 C 26.97875 11.119078 27.221766 10.534437 27.009766 10.023438 C 26.798766 9.5134375 26.214125 9.2704219 25.703125 9.4824219 L 25.542969 9.5488281 C 25.101969 9.7318281 24.581125 9.5846875 24.328125 9.1796875 C 24.206125 8.9836875 24.079312 8.7915156 23.945312 8.6035156 C 23.668312 8.2155156 23.731359 7.6787969 24.068359 7.3417969 L 24.191406 7.2207031 C 24.582406 6.8297031 24.582406 6.1966406 24.191406 5.8066406 C 23.800406 5.4156406 23.167344 5.4156406 22.777344 5.8066406 L 22.65625 5.9296875 C 22.31925 6.2666875 21.782531 6.3316875 21.394531 6.0546875 C 21.206531 5.9206875 21.014359 5.7919219 20.818359 5.6699219 C 20.413359 5.4179219 20.266219 4.8960781 20.449219 4.4550781 L 20.515625 4.296875 C 20.726625 3.786875 20.484609 3.2002812 19.974609 2.9882812 C 19.464609 2.7772813 18.879969 3.0192969 18.667969 3.5292969 L 18.601562 3.6855469 C 18.419563 4.1245469 17.950328 4.3892031 17.486328 4.2832031 C 17.262328 4.2322031 17.035641 4.1873906 16.806641 4.1503906 C 16.336641 4.0753906 16 3.649875 16 3.171875 L 16 3 C 16 2.448 15.552 2 15 2 z M 15 7 C 19.078645 7 22.438586 10.054876 22.931641 14 L 16.728516 14 A 2 2 0 0 0 15 13 A 2 2 0 0 0 14.998047 13 L 11.896484 7.625 C 12.850999 7.222729 13.899211 7 15 7 z M 10.169922 8.6328125 L 13.269531 14 A 2 2 0 0 0 13 15 A 2 2 0 0 0 13.269531 15.996094 L 10.167969 21.365234 C 8.2464258 19.903996 7 17.600071 7 15 C 7 12.398945 8.2471371 10.093961 10.169922 8.6328125 z M 16.730469 16 L 22.931641 16 C 22.438586 19.945124 19.078645 23 15 23 C 13.899211 23 12.850999 22.777271 11.896484 22.375 L 14.998047 17 A 2 2 0 0 0 15 17 A 2 2 0 0 0 16.730469 16 z"
            ></path>
          </svg>
          Settings
        </button>
      </div>
      <div
        id="forecast-plot"
        class="w-full h-full rounded-2xl overflow-hidden"
      ></div>
    </div>

    <div
      class={`card col-start-4 transition-all duration-500 ease-in-out
      ${setOpen ? "row-start-2 row-end-4" : "row-start-1 row-end-4"}`}
    >
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
