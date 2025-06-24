<script lang="ts">
    import { GoTrueClient } from "@supabase/supabase-js";
    import { supabase } from "../lib/supabaseClient";
    import shadeHexMap from "../lib/shade_hex_map.json";
    import { marked } from "marked";
    import { tweened } from "svelte/motion";
    import { onMount } from "svelte";
    import { cubicOut } from "svelte/easing";

    // Create tweened stores
    const animatedItemRank = tweened(0, { duration: 2000, easing: cubicOut });
    const animatedShadeRank = tweened(0, { duration: 2000, easing: cubicOut });

    $: animatedItemRank.set(item_rank);
    $: animatedShadeRank.set(shade_rank);

    // Update values when component mounts
    onMount(() => {
        animatedItemRank.set(item_rank);
        animatedShadeRank.set(shade_rank);
    });

    export let chupps_23_25_full;
    export let ranked_items_by_sales;
    export let ranked_shades_by_sales;

    let items = [];
    // let selectedItem = "CHUPPS X MI LEGACY";
    // let selectedShade = "BLUE";
    let selectedItem = "APEX";
    let selectedShade = "BLACK";
    let shades = [];
    let sku = "";
    let filteredData = [];
    let aggFilteredData = [];
    let images = [];
    let loading = 0;
    let yearDiff = 0;
    let shadeItemSelected = false;
    let thinking = false;

    // let llmResponse = "Loading...";
    let llmResponse = `Okay, let's break down these sales figures for our open footwear in India. Here’s what I'm seeing, thinking from a product and marketing perspective: **1. Performance: Winners & Laggards** * **Clear Winners:** Navy Blue and Black are the strongest performers, consistently showing the highest sales volume. Navy Blue in particular has strong peaks, suggesting a real pull with our customers. Black has a more steady demand, a solid base. * **Solid Performers:** Grey is doing decently well, with fluctuations, but a consistently positive volume. Brown also has decent, though lower, performance. * **Underperformers:** Grey Brown, Black Brown, and Navy Grey significantly lag behind in sales. Navy Grey is barely registering on the chart – this shade is a considerable concern and we need to understand why. **2. Understanding the Peaks & Dips - What's Happening in India?** * **Festival/Wedding Season (Oct-Dec):** The spike we see in Navy Blue, Black and Grey around October through December strongly suggests a link to festival and wedding seasons. People are buying new footwear for celebrations! This is *huge* for our marketing plans. * **New Year & Heat (Jan-Mar):** The dip in some colors after the New Year likely reflects settling back into routine after spending. The gradual uptick as we move towards March could be anticipating spring festivals or warmer weather. We should look at regional heat maps – perhaps sales accelerate sooner in warmer parts of India. * **Regional Events:** It’s difficult to pinpoint without more granular data, but smaller peaks in certain shades could be tied to regional festivals or events happening at those times. * **Potential Discount Timing:** The dips in some shades after a peak may indicate promotion end or discounts expiring. **3. Shades That Work Well Together - Bundling Opportunities** * **Navy Blue & Black:** These two show remarkably similar behavior. They peak and dip around the same times. *Definitely* explore bundling these – "Classic Comfort" or "Everyday Essentials" package. Promote them as complementing each other (one for celebrations, one for daily wear). * **Grey & Brown:** These shades have some correlation. They are not as strong as Navy and Black but could work together in a "Neutral Style" offering. * **Avoid Pairing Navy Grey**: As it barely sells, I would avoid marketing opportunities with this shade for the time being. **4. Geography - Where are Sales Differing?** This is where we *need* to dig deeper with our data. Here’s how geography likely influences sales: * **Metro Cities (Delhi, Mumbai, Bangalore, Kolkata):** We can expect higher volume across *all* shades in these areas. Trends will likely be faster, following newer fashion trends. Focus premium marketing efforts here. * **Tier 2/3 Cities:** Classic colors like Black and Navy will likely be far more popular than trendier shades. Marketing should focus on durability, value, and comfort. * **Humid Zones (Coastal Areas):** We need to see if specific shades perform better in humid climates – perhaps lighter, breathable-looking shades (though we don't have those here) are preferred. We should also determine whether the material is suitable for the climate. * **Dry Zones (Rajasthan, Gujarat):** Here, colours can be driven by local traditions, colours used for weddings and other cultural events. **5. Marketing & Product Strategies for India** * **Festival Focus:** *Aggressively* market Navy Blue, Black and Grey in the lead-up to major festivals (Diwali, Durga Puja, weddings, Holi). Run festival-themed campaigns. Pre-season discounts can work wonders. * **Regional Customization:** Tailor marketing messages and even product offerings to specific regions. What works in Delhi won’t necessarily work in Chennai. Explore regional color preferences. * **Bundling & Promotions:** Immediately implement the Navy Blue/Black and Grey/Brown bundle suggestions. Run promotions around these. * **Re-evaluate Underperformers:** We need to seriously question Grey Brown, Black Brown, and *especially* Navy Grey. * **Market Research:** Why aren’t they selling? Is it color perception? Do customers find them unattractive? * **Narrow Focus:** If they do have a small niche in specific areas, focus limited marketing there. * **Discontinue:** Be prepared to discontinue if they remain consistently poor performers. * **Colour Expansion**: Add more colours to the portfolio to take advantage of emerging trends. * **Material Science**: Ensure the footwear material is suitable for all types of climates in the country. * **Mobile-First Marketing:** India is a mobile-first market. Ensure all marketing is optimized for mobile devices. * **Influencer Marketing:** Partner with regional influencers to promote our footwear. To move forward, I'd recommend we pull sales data sliced by geography, demographics, and if possible, the source of the sale (online vs. retail store). This will give us a far more nuanced understanding of what's driving these trends and refine these strategies further.`;
    let marked_llmResponse = "";
    let salesOff = false;

    let primaryColor = "#fff";
    let secondaryColor = "#000";

    let historical_total_sales = 2518;
    let historical_yearly_average = 0;
    let numUniqueParties = 0;
    let item_rank = 0;
    let shade_rank = 0;

    // Update the colors when selectedShade changes
    $: if (selectedShade && shadeHexMap[selectedShade]) {
        primaryColor = shadeHexMap[selectedShade].primary;
        secondaryColor = shadeHexMap[selectedShade].secondary;
        shade_rank = calculateShadeRank(selectedShade);
    }

    // Load distinct items from Supabase
    onMount(async () => {
        const { data, error } = await supabase
            .from("chupps_23_25_full")
            .select("item", { count: "exact" })
            .order("item", { ascending: true });

        if (!error) {
            items = [...new Set(data.map((row) => row.item))];
        }

        const total_data = chupps_23_25_full.map((row) => ({
            purDate: row.purDate,
            shade: row.shade,
            item: row.item,
            sales: row.sales,
        }));

        historical_total_sales = 2518;

        try {
            const res = await fetch(
                `http://localhost:8000/item-shade/${selectedItem}-${selectedShade}`,
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ data: total_data }),
                },
            );
            aggFilteredData = await res.json();
            console.log("received filtered data: ", aggFilteredData);
        } catch (error) {
            console.error("heres the error, brother: ", error);
        }

        const trace1 = {
            x: aggFilteredData.map((d) => d.ds),
            y: aggFilteredData.map((d) => d.y),
            mode: "lines",
            name: "Forecast",
        };

        const layout = {
            title: "Item / Shade Sales",
            margin: { t: 60, l: 60, r: 60, b: 60 },
            xaxis: { title: "Date" },
            yaxis: { title: "Sales" },
        };

        (window as any).Plotly.newPlot("actual-plot", [trace1], layout, {
            displayModeBar: false,
            responsive: true,
        });

        plotAggSales(aggFilteredData);

        const tableData = {
            type: "table",
            header: {
                values: [
                    "Date",
                    "Party",
                    "Item",
                    "Gender",
                    "SKU",
                    "Shade",
                    "Sales",
                    "Size",
                    "Party Category",
                    "Mode",
                    "Location",
                    "Zone",
                    "State",
                ],
                align: "center",
                line: { width: 1, color: "black" },
                fill: { color: "lightgray" },
                font: { family: "Arial", size: 12, color: "black" },
            },
            cells: {
                values: [
                    filteredData.map((d) => d.purDate.split("T")[0]),
                    filteredData.map((d) => d.party),
                    filteredData.map((d) => d.item),
                    filteredData.map((d) => d.gender),
                    filteredData.map((d) => d.sku),
                    filteredData.map((d) => d.shade),
                    filteredData.map((d) => d.sales),
                    filteredData.map((d) => d.size),
                    filteredData.map((d) => d.party_category),
                    filteredData.map((d) => d.mode),
                    filteredData.map((d) => d.location),
                    filteredData.map((d) => d.zone),
                    filteredData.map((d) => d.state),
                ],
                align: "center",
                line: { color: "black", width: 1 },
                font: { family: "Arial", size: 11, color: ["black"] },
                height: 24,
            },
        };

        (window as any).Plotly.newPlot(
            "sales-table",
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

        const stateDataMap = {
            type: "table",
            header: {
                values: ["State", "Sales"],
                align: "center",
                line: { width: 1, color: "black" },
                fill: { color: "lightgray" },
                font: { family: "Arial", size: 12, color: "black" },
            },
            cells: {
                values: [
                    filteredData.map((d) => d.state),
                    filteredData.map((d) => d.sales),
                ],
                align: "center",
                line: { color: "black", width: 1 },
                font: { family: "Arial", size: 11, color: ["black"] },
                height: 24,
            },
        };
    });

    // Watch for selectedItem change and load matching shades
    $: if (selectedItem) {
        shadeItemSelected = true;
        loadShades(selectedItem);
        item_rank = calculateItemRank(selectedItem);
    }

    function toggleSales() {
        salesOff = !salesOff;
    }

    async function loadShades(item) {
        const { data, error } = await supabase
            .from("chupps_23_25_full")
            .select("shade")
            .eq("item", item)
            .order("shade", { ascending: true });
        // .select('shade', { distinct: true });

        if (!error) {
            shades = [...new Set(data.map((row) => row.shade))];
        }
    }

    $: if (selectedItem && selectedShade) {
        loadSKU(selectedItem, selectedShade);
    }

    $: if (aggFilteredData.length > 0) {
        historical_total_sales = calculateTotalSales();
        historical_yearly_average = calculateYearlyAverage();
    }

    function calculateTotalSales() {
        const totalsales = aggFilteredData.reduce((sum, d) => sum + d.y, 0);
        return totalsales;
        //already filtered by item and shade, we just need to return the sum of sales
    }

    function calculateYearlyAverage() {
        const totalsales = calculateTotalSales();

        const years = aggFilteredData.map((d) => new Date(d.ds).getFullYear());
        const minYear = Math.min(...years);
        const maxYear = Math.max(...years);

        yearDiff = maxYear - minYear + 1;

        const average = totalsales / yearDiff;

        return Math.round(average);
    }

    async function loadSKU(item, shade) {
        const { data, error } = await supabase
            .from("chupps_23_25_full")
            .select("sku")
            .eq("item", item)
            .eq("shade", shade)
            .limit(1); // assuming item-shade pair has only one SKU

        if (!error && data.length > 0) {
            sku = data[0].sku;
        } else {
            sku = "Not found";
        }
    }

    $: if (sku) {
        shadeItemSelected = true;
        loadImagesFromDropbox(sku);
    }

    async function filterTable(item, shade) {
        const query = supabase.from("chupps_23_25_full").select("*");

        if (item) query.eq("item", item);
        if (shade) query.eq("shade", shade);

        const { data, error } = await query;

        if (!error) {
            filteredData = data;
            numUniqueParties = calculateClient(data);
            renderTable(filteredData);

            const salesMap = getStateSalesMap(filteredData);
            updateMapColors(salesMap); // ← update the SVG map!
        } else {
            console.error("Filtering failed:", error.message);
            filteredData = [];
        }
    }

    function calculateItemRank(item) {
        const match = ranked_items_by_sales.find((row) => row.item === item);
        return match ? match.item_rank : null;
    }

    function calculateShadeRank(shade) {
        const match = ranked_shades_by_sales.find((row) => row.shade === shade);
        return match ? match.shade_rank : null;
    }

    function calculateClient(data) {
        const uniqueParties = new Set();

        data.forEach((row) => {
            if (row.party) {
                uniqueParties.add(row.party);
            }
        });

        return uniqueParties.size;
    }

    async function aggfilterTable(item, shade) {
        if (!item || !shade) return;

        const total_data = chupps_23_25_full.map((row) => ({
            purDate: row.purDate,
            shade: row.shade,
            item: row.item,
            sales: row.sales,
        }));

        try {
            const res = await fetch(
                `http://localhost:8000/item-shade/${item}-${shade}`,
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ data: total_data }),
                },
            );
            aggFilteredData = await res.json();

            plotAggSales(aggFilteredData);

            console.log("received filtered data: ", aggFilteredData);
        } catch (error) {
            console.error("aggFilterData fetching failed", error);
            aggFilteredData = [];
        }
    }

    $: if (selectedItem || selectedShade) {
        filterTable(selectedItem, selectedShade);
    }

    $: if (selectedShade && selectedItem !== "") {
        aggfilterTable(selectedItem, selectedShade);
    }

    function renderTable(data) {
        const tableData = {
            type: "table",
            header: {
                values: [
                    "Date",
                    "Party",
                    "Item",
                    "Gender",
                    "SKU",
                    "Shade",
                    "Sales",
                    "Size",
                    "Party Category",
                    "Mode",
                    "Location",
                    "Zone",
                    "State",
                ],
                align: "center",
                fill: { color: "lightgray" },
                font: { family: "Arial", size: 12, color: "black" },
            },
            cells: {
                values: [
                    data.map((d) => d.purDate?.split("T")[0] || ""),
                    data.map((d) => d.party),
                    data.map((d) => d.item),
                    data.map((d) => d.gender),
                    data.map((d) => d.sku),
                    data.map((d) => d.shade),
                    data.map((d) => d.sales),
                    data.map((d) => d.size),
                    data.map((d) => d.party_category),
                    data.map((d) => d.mode),
                    data.map((d) => d.location),
                    data.map((d) => d.zone),
                    data.map((d) => d.state),
                ],
                align: "center",
                font: { family: "Arial", size: 11, color: "black" },
                height: 24,
            },
        };

        (window as any).Plotly.newPlot(
            "sales-table",
            [tableData],
            {
                margin: { t: 0, b: 0, l: 20, r: 20 },
                paper_bgcolor: "rgba(0,0,0,0)",
                plot_bgcolor: "rgba(0,0,0,0)",
            },
            {
                displayModeBar: false,
                responsive: true,
            },
        );
    }

    function plotAggSales(data) {
        const trace1 = {
            x: data.map((d) => d.ds),
            y: data.map((d) => d.y),
            mode: "lines",
            name: "Sales",
        };

        const layout = {
            title: "Item / Shade Sales",
            margin: { t: 60, l: 60, r: 60, b: 60 },
            xaxis: { title: "Date" },
            yaxis: { title: "Sales" },
        };

        (window as any).Plotly.newPlot("actual-plot", [trace1], layout, {
            displayModeBar: false,
            responsive: true,
        });
    }

    async function getLLMResponse(item_name) {
        const total_data = chupps_23_25_full.map((row) => ({
            purDate: row.purDate,
            shade: row.shade,
            item: row.item,
            sales: row.sales,
        }));

        try {
            thinking = true;
            const res = await fetch(
                `http://localhost:8000/api/imgchat/itemshade/${encodeURIComponent(item_name)}`, // pass in path!
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ data: total_data }), // only send data in body
                },
            );

            const data = await res.json();
            console.log("recevied llm resopnse in frontend: ", data);
            llmResponse = data.choices[0]?.message?.content || "NULL RESPONSE";
            marked_llmResponse = marked(llmResponse);
        } catch (error) {
            console.error("error in generating llm response: ", error);
            return error;
        } finally {
            thinking = false;
        }
    }

    //dropbox functions!
    async function getAccessTokenFromRefreshToken() {
        const refreshToken = import.meta.env.VITE_DROPBOX_REFRESH_TOKEN;
        const clientId = import.meta.env.VITE_DROPBOX_KEY;
        const clientSecret = import.meta.env.VITE_DROPBOX_SECRET;

        const response = await fetch(
            "https://api.dropboxapi.com/oauth2/token",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    Authorization:
                        "Basic " + btoa(`${clientId}:${clientSecret}`),
                },
                body: new URLSearchParams({
                    grant_type: "refresh_token",
                    refresh_token: refreshToken,
                }),
            },
        );

        const data = await response.json();

        return data.access_token;
    }

    async function loadImagesFromDropbox(sku) {
        loading = 1;
        const accessToken = await getAccessTokenFromRefreshToken();
        const path = `/all-products-dump/${sku}`;

        const response = await fetch(
            "https://api.dropboxapi.com/2/files/list_folder",
            {
                method: "POST",
                headers: {
                    Authorization: `Bearer ${accessToken}`,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ path }),
            },
        );

        const data = await response.json();
        console.log("Dropbox response:", data);

        if (data.entries) {
            const imageFiles = data.entries.filter((entry) =>
                entry.name.match(/\.(jpg|jpeg|png|webp)$/i),
            );

            const links = await Promise.all(
                imageFiles.map((file) => getTemporaryLink(file.path_display)),
            );
            images = links;
        } else {
            loading = 2;
            console.warn("No entries or error:", data);
            images = [];
        }
    }

    async function getTemporaryLink(path) {
        const accessToken = await getAccessTokenFromRefreshToken();

        const res = await fetch(
            "https://api.dropboxapi.com/2/files/get_temporary_link",
            {
                method: "POST",
                headers: {
                    Authorization: `Bearer ${accessToken}`,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ path }),
            },
        );

        const data = await res.json();
        return data.link; // usable temporary URL
    }

    function getStateSalesMap(data) {
        const stateSales = new Map();

        data.forEach((d) => {
            const state = d.state;
            const sales = parseFloat(d.sales) || 0;

            if (!state) return;

            const current = stateSales.get(state) || 0;
            stateSales.set(state, current + sales);
        });

        return stateSales;
    }

    let salesTableRef;

    function scrollToSalesTable() {
        if (salesTableRef) {
            salesTableRef.scrollIntoView({ behavior: "smooth" });
        }
    }

    import { geoMercator, geoPath } from "d3-geo";
    import { select } from "d3-selection";
    import { zoom } from "d3-zoom";
    import { scaleLinear } from "d3-scale";
    import indiaGeoJSON from "../lib/in.json"; // Make sure the path is correct

    let svg;
    const width = 900;
    const height = 900;

    let mapPaths;
    let stateDataMap = [];
    let currentStateSalesMap = new Map();

    const maxSales = Math.max(...Array.from(stateDataMap.values()));
    const colorScale = scaleLinear()
        .domain([0, maxSales])
        .range(["#e0f3f8", "#08589e"]); // Light to dark blue

    onMount(() => {
        const projection = geoMercator().fitSize([width, height], indiaGeoJSON);
        const path = geoPath().projection(projection);

        const map = select(svg).attr("width", width).attr("height", height);
        const tooltip = document.getElementById("tooltip");

        mapPaths = map
            .selectAll("path")
            .data(indiaGeoJSON.features)
            .enter()
            .append("path")
            .attr("d", path)
            .attr("stroke", "#fff")
            .attr("stroke-width", 0.1)
            .on("mouseover", function (event, d) {
                const stateName = d.properties.name;
                const sales = currentStateSalesMap?.get(stateName) || 0;

                // Show tooltip
                tooltip.style.visibility = "visible";
                tooltip.innerHTML = `   <div style="padding: 6px 10px;">
                                            <div style="font-weight: bold; font-size: 14px; margin-bottom: 4px;">
                                            ${stateName}
                                            </div>
                                            <div style="font-size: 12px;">
                                            Sales: <strong>${sales}</strong>
                                            </div>
                                        </div>
                                        `;

                // Highlight the hovered path
                select(this)
                    .attr("stroke", "#000") // darker border
                    .attr("stroke-width", 1.2);
                // .attr("transform", "scale(1.05)");
            })
            .on("mousemove", function (event) {
                tooltip.style.top = event.pageY + 10 + "px";
                tooltip.style.left = event.pageX + 10 + "px";
            })
            .on("mouseout", function () {
                tooltip.style.visibility = "hidden";

                select(this).attr("stroke-width", 0);
                // .attr("transform", "scale(1)");
            });
    });

    function updateMapColors(stateSalesMap) {
        currentStateSalesMap = stateSalesMap; // store for tooltip use
        const values = Array.from(stateSalesMap.values());
        const maxSales = values.length > 0 ? Math.max(...values) : 0;

        const colorScale = scaleLinear()
            .domain([0, maxSales])
            .range(["#ffeda0", "#f03b20"]);

        mapPaths.attr("fill", (d) => {
            const rawName = d.properties.name;
            const sales = stateSalesMap.get(rawName);
            return sales ? colorScale(sales) : "#ccc";
        });
    }
