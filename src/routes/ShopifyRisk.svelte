<script>
    import { onMount } from "svelte";

    let shopify_order_with_risk = [];
    let pageInfo = {};
    let currentCursor = null;
    let sortEnabled = false;
    let sortedOrders = [];
    let tableLoading = true;

    async function fetchOrders(cursor = null) {
        let url = `${import.meta.env.VITE_BACKEND_LINK}/shopify/all-orders`;
        if (cursor) {
            url += `?cursor=${cursor}`;
        }

        try {
            tableLoading = true;
            const res = await fetch(url, {
                method: "GET",
                headers: { "Content-Type": "application/json" },
            });

            const data = await res.json();
            shopify_order_with_risk = data.results || [];
            pageInfo = data.pageInfo || {};
            currentCursor = cursor;           
        } catch (error) {
            console.error("error: ", error);            
        } finally {
            tableLoading = false;
        }

        if (sortEnabled) {
            try{
                tableLoading = true;
                sortOrders();
            } catch (error) {
                console.error("error: ", error);
            } finally {
                tableLoading = false;
            }
        }

        tableLoading = false;
    }

    function nextPage() {
        if (pageInfo.hasNextPage) {
            fetchOrders(pageInfo.endCursor);
        }
    }

    function sortOrders() {
        sortedOrders = [...shopify_order_with_risk].sort(
            (a, b) => b.risk_score - a.risk_score,
        );
    }

    function toggleSort() {
        sortEnabled = !sortEnabled;
        if (sortEnabled) {
            sortOrders();
        }
    }

    function getRiskColor(score) {
        if (score < 0.3) return "#10b981"; // green
        if (score < 0.7) return "#facc15"; // yellow
        return "#ef4444"; // red
    }

    onMount(() => {
        fetchOrders();
    });
</script>

<div class="w-screen h-screen relative">
    <div class="grid grid-rows-4 h-full p-5">
        <!-- HEADER -->
        <div class="row-span-1 flex flex-row justify-start gap-10 w-full px-10">
            <img src="/shopify-logo.svg" alt="shopify_logo" class="w-1/12" />
            <div class="flex flex-col">
                <span class="text-5xl text-gray-900 mb-5"
                    >Shopify Order Risk Scores</span
                >
                <span class="text-md"
                    >• View latest Shopify orders with detailed order and
                    transaction info</span
                >
                <span class="text-md"
                    >• Click "Calculate Risk Score" to estimate risk</span
                >
                <span class="text-md"
                    >• Sort the list by clicking "..." icon</span
                >
            </div>
        </div>

        <!-- TABLE -->
        <div
            class="row-span-3 bg-white bxsdw rounded-xl border border-gray-200 p-5 flex flex-col"
        >
            <div
                class="border border-black w-full rounded-xl p-5 overflow-y-hidden flex flex-col"
            >
                <!-- BUTTONS -->
                <div class="ml-auto flex gap-5 mb-4">
                    <button
                        class="px-4 py-2 bg-blue-300 rounded-lg bxsdw transition duration-150 active:scale-95 scale-100 ease-in-out"
                        on:click={toggleSort}
                    >
                        {sortEnabled
                            ? "Show Original Order"
                            : "Sort page by Risk Score"}
                    </button>

                    <button
                        class="px-4 py-2 bg-gray-300 rounded-lg disabled:opacity-50 bxsdw transition duration-150 active:scale-95 scale-100 ease-in-out"
                        on:click={nextPage}
                        disabled={!pageInfo.hasNextPage}
                    >
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
                {#if !tableLoading}
                <div class="flex flex-col gap-3 w-full h-full overflow-y-auto">
                    {#each sortEnabled ? sortedOrders : shopify_order_with_risk as order}
                        <div
                            class="border-b border-black text-black rounded-2xl shadow-sm flex flex-row justify-between p-5"
                        >
                            <span class="w-[100px]">{order.orderNum}</span>
                            <span class="w-[100px]"
                                >{order["Payment Method"]}</span
                            >
                            <span class="w-[100px]"
                                >{order["Product Title"]}</span
                            >
                            <span class="w-[100px]"
                                >{order["Lineitem sku"]}</span
                            >
                            <span class="w-[100px]"
                                >{order["Lineitem price"]}</span
                            >
                            <span class="w-[100px]"
                                >{order["Shipping Zip"]}</span
                            >
                            <span class="w-[100px]"
                                >{order["Shipping City"]}</span
                            >
                            <span class="w-[100px]"
                                >{order["Shipping Province"]}</span
                            >
                            <div class="w-[100px] flex flex-col items-center">
                                <svg viewBox="0 0 100 50" class="w-full -mb-5">
                                    <!-- Background semicircle -->
                                    <path
                                        d="M 10 50 A 40 40 0 0 1 90 50"
                                        fill="transparent"
                                        stroke="#e5e7eb"
                                        stroke-width="10"
                                    />
                                    <!-- Progress arc -->
                                    <path
                                        d="M 10 50 A 40 40 0 0 1 90 50"
                                        fill="transparent"
                                        stroke={getRiskColor(order.risk_score)}
                                        stroke-width="10"
                                        stroke-dasharray="126"
                                        stroke-dashoffset={126 -
                                            order.risk_score * 126}
                                        stroke-linecap="round"
                                    />
                                </svg>
                                <span class="text-lg text-black"
                                    >{(order.risk_score * 100).toFixed(
                                        1,
                                    )}%</span
                                >
                            </div>
                        </div>
                    {/each}
                </div>
                {:else}
                <div class="h-full mx-auto animate-ping text-2xl">
                    Loading...
                </div>
                {/if}
            </div>
        </div>
    </div>
</div>

<style>
    @reference "tailwindcss";
</style>
