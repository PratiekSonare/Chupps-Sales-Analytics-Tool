<script lang="ts">
    import { onMount } from "svelte";
    import ChuppsButton from "./ChuppsButton.svelte";
    import { render } from "svelte/server";

    export let ml_train_data;

    let form = {
        "Payment Method": "",
        "Lineitem sku": "",
        "Lineitem price": "",
        "Shipping Zip": "",
        "Shipping City": "",
        "Shipping Province": "",
    };

    let loading = false;
    let priceList = [399, 449, 599, 699, 799, 899, 999, 1099, 1299];
    let provinceList = [
        "GA",
        "GJ",
        "DL",
        "AP",
        "KA",
        "TN",
        "KL",
        "RJ",
        "OR",
        "TS",
        "BR",
        "UP",
        "MN",
        "ML",
        "PY",
        "MH",
        "HR",
        "MP",
        "JH",
        "WB",
        "JK",
        "AN",
        "AS",
        "PB",
        "CG",
        "AR",
        "UK",
        "HP",
        "TR",
        "NL",
        "MZ",
        "CH",
        "DN",
        "DD",
    ];

    async function submitForm() {
        try {
            loading = true;
            const response = await fetch("http://localhost:8000/predict", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ data: [form] }), // wrap in array as your API expects list of rows
            });

            const result = await response.json();
            console.log("Prediction result:", result);

            risk_score = result.risk_score.toFixed(2);

            // alert(`Risk Score: ${result.risk_score}`);
        } catch (error) {
            console.error("error: ", error);
        } finally {
            loading = false;
        }
    }

    let risk_score = 0.0;
    let color_scheme = 0;
    let colorClass = "";

    $: {
        if (risk_score <= 0.4) {
            color_scheme = 0;
        } else if (risk_score <= 0.75) {
            color_scheme = 1;
        } else {
            color_scheme = 2;
        }

        colorClass =
            color_scheme === 0
                ? "bg-green-500 shadow-[0_4px_20px_#00C850] border-green-300 text-green-800"
                : color_scheme === 1
                  ? "bg-yellow-400 shadow-[0_4px_20px_#FFEB3B] border-yellow-300 text-yellow-800"
                  : "bg-red-500 shadow-[0_4px_20px_#F44336] border-red-300 text-red-800";
    }

    const trainData = ml_train_data.map((p) => ({
        payment_method: p.payment_method,
        product_sku: p.product_sku,
        product_price: p.product_price,
        pincode: p.pincode,
        city: p.city,
        state: p.state,
        scr: p.scr,
        pcr: p.pcr,
        prcr: p.prcr,
        ccr: p.ccr,
        final_status: p.final_status,
    }));

    function renderTable(data) {
        const tableData = {
            type: "table",
            header: {
                values: [
                    "payment_method",
                    "product_sku",
                    "product_price",
                    "pincode",
                    "city",
                    "state",
                    "scr",
                    "pcr",
                    "prcr",
                    "ccr",
                    "returned?",
                ],
                align: "center",
                fill: { color: "lightgray" },
                font: { family: "Arial", size: 12, color: "black" },
            },
            cells: {
                values: [
                    data.map((d) => d.payment_method),
                    data.map((d) => d.product_sku),
                    data.map((d) => d.product_price),
                    data.map((d) => d.pincode),
                    data.map((d) => d.city),
                    data.map((d) => d.state),
                    data.map((d) => d.scr),
                    data.map((d) => d.pcr),
                    data.map((d) => d.prcr),
                    data.map((d) => d.ccr),
                    data.map((d) => d.final_status),
                ],
                align: "center",
                font: { family: "Arial", size: 11, color: "black" },
                height: 24,
            },
        };

        (window as any).Plotly.newPlot(
            "traindata-table",
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

    onMount(() => {
        renderTable(trainData);
    });

    function autoFillAddress() {
        const match = ml_train_data.find(
            (item) => item.pincode === form["Shipping Zip"],
        );
        if (match) {
            form["Shipping City"] = match.city;
            form["Shipping Province"] = match.state;
        }
    }

    function autoFillPrice() {
        const match = ml_train_data.find(
            (item) => item.product_sku === form["Lineitem sku"],
        );
        if (match) {
            // Make sure price exists in the dropdown
            if (!priceList.includes(match.product_price)) {
                priceList = [...priceList, match.product_price];
            }
            form["Lineitem price"] = match.product_price;
        }
    }

    const content = [
        "A machine learning model was trained using the given location and transaction parameters.",
        "The data table (displayed on bottom-right) was used for training this machine learning model. ",
        "Naturally, it also expects a parameter that it was trained on.",
        "Higher the risk score, higher is the probability that this given transaction would fail!",
    ];
</script>

<div class="p-5 grid grid-cols-2 grid-rows-2 gap-5 h-screen w-screen">
    <div
        class="row-span-2 bg-white rounded-xl p-5 bxsdw h-full border border-gray-300 overflow-x-auto"
    >
        <div class="flex flex-row gap-5 -mt-5 mb-5">
            <ChuppsButton />
            <span class="mt-5 text-center text-3xl">Order Risk Prediction</span>
        </div>
        <div
            class="mb-10 group bxsdw rounded-xl bg-gray-300 flex flex-col justify-center px-5 py-1 text-gray-500 hover:text-black hover:scale-102 transition-all duration-300 ease-in-out"
        >
            <!-- svg and title -->
            <div
                class="flex flex-row items-center justify-center gap-3 mt-3 mb-2"
            >
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    x="0px"
                    y="0px"
                    width="18"
                    height="18"
                    class="fill-current"
                    viewBox="0 0 24 24"
                >
                    <path
                        d="M 12 2 C 6.4889971 2 2 6.4889971 2 12 C 2 17.511003 6.4889971 22 12 22 C 17.511003 22 22 17.511003 22 12 C 22 6.4889971 17.511003 2 12 2 z M 12 4 C 16.430123 4 20 7.5698774 20 12 C 20 16.430123 16.430123 20 12 20 C 7.5698774 20 4 16.430123 4 12 C 4 7.5698774 7.5698774 4 12 4 z M 11 7 L 11 9 L 13 9 L 13 7 L 11 7 z M 11 11 L 11 17 L 13 17 L 13 11 L 11 11 z"
                    ></path>
                </svg>
                <span class="text-lg">How does risk prediction work?</span>
            </div>

            <!-- content span list section (hidden until hover) -->
            <div
                class="hidden group-hover:block transition-all duration-300 ease-in-out"
            >
                {#each content as c}
                    <div class="flex flex-row items-center gap-5">
                        <span class="text-lg text-gray-500">• </span>
                        <span
                            class="text-base text-gray-500 tracking-tight block textlight"
                            >{c}</span
                        >
                    </div>
                {/each}
            </div>
        </div>

        <form on:submit|preventDefault={submitForm} class="">
            <label>
                <p>Payment Method:</p>
                <select bind:value={form["Payment Method"]}>
                    <option disabled selected value=""
                        >--Select Payment Method--</option
                    >
                    <option value="COD">CASH ON DELIVERY</option>
                    <option value="PREPAID">PREPAID</option>
                </select>
                <!-- <input type="text" bind:value={form["Payment Method"]} /> -->
            </label>
            <label>
                <p>Lineitem SKU:</p>
                <input
                    type="text"
                    bind:value={form["Lineitem sku"]}
                    on:blur={autoFillPrice}
                />
            </label>
            <label>
                <p>Lineitem Price:</p>
                <select bind:value={form["Lineitem price"]}>
                    <option disabled selected value="">--Select Price--</option>
                    {#each priceList as price}
                        <option value={price}>₹{price}</option>
                    {/each}
                </select>
            </label>
            <label>
                <p>Shipping Zip:</p>
                <input
                    type="text"
                    bind:value={form["Shipping Zip"]}
                    on:blur={autoFillAddress}
                />
            </label>
            <label>
                <p>Shipping City:</p>
                <input type="text" bind:value={form["Shipping City"]} />
            </label>
            <label>
                <p>Shipping Province:</p>
                <select bind:value={form["Shipping Province"]}>
                    <option disabled selected value="">--Select Shade--</option>
                    {#each provinceList as price}
                        <option value={price}>{price}</option>
                    {/each}
                </select>
            </label>

            {#if loading}
                <div class="mt-10 flex justify-center">
                    <div
                        class="w-8 h-8 border-4 border-green-500 border-t-transparent rounded-full animate-spin"
                    ></div>
                </div>
            {:else}
                <button
                    type="submit"
                    class="hover:shadow-[0_4px_20px_#00C850] mt-5 px-6 py-2 rounded bg-green-500 text-white font-semibold"
                >
                    Submit
                </button>
            {/if}
        </form>
    </div>

    <div
        class="bg-white rounded-xl bxsdw h-full w-full border border-gray-300 py-5 flex flex-col row-span-2"
    >
        <div class="flex flex-row gap-5 -mt-5 mb-5 px-5">
            <ChuppsButton />
            <span class="mt-5 text-center text-3xl">Risk Score</span>
        </div>

        <span class={`text-center text-8xl py-2 ${colorClass}`}
            >{risk_score}</span
        >

        <div class="my-6 flex flex-col items-center justify-center gap-1">
            <span class="text-xl">Remark:</span>
            {#if risk_score === 0}
                <span class="text-gray-800 text2">---</span>
            {:else if color_scheme === 0 && risk_score !== 0}
                <span class="text-green-500 text2"
                    >Customer most likely verified, successful transaction
                    highly probable.</span
                >
            {:else if color_scheme === 1}
                <span class="text-yellow-500 text2"
                    >Customer pincode, address aligns with cancelled orders,
                    verify customer address before proceeding.</span
                >
            {:else}
                <span class="text-red-500 text2"
                    >Customer pincode, address aligns perfectly with cancelled
                    orders. Proceed only after verifying!</span
                >
            {/if}
        </div>

        <div
            class=" mb-5 px-60 opacity-50 hover:opacity-100 transition duration-100"
        >
            <div
                class="flex flex-col items-center justify-center border border-gray-300 rounded-xl"
            >
                <span class=" text-xl">Classification Criteria</span>

                <span
                    class={`w-full text-center text-lg py-1 bg-green-500 border-green-300 text-green-800`}
                >
                    &lt;= 0.4
                </span>
                <span
                    class={`w-full text-center text-lg py-1 bg-yellow-400 border-yellow-300 text-yellow-800`}
                    >0.4 &lt; and &lt;= 0.75
                </span>
                <span
                    class={`rounded-b-xl w-full text-center text-lg py-1 bg-red-500 border-red-300 text-red-800`}
                >
                    &gt; 0.75</span
                >
            </div>
        </div>

        <div class="w-full overflow-y-hidden">
            <div><div id="traindata-table"></div></div>
        </div>
    </div>
</div>

<style>
    @reference "tailwindcss";

    form {
        @apply flex flex-col gap-5;
    }

    form label {
        @apply flex flex-col pt-0 w-full h-full shadow-xl rounded-xl hover:scale-102 transition-all duration-100;
    }

    form p {
        @apply px-2 bg-gray-800 text-white rounded-t-xl p-2;
    }

    form input,
    select {
        @apply rounded-b-xl bg-blue-200 shadow-2xl p-2 transform transition active:bg-green-300 duration-100;
    }

    form button {
        @apply hover:scale-102 hover:bg-gradient-to-r hover:from-green-500 hover:to-green-300 transition transform active:scale-95 scale-100 border border-green-200 rounded-xl bg-amber-500 text-3xl duration-300 ease-in-out;
    }
</style>