</script>

<div
    id="tooltip"
    style="
    position: absolute;
    pointer-events: none;
    background: rgba(0, 0, 0, 0.8);
    color: white;
    padding: 6px 10px;
    border-radius: 4px;
    font-size: 32px;
    visibility: hidden;
    z-index: 999;
"
></div>

<div class="w-screen h-screen">
    <div class="grid grid-cols-12 grid-rows-4 gap-3 h-full p-5">
        <div
            class="col-span-4 overflow-y-auto row-span-4 bg-white rounded-xl p-5 h-full bxsdw border border-gray-300"
        >
            <div class="grid grid-rows-[1fr_2fr] gap-5 h-full">
                <div class="flex flex-col gap-2">
                    <!-- Dropdowns -->
                    <label
                        class="flex bg-yellow-100 p-5 rounded-xl flex-col justify-start items-center w-full"
                    >
                        <p class="text-4xl">Item:</p>
                        <select
                            class="border bg-amber-300 border-gray-400 rounded h-fit p-1 w-full"
                            bind:value={selectedItem}
                        >
                            <option disabled selected value=""
                                >--Select Item--</option
                            >
                            {#each items as item}
                                <option value={item}>{item}</option>
                            {/each}
                        </select>
                    </label>

                    <label
                        class="flex bg-red-100 p-5 rounded-xl flex-col justify-start items-center w-full"
                    >
                        <p class="text-4xl">Shade:</p>
                        <select
                            class="border bg-red-400 border-gray-400 w-full rounded h-fit p-1"
                            bind:value={selectedShade}
                        >
                            <option disabled selected value=""
                                >--Select Shade--</option
                            >
                            {#each shades as shade}
                                <option value={shade}>{shade}</option>
                            {/each}
                        </select>
                    </label>

                    <div class="flex flex-row gap-2">
                        <div
                            class="flex bg-blue-100 p-5 rounded-xl flex-col justify-start items-center w-full"
                        >
                            <p class="text-4xl">SKU:</p>
                            <p class="text-red-600 text2 text-3xl">{sku}</p>
                        </div>

                        <div
                            class="flex bg-blue-100 p-5 rounded-xl flex-col justify-start items-center w-full"
                        >
                            <p class="text-4xl">Colour:</p>
                            <!-- Color Display -->
                            <div class="flex flex-row gap-2 mt-4">
                                <!-- primary colour -->
                                <div
                                    class="border-4 border-gray-500 w-[80px] h-[80px]"
                                    style="background-color: {primaryColor};"
                                ></div>
                                <!-- secondary colour -->
                                <div
                                    class="border-4 border-gray-500 w-[80px] h-[80px]"
                                    style="background-color: {secondaryColor};"
                                ></div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- images -->
                <div class="">
                    {#if images.length > 0}
                        <div class="grid grid-cols-2 md:grid-cols-3 gap-4 mt-4">
                            {#each images as image}
                                <img
                                    src={image}
                                    alt="Product image"
                                    class="rounded shadow-lg hover:scale-125 transition-all ease-in-out duration-200 border border-gray-400 hover:shadow-2xl"
                                />
                            {/each}
                        </div>
                    {:else if loading === 0}
                        <p class="text-gray-500">
                            Select a preferred Item/Shade combination!
                        </p>
                    {:else if loading === 1}
                        <div
                            class="flex flex-col mt-10 gap-5 items-center justify-center"
                        >
                            <div
                                class="w-12 h-12 border-4 border-blue-400 border-dashed rounded-full animate-spin"
                            ></div>
                            <p class="text-gray-500">Loading images...</p>
                        </div>
                    {:else if loading === 2}
                        <div
                            class="flex flex-col items-center justify-center gap-5 mt-auto"
                        >
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                viewBox="0 0 512 512"
                                width="50"
                                height="50"
                                ><!--!Font Awesome Free 6.7.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc.--><path
                                    d="M367.2 412.5L99.5 144.8C77.1 176.1 64 214.5 64 256c0 106 86 192 192 192c41.5 0 79.9-13.1 111.2-35.5zm45.3-45.3C434.9 335.9 448 297.5 448 256c0-106-86-192-192-192c-41.5 0-79.9 13.1-111.2 35.5L412.5 367.2zM0 256a256 256 0 1 1 512 0A256 256 0 1 1 0 256z"
                                /></svg
                            >
                            <p class="text-black text-lg">
                                No images available for this item/shade!
                            </p>
                        </div>
                    {/if}
                </div>
            </div>
        </div>

        <div
            class="col-start-5 col-span-8 row-span-4 bg-white relative rounded-xl bxsdw border border-gray-300 overflow-y-auto"
        >
            <!-- <img src="/india.svg" alt="india"> -->

            <div class="flex items-center justify-center overflow-x-hidden">
                <svg bind:this={svg} />
            </div>

            <div class="px-5 w-full flex items-start justify-between">
                <span class="text-4xl">Sales Data</span>
            </div>
            <div class="relative">
                <!-- Table on top -->
                <div
                    id="sales-table"
                    class="w-full h-full z-100 relative"
                    bind:this={salesTableRef}
                ></div>

                <!-- Spans behind the table -->
                <!-- Spans behind the table -->
                <div class="flex flex-row gap-5 absolute -top-9 right-5 z-0">
                    <span
                        class="text2b text-white text-lg p-2 rounded-t-lg"
                        style="
							background-color: {primaryColor};
							border-left: 1px solid {secondaryColor};
							border-top: 4px solid {secondaryColor};
							border-right: 1px solid {secondaryColor};
							box-shadow: 0 4px 12px {secondaryColor};
							"
                    >
                        {selectedItem}
                    </span>

                    <span
                        class="text2b text-lg text-white p-2 rounded-t-lg"
                        style="
							background-color: {secondaryColor};
							border-left: 1px solid {primaryColor};
							border-top: 4px solid {primaryColor};
							border-right: 1px solid {primaryColor};
							box-shadow: 0 4px 12px {primaryColor};
							"
                    >
                        {selectedShade}
                    </span>
                </div>
            </div>

            <button
                class="absolute top-5 right-5 p-2 text2 text-sm flex flex-row gap-2 rounded-lg border hover:bg-gray-400 hover:text-white duration-200"
                on:click={scrollToSalesTable}
            >
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 512 512"
                    width="20"
                    height="20"
                    class="fill-current"
                    ><!--!Font Awesome Free 6.7.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc.--><path
                        d="M64 256l0-96 160 0 0 96L64 256zm0 64l160 0 0 96L64 416l0-96zm224 96l0-96 160 0 0 96-160 0zM448 256l-160 0 0-96 160 0 0 96zM64 32C28.7 32 0 60.7 0 96L0 416c0 35.3 28.7 64 64 64l384 0c35.3 0 64-28.7 64-64l0-320c0-35.3-28.7-64-64-64L64 32z"
                    /></svg
                >
                <span>View Data</span>
            </button>
        </div>

        <div
            class="col-start-11 col-span-2 row-span-4 bg-white rounded-xl bxsdw border border-gray-300"
        ></div>
    </div>
</div>

<style>
</style>
