<script lang="ts">
	export let data;
	const { wo_centro_prophet, chupps_23_25_full, total_sales, total_revenue, total_parties, chupps_items, chupps_shades, itemFilteredDB } = data;

	import Forecast from "./Forecast.svelte";
	import Sidebar from "./sidebar/Sidebar.svelte";
	import Home from "./Home.svelte";
	import Data from "./Data.svelte";
    import ItemShade from "./ItemShade.svelte";
    import Regional from "./Regional.svelte";

	let activeView = "home";

	function handleView(view) {
		activeView = view;
	}
	
</script>

<svelte:head>
	<title>Sales Analytics - Chupps</title>
	<meta name="description" content="Svelte demo app" />
</svelte:head>

<main class="flex w-screen h-screen overflow-hidden">
	<!-- Sidebar -->
	<div class="w-32 h-full bg-gray-800">
		<Sidebar onSelect={handleView} {activeView} />
	</div>

	<!-- Main content -->
	<section class="flex-1 flex justify-center items-center h-full overflow-auto p-6">
		{#if activeView === "home"}
			<Home />
		{:else if activeView === "data"}
			<Data />
		{:else if activeView === "item-shade"}
			<ItemShade {itemFilteredDB} />
		{:else if activeView === "regional"}
			<Regional />
		{:else if activeView === "forecast"}
			<Forecast {wo_centro_prophet} {chupps_23_25_full} total_sales={total_sales} total_revenue={total_revenue} total_parties={total_parties} chupps_items={chupps_items} chupps_shades={chupps_shades} />
		{/if}
	</section>
</main>


<style>
	@reference "tailwindcss";
	
	section {
		margin: 0 !important;
		padding: 0 !important;
	}

</style>
