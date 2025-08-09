<script>
    import { onMount } from "svelte";

    let shopify_order_with_risk = [];
    let pageInfo = {};
    let currentCursor = null;

    async function fetchOrders(cursor = null) {
        let url = `${import.meta.env.VITE_BACKEND_LINK}/shopify/all-orders`;
        if (cursor) {
            url += `?cursor=${cursor}`;
        }

        const res = await fetch(url, {
            method: "GET",
            headers: { "Content-Type": "application/json" },
        });

        const data = await res.json();
        shopify_order_with_risk = data.results || [];
        pageInfo = data.pageInfo || {};
        currentCursor = cursor;
    }

    function nextPage() {
        if (pageInfo.hasNextPage) {
            fetchOrders(pageInfo.endCursor);
        }
    }

    function prevPage() {
        if (pageInfo.hasPreviousPage) {
            // NOTE: For true Shopify backward pagination,
            // you'd want to use `before: startCursor` instead
            fetchOrders(pageInfo.startCursor);
        }
    }

    onMount(() => {
        fetchOrders();
    });
</script>

<div class="w-screen h-screen relative">
    <div class="grid grid-rows-4 h-full p-5">
        
        <!-- HEADER -->
        <div class="row-span-1 flex flex-row justify-start gap-10 w-full px-10">
            <img src="/shopify-logo.svg" alt="shopify_logo" class="w-1/12">
            <div class="flex flex-col">
                <span class="text-5xl text-gray-900 mb-5">Shopify Order Risk Scores</span>
                <span class="text-md">• View latest Shopify orders with detailed order and transaction info</span>
                <span class="text-md">• Click "Calculate Risk Score" to estimate risk</span>
                <span class="text-md">• Sort the list by clicking "..." icon</span>
            </div>
        </div>

        <!-- TABLE -->
        <div class="row-span-3 bg-white bxsdw rounded-xl border border-gray-200 p-5 flex flex-col">
            <div class="border border-black w-full rounded-xl p-5 overflow-y-hidden flex flex-col">

                <!-- PAGINATION BUTTONS -->
                <div class="flex justify-between gap-5 mb-4">
                    <div class="w-full bg-gray-300 rounded-lg px-4 py-2 shadow-sm transition duration-150 active:scale-90 scale-100 ease-in-out">
                        <span></span>
                    </div>

                    <button 
                        class="px-4 py-2 bg-gray-300 rounded-lg disabled:opacity-50 bxsdw transition duration-150 active:scale-95 scale-100 ease-in-out"
                        on:click={nextPage}
                        disabled={!pageInfo.hasNextPage}>
                        Next
                    </button>

                </div>
                
                <!-- HEADER ROW -->
                <div class="text-white bg-gray-900 rounded-xl p-5 mb-5">
                    <div class="flex flex-row justify-between w-full text-md">
                        <span class="w-[100px]">Order Num</span>
                        <span class="w-[100px]">Payment Method</span>
                        <span class="w-[100px]">Product Title</span>
                        <span class="w-[100px]">Lineitem SKU</span>
                        <span class="w-[100px]">Lineitem Price</span>
                        <span class="w-[100px]">Shipping Zip</span>
                        <span class="w-[100px]">Shipping City</span>
                        <span class="w-[100px]">Shipping Province</span>
                        <span class="w-[100px]">Risk Scores</span>
                    </div>
                </div>

                <!-- ORDER ROWS -->
                <div class="flex flex-col gap-3 w-full h-full overflow-y-auto">
                    {#each shopify_order_with_risk as order}
                        <div class="border-b border-black text-black rounded-2xl shadow-sm flex flex-row justify-between p-5">
                            <span class="w-[100px]">{order.orderNum}</span>
                            <span class="w-[100px]">{order["Payment Method"]}</span>
                            <span class="w-[100px]">{order["Product Title"]}</span>
                            <span class="w-[100px]">{order["Lineitem sku"]}</span>
                            <span class="w-[100px]">{order["Lineitem price"]}</span>
                            <span class="w-[100px]">{order["Shipping Zip"]}</span>
                            <span class="w-[100px]">{order["Shipping City"]}</span>
                            <span class="w-[100px]">{order["Shipping Province"]}</span>
                            <span class="w-[100px]">{order.risk_score.toFixed(3)}</span>
                        </div>
                    {/each}
                </div>
            </div>
        </div>
        
    </div>
</div>

<style>
    @reference "tailwindcss";
</style>
