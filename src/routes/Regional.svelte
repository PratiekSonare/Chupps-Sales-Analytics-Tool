<script lang="ts">
    import { supabase } from "../lib/supabaseClient";
    import shadeHexMap from "../lib/shade_hex_map.json";
    import { onMount } from "svelte";


    export let chupps_23_25_full;
    export let ranked_items_by_sales;
    export let ranked_shades_by_sales;

    let items = [];
    let states = [];
    let infoOpen = false;
    let selectedItem = "FLOW";
    // let selectedItem = "";
    let selectedShade = "BLACK BLACK";
    // let selectedShade = "";
    let selectedState = "";
    let shades = [];
    let sku = "";
    let filteredData = [];
    let images = [];
    let loading = 0;
    let shadeItemSelected = false;
    let salesOff = false;

    let primaryColor = "#fff";
    let secondaryColor = "#000";

    let numUniqueParties = 0;

    // Update the colors when selectedShade changes
    $: if (selectedShade && shadeHexMap[selectedShade]) {
        primaryColor = shadeHexMap[selectedShade].primary;
        secondaryColor = shadeHexMap[selectedShade].secondary;
    }

    // Load distinct items from Supabase
    onMount(async () => {
        const { data, error } = await supabase
            .from("prod_1")
            .select("item", { count: "exact" })
            .order("item", { ascending: true });

        if (!error) {
            items = [...new Set(data.map((row) => row.item))];
        } else {
            console.error("Error loading items:", error);
        }

        const { data: stdata, error: sterror } = await supabase
            .from("prod_1")
            .select("state", { count: "exact" })
            .order("state", { ascending: true });

        if (!sterror) {
            states = [...new Set(stdata.map((row) => row.state))]; // ✅ Fixed
        } else {
            console.error("Error loading states:", sterror);
        }

        const total_data = chupps_23_25_full.map((row) => ({
            purDate: row.purDate,
            shade: row.shade,
            item: row.item,
            sales: row.sales,
        }));

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
                outerHeight: 600,
                innerHeight: 600,
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
    }

    async function loadShades(item) {
        const { data, error } = await supabase
            .from("chupps_23_25_full")
            .select("shade")
            .eq("item", item)
            .order("shade", { ascending: true });

        if (!error) {
            shades = [...new Set(data.map((row) => row.shade))];
        }
    }

    $: if (selectedItem && selectedShade) {
        loadSKU(selectedItem, selectedShade);
    }

    async function loadSKU(item, shade) {
        const { data, error } = await supabase
            .from("prod_1")
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

    async function filterTable(item, shade, state) {
        const query = supabase.from("prod_1").select("*");

        if (item) query.eq("item", item);
        if (shade) query.eq("shade", shade);
        if (state) query.eq("state", state);

        const { data, error } = await query;

        if (!error) {
            filteredData = data;
            renderTable(filteredData);

            const salesMap = getStateSalesMap(filteredData);
            updateMapColors(salesMap); // ← update the SVG map!
        } else {
            console.error("Filtering failed:", error.message);
            filteredData = [];
        }
    }

    $: if (selectedItem || selectedShade || selectedState) {
        filterTable(selectedItem, selectedShade, selectedState);
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
                margin: { t: 10, b: 10, l: 20, r: 20 },
                outerHeight: 600,
                innerHeight: 600,
                paper_bgcolor: "rgba(0,0,0,0)",
                plot_bgcolor: "rgba(0,0,0,0)",
            },
            {
                displayModeBar: false,
                responsive: true,
            },
        );
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
    import indiaGeoJSON from "../lib/in.json";

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

    let rules = [
        {
            index: "1",
            rule: "Only offline parties (distributors) have been tagged with location, <strong>no mapping</strong> for sales done in online marketplaces (Myntra, Flipkar, etc.)",
            code: "",
        },
        {
            index: "2",
            rule: "From the entire database, only a certain offline distributor parties have been tagged with locations. Additionally, the names of the same distributors were different, which have been updated to maintain uniformity.",
            code: `
                    <br/> 'ADITI FOOTWEAR                -CHITTORGARH': 'ADITI FOOTWEAR', 
                    <br/> 'AG TRENDS                     -HYDRABAD': 'AG TRENDS',
                    <br/> 'AIREN ENTERPRISES             -HISAR': 'AIREN ENTERPRISES',
                    <br/> 'BAGGA SALES AGENCY            -AHEDABAD': 'BAGGA SALES AGENCY',
                    <br/> 'DEVRAJ AND SONS               -KORAPUT': 'DEVRAJ AND SONS',
                    <br/> 'GNM FOOTWEAR                  -DELHI': 'GNM FOOTWEAR',
                    <br/> 'GURU SHOES TECH PVT. LTD      -AGRA': 'GURU SHOES TECH PVT. LTD',
                    <br/> 'J.S.DISTRIBUTOR               -BANGLORE': 'J.S.DISTRIBUTORS',
                    <br/> 'JAYSHREE MARKETING            -BHOPAL': 'JAYSHREE MARKETING',
                    <br/> 'KIRANAKART TECHNOLOGIES PVT LTD -MUMBAI': 'KIRANAKART TECHNOLOGIES PVT LTD',
                    <br/> 'KIRANAKART TECHNOLOGIES PVT LTD BR -BANGLORE': 'KIRANAKART TECHNOLOGIES PVT LTD',
                    <br/> 'KIRANAKART TECHNOLOGIES PVT LTD CH -CHENNAI': 'KIRANAKART TECHNOLOGIES PVT LTD',
                    <br/> 'KIRANAKART TECHNOLOGIES PVT LTD HR -GURUGRAM': 'KIRANAKART TECHNOLOGIES PVT LTD',
                    <br/> 'KWALITY ENTERPRISES           -BHAWANIPATNA': 'KWALITY ENTERPRISES',
                    <br/> 'M/S SHOE PARK                 -JAGDALPUR': 'M/S SHOEPARK (JAGDALPUR)',
                    <br/> 'M/S STYLE SHOES               -BHUBNESHWAR': 'M/S STYLE SHOES',
                    <br/> 'MAHARAJA ENTERPRISES          -RAIPUR': 'MAHARAJA ENTERPRISES',
                    <br/> 'MANOHAR BOOT HOUSE            -BILASPUR': 'MANOHAR BOOT HOUSE',
                    <br/> 'MK FOOTWEAR                   -HARIDWAR': 'MK FOOTWEAR',
                    <br/> 'NEW STAR FOOTWEAR             -KORAPUT': 'NEW STAR FOOTWEAR ODISHA',
                    <br/> 'RAMDEV SHOE TRADING COMPANY   -CHENNAI': 'RAMDEV SHOE TRADING COMPANY',
                    <br/> 'BOOTS MADGAON                 -GOA': 'BOOTS',
                    <br/> 'BOOTS PANJI                   -GOA': 'BOOTS',
                    <br/> 'CENTRO (V-RETAIL PVT LTD - WAREHOUSE)': 'CENTRO',
                    <br/> 'CENTRO - CNR-CEN (V-RETAIL PVT LTD)': 'CENTRO',
                    <br/> 'CENTRO SAGX (V-RETAIL LTD)    -HYDRABAD': 'CENTRO',
                    <br/> 'CENTRO SAGX (V-RETAIL PVT LTD)': 'CENTRO',
                    <br/> 'CENTRO- 6 MALL SS (V-RETAIL PVT LTD)': 'CENTRO',
                    <br/> 'CENTRO- ASRN (V-RETAIL PVT LTD)': 'CENTRO',
                    <br/> 'CENTRO- CP (V-RETAIL PVT LTD)': 'CENTRO',
                    <br/> 'CENTRO- FRM (V-RETAIL PVT LTD)': 'CENTRO',
                    <br/> 'CENTRO- GBS (V-RETAIL PVT LTD)': 'CENTRO',
                    <br/> 'CENTRO- HNR (V-RETAIL PVT LTD)': 'CENTRO',
                    <br/> 'CENTRO- KMPL (V-RETAIL PVT LTD)': 'CENTRO',
                    <br/> 'CENTRO- KP (V-RETAIL PVT LTD)': 'CENTRO',
                    <br/> 'CENTRO- KPT-LB (V-RETAIL PVT LTD)': 'CENTRO',
                    <br/> 'CENTRO- KRK (V-RETAIL PVT LTD)': 'CENTRO',
                    <br/> 'CENTRO- VZM (V-RETAIL PVT LTD)': 'CENTRO',
                    <br/> 'CENTRO-CELEST (V-RETAIL PVT LTD)': 'CENTRO',
                    <br/> 'CENTRO-GSM-SS (V-RETAIL PVT LTD)': 'CENTRO',
                    <br/> 'CENTRO-HNK-CEN (V-RETAIL PVT LTD)': 'CENTRO',
                    <br/> 'CENTRO-KKD-SBR-CEN (V-RETAIL PVT LTD)': 'CENTRO',
                    <br/> 'CENTRO-KKD-SRMT (V-RETAIL PVT LTD)': 'CENTRO',
                    <br/> 'CENTRO-KRM-CEN (V-RETAIL PVT LTD)': 'CENTRO',
                    <br/> 'CENTRO-LNT-L4-SS (V-RETAIL PVT LTD)': 'CENTRO',
                    <br/> 'CENTRO-MALHAR (V-RETAIL PVT LTD)': 'CENTRO',
                    <br/> 'CENTRO-NIZAMABAD (V-RETAIL PVT LTD)': 'CENTRO',
                    <br/> 'CENTRO-SCM-SS (V-RETAIL PVT LTD)': 'CENTRO',
                    <br/> 'SIKKIM COMMERCIAL             -BHUBNESHWAR': 'SIKKIM COMMERCIAL',
                    <br/> 'SIKKIM COMMERCIAL CORPORATION -KOLKATA': 'SIKKIM COMMERCIAL CORPORATION',
                    <br/> 'SHREE KRISHNA FOOTWEAR        -BAHADURGARH': 'SHREE KRISHNA FOOTWEAR',
                    <br/> 'SHREEJI FOOTWEAR              -BAHADURGARH': 'SHREEJI FOOTWEAR',
                    <br/> 'MAA VAISHNAVI INTERNATIONAL   -GURUGRAM': 'MAA VAISHNAVI INTERNATIONAL',
                    <br/> 'STEP IN                       -RANCHI': 'STEP IN',
                    <br/> 'SURE LEATHER EXPORTS          -AGRA': 'SURE LEATHER EXPORTS',
                    <br/> 'TATA UNISTORE LIMITED-KORALURU -BANGALORE': 'TATA UNISTORE LIMITED',
                    <br/> 'TWAM ENTERPRISE               -THANE': 'TWAM ENTERPRISE',
                    <br/> 'M/S SOFT WALK                 -BHADRAK': 'M/S SOFT WALK'
            `,
        },

        {
            index: "3",
            rule: "Final distributor names with locations (considered for mapping) are:",
            code: `
            <br/> 'ADITI FOOTWEAR',
            <br/> 'AG TRENDS',
            <br/> 'AIREN ENTERPRISES',
            <br/> 'BAGGA SALES AGENCY',
            <br/> 'DEVRAJ AND SONS',
            <br/> 'GNM FOOTWEAR',
            <br/> 'GURU SHOES TECH PVT. LTD',
            <br/> 'J.S.DISTRIBUTORS',
            <br/> 'JAYSHREE MARKETING',
            <br/> 'KIRANAKART TECHNOLOGIES PVT LTD',
            <br/> 'KWALITY ENTERPRISES',
            <br/> 'M/S SHOEPARK (JAGDALPUR)',
            <br/> 'M/S STYLE SHOES',
            <br/> 'MAHARAJA ENTERPRISES',
            <br/> 'MANOHAR BOOT HOUSE',
            <br/> 'MK FOOTWEAR',
            <br/> 'NEW STAR FOOTWEAR ODISHA',
            <br/> 'RAMDEV SHOE TRADING COMPANY',
            <br/> 'SIKKIM COMMERCIAL',
            <br/> 'SIKKIM COMMERCIAL CORPORATION',
            <br/> 'SHREE KRISHNA FOOTWEAR',
            <br/> 'SHREEJI FOOTWEAR',
            <br/> 'MAA VAISHNAVI INTERNATIONAL',
            <br/> 'STEP IN',
            <br/> 'SURE LEATHER EXPORTS',
            <br/> 'TATA UNISTORE LIMITED',
            <br/> 'TWAM ENTERPRISE',
            <br/> 'CENTRO',
    `,
        },
        {
            index: "4",
            rule: "The following locations have been enabled to each distributor for mapping: ",
            code: ` <br/> 'ADITI FOOTWEAR': 'CHITTORGARH',
                <br/> 'AG TRENDS': 'HYDERABAD',
                <br/> 'AIREN ENTERPRISES': 'HISAR',
                <br/> 'BAGGA SALES AGENCY': 'AHMEDABAD',
                <br/> 'DEVRAJ AND SONS': 'KORAPUT',
                <br/> 'GNM FOOTWEAR': 'DELHI',
                <br/> 'GURU SHOES TECH PVT. LTD': 'AGRA',
                <br/> 'J.S.DISTRIBUTORS': 'BANGALORE',
                <br/> 'JAYSHREE MARKETING': 'BHOPAL',
                <br/> 'KIRANAKART TECHNOLOGIES PVT LTD': 'MULTIPLE',
                <br/> 'KWALITY ENTERPRISES': 'BHAWANIPATNA',
                <br/> 'M/S SHOEPARK (JAGDALPUR)': 'JAGDALPUR',
                <br/> 'M/S STYLE SHOES': 'BHUBANESWAR',
                <br/> 'MAHARAJA ENTERPRISES': 'RAIPUR',
                <br/> 'MANOHAR BOOT HOUSE': 'BILASPUR',
                <br/> 'MK FOOTWEAR': 'HARIDWAR',
                <br/> 'NEW STAR FOOTWEAR ODISHA': 'KORAPUT',
                <br/> 'RAMDEV SHOE TRADING COMPANY': 'CHENNAI',
                <br/> 'SIKKIM COMMERCIAL': 'BHUBANESWAR',
                <br/> 'SIKKIM COMMERCIAL CORPORATION': 'KOLKATA',
                <br/> 'SHREE KRISHNA FOOTWEAR': 'BAHADURGARH',
                <br/> 'SHREEJI FOOTWEAR': 'BAHADURGARH',
                <br/> 'MAA VAISHNAVI INTERNATIONAL': 'GURUGRAM',
                <br/> 'STEP IN': 'RANCHI',
                <br/> 'SURE LEATHER EXPORTS': 'AGRA',
                <br/> 'TATA UNISTORE LIMITED': 'BANGALORE',
                <br/> 'TWAM ENTERPRISE': 'THANE',
                <br/> 'CENTRO': 'MULTIPLE'
    `,
        },
        {
            index: "5",
            rule: "Finally, zones and states were decided based on maps as follows: ",
            code: `
                ---------ZONES-------------
                <br/> 'AGRA': 'NORTH',
                <br/> 'AHMEDABAD': 'WEST',
                <br/> 'BAHADURGARH': 'EAST',
                <br/> 'BANGALORE': 'SOUTH',
                <br/> 'BHAWANIPATNA': 'EAST',
                <br/> 'BHOPAL': 'WEST',
                <br/> 'BHUBANESWAR': 'EAST',
                <br/> 'BILASPUR': 'NORTH',
                <br/> 'CHENNAI': 'SOUTH',
                <br/> 'CHITTORGARH': 'WEST',
                <br/> 'DELHI': 'NORTH',
                <br/> 'GURUGRAM': 'NORTH',
                <br/> 'HARIDWAR': 'NORTH',
                <br/> 'HISAR': 'NORTH',
                <br/> 'HYDERABAD': 'SOUTH',
                <br/> 'JAGDALPUR': 'NORTH',
                <br/> 'KOLKATA': 'EAST',
                <br/> 'KORAPUT': 'EAST',
                <br/> 'RAIPUR': 'NORTH',
                <br/> 'RANCHI': 'EAST',
                <br/> 'THANE': 'WEST',

                <br/>
                <br/>

                <br/> --------STATES-------------
                <br/> 'AGRA': 'Uttar Pradesh',
                <br/> 'AHMEDABAD': 'Gujarat',
                <br/> 'BAHADURGARH': 'Haryana',
                <br/> 'BANGALORE': 'Karnataka',
                <br/> 'BHAWANIPATNA': 'Odisha',
                <br/> 'BHOPAL': 'Madhya Pradesh',
                <br/> 'BHUBANESWAR': 'Odisha',
                <br/> 'BILASPUR': 'Chhattisgarh',
                <br/> 'CHENNAI': 'Tamil Nadu',
                <br/> 'CHITTORGARH': 'Rajasthan',
                <br/> 'DELHI': 'Delhi',
                <br/> 'GURUGRAM': 'Haryana',
                <br/> 'HARIDWAR': 'Uttarakhand',
                <br/> 'HISAR': 'Haryana',
                <br/> 'HYDERABAD': 'Telangana',
                <br/> 'JAGDALPUR': 'Chhattisgarh',
                <br/> 'KOLKATA': 'West Bengal',
                <br/> 'KORAPUT': 'Odisha',
                <br/> 'MULTIPLE': 'UNKNOWN',
                <br/> 'RAIPUR': 'Chhattisgarh',
                <br/> 'RANCHI': 'Jharkhand',
                <br/> 'THANE': 'Maharashtra',
                <br/> 'UNKNOWN': 'UNKNOWN'
                                                
    `,
        },
    ];
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

<div class="w-screen h-screen relative">
    {#if infoOpen}
        <div
            class="rounded-xl bxsdw absolute overflow-y-auto z-[250] p-5 w-1/2 h-3/4 top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-gray-300 border border-gray-700"
        >
            <button
                on:click={() => (infoOpen = false)}
                class="absolute top-8 right-10 text-2xl text-red-400 hover:text-red-600"
                >x</button
            >

            <div class="mt-10"></div>

            {#each rules as content}
                <div
                    class="flex flex-col items-center justify-start h-fit text2 p-5 mt-1"
                >
                    <span class="text-3xl">{content.index}.</span>
                    <span class="text-center">{@html content.rule}</span>
                    {#if content.code !== ""}
                        <div
                            class=" mt-2 h-[250px] w-full overflow-y-scroll bg-white rounded-xl text-xs p-3"
                        >
                            <span class="text-left font-mono"
                                >{@html content.code}</span
                            >
                        </div>
                    {/if}
                </div>
            {/each}
        </div>
    {/if}

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
                            <option selected value=""
                                >All Items</option
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
                            <option selected value=""
                                >All Shades</option
                            >
                            {#each shades as shade}
                                <option value={shade}>{shade}</option>
                            {/each}
                        </select>
                    </label>

                    <label
                        class="flex bg-green-100 p-5 rounded-xl flex-col justify-start items-center w-full"
                    >
                        <p class="text-4xl">State:</p>
                        <select
                            class="border bg-green-300 border-gray-400 rounded h-fit p-1 w-full"
                            bind:value={selectedState}
                        >
                            <option selected value="">INDIA</option>
                            {#each states as item}
                                <option value={item}>{item}</option>
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
                                <!-- svelte-ignore a11y_img_redundant_alt -->
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

            <div
                class="flex items-center justify-center overflow-x-hidden mt-5"
            >
                <svg bind:this={svg} />
            </div>

            <div class="px-5 w-full flex items-start justify-between mt-32">
                <span class="text-4xl" bind:this={salesTableRef}
                    >Sales Data</span
                >
            </div>
            <div class="relative h-full">
                <!-- Table on top -->
                <div
                    id="sales-table"
                    class="w-full h-full z-100 relative"
                ></div>

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

            <div class="flex flex-row gap-2 absolute top-5 right-5">
                <!-- svelte-ignore a11y_consider_explicit_label -->
                <button
                    on:click={() => (infoOpen = !infoOpen)}
                    class="text-gray-700 hover:text-black"
                >
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        x="0px"
                        y="0px"
                        width="24"
                        height="24"
                        class="fill-current"
                        viewBox="0 0 24 24"
                    >
                        <path
                            d="M 12 2 C 6.4889971 2 2 6.4889971 2 12 C 2 17.511003 6.4889971 22 12 22 C 17.511003 22 22 17.511003 22 12 C 22 6.4889971 17.511003 2 12 2 z M 12 4 C 16.430123 4 20 7.5698774 20 12 C 20 16.430123 16.430123 20 12 20 C 7.5698774 20 4 16.430123 4 12 C 4 7.5698774 7.5698774 4 12 4 z M 11 7 L 11 9 L 13 9 L 13 7 L 11 7 z M 11 11 L 11 17 L 13 17 L 13 11 L 11 11 z"
                        ></path>
                    </svg>
                </button>

                <button
                    class="px-2 py-1 text2 text-sm flex flex-row gap-2 rounded-lg border hover:bg-gray-400 hover:text-white duration-200"
                    on:click={scrollToSalesTable}
                >
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 512 512"
                        width="16"
                        height="16"
                        class="fill-current"
                        ><!--!Font Awesome Free 6.7.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc.--><path
                            d="M64 256l0-96 160 0 0 96L64 256zm0 64l160 0 0 96L64 416l0-96zm224 96l0-96 160 0 0 96-160 0zM448 256l-160 0 0-96 160 0 0 96zM64 32C28.7 32 0 60.7 0 96L0 416c0 35.3 28.7 64 64 64l384 0c35.3 0 64-28.7 64-64l0-320c0-35.3-28.7-64-64-64L64 32z"
                        /></svg
                    >
                    <span class="text-xs">View Data</span>
                </button>
            </div>
        </div>
    </div>
</div>

<style>
    @reference "tailwindcss";

    button {
        @apply transition-all transform cursor-pointer active:scale-95 scale-100 duration-100 ease-in;
    }
</style>
