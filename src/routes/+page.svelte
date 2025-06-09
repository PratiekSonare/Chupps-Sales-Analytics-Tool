<script lang="ts">

	export let data;
	const { wo_centro_prophet } = data;

	import Forecast from './Forecast.svelte'
	import Sidebar from './sidebar/Sidebar.svelte'
	import Home from './Home.svelte'
	import Data from './Data.svelte'

	let activeView = 'home'

	function handleView(view) {
		activeView = view;
	}
</script>

<svelte:head>
	<title>Sales Analytics - Chupps</title>
	<meta name="description" content="Svelte demo app" />
</svelte:head>

<main class="m-0">
	<div class="flex w-full h-full">

		<!-- Sidebar -->
		<Sidebar onSelect={handleView} />

		<!-- Main content -->
		<section class="flex-1 p-6 w-full flex justify-center items-center">
			{#if activeView === 'home'}
				<Home />
			{:else if activeView === 'data'}
				<Data />
			{:else if activeView === 'forecast'}
				<Forecast {wo_centro_prophet} />
			{/if}
		</section>
	</div>
</main>

<style>
	@reference "tailwindcss";

	section {
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		flex: 0.6;
	}
</style>