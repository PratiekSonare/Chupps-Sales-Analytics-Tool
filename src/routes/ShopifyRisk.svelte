<script>
    import { onMount } from "svelte";
    import { supabase } from "$lib/supabaseClient";

    let shopify_order_with_risk = [];
    let sortedOrders = [];
    let confirmedOrderList = [];
    let cancelledOrdersList = [];
    let pageInfo = {};
    let currentCursor = null;
    let sortEnabled = false;
    let sortEnabledConfirm = false;
    let sortEnabledCancel = false;
    let filterConfirmed = [];
    let filterCancelled = [];
    let tableLoading = true;
    let numberLoading = false;

    async function confirmOrder(orderNum) {
        // Step 1: Check if it already exists
        const { data: existing, error: fetchError } = await supabase
            .from("RiskScore_confirmed_orders")
            .select("orderNum")
            .eq("orderNum", orderNum);

        if (fetchError) {
            console.error("Error checking confirmation:", fetchError);
            alert("Error checking confirmation");
            return;
        }

        if (existing && existing.length > 0) {
            alert(`Order ${orderNum} is already confirmed. Refresh page once again if errors persist.`);
            return;
        }

        // Step 2: Insert if not found
        const { data, error: insertError } = await supabase
            .from("RiskScore_confirmed_orders")
            .insert([{ orderNum }]);

        if (insertError) {
            console.error("Error saving confirmation:", insertError);
            alert("Failed to confirm order");
        } else {
            alert(`Order ${orderNum} marked as confirmed!`);
            console.log("Order confirmed:", data);
        }
    }

    async function cancelOrder(orderNum) {
        // Step 1: Check if it already exists
        const { data: existing, error: fetchError } = await supabase
            .from("RiskScore_cancelled_orders")
            .select("orderNum")
            .eq("orderNum", orderNum);

        if (fetchError) {
            console.error("Error checking cancellation:", fetchError);
            alert("Error checking to cancellation");
            return;
        }

        if (existing && existing.length > 0) {
            alert(`Order ${orderNum} is already cancelled. Refresh page once again if errors persist.`);
            return;
        }

        // Step 2: Insert if not found
        const { data, error: insertError } = await supabase
            .from("RiskScore_cancelled_orders")
            .insert([{ orderNum }]);

        if (insertError) {
            console.error("Error saving to cancel:", insertError);
            alert("Failed to cancel order");
        } else {
            alert(`Order ${orderNum} marked as CANCELLED!`);
            console.log("Order to canceled:", data);
        }
    }

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
            try {
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

    async function filterTableConfirm() {
        try {
            tableLoading = true;

            // Step 1: Fetch all confirmed order numbers from Supabase
            const { data: confirmedOrders, error } = await supabase
                .from("RiskScore_confirmed_orders")
                .select("orderNum");

            if (error) {
                console.error("Error fetching confirmed orders:", error);
                alert("Failed to fetch confirmed orders");
                return;
            }

            const confirmedNums = confirmedOrders.map((o) => o.orderNum);

            // Step 2: Fetch all Shopify orders (no pagination for now)
            const res = await fetch(
                `${import.meta.env.VITE_BACKEND_LINK}/shopify/confirmed-orders`,
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(confirmedNums.map(String)),
                },
            );

            const data = await res.json();
            confirmedOrderList = data.results || [];

            pageInfo = {}; // reset pagination since it's filtered data
        } catch (err) {
            console.error("Error filtering confirmed orders:", err);
        } finally {
            tableLoading = false;
        }
    }

    async function filterTableCancel() {
        try {
            tableLoading = true;

            // Step 1: Fetch all cancelled order numbers from Supabase
            const { data: cancelledOrders, error } = await supabase
                .from("RiskScore_cancelled_orders")
                .select("orderNum");

            if (error) {
                console.error("Error fetching cancelled orders:", error);
                alert("Failed to fetch cancelled orders");
                return;
            }

            const cancelledNums = cancelledOrders.map((o) => o.orderNum);

            // Step 2: Fetch all Shopify orders
            const res = await fetch(
                `${import.meta.env.VITE_BACKEND_LINK}/shopify/cancelled-orders`,
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(cancelledNums.map(String)),
                },
            );

            const data = await res.json();
            cancelledOrdersList = data.results || [];
                
            pageInfo = {};
        } catch (err) {
            console.error("Error filtering cancelled orders:", err);
        } finally {
            tableLoading = false;
        }
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

    function toggleSortConfirm() {
        sortEnabled = false;
        sortEnabledCancel = false;
        sortEnabledConfirm = !sortEnabledConfirm;
        if (sortEnabledConfirm) {
            filterTableConfirm();
        }
    }

    function toggleSortCancel() {
        sortEnabled = false;
        sortEnabledConfirm = false;
        sortEnabledCancel = !sortEnabledCancel;
        if (sortEnabledCancel) {
            filterTableCancel();
        }
    }

    function getRiskColor(score) {
        if (score < 0.4) return "#10b981"; // green
        if (score < 0.75) return "#facc15"; // yellow
        return "#ef4444"; // red
    }

    onMount(() => {
        fetchOrders();
        filterTableCancel();
        filterTableConfirm();
    });

    async function fetchNumber(orderIndex) {
        const currentTable = sortEnabled
            ? sortedOrders
            : shopify_order_with_risk;
        const order = currentTable[orderIndex];

        try {
            numberLoading = true;
            const res = await fetch(
                `${import.meta.env.VITE_BACKEND_LINK}/shopify/order-phone?order_num=${order.orderNum}`,
            );
            const data = await res.json();

            currentTable[orderIndex] = {
                ...order,
                phoneNumber: data.phone || "NOT FOUND",
            };
            shopify_order_with_risk = [...shopify_order_with_risk];
            sortedOrders = [...sortedOrders];
        } catch (error) {
            console.error("error: ", error);
        } finally {
            numberLoading = false;
        }
    }
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
                <span class="text-md text2 text-gray-500"
                    >• View latest Shopify orders <span class="text1 text-red-400">(max. 50 at once)</span> with detailed order and transaction metadata</span
                >
                <span class="text-md text2 text-gray-500"
                    >• The Risk Meter is a measure of how likely any given transaction can be cancelled!</span>
                <span class="text-md text2 text-gray-500"
                    >• Click on <span class="text1 text-red-400">"Sort by Risk Score"</span> to get the transactions with highest risk</span
                >
                <span class="text-md text2 text-gray-500"
                    >• For transactions with high risk scores, get their contact phone number and call to confirm their transaction</span
                >
                <span class="text-md text2 text-gray-500"
                    >• Mark transactions as <span class="text1 text-red-400">"Confirmed"</span> or <span class="text1 text-red-400">"Cancelled"</span> to keep track of the transactions </span
                >
            </div>
        </div>

        <!-- TABLE -->
        <div
            class="row-span-3 bg-white bxsdw rounded-xl border border-gray-200 p-5 flex flex-col"
        >
            <div
                class="border border-black w-full rounded-xl p-5 overflow-y-hidden flex flex-col h-full"
            >
                <!-- BUTTONS -->
                <div class="flex flex-row justify-between gap-5 mb-4">
                    <div class="flex flex-row gap-5">
                        <button
                            disabled={sortEnabledCancel}
                            class={`px-4 py-2 rounded-lg bxsdw transition duration-150 active:scale-95 scale-100 ease-in-out ${sortEnabledCancel? 'bg-gray-500 opacity-50' : 'bg-green-500'}`}
                            on:click={toggleSortConfirm}
                        >
                            {sortEnabledConfirm
                                ? "Show all"
                                : "Confirmed Orders"}
                        </button>

                        <button
                            disabled={sortEnabledConfirm}
                            class={`px-4 py-2 rounded-lg bxsdw transition duration-150 active:scale-95 scale-100 ease-in-out ${sortEnabledConfirm ? 'bg-gray-500 opacity-50' : 'bg-red-500'}`}
                            on:click={toggleSortCancel}
                        >
                            {sortEnabledCancel
                                ? "Show all"
                                : "Cancelled Orders"}
                        </button>
                    </div>
                    <div class="flex flex-row items-center gap-5">
                        <span class="text-gray-500">Count: {sortEnabled ? sortedOrders.length : sortEnabledConfirm ? confirmedOrderList.length : sortEnabledCancel ? cancelledOrdersList.length : shopify_order_with_risk.length}</span>
                        <button
                            class="px-4 py-2 bg-blue-300 rounded-lg bxsdw transition duration-150 active:scale-95 scale-100 ease-in-out"
                            on:click={toggleSort}
                        >
                            {sortEnabled
                                ? "Show all"
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
                </div>

                <!-- HEADER ROW -->
                <div class="text-white bg-gray-900 rounded-xl p-5 shadow-lg">
                    <div class="flex flex-row justify-between items-center w-full text-md">
                        <span class="w-[150px]">Order Num</span>
                        <div class="w-[1px] h-[15px] bg-gray-400 rounded"></div>
                        <span class="w-[100px]">Payment Method</span>
                        <div class="w-[1px] h-[15px] bg-gray-400 rounded"></div>
                        <span class="w-[100px]">Product Title</span>
                        <div class="w-[1px] h-[15px] bg-gray-400 rounded"></div>
                        <span class="w-[100px]">Lineitem SKU</span>
                        <div class="w-[1px] h-[15px] bg-gray-400 rounded"></div>
                        <span class="w-[100px]">Lineitem Price</span>
                        <div class="w-[1px] h-[15px] bg-gray-400 rounded"></div>
                        <span class="w-[100px]">Shipping Zip</span>
                        <div class="w-[1px] h-[15px] bg-gray-400 rounded"></div>
                        <span class="w-[100px]">Shipping City</span>
                        <div class="w-[1px] h-[15px] bg-gray-400 rounded"></div>
                        <span class="w-[100px]">Shipping Province</span>
                        <div class="w-[1px] h-[15px] bg-gray-400 rounded"></div>
                        <span class="w-[100px]">Risk Scores</span>
                    </div>
                </div>

                <!-- ORDER ROWS -->
                {#if !tableLoading}
                    <div
                        class="flex flex-col gap-3 w-full h-full overflow-y-auto"
                    >
                        {#each sortEnabled ? sortedOrders : sortEnabledConfirm ? confirmedOrderList : sortEnabledCancel ? cancelledOrdersList : shopify_order_with_risk as order, index}
                            <div
                                class="relative border-b border-black text-black rounded-2xl shadow-sm flex flex-row justify-between p-5"
                            >
                                {#if order.tags && order.tags.length > 0}
                                    <div
                                        class="absolute bottom-2 right-2 flex flex-wrap gap-1"
                                    >
                                        {#each order.tags as tag}
                                            <span
                                                class="bg-yellow-200 text-black px-2 py-0.5 rounded-full text-xs shadow-sm"
                                            >
                                                {tag}
                                            </span>
                                        {/each}
                                    </div>
                                {/if}

                                <div class="flex flex-col gap-1 w-[150px]">
                                    <span class="mx-auto">{order.orderNum}</span
                                    >
                                    <button
                                        on:click={() => fetchNumber(index)}
                                        class:bg-gray-400={numberLoading}
                                        disabled={numberLoading ||
                                            order.phoneNumber}
                                        class="px-2 py-1 bg-blue-300 rounded-lg shadow-sm transition duration-150 active:scale-95 scale-100 ease-in-out text-sm"
                                    >
                                        <span
                                            >{order.phoneNumber
                                                ? order.phoneNumber
                                                : "📞 Phone"}</span
                                        >
                                    </button>
                                    <button
                                        on:click={() =>
                                            confirmOrder(order.orderNum)}
                                        class="px-2 py-1 bg-green-500 rounded-lg shadow-sm transition duration-150 active:scale-95 scale-100 ease-in-out text-sm"
                                        >Confirmed?</button
                                    >
                                    <button
                                        on:click={() =>
                                            cancelOrder(order.orderNum)}
                                        class="px-2 py-1 bg-red-300 rounded-lg shadow-sm transition duration-150 active:scale-95 scale-100 ease-in-out text-sm"
                                        >Cancelled?</button
                                    >
                                </div>
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
                                <div
                                    class="w-[100px] flex flex-col items-center scale-105"
                                >
                                    <svg
                                        viewBox="0 0 100 50"
                                        class="w-full -mb-5"
                                    >
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
                                            stroke={getRiskColor(
                                                order.risk_score,
                                            )}
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
                    <div class="mx-auto animate-ping text-2xl mt-10">
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
