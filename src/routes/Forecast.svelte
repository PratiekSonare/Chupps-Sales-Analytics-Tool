<script lang="ts">
  import { onMount } from "svelte";
  import { marked } from "marked";
  import SvelteMarkdown from "svelte-markdown";

  import { blur } from "svelte/transition";
  import { format } from "d3-format";
  import ChuppsButton from "./ChuppsButton.svelte";
    import CalculationPopup from "./CalculationPopup.svelte";

  const formatNumber = format(",");

  export let wo_centro_prophet;
  // export let non_zero_no_spikes_prophet;
  // export let chupps_23_25_full;
  export let chupps_23_25_full;
  export let total_sales;
  export let total_revenue;
  export let total_parties;
  export let chupps_items;
  export let chupps_shades;

  let forecast = [];
  let og_forecast = [];

  let filteredForecast = [];
  let dataToPlot = [];

  let naData = false;
  let calculationOpen = false;
  let llm_used = 30;

  // Dropdown & calendar variables
  let startDate = "2024-04-01";
  let endDate = "2025-02-01";
  let maxEntry = 0;
  let max_sales_day = 0;
  let firstTrend = 0;
  let lastTrend = 0;
  let forecast_trend = "Upward";

  //from 2024-04-01 to 2025-02-01
  let forecast_total_sales = 156596;
  let monthly_avg_sales = 15578;
  let weekly_avg_sales = 3582;
  let yearly_avg_sales = 195370;
  let percentage_growth = 137;

  let llm_response = "Select an item/shade and hit enter!"; // Better initial state
  let renderedMarkdown = "";

  if (yearly_avg_sales === 0) {
    forecast_trend = "NO TREND";
  }

  let item_name = "";
  let shade_name = "";
  let setOpen = true;
  let isLLMon = false;
  let isLLMthinking = false;
  let expand_rotate = false;
  let expand_forecast = false;

  let item_sales_data = wo_centro_prophet;
  let currentSalesData = wo_centro_prophet; // default (global data)

  $: formatted_total_sales = formatNumber(total_sales.toFixed(0));
  $: formatted_forecast_total_sales = formatNumber(
    forecast_total_sales.toFixed(0),
  );
  $: formatted_total_revenue = formatNumber(total_revenue.toFixed(0));
  $: formatted_monthly_avg_sales = formatNumber(monthly_avg_sales.toFixed(0));
  $: formatted_weekly_avg_sales = formatNumber(weekly_avg_sales.toFixed(0));
  $: formatted_yearly_avg_sales = formatNumber(yearly_avg_sales.toFixed(0));
  // $: formatted_percentage_growth = formatNumber(percentage_growth);

  $: stats = [
    {
      title: "Expected Total Sales",
      value: formatted_forecast_total_sales,
    },
    {
      title: "Yearly Avg. Sales",
      value: formatted_yearly_avg_sales,
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
    {
      title: "Params...",
      value: 1000,
    },
  ];

  $: details = [
    {
      title: "Period of forecast",
      value: 365,
    },
    {
      title: "Number of days forecasted",
      value: forecast.length,
    },
  ];

  $: if (item_name) {
    itemChosenForForecast(item_name);
  }

  $: if (shade_name) {
    shadeChosenForForecast(shade_name);
  }

  async function runLLM() {
    if (llm_used <= 0) {
      console.log("LLM usage limit reached");
      return;
    }

    isLLMthinking = true;
    llm_used = llm_used - 1;

    if (item_name || shade_name || (!item_name && !shade_name)) {
      try {
        // Show loading state
        llm_response = "Analyzing data...";

        // Generate appropriate metadata
        const curr_metadata = generateMetadata();
        console.log("curr_metadata: ", curr_metadata);

        // Get LLM response (with error handling)
        const response = await getLLMResponse(curr_metadata);
        console.log("llm_response: ", response);

        renderedMarkdown = marked(response || "Could not generate insights");
      } catch (error) {
        console.error("Error generating insights:", error);
        llm_response = "Error generating insights. Please try again.";
        renderedMarkdown = marked(
          "Error generating insights. Please try again.",
        );
      } finally {
        isLLMthinking = false;
      }
    }
  }

  onMount(async () => {
    const agg_data = wo_centro_prophet.map((row) => ({
      ds: row.ds,
      y: row.y,
    }));

    const res = await fetch("http://localhost:8000/forecast", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ data: agg_data }),
    });

    forecast = await res.json();
    og_forecast = forecast;

    filteredForecast = filterForecast(startDate, endDate);
    plotForecast(filteredForecast);
  });

  async function itemChosenForForecast(item) {
    const total_data = chupps_23_25_full.map((row) => ({
      purDate: row.purDate,
      item: row.item,
      sales: row.sales,
    }));

    try {
      const res = await fetch(
        `http://localhost:8000/forecast/item/${encodeURIComponent(item)}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ data: total_data }),
        },
      );
      forecast = await res.json();
    } catch (err) {
      console.error(`Failed to fetch forecast for item - ${item}:`, err);
    }

    try {
      const res2 = await fetch(
        `http://localhost:8000/item/${encodeURIComponent(item)}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ data: total_data }),
        },
      );

      item_sales_data = await res2.json();
      currentSalesData = item_sales_data;
    } catch (err) {
      console.error(`Failed to fetch sales data for item - ${item}:`, err);
    }
  }

  async function shadeChosenForForecast(shade) {
    const total_data = chupps_23_25_full.map((row) => ({
      purDate: row.purDate,
      shade: row.shade,
      sales: row.sales,
    }));

    try {
      const res = await fetch(
        `http://localhost:8000/forecast/shade/${encodeURIComponent(shade)}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ data: total_data }),
        },
      );
      forecast = await res.json();
    } catch (err) {
      console.error(`Failed to fetch forecast for item - ${shade}:`, err);
    }

    try {
      const res2 = await fetch(
        `http://localhost:8000/shade/${encodeURIComponent(shade)}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ data: total_data }),
        },
      );

      item_sales_data = await res2.json();
      currentSalesData = item_sales_data;
    } catch (err) {
      console.error(`Failed to fetch sales data for item - ${shade}:`, err);
    }
  }

  function filterForecast(startDate, endDate) {
    if (!forecast.length) return [];

    return forecast.filter((d) => {
      const date = new Date(d.ds);
      const inRange =
        (!startDate || date >= new Date(startDate)) &&
        (!endDate || date <= new Date(endDate));

      return inRange;
    });
  }

  function calculatePercentageGrowth(aggSourceData = currentSalesData) {
    const agg_data = aggSourceData.map((row) => ({
      ds: new Date(row.ds || row.purDate), // ensure correct date field
      y: row.y || row.sales, // support both field names
    }));

    const custom_startDate = new Date("2025-04-01");
    const custom_endDate = new Date("2026-03-01");

    const filteredForecastGrowth = filterForecast(custom_startDate, custom_endDate);
    console.log("filtered forecast:", filteredForecastGrowth);

    const startDate_history = new Date("2024-03-01");
    const endDate_history = new Date("2025-03-01");

    const sales_2025 = agg_data
      .filter((row) => row.ds >= startDate_history && row.ds < endDate_history)
      .reduce((sum, row) => sum + row.y, 0);

    const sales_2026 = filteredForecastGrowth.reduce(
      (sum, d) => sum + d.yhat,
      0,
    );

    const growth =
      sales_2025 === 0 ? 0 : ((sales_2026 - sales_2025) / sales_2025) * 100;

    console.log("2025 sales:", sales_2025);
    console.log("2026 forecast:", sales_2026);
    console.log("Growth (%):", growth.toFixed(2));

    return growth;
  }

  function applyFilters() {
    const filtered = filterForecast(startDate, endDate);
    filteredForecast = filterForecast(startDate, endDate);

    //total sales for timeframe
    forecast_total_sales = filteredForecast.reduce((sum, d) => sum + d.yhat, 0);

    if (forecast_total_sales === 0) {
      naData = true;
      forecast_trend = "NO TREND";
    }

    //avg sales calculation
    const msDiff = new Date(endDate).getTime() - new Date(startDate).getTime();
    const daysDiff = msDiff / (1000 * 60 * 60 * 24);
    const weeksDiff = daysDiff / 7;
    const monthsDiff = daysDiff / 30.44; // Average month duration
    const yearsDiff = monthsDiff / 12;

    monthly_avg_sales = monthsDiff > 0 ? forecast_total_sales / monthsDiff : 0;
    weekly_avg_sales = weeksDiff > 0 ? forecast_total_sales / weeksDiff : 0;
    yearly_avg_sales = yearsDiff > 0 ? forecast_total_sales / yearsDiff : 0;

    //trend calculation
    const firstTrend = forecast[0]?.trend ?? 0;
    const lastTrend = forecast[forecast.length - 1]?.trend ?? 0;

    if (yearly_avg_sales === 0) {
      forecast_trend = "NO TREND";
    } else {
      forecast_trend = lastTrend > firstTrend ? "Upward" : "Downward";
    }

    console.log("firstTrend: ", firstTrend);
    console.log("lastTrend: ", lastTrend);

    percentage_growth = calculatePercentageGrowth();

    //call plotting of forecast
    if (filtered.length) {
      plotForecast(filtered);
    }
  }

  function resetDate() {
    startDate = "2025-03-01";
    endDate = "2026-02-01";

    const filtered = filterForecast(startDate, endDate);
    if (filtered.length) {
      plotForecast(filtered);
    }
  }

  function resetItem() {
    forecast = og_forecast;
    item_sales_data = wo_centro_prophet;
    item_name = "";
    shade_name = "";

    const filtered = filterForecast(startDate, endDate);
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
      y: dataToPlot.map((d) => d.trend),
      mode: "lines",
      // fill: "tonexty",
      line: { width: 2 },
      name: "Trend",
      // fillcolor: "rgba(0,100,80,0.2)",
      showlegend: true,
    };

    const daily_sales_plot = {
      x: item_sales_data.map((d) => d.ds),
      y: item_sales_data.map((d) => d.y),
      mode: "lines",
      name: "Forecast",
    };

    const layout = {
      title: "Forecast",
      margin: { t: 50, l: 50, r: 50, b: 50 },
      xaxis: { title: "Date" },
      yaxis: { title: "Sales" },
    };

    const layoutForecast = {
      title: "Forecast",
      height: 350,
      margin: { t: 50, l: 50, r: 50, b: 50 },
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

    (window as any).Plotly.newPlot(
      "forecast-plot",
      [trace1, trace2, trace3],
      layoutForecast,
      {
        displayModeBar: false,
        responsive: true,
      },
    );

    (window as any).Plotly.newPlot("actual-plot", [daily_sales_plot], layout, {
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

  function openSet() {
    setOpen = !setOpen;
  }

  function setLLM() {
    isLLMon = !isLLMon;
    renderedMarkdown = "";
  }

  function expandForecast() {
    expand_forecast = !expand_forecast;
  }
  //LLM PARSING
  function generateMetadata() {
    const isFiltered = item_name || shade_name;
    const filteredData = isFiltered ? item_sales_data : wo_centro_prophet;
    const currentForecast = isFiltered ? forecast : og_forecast;

    return {
      context: {
        isFiltered,
        filterType: item_name ? "item" : shade_name ? "shade" : "all products",
        filterValue: item_name || shade_name || "none",
      },
      dateRange: {
        start: startDate,
        end: endDate,
      },
      statistics: {
        totalSales: currentForecast.reduce((sum, d) => sum + d.yhat, 0),
        trend: forecast_trend,
        dataPoints: filteredData.length,
        forecastPoints: currentForecast.length,
        averages: {
          daily: weekly_avg_sales / 7,
          weekly: weekly_avg_sales,
          monthly: monthly_avg_sales,
          yearly: yearly_avg_sales,
        },
      },
      modelDetails: {
        type: "Prophet",
        seasonality: "yearly",
        holidaysIncluded: true,
        confidenceInterval: 80, //%
      },
      // Add any other relevant data
      rawSample: isFiltered
        ? filteredData.slice(0, 5) // Sample of filtered data
        : wo_centro_prophet.slice(0, 5), // Sample of all data
    };
  }

  async function getLLMResponse(metadata) {
    try {
      // const prompt = `You are a data analyst assistant skilled at interpreting sales dashboards and sales metadata. I am providing to you metadata pertaining to sales data of a footwear brand from India. This data has been used to forecast sales for the next 365 days using the Prophet model, with yearly seasonlity.
      //             Draw crucial insights from the metadata and relate this metadata with the geographical, economical and temporal (seasons, time of the year) knowledge to give a summary on your insights.
      //             From your analytical insights, return what possible actions the sales manager at this firm should perform to improve the sales of this product.

      //             Some background/domain about the brand with the sales: The sales belong to a budding open footwear brand in India. The brand currently operates on a distributor model, with major distributors across India ordering footwear in bulk at a time.
      //             Recently, they have also started online marketplace and offline store based sales. The input data to the forecasting model contains this data.

      //             Now, some background/domain about the metadata that is being provided to you:
      //               1. filters: specifies the item or shade used to filter and display sales and forecasted data belonging to that item or shade. it also includes date filtering, that you musst take into account while analyzing. If aggregationLevel is 'All Products', that means the meta-data belongs to total sales record, otherwise it is for a particular item or a shade. dateRange is the range of dates used to filter display data for.
      //               2. metrics: some metrics that are being displayed in the tool, avg_sales contain yearly, monthly and weekly average sales of entire sales or for a particular item or shade. forecastTotalSales is the sum of forecasted sales for all products or either a particular item or shade, within the dateRange.
      //               3. prophet_model_stats: the parameters used for fitting the sales data with Prophet model by Meta. holidays mentions days of importance, since we notice a spike in sales during these days. predictionPeriod is the number of days predicted by the model ahdead of the latest day in the input data.

      //               Here's the input meta-data: ${JSON.stringify(metadata, null, 2)}

      //               Focus on:
      //               1. Key trends in the data
      //               2. Anomalies or unexpected patterns
      //               3. Business recommendations based on the metrics`;

      const prompt = `You are a data analyst assistant skilled at interpreting sales dashboards and sales metadata. I am providing to you metadata pertaining to sales data of a footwear brand from India. This data has been used to forecast sales for the next 365 days using the Prophet model, with yearly seasonlity. 
                  Draw crucial insights from the metadata and relate this metadata with the geographical, economical and temporal (seasons, time of the year) knowledge to give a summary on your insights.
                  From your analytical insights, return what possible actions the sales manager at this firm should perform to improve the sales of this product. 

                  Some background/domain about the brand with the sales: The sales belong to a budding open footwear brand in India. The brand currently operates on a distributor model, with major distributors across India ordering footwear in bulk at a time.
                  Recently, they have also started online marketplace and offline store based sales. The input data to the forecasting model contains this data.
                  
                  Now, some background/domain about the metadata that is being provided to you: 
                    1. filters: specifies the item or shade used to filter and display sales and forecasted data belonging to that item or shade. it also includes date filtering, that you musst take into account while analyzing. If aggregationLevel is 'All Products', that means the meta-data belongs to total sales record, otherwise it is for a particular item or a shade. dateRange is the range of dates used to filter display data for.
                    2. metrics: some metrics that are being displayed in the tool, avg_sales contain yearly, monthly and weekly average sales of entire sales or for a particular item or shade. forecastTotalSales is the sum of forecasted sales for all products or either a particular item or shade, within the dateRange.
                    3. prophet_model_stats: the parameters used for fitting the sales data with Prophet model by Meta. holidays mentions days of importance, since we notice a spike in sales during these days. predictionPeriod is the number of days predicted by the model ahdead of the latest day in the input data.
                    
                    Here's the input meta-data: ${JSON.stringify(metadata, null, 2)}

                    Focus on:
                    1. Key trends in the data
                    2. Anomalies or unexpected patterns
                    3. Business recommendations based on the metrics`;

      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({
          messages: [{ role: "user", content: prompt }],
        }),
      });

      const data = await response.json();
      return data.choices[0]?.message?.content || "No analysis available";
    } catch (error) {
      console.error("LLM Error:", error);
      return "Unable to generate analysis at this time";
    }
  }
</script>

{#if calculationOpen}
  <CalculationPopup bind:calculationOpen />
{/if}

<div class="w-screen h-screen">
  <div class="grid grid-cols-4 grid-rows-[1fr_3fr_3fr_1fr] gap-3 h-full p-2">
    <div class="card flex flex-col p-2">
      <span class="text-xl mt-auto">Total Pairs Sold</span>
      <span class="text-gray-400 text-[10px] -my-1">(All Time)</span>
      <span class="text-5xl text-black my-auto">{formatted_total_sales}</span>
    </div>

    <div class="card flex flex-col p-2">
      <span class="text-xl mt-auto">Total Revenue Generated</span>
      <span class="text-gray-400 text-[10px] -my-1">(All Time)</span>
      <span class="text-5xl text-black my-auto">{formatted_total_revenue}</span>
    </div>

    <div class="flex flex-row gap-3">
      <div class="card flex flex-col p-2">
        <span class="text-xl mt-auto">Total Parties</span>
        <span class="text-gray-400 text-[10px] -my-1">(All Time)</span>
        <span class="text-5xl text-black my-auto">{total_parties}</span>
      </div>
      <div
        class="card-growth flex flex-col p-2"
        class:bg-green-300={percentage_growth > 0}
        class:bg-red-300={percentage_growth < 0}
      >
        <div class="flex flex-col mt-auto gap-0 items-center">
          <span class="text-xl mt-auto">Growth</span>
          <!-- svelte-ignore a11y_consider_explicit_label -->
          <button
          on:click={() => calculationOpen = !calculationOpen}>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              x="0px"
              y="0px"
              width="12"
              height="12"
              class="fill-current"
              viewBox="0 0 24 24"
            >
              <path
                d="M 12 2 C 6.4889971 2 2 6.4889971 2 12 C 2 17.511003 6.4889971 22 12 22 C 17.511003 22 22 17.511003 22 12 C 22 6.4889971 17.511003 2 12 2 z M 12 4 C 16.430123 4 20 7.5698774 20 12 C 20 16.430123 16.430123 20 12 20 C 7.5698774 20 4 16.430123 4 12 C 4 7.5698774 7.5698774 4 12 4 z M 11 7 L 11 9 L 13 9 L 13 7 L 11 7 z M 11 11 L 11 17 L 13 17 L 13 11 L 11 11 z"
              ></path>
            </svg>
          </button>
        </div>

        <div class="flex flex-row gap-2 items-center my-auto">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="32"
            height="32"
            fill="currentColor"
            class="bi bi-caret-up-fill"
            class:text-green-600={percentage_growth > 0}
            class:text-red-600={percentage_growth < 0}
            class:rotate-180={percentage_growth < 0}
            viewBox="0 0 16 16"
          >
            <path
              d="m7.247 4.86-4.796 5.481c-.566.647-.106 1.659.753 1.659h9.592a1 1 0 0 0 .753-1.659l-4.796-5.48a1 1 0 0 0-1.506 0z"
            />
          </svg>
          <span
            class="text-5xl text-black"
            class:text-green-600={percentage_growth > 0}
            class:text-red-600={percentage_growth < 0}
            >{percentage_growth.toFixed(1)}<span class="text-base ml-1">%</span
            ></span
          >
        </div>
      </div>
    </div>

    <!-- <span>Settings</span> -->
    {#if setOpen}
      <div
        class="col-start-4 row-start-1 transition-all duration-500 ease-in-out"
        transition:blur
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
            <span class="text-xs">Choose Item or Shade</span>
            <div class="flex flex-row gap-1 w-full">
              <button
                on:click={resetItem}
                class="border rounded p-1 border-green-500 hover:bg-green-500 hover:text-white transition-colors duration-300 ease-in-out"
                >All</button
              >
              <!-- Item Selector -->
              <select
                bind:value={item_name}
                class="border rounded px-1 py-1 w-full transition-colors"
                class:bg-gray-400={shade_name !== ""}
                class:text-gray-500={shade_name !== ""}
                class:cursor-not-allowed={shade_name !== ""}
                disabled={shade_name !== ""}
              >
                <!-- Placeholder option (disabled, hidden in dropdown) -->
                <option value="" disabled selected hidden>
                  {shade_name !== "" ? "" : "Select item"}
                </option>

                {#each [...chupps_items].sort( (a, b) => a.item.localeCompare(b.item), ) as i}
                  <option value={i.item}>{i.item}</option>
                {/each}
              </select>

              <!-- Shade Selector -->
              <select
                bind:value={shade_name}
                class="border rounded px-1 py-1 w-full transition-colors"
                class:bg-gray-400={item_name !== ""}
                class:text-gray-500={item_name !== ""}
                class:cursor-not-allowed={item_name !== ""}
                disabled={item_name !== ""}
              >
                <!-- Placeholder option -->
                <option value="" disabled selected hidden>
                  {item_name !== "" ? "" : "Select shade"}
                </option>

                {#each [...chupps_shades].sort( (a, b) => a.shade.localeCompare(b.shade), ) as i}
                  <option value={i.shade}>{i.shade}</option>
                {/each}
              </select>
            </div>
          </div>

          <button
            class="p-0 mt-1 border border-blue-500 rounded py-0 px-2 h-full hover:bg-blue-500 hover:text-white transition-all duration-300 ease-out"
            on:click={applyFilters}
            class:bg-blue-500={item_name !== "" || shade_name !== ""}
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

    <div class="card-alt2 col-start-3 row-start-3 flex-col w-full h-full">
      <div class="flex flex-col justify-center items-center my-5">
        <span class="">Data Statistics</span>
        <span class="text-gray-400 text-[10px] -mt-1"
          >(in the selected timeframe)</span
        >
      </div>
      {#each stats as stat, i}
        <div
          class="flex flex-row justify-between items-center pt-1 border-b border-gray-400 rounded-r-xl w-11/12"
          class:border-b-0={i === stats.length - 1}
        >
          <span class="text-base text-gray-500">{stat.title}</span>
          <span
            class={`text-xl font-medium text-right mr-2
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

    <div
      class="card-alt2 col-start-3 row-start-4 row-end-6 flex-col w-full h-full"
    >
      <span class="mt-2">Forecast Details</span>
      {#each details as stat, i}
        <div
          class="flex flex-row justify-between items-center pt-1 border-b border-gray-400 rounded-r-xl w-11/12"
          class:border-b-0={i === details.length - 1}
        >
          <span class="text-base text-gray-500">{stat.title}</span>
          <span class={`text-xl font-medium text-right mr-2`}>
            {stat.value}
          </span>
        </div>
      {/each}
    </div>

    <div
      class="col-span-2 card flex flex-col"
      class:row-start-1={expand_forecast}
      class:row-end-3={expand_forecast}
    >
      <div
        class="flex flex-row items-center justify-between w-full gap-0 px-10"
      >
        <div class="flex flex-row gap-5">
          <ChuppsButton />
          <span class="mt-5 text-center text-3xl">Daily Sales</span>
        </div>
      </div>
      <div
        id="actual-plot"
        class="w-full h-full rounded-2xl overflow-hidden"
      ></div>
    </div>

    <div class="col-span-2 row-span-3 card flex flex-col">
      <div
        class="flex flex-row items-center justify-between w-full gap-0 px-10"
      >
        <div class="flex flex-row gap-5">
          <ChuppsButton />
          <span class="mt-5 text-center align-middle text-3xl"
            >Forecasted Sales</span
          >
        </div>
        <button
          class="z-100 flex mt-auto flex-row gap-2 items-center justify-center text-gray-500 hover:text-black shadow-none hover:shadow-[0_3px_8px_rgba(0,0,0,0.24)] border border-gray-300 p-2 rounded-lg text-xs transition-all duration-300 ease-in-out"
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

      {#if !naData}
        <div
          id="forecast-plot"
          class="w-full h-full rounded-2xl overflow-auto"
        ></div>
      {:else}
        <div
          class="flex flex-col justify-center items-center gap-5 mt-10 px-32"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="80"
            height="80"
            fill="red-500"
            class="bi bi-ban"
            viewBox="0 0 16 16"
          >
            <path
              d="M15 8a6.97 6.97 0 0 0-1.71-4.584l-9.874 9.875A7 7 0 0 0 15 8M2.71 12.584l9.874-9.875a7 7 0 0 0-9.874 9.874ZM16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0"
            />
          </svg><span class="text-red-500 text-3xl text-center"
            >Not enough data for this shade/item to forecast!</span
          >
        </div>
      {/if}
    </div>

    <div
      class="flex flex-col justify-start rounded-xl items-center shadow-xl h-full col-start-4 row-end-6 overflow-y-auto pt-4 px-2 bg-white"
      class:row-start-1={!setOpen}
      class:row-start-2={setOpen}
    >
      <span class="font-semibold text-lg">AI Insights</span>
      <span class="font-semibold text-xs mb-2 text-red-500"
        >Usage left: {llm_used}</span
      >

      <button
        class="flex flex-row gap-2 items-center justify-center text-gray-500 hover:text-black shadow-none hover:shadow-[0_3px_8px_rgba(0,0,0,0.24)] border border-gray-300 p-2 rounded-lg text-xs transition-all duration-300 ease-in-out disabled:cursor-not-allowed"
        disabled={isLLMthinking}
        on:click={runLLM}
        on:click={setLLM}
      >
        <img
          width="20"
          height="20"
          src="https://img.icons8.com/ios-glyphs/30/bot.png"
          alt="bot"
          class="fill-current"
        />

        {#if !isLLMthinking}
          <span>Run AI Analysis</span>
        {:else}
          <span class="animate-pulse">Thinking...</span>
        {/if}
      </button>

      <div class="bg-gray-300 w-3/4 h-[2px] my-3 rounded-xl"></div>

      <div
        class="w-full h-full bg-gray-200 rounded-xl p-2 group hover:bg-gray-100 transition-all duration-100 ease-in-out overflow-y-auto scrollbar-thin scrollbar-thumb-gray-400 scrollbar-track-gray-200"
        class:animate-pulse={isLLMthinking}
      >
        <div
          class="whitespace-pre-wrap break-words max-w-full overflow-y-auto prose max-h-full group-hover:text-black"
        >
          {@html renderedMarkdown}

          {#if !isLLMon && !isLLMthinking}
            <ul class="list-disc pl-10">
              <li>Select item/shade and hit enter</li>
              <li>Run AI Analysis to gain advanced insights!</li>
            </ul>
          {/if}
        </div>
      </div>
    </div>
  </div>
</div>

<style>
  @reference "tailwindcss";

  .card {
    @apply bg-white w-full h-full rounded-lg flex flex-col items-center justify-start shadow-xl;
  }
  .card-alt {
    @apply bg-transparent w-full h-full rounded-lg flex items-center justify-center;
  }
  .card-alt2 {
    @apply bg-white w-full h-full rounded-lg flex items-center justify-start shadow-xl;
  }

  .card-growth {
    @apply w-full h-full rounded-lg flex items-center justify-start shadow-xl;
  }
</style>
