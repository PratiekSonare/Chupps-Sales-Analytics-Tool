<script>
	import { GoTrueClient } from "@supabase/supabase-js";
	import { supabase } from "../lib/supabaseClient";
	import shadeHexMap from "../lib/shade_hex_map.json";
	import { onMount } from "svelte";
	let items = [];
	let selectedItem = "";
	let shades = [];
	let selectedShade = "";
	let sku = "";
	let images = [];
	let loading = 0;
	let shadeItemSelected = false;

	let primaryColor = "#fff";
	let secondaryColor = "#000";

	// Update the colors when selectedShade changes
	$: if (selectedShade && shadeHexMap[selectedShade]) {
		primaryColor = shadeHexMap[selectedShade].primary;
		secondaryColor = shadeHexMap[selectedShade].secondary;
	}

	// Load distinct items from Supabase
	onMount(async () => {
		const { data, error } = await supabase
			.from("chupps_23_25_full")
			.select("item", { count: "exact" })
			.order("item", { ascending: true });
		// .select('item', { distinct: true });

		if (!error) {
			items = [...new Set(data.map((row) => row.item))];
		}
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
		// .select('shade', { distinct: true });

		if (!error) {
			shades = [...new Set(data.map((row) => row.shade))];
		}
	}

	$: if (selectedItem && selectedShade) {
		loadSKU(selectedItem, selectedShade);
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

	async function loadImagesFromDropbox(sku) {
		loading = 1;

		console.log("Running image fetch with SKU:", sku);
		const accessToken = import.meta.env.VITE_DROPBOX_ACCESS_TOKEN;
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
		const accessToken = import.meta.env.VITE_DROPBOX_ACCESS_TOKEN;

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
									class="rounded shadow"
								/>
							{/each}
						</div>
					{:else if loading === 0}
						<p class="text-gray-500">
							Select a preferred Item/Shade combination!
						</p>
					{:else if loading === 1}
						<div class="flex flex-col mt-10 gap-5 items-center justify-center">
							<div
								class="w-12 h-12 border-4 border-blue-400 border-dashed rounded-full animate-spin"
							></div>
							<p class="text-gray-500">Loading images...</p>
						</div>
					{:else if loading === 2}
						<p class="text-black text-3xl">
							No images available for this item/shade!
						</p>
					{/if}
				</div>
			</div>
		</div>
		<div
			class="col-start-2 col-span-2 row-start-0 row-span-2 bg-white rounded-xl shadow-xl border border-gray-300"
		></div>
		<div
			class="col-start-2 col-span-2 row-start-3 row-span-2 bg-white rounded-xl shadow-xl border border-gray-300"
		></div>
	</div>
</div>
