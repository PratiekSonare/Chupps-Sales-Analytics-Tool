<script lang="ts">
  export let data;
  const { wo_centro_prophet } = data;
  import Tool from '../routes/Tool.svelte'
</script>

<svelte:head>
	<title>Sales Analytics - Chupps</title>
	<meta name="description" content="Svelte demo app" />
</svelte:head>

<section>
	<h2>Trial Forecast</h2>

	<!-- {#if wo_centro_prophet?.length}
	<table class="table-auto border border-gray-400">
		<thead>
		<tr>
			{#each Object.keys(wo_centro_prophet[0]) as key}
			<th class="border px-2 py-1">{key}</th>
			{/each}
		</tr>
		</thead>
		<tbody>
		{#each wo_centro_prophet as row}
			<tr>
			{#each Object.values(row) as value}
				<td class="border px-2 py-1">{value}</td>
			{/each}
			</tr>
		{/each}
		</tbody>
	</table>
	{:else}
	<p>No data in wo_centro_prophet.</p>
	{/if} -->

	<Tool {wo_centro_prophet} />
</section>

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
