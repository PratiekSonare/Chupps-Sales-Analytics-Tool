<script lang="ts">
	import { onMount } from "svelte";
	import { supabase } from "$lib/supabaseClient";
	import { goto } from "$app/navigation";
	import { activeView } from "$lib/stores/view"; // 👈 import the store

	onMount(async () => {
		const {
			data: { session },
		} = await supabase.auth.getSession();
		if (!session) {
			goto("/login");
		} else {
			authLoading = false;
		}
	});

	export let data;
	const {
		wo_centro_prophet,
		chupps_23_25_full,
		ml_train_data,
		curr_max_data,
		ranked_items_by_sales,
		ranked_shades_by_sales,
		total_sales,
		total_revenue,
		total_parties,
		chupps_items,
		chupps_shades,
	} = data;

	import { fade } from "svelte/transition";

	import Forecast from "./Forecast.svelte";
	import Sidebar from "./sidebar/Sidebar.svelte";
	import Home from "./Home.svelte";
	import Data from "./Data.svelte";
	import ItemShade from "./ItemShade.svelte";
	import Regional from "./Regional.svelte";
	import Risk from "./RiskScore.svelte";

	let loading = false;

	let authLoading = true;
	let localActiveView = "home"; // for `#key` block and rendering

	// reactively update on store change
	$: activeView.subscribe((val) => {
		localActiveView = val;
	});

	let viewLoading = false;

	async function handleView(view: string) {
		if (view === localActiveView) return;
		viewLoading = true;
		await new Promise((res) => setTimeout(res, 600));
		activeView.set(view); // 👈 update store
		await new Promise((res) => setTimeout(res, 300));
		viewLoading = false;
	}

</script>

<svelte:head>
	<title>Chupps Analytics</title>
	<meta name="description" content="AI based analytics for Chupps!" />
</svelte:head>

<!-- Loading overlay -->
{#if loading}
	<div class="loader-overlay flex flex-col gap-0 justify-center items-center">
		<img
			src="/chupps-white.svg"
			alt="logo"
			style="width: 175px;"
			class="animate-bounce"
		/>
	</div>
{/if}

<main class="flex w-screen h-screen overflow-hidden">
	{#if !authLoading}
		<!-- Sidebar -->
		<div class="w-32 h-full bg-gray-800">
			<Sidebar onSelect={handleView} {activeView} />
		</div>

		<!-- Main content -->
		<section
			transition:fade
			class="flex-1 flex justify-center items-center h-full overflow-auto p-6"
		>
			{#key localActiveView}
				{#if localActiveView === "Home"}
					<Home />
				{:else if localActiveView === "Data"}
					<Data {curr_max_data} />
				{:else if localActiveView === "Item & Shade"}
					<ItemShade
						{ranked_items_by_sales}
						{ranked_shades_by_sales}
						{chupps_23_25_full}
					/>
				{:else if localActiveView === "Regional"}
					<Regional
						{chupps_23_25_full}
					/>
				{:else if localActiveView === "Forecast"}
					<Forecast
						{wo_centro_prophet}
						{chupps_23_25_full}
						{total_sales}
						{total_revenue}
						{total_parties}
						{chupps_items}
						{chupps_shades}
					/>
				{:else if localActiveView === "Risk Score"}
					<Risk {ml_train_data} />
				{/if}
			{/key}
		</section>
		{:else}
		<div class="m-auto text-4xl animate-pulse flex flex-col items-center justify-center gap-5">
			<img src='/chupps-black.svg' class="animate-bounce w-1/5 h-1/5" alt="chupps-logo"> 
			<span>Checking Authentication...</span>
		</div>
	{/if}
</main>

<style>
	@reference "tailwindcss";

	section {
		margin: 0 !important;
		padding: 0 !important;
	}

	.loader-overlay {
		position: fixed;
		inset: 0;
		background: rgba(8, 0, 36, 0.5);
		display: flex;
		justify-content: center;
		align-items: center;
		z-index: 999;
	}

	@keyframes blink {
		0%,
		100% {
			opacity: 1;
		}
		50% {
			opacity: 0.3;
		}
	}
</style>
