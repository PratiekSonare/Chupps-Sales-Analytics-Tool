<script lang="ts">
  import { onMount } from "svelte";
  import { marked } from "marked";
  import { blur } from "svelte/transition";
  import { format } from "d3-format";
  import ChuppsButton from "./ChuppsButton.svelte";
  import CalculationPopup from "./CalculationPopup.svelte";
  const formatNumber = format(",");

  let tooltipHTML = `
    <div class="p-2">
      <div class="flex flex-col items-center gap-4 mb-4 w-full">
        <span class="text-lg font-semibold text-white">Calculation Used:</span>
        <img src="/equation.svg" alt="Calculation equation" class="w-full invert mx-auto" />
      </div>
      <div class="space-y-2">
        <span class="text-xs font-semibold text-gray-100">Current Version Details:</span>
        <ul class="list-disc list-inside text-xs text-yellow-500 pl-4">
          <li>Previous year sales are considered from <strong>2024-03-01</strong> to <strong>2025-03-01</strong>.</li>
          <li>Forecasted sales are based on your selected filter time frame.</li>
        </ul>
      </div>
    </div>
  `;

  function showTooltip(e) {
    const tooltip = document.getElementById("tooltip");
    tooltip.innerHTML = tooltipHTML;
    tooltip.style.top = `${e.clientY + 10}px`;
    tooltip.style.left = `${e.clientX - 350}px`;
    tooltip.style.opacity = 0.85;
  }

  function hideTooltip() {
    const tooltip = document.getElementById("tooltip");
    tooltip.style.opacity = 0;
  }

  let tooltipHTML2 = `
    <div class="p-2">
      <div class="flex flex-col items-center gap-4 mb-4 w-full">
        <span class="text-base font-semibold text-white">Based upon an association rule mining method called -- 'Apriori Method'</span>
      </div>
      <div class="space-y-2">
        <ul class="list-disc list-inside text-xs text-yellow-500">
          <li class="">If two shades are bought together more frequently on the same date, this gives them a higher score!</li>
          <li>In short, higher score => both shades bought together more frequently</li>
        </ul>
      </div>
    </div>
  `;

  function showTooltip2(e) {
    const tooltip = document.getElementById("tooltip");
    tooltip.innerHTML = tooltipHTML2;
    tooltip.style.top = `${e.clientY + 10}px`;
    tooltip.style.left = `${e.clientX - 350}px`;
    tooltip.style.opacity = 0.85;
  }

  function hideTooltip2() {
    const tooltip = document.getElementById("tooltip");
    tooltip.style.opacity = 0;
  }

  export let wo_centro_prophet;
  export let chupps_23_25_full;
  export let curr_max_data;

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
  let startDate = "2025-03-01";
  let endDate = "2026-02-01";
  let maxEntry = 0;
  let max_sales_day = 0;
  let firstTrend = 0;
  let lastTrend = 0;
  let forecast_trend = "Upward";

  //from 2025-03-01 to 2026-03-01
  let forecast_total_sales = 458810;
  let monthly_avg_sales = 41443;
  let weekly_avg_sales = 9530;
  let yearly_avg_sales = 497312;
  let percentage_growth = 114.5;

  let historicalTotalSales = 344390;
  let historical_avg = 114797;

  let llm_response = "Select an item/shade and hit enter!"; // Better initial state
  let renderedMarkdown = "";
  let renderedMarkdownGraph = "";
  let activeButton = "data";

  if (yearly_avg_sales === 0) {
    forecast_trend = "NO TREND";
  }

  let item_name = "";
  let shade_name = "";
  let setOpen = true;
  let setGraph = false;
  let isLLMon = false;
  let isLLMthinking = false;
  let isLLMthinkingGraph = false;
  let graphAnDone = 0;
  let anDone = 0;
  let expand_rotate = false;
  let expand_llm_response = false;
  let bestShades = [];

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
  $: formatted_historial_total = formatNumber(historicalTotalSales.toFixed(0));
  $: formatted_historical_yearly_avg_sales = formatNumber(
    historical_avg.toFixed(0),
  );

  // Get all unique years from the data
  let years = [];
  let numberOfYears = 0;

  $: history = [
    {
      title: "All-Time Sales",
      value: formatted_historial_total,
    },
    {
      title: "All-time Yearly Avg.",
      value: formatted_historical_yearly_avg_sales,
    },
  ];

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

    anDone = 0;
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
        // console.log("llm_response: ", response);

        renderedMarkdown = marked(response || "Could not generate insights");
      } catch (error) {
        console.error("Error generating insights:", error);
        llm_response = "Error generating insights. Please try again.";
        renderedMarkdown = marked(
          "Error generating insights. Please try again.",
        );

        console.log("Rendered Markdown: ", renderedMarkdown);
      } finally {
        anDone = 1;
        isLLMthinking = false;
      }
    }
  }

  async function runLLMforGraph() {
    if (llm_used <= 0) {
      console.log("LLM usage limit reached");
      return;
    }

    graphAnDone = 0;
    isLLMthinkingGraph = true;
    llm_used = llm_used - 1;

    if (item_name || shade_name || (!item_name && !shade_name)) {
      try {
        // Generate appropriate metadata
        const curr_metadata = generateMetadata();
        console.log("curr_metadata: ", curr_metadata);

        const response = await getLLMReponseGraph(curr_metadata);

        renderedMarkdownGraph = marked(
          response || "Could not generate insights",
        );
      } catch (error) {
        console.error("Error generating insights:", error);
        llm_response = "Error generating insights. Please try again.";
        renderedMarkdownGraph = marked(
          "Error generating insights. Please try again.",
        );
      } finally {
        isLLMthinkingGraph = false;
        graphAnDone = 1;
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
    bestShadeComb();
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

    applyFilters();
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

    const filteredForecastGrowth = filterForecast(startDate, endDate);

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
    console.log("startDate:", startDate);
    console.log("endDate:", endDate);
    console.log("Growth (%):", growth.toFixed(2));

    return growth;
  }

  function applyFilters() {
    if (!item_name && !shade_name) {
      currentSalesData = wo_centro_prophet;
    }

    anDone = 0;
    graphAnDone = 0;
    renderedMarkdown = "";
    renderedMarkdownGraph = "";

    const filtered = filterForecast(startDate, endDate);
    filteredForecast = filterForecast(startDate, endDate);

    //total sales for timeframe
    forecast_total_sales = filteredForecast.reduce((sum, d) => sum + d.yhat, 0);

    if (forecast_total_sales === 0) {
      naData = true;
      forecast_trend = "NO TREND";
    } else {
      naData = false;
    }

    historicalTotalSales = currentSalesData.reduce((sum, d) => sum + d.y, 0);
    years = [
      ...new Set(currentSalesData.map((d) => new Date(d.ds).getFullYear())),
    ];
    numberOfYears = years.length;

    historical_avg =
      numberOfYears > 0 ? historicalTotalSales / numberOfYears : 0;
    console.log("historical average of given item: ", historical_avg);

    // Generate appropriate metadata
    const curr_metadata = generateMetadata();
    console.log("curr_metadata: ", curr_metadata);

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
    forecast_total_sales = 458810;
    monthly_avg_sales = 41443;
    weekly_avg_sales = 9530;
    yearly_avg_sales = 497312;
    percentage_growth = 114.5;
    historicalTotalSales = 344390;
    historical_avg = 114797;

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

    const layout = {
      title: "Forecast",
      margin: { t: 50, l: 50, r: 50, b: 50 },
      xaxis: { title: "Date" },
      yaxis: { title: "Sales" },
    };

    const daily_sales_plot = {
      x: item_sales_data.map((d) => d.ds),
      y: item_sales_data.map((d) => d.y),
      mode: "lines",
      name: "Forecast",
    };

    const layoutForecast = {
      title: "Forecast",
      height: 350,
      margin: { t: 50, l: 60, r: 50, b: 20 },
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
        line: { width: 1, color: "lightgray" },
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

  function openGraphAn() {
    setGraph = !setGraph;
  }

  function setLLM() {
    isLLMon = !isLLMon;
    renderedMarkdown = "";
  }

  function expandLLMresponse() {
    expand_llm_response = !expand_llm_response;
  }

  //LLM PARSING
  function generateMetadata() {
    const isFiltered = item_name || shade_name;
    const filteredData = isFiltered ? item_sales_data : wo_centro_prophet;
    const originalData = wo_centro_prophet;
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
        forecastTotalSales: currentForecast.reduce((sum, d) => sum + d.yhat, 0),
        forecast_averages: {
          daily: weekly_avg_sales / 7,
          weekly: weekly_avg_sales,
          monthly: monthly_avg_sales,
          yearly: yearly_avg_sales,
        },
        historicalTotalSales: historicalTotalSales,
        historical_averages: {
          yearly: historical_avg,
        },
        trend: forecast_trend,
        dataPoints: filteredData.length,
        forecastPoints: currentForecast.length,
      },
      modelDetails: {
        type: "Prophet",
        seasonality: "yearly",
        holidaysIncluded: true,
      },
    };
  }

  async function getLLMResponse(metadata) {
    try {
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

                    Give directional insights, not based just a summary on the metadata but insights based on external knowledge.

                    Focus on:
                    1. Business recommendations based on the metrics
                    2. Directional insights based on external knowledge on time, India and open footwear
                    
                    Give a brief summary in under 500 words only.`;

      const alt_prompt = `
          **Role**: You are a **strategic sales analyst** with deep expertise in:  
            - Indian consumer behavior (geography, economics, culture)  
            - Footwear industry trends (open footwear, seasonal demand, distribution models)  
            - Forecasting-driven business actions (not just model stats, but what to *do* with them)  

            **Task**: Analyze the metadata from a **Prophet-based sales forecast** for an Indian open-footwear brand and provide:  
            1. **Strategic insights** (combining metadata + external knowledge)  
            2. **Concrete actions** for the sales manager (prioritized by impact)  

            ---  

            **Metadata Background**:  The sales belong to a budding open footwear brand in India. The brand currently operates on a distributor model, with major distributors across India ordering footwear in bulk at a time.
                  Recently, they have also started online marketplace and offline store based sales. The input data to the forecasting model contains this data.
                  
                  Now, some background/domain about the metadata that is being provided to you: 
                    1. filters: specifies the item or shade used to filter and display sales and forecasted data belonging to that item or shade. it also includes date filtering, that you musst take into account while analyzing. If aggregationLevel is 'All Products', that means the meta-data belongs to total sales record, otherwise it is for a particular item or a shade. dateRange is the range of dates used to filter display data for.
                    2. metrics: some metrics that are being displayed in the tool, avg_sales contain yearly, monthly and weekly average sales of entire sales or for a particular item or shade. forecastTotalSales is the sum of forecasted sales for all products or either a particular item or shade, within the dateRange.
                    3. prophet_model_stats: the parameters used for fitting the sales data with Prophet model by Meta. holidays mentions days of importance, since we notice a spike in sales during these days. predictionPeriod is the number of days predicted by the model ahdead of the latest day in the input data.

            **Input Metadata**:  ${JSON.stringify(metadata, null, 2)}
        `;

      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({
          model: "deepseek/deepseek-chat-v3-0324:free",
          messages: [{ role: "user", content: alt_prompt }],
        }),
      });

      const data = await response.json();
      return data.choices[0]?.message?.content || "No analysis available";
    } catch (error) {
      console.error("LLM Error:", error);
      return "Unable to generate analysis at this time";
    }
  }

  async function getLLMReponseGraph(metadata) {
    filteredForecast = filterForecast(startDate, endDate);

    const data = filteredForecast.map((row) => ({
      ds: row.ds,
      yhat: row.yhat,
      yhat_upper: row.yhat_upper,
      yhat_lower: row.yhat_lower,
      trend: row.trend,
    }));

    try {
      const res = await fetch(`http://localhost:8000/api/imgchat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          data: data,
          message: JSON.stringify(metadata, null, 2),
        }),
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const llm_response_for_img = await res.json();
      console.log("graph llm response: ", llm_response_for_img);

      return (
        llm_response_for_img.choices?.[0]?.message?.content ||
        llm_response_for_img.message ||
        "No analysis available"
      );
    } catch (error) {
      console.error(`Failed to call graph api:`, error);
      return "Error analyzing graph data";
    }
  }

  async function bestShadeComb() {
    const data = chupps_23_25_full.map((row) => ({
      purDate: row.purDate,
      shade: row.shade,
      sales: row.sales,
    }));

    try {
      const res = await fetch(`http://localhost:8000/api/bestshade`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ data }),
      });

      bestShades = await res.json();
      renderBestShadesTable(bestShades);
    } catch (error) {
      console.error("error faced: ", error);
    }
  }

  function renderBestShadesTable(data) {
    const bestShadesTable = {
      type: "table",
      header: {
        values: ["First Shade", "Second Shade", "Score"],
        align: "center",
        line: { width: 1, color: "black" },
        fill: { color: "lightgray" },
        font: { family: "Arial", size: 12, color: "black" },
      },
      cells: {
        values: [
          data.map((d) => d.shade1),
          data.map((d) => d.shade2),
          data.map((d) => d.support),
        ],
        align: "left",
        line: { color: "black", width: 1 },
        font: { family: "Arial", size: 11, color: ["black"] },
        height: 24,
      },
    };

    (window as any).Plotly.newPlot("best-shades-table", [bestShadesTable], {
      margin: { t: 10, b: 10, l: 20, r: 20 },
      displayModeBar: false,
      responsive: true,
    });
  }
