<!-- 

<div class="w-screen h-screen">
    <div class="grid grid-cols-3 grid-rows-4 gap-3 h-full p-5">
        <div class="col-span-1 row-span-4 bg-white rounded-xl shadow-xl border border-gray-300"></div>
        <div class="col-start-2 col-span-2 row-start-0 row-span-2 bg-white rounded-xl shadow-xl border border-gray-300"></div>
        <div class="col-start-2 col-span-2 row-start-3 row-span-2 bg-white rounded-xl shadow-xl border border-gray-300"></div>
    </div>
</div> -->
<script>
	import { supabase } from '../lib/supabaseClient';
	import { onMount } from 'svelte';
	let items = [];
	let selectedItem = '';
	let shades = [];
	let selectedShade = '';

	// Load distinct items from Supabase
	onMount(async () => {
		const { data, error } = await supabase
			.from('chupps_23_25_full')
			.select('item', { count: 'exact' })
			.order('item', { ascending: true })
			// .select('item', { distinct: true });

		if (!error) {
			items = [...new Set(data.map((row) => row.item))];
		}
	});

	// Watch for selectedItem change and load matching shades
	$: if (selectedItem) {
		loadShades(selectedItem);
	}

	async function loadShades(item) {
		const { data, error } = await supabase
			.from('chupps_23_25_full')
			.select('shade')
			.eq('item', item)
			.order('shade', { ascending: true })
			// .select('shade', { distinct: true });

		if (!error) {
			shades = [...new Set(data.map((row) => row.shade))];
		}
	}
</script>

<!-- Dropdowns -->
<label>
	Item:
	<select class="border border-gray-400 rounded" bind:value={selectedItem}>
		<option disabled selected value="">--Select Item--</option>
		{#each items as item}
			<option value={item}>{item}</option>
		{/each}
	</select>
</label>

{#if selectedItem}
	<label>
		Shade:
		<select class="border border-gray-400 rounded" bind:value={selectedShade}>
			<option disabled selected value="">--Select Shade--</option>
			{#each shades as shade}
				<option value={shade}>{shade}</option>
			{/each}
		</select>
	</label>
{/if}
