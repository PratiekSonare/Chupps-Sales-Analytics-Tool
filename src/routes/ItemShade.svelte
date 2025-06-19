<script lang="ts">
	import { GoTrueClient } from "@supabase/supabase-js";
	import { supabase } from "../lib/supabaseClient";
	import shadeHexMap from "../lib/shade_hex_map.json";

	export let chupps_23_25_full;
	export let ranked_items_by_sales;
	export let ranked_shades_by_sales;

	import { onMount } from "svelte";
	let items = [];
	// let selectedItem = "CHUPPS X MI LEGACY";
	// let selectedShade = "BLUE";
	let selectedItem = "AIRFLOW";
	let selectedShade = "BLACK BROWN";
	let shades = [];
	let sku = "";
	let filteredData = [];
	let aggFilteredData = [];
	let images = [];
	let loading = 0;
	let shadeItemSelected = false;

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
	});

	// Watch for selectedItem change and load matching shades
	$: if (selectedItem) {
		shadeItemSelected = true;
		loadShades(selectedItem);
		item_rank = calculateItemRank(selectedItem);
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
	}

	function calculateTotalSales() {
		console.log();
		const totalsales = aggFilteredData.reduce((sum, d) => sum + d.y, 0);
		return totalsales;
		//already filtered by item and shade, we just need to return the sum of sales
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

		if (item) {
			query.eq("item", item);
		}
		if (shade) {
			query.eq("shade", shade);
		}

		const { data, error } = await query;

		if (!error) {
			filteredData = data;
			renderTable(filteredData);
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
</script>

<div class="w-screen h-screen">
	<div class="grid grid-cols-3 grid-rows-4 gap-3 h-full p-5">
		<div
			class="col-span-1 overflow-y-auto row-span-4 bg-white rounded-xl p-5 h-full shadow-xl border border-gray-300"
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
									class="rounded shadow-lg hover:scale-125 transition-all ease-in-out duration-200 border border-gray-300 hover:shadow-2xl"
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
			class="col-start-2 p-5 col-span-3 row-start-3 row-span-2 bg-white rounded-xl shadow-xl border border-gray-300 overflow-hidden"
		>
			<div class="w-full flex items-start justify-between">
				<span class="text-4xl">Sales Data</span>
			</div>
			<div class="relative">
				<!-- Table on top -->
				<div
					id="sales-table"
					class="w-full h-full z-100 relative"
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
		</div>

		<div
			class="col-start-2 col-span-2 row-start-0 row-span-2 flex gap-5 flex-row w-full h-full"
		>
			<div
				class="bg-white rounded-xl shadow-xl p-5 border flex-3/4 border-gray-300"
			>
				<span class="text-4xl">Sales Chart</span>
				<div id="actual-plot" class="w-11/12 h-11/12 self-center"></div>
			</div>

			<div
				class=" bg-white rounded-xl shadow-xl border flex-1/4 border-gray-300"
			>
				<div
					class="flex flex-col py-2 items-center justify-center gap-0 mt-auto"
				>
					<span class="text-2xl">Item Rank</span>
					<span class="text-4xl w-full bg-green-500 text-center"
						>{item_rank}</span
					>
				</div>
				<div class="flex flex-col items-center justify-center gap-0">
					<span class="text-2xl">Shade Rank</span>
					<span
						class="text-4xl w-full bg-blue-500 text-white text-center"
						>{shade_rank}</span
					>
				</div>

				<div class="py-5"></div>
				<div class="flex flex-col items-center justify-center gap-0">
					<span class="text-2xl">Total Sales</span>
					<span
						class="text-4xl w-full bg-blue-500 text-white text-center"
						>{historical_total_sales}</span
					>
				</div>
			</div>
		</div>
	</div>
</div>