</script>

{#if calculationOpen}
  <CalculationPopup bind:calculationOpen />
{/if}

<div class="w-screen h-screen relative">
  {#if expand_llm_response}
    <div
      class="rounded-xl bxsdw absolute z-[250] p-5 w-1/2 h-3/4 top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-gray-300 border border-gray-700"
    >
      <button
        on:click={() => (expand_llm_response = false)}
        class="absolute top-8 right-10 text-2xl text-red-400">x</button
      >

      {#if activeButton === "data"}
        <div
          class="text2 border w-full h-full p-10 rounded-xl border-gray-400 bxsdw bg-gray-200 whitespace-pre-wrap break-words max-w-full overflow-y-auto prose max-h-full group-hover:text-black"
        >
          {@html renderedMarkdown}

          {#if !isLLMon && !isLLMthinking}
            <ul class="list-disc pl-10">
              <li>Select item/shade and hit enter</li>
              <li>Run AI Analysis to gain advanced insights!</li>
            </ul>
          {/if}
        </div>
      {:else}
        <div
          class="text2 whitespace-pre-wrap break-words max-w-full overflow-y-auto prose max-h-full group-hover:text-black"
        >
          {@html renderedMarkdownGraph}

          {#if !isLLMon && !isLLMthinking}
            <ul class="list-disc pl-10">
              <li>Select item/shade and hit enter</li>
              <li>Run Graph Analysis to gain advanced insights!</li>
            </ul>
          {/if}
        </div>
      {/if}
    </div>
  {/if}

  <div class="grid grid-cols-4 grid-rows-[1fr_3fr_3fr_1fr] gap-3 h-full p-5">
    <div class="card bxsdw flex flex-col p-2">
      <span class="text-xl mt-auto">Total Pairs Sold</span>
      <span class="text-gray-400 text-[10px] -my-1">(All Time)</span>
      <span class="text-5xl text-black my-auto">{formatted_total_sales}</span>
    </div>

    <div class="card bxsdw flex flex-col p-2">
      <span class="text-xl mt-auto">Total Revenue Generated</span>
      <span class="text-gray-400 text-[10px] -my-1">(All Time)</span>
      <span class="text-5xl text-black my-auto">{formatted_total_revenue}</span>
    </div>

    <div class="flex flex-row gap-3">
      <div class="card bxsdw flex flex-col p-2">
        <span class="text-xl mt-auto">Total Parties</span>
        <span class="text-gray-400 text-[10px] -my-1">(All Time)</span>
        <span class="text-5xl text-black my-auto">{total_parties}</span>
      </div>
      <!-- svelte-ignore a11y_no_static_element_interactions -->
      <div
        class="card-growth bxsdw shadow-xl flex flex-col p-2"
        on:mousemove={(e) => showTooltip(e)}
        on:mouseenter={showTooltip}
        on:mouseleave={hideTooltip}
        class:bg-green-300={percentage_growth > 0}
        class:bg-red-300={percentage_growth < 0}
      >
        <div class="flex flex-col mt-auto gap-0 items-center">
          <span class="text-xl mt-auto">Growth</span>
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
            class="p-0 mt-1 border border-blue-500 rounded py-0 px-2 h-full hover:bg-blue-500 text-gray-400 hover:text-white transition-all duration-300 ease-out"
            on:click={applyFilters}
            class:bg-blue-500={item_name !== "" || shade_name !== ""}
          >
            Enter
          </button>
        </div>
      </div>
    {/if}

    <!-- //if setOpen = true, then change row-start-2 to row-start-1 -->
    <div
      class={`card bxsdw col-start-3 row-start-2 row-end-3 flex flex-col pt-2`}
    >
      <span>Data Input</span>
      <div id="forecast-table" class="w-full h-full"></div>
    </div>

    <div
      class="card-alt2 bxsdw col-start-3 row-start-3 row-span-3 flex-col w-full h-full"
    >
      <div class="flex flex-col justify-center items-center mt-5">
        <span class="">Data Statistics</span>
        <span class="text-gray-400 text-[10px] -mt-1"
          >(in the selected timeframe)</span
        >
      </div>

      <!-- trend -->
      <div
        class="flex flex-row justify-between text-2xl w-full my-2 px-4 py-1 {forecast_trend ===
        'Upward'
          ? 'bg-green-400'
          : 'bg-red-400'}"
      >
        <span class="text-white">Trend</span>
        <span
          class={forecast_trend === "Upward"
            ? "text-green-600"
            : "text-red-600"}>{forecast_trend}</span
        >
      </div>

      <span class="self-start px-4 mt-1 text-lg border-y border-r rounded-r-xl"
        >Forecast</span
      >
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

      <span class="self-start px-4 mt-1 text-lg border-y border-r rounded-r-xl"
        >History</span
      >
      {#each history as stat, i}
        <div
          class="flex flex-row justify-between items-center pt-1 border-b border-gray-400 rounded-r-xl w-11/12"
          class:border-b-0={i === history.length - 1}
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

    <div class="col-span-2 card-noclick bxsdw flex flex-col">
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

    <div class="col-span-2 row-span-3 card-noclick bxsdw flex flex-col">
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

    <!-- Tooltip -->
    <div
      id="tooltip"
      class="fixed z-50 bg-gray-800 text-white text-xs rounded px-2 py-1 pointer-events-none opacity-0 transition-opacity duration-200"
    ></div>

    <!-- Your target div -->
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div
      class="flex flex-col bxsdw justify-start rounded-xl items-center h-full col-start-4 row-end-3 overflow-y-auto overflow-x-hidden py-2 px-2 bg-white"
      class:row-start-1={!setOpen}
      class:row-start-2={setOpen}
      on:mousemove={(e) => showTooltip2(e)}
      on:mouseenter={showTooltip2}
      on:mouseleave={hideTooltip2}
    >
      <div class="flex w-full flex-col items-center overflow-hidden">
        <span class="">Best Shade Combinations</span>
        <span class="text-gray-400 text-[10px] -mt-1">
          (in the selected timeframe)
        </span>
        <div id="best-shades-table" class="w-full h-full"></div>
      </div>
    </div>

    <div
      class="flex flex-col bxsdw justify-start rounded-xl items-center h-full col-start-4 row-start-3 row-end-6 overflow-y-auto pt-4 px-2 bg-white"
    >
      <!-- <span class="font-semibold text-2xl ai-font">AI Insights</span> -->
      <img src="/chupps-ai.svg" alt="chupps ai logo" class="w-[30%]" />

      <span class="font-semibold text-xs mb-2 text-red-500"
        >Usage limit: {llm_used}</span
      >
      <div class="flex flex-row gap-1">
        <!-- DATA ANALYSIS BUTTON -->
        <button
          class={`flex flex-row gap-2 items-center justify-center border border-gray-300 p-2 rounded-lg text-xs transition-all duration-300 ease-in-out disabled:cursor-not-allowed ${
            anDone === 1
              ? activeButton === "data"
                ? "bg-green-600 text-white hover:shadow-md"
                : "bg-white text-gray-700 hover:bg-gray-100"
              : "text-gray-500 hover:text-black"
          }`}
          disabled={isLLMthinking}
          on:click={() => {
            activeButton = "data";
            if (anDone !== 1) {
              runLLM();
              setLLM();
            }
          }}
        >
          <svg
            width="20"
            height="20"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 640 512"
            class="fill-current"
          >
            <path
              d="M320 0c17.7 0 32 14.3 32 32l0 64 120 0c39.8 0 72 32.2 72 72l0 272c0 39.8-32.2 72-72 72l-304 0c-39.8 0-72-32.2-72-72l0-272c0-39.8 32.2-72 72-72l120 0 0-64c0-17.7 14.3-32 32-32zM208 384c-8.8 0-16 7.2-16 16s7.2 16 16 16l32 0c8.8 0 16-7.2 16-16s-7.2-16-16-16l-32 0zm96 0c-8.8 0-16 7.2-16 16s7.2 16 16 16l32 0c8.8 0 16-7.2 16-16s-7.2-16-16-16l-32 0zm96 0c-8.8 0-16 7.2-16 16s7.2 16 16 16l32 0c8.8 0 16-7.2 16-16s-7.2-16-16-16l-32 0zM264 256a40 40 0 1 0 -80 0 40 40 0 1 0 80 0zm152 40a40 40 0 1 0 0-80 40 40 0 1 0 0 80zM48 224l16 0 0 192-16 0c-26.5 0-48-21.5-48-48l0-96c0-26.5 21.5-48 48-48zm544 0c26.5 0 48 21.5 48 48l0 96c0 26.5-21.5 48-48 48l-16 0 0-192 16 0z"
            />
          </svg>
          <span>
            {#if isLLMthinking}
              <span class="animate-pulse">Thinking...</span>
            {:else if anDone === 1}
              {activeButton === "data"
                ? "Viewing Data Analysis"
                : "View Data Analysis"}
            {:else}
              Run Data Analysis
            {/if}
          </span>
        </button>

        <!-- GRAPH ANALYSIS BUTTON -->
        <button
          class={`flex flex-row gap-2 items-center justify-center border border-gray-300 p-2 rounded-lg text-xs transition-all duration-300 ease-in-out disabled:cursor-not-allowed ${
            graphAnDone === 1
              ? activeButton === "graph"
                ? "bg-green-600 text-white hover:shadow-md"
                : "bg-white text-gray-700 hover:bg-gray-100"
              : "text-gray-500 hover:text-black"
          }`}
          disabled={isLLMthinkingGraph}
          on:click={() => {
            activeButton = "graph";
            if (graphAnDone !== 1) {
              setLLM();
              runLLMforGraph();
            }
          }}
        >
          <svg
            width="20"
            height="20"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 448 512"
            class="fill-current"
          >
            <path
              d="M160 80c0-26.5 21.5-48 48-48l32 0c26.5 0 48 21.5 48 48l0 352c0 26.5-21.5 48-48 48l-32 0c-26.5 0-48-21.5-48-48l0-352zM0 272c0-26.5 21.5-48 48-48l32 0c26.5 0 48 21.5 48 48l0 160c0 26.5-21.5 48-48 48l-32 0c-26.5 0-48-21.5-48-48L0 272zM368 96l32 0c26.5 0 48 21.5 48 48l0 288c0 26.5-21.5 48-48 48l-32 0c-26.5 0-48-21.5-48-48l0-288c0-26.5 21.5-48 48-48z"
            />
          </svg>
          <span>
            {#if isLLMthinkingGraph}
              <span class="animate-pulse">Thinking...</span>
            {:else if graphAnDone === 1}
              {activeButton === "graph"
                ? "Viewing Graph Analysis"
                : "View Graph Analysis"}
            {:else}
              Run Graph Analysis
            {/if}
          </span>
        </button>
      </div>

      <div class="bg-gray-300 w-3/4 h-[2px] my-3 rounded-xl"></div>

      <div
        class="w-full h-full bg-gray-200 rounded-xl p-2 group hover:bg-gray-100 transition-all duration-100 ease-in-out overflow-y-auto scrollbar-thin scrollbar-thumb-gray-400 scrollbar-track-gray-200"
        class:animate-pulse={isLLMthinking}
      >
        <button
          class="text-gray-400 hover:text-black justify-end"
          on:click={expandLLMresponse}
          ><svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 512 512"
            width="20"
            height="20"
            class="fill-current"
            ><!--!Font Awesome Free 6.7.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc.--><path
              d="M200 32L56 32C42.7 32 32 42.7 32 56l0 144c0 9.7 5.8 18.5 14.8 22.2s19.3 1.7 26.2-5.2l40-40 79 79-79 79L73 295c-6.9-6.9-17.2-8.9-26.2-5.2S32 302.3 32 312l0 144c0 13.3 10.7 24 24 24l144 0c9.7 0 18.5-5.8 22.2-14.8s1.7-19.3-5.2-26.2l-40-40 79-79 79 79-40 40c-6.9 6.9-8.9 17.2-5.2 26.2s12.5 14.8 22.2 14.8l144 0c13.3 0 24-10.7 24-24l0-144c0-9.7-5.8-18.5-14.8-22.2s-19.3-1.7-26.2 5.2l-40 40-79-79 79-79 40 40c6.9 6.9 17.2 8.9 26.2 5.2s14.8-12.5 14.8-22.2l0-144c0-13.3-10.7-24-24-24L312 32c-9.7 0-18.5 5.8-22.2 14.8s-1.7 19.3 5.2 26.2l40 40-79 79-79-79 40-40c6.9-6.9 8.9-17.2 5.2-26.2S209.7 32 200 32z"
            /></svg
          ></button
        >

        {#if activeButton === "data"}
          <div
            class="text2 whitespace-pre-wrap break-words max-w-full overflow-y-auto prose max-h-full group-hover:text-black"
          >
            {@html renderedMarkdown}

            {#if !isLLMon && !isLLMthinking}
              <ul class="list-disc pl-10">
                <li>Select item/shade and hit enter</li>
                <li>Run AI Analysis to gain advanced insights!</li>
              </ul>
            {/if}
          </div>
        {:else}
          <div
            class="text2 whitespace-pre-wrap break-words max-w-full overflow-y-auto prose max-h-full group-hover:text-black"
          >
            {@html renderedMarkdownGraph}

            {#if !isLLMon && !isLLMthinking}
              <ul class="list-disc pl-10">
                <li>Select item/shade and hit enter</li>
                <li>Run Graph Analysis to gain advanced insights!</li>
              </ul>
            {/if}
          </div>
        {/if}
      </div>
    </div>
  </div>
</div>

<style>
  @reference "tailwindcss";

  button {
    @apply transition-all transform cursor-pointer active:scale-95 scale-100 duration-100 ease-in;
  }

  .bxsdw {
    box-shadow:
      rgba(0, 0, 0, 0.09) 0px 2px 1px,
      rgba(0, 0, 0, 0.09) 0px 4px 2px,
      rgba(0, 0, 0, 0.09) 0px 8px 4px,
      rgba(0, 0, 0, 0.09) 0px 16px 8px,
      #00000017 0px 32px 16px;
  }
  .card {
    @apply bg-white w-full h-full rounded-lg flex flex-col items-center justify-start  border border-gray-300 cursor-pointer transition transform active:scale-95 duration-100 ease-in-out;
  }
  .dark-card {
    @apply bg-gray-900 w-full h-full rounded-lg flex flex-col items-center justify-start  border border-gray-700 cursor-pointer transition transform active:scale-95 duration-100 ease-in-out;
  }
  .card-alt {
    @apply cursor-pointer transition transform active:scale-95 duration-100 ease-in-out bg-transparent w-full h-full rounded-lg flex items-center justify-center border border-gray-300;
  }
  .card-alt2 {
    @apply cursor-pointer transition transform active:scale-95 duration-100 ease-in-out bg-white w-full h-full rounded-lg flex items-center justify-start  border border-gray-300;
  }

  .card-growth {
    @apply w-full h-full rounded-lg flex items-center justify-start  border border-gray-300 cursor-pointer transition transform active:scale-95 duration-100 ease-in-out;
  }

  .card-noclick {
    @apply bg-white w-full h-full rounded-lg flex flex-col items-center justify-start border border-gray-300 cursor-pointer;
  }
</style>
