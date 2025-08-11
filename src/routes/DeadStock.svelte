<script>
// @ts-nocheck

    let xlsxFile = null;
    let data_with_deadScore = [];
    let sortedInventory = [];
    let filterMonthly = [];
    let sortEnabled = false;
    let previewData = [];
    let sortMonths = false;
    let selectedMonths = ""; // dropdown value
    let setFormula = false;

    function getRiskColor(score) {
        if (score < 0.4) return "#10b981"; // green
        if (score < 0.75) return "#facc15"; // yellow
        return "#ef4444"; // red
    }

    function sortInventory() {
        sortedInventory = [...data_with_deadScore].sort(
            (a, b) => b.deadScore - a.deadScore,
        );
    }

    function filterMonths() {
        // convert selected months to number
        const months = parseInt(selectedMonths, 10);

        // Filter rows where Age <= selected months
        filterMonthly = data_with_deadScore.filter(row => {
            const ageValue = parseFloat(row.Age); // assuming 'Age' is numeric in months
            return ageValue <= months;
        });
    }

    function toggleSort() {
        sortEnabled = !sortEnabled;
        if (sortEnabled) {
            sortInventory();
        }
    }

    function toggleMonths() {
        sortMonths = !sortMonths;

        if (sortMonths && selectedMonths) {
            filterMonths();
        }
    }


    async function evaluateDeadScore({ input_xlsx }) {
        try {
            const formData = new FormData();
            formData.append("file", input_xlsx);

            const res = await fetch(
                `${import.meta.env.VITE_BACKEND_LINK}/mis-report/dead-stock`,
                {
                    method: "POST",
                    body: formData,
                },
            );

            const data = await res.json();
            data_with_deadScore = [...data];
        } catch (error) {
            console.error("error: ", error);
        }
    }

    async function uploadXLSX() {
        if (!xlsxFile) {
            alert("Please upload a file first.");
            return;
        }
        await evaluateDeadScore({ input_xlsx: xlsxFile });
    }

    function handleFileChange(event) {
        xlsxFile = event.target.files[0];
        if (!xlsxFile) return;
    }
</script>

<div class="w-screen h-screen relative">
    <div class="grid grid-rows-4 gap-5 h-full p-5">
        <!-- upload latest data  -->
        <div class="relative row-span-1 bg-white rounded-xl bxsdw h-full w-full p-5">

            {#if setFormula}
                <img alt="formula" src="/formula.png" class="p-2 rounded-xl shadow-sm border border-gray-400 absolute bottom-1/4 left-1/3">
            {/if}
            <div
                class="flex flex-row justify-between items-center h-full w-full"
            >
                <div class="flex flex-col gap-1 px-5">
                    <span class="text-4xl mb-2 text-gray-900"
                        >Dead Stock Analysis</span
                    >
                    <span class="text-sm text-gray-500 text2"
                        >• Upload the latest "MIS-Stock" report (please make sure only <span class="text1 text-red-500 underline">STOCK</span> is uploaded)</span
                    >
                    <span class="text-sm text-gray-500 text2"
                        >• Stock represents current inventory at the Bhiwandi
                        warehouse</span
                    >
                    <span class="text-sm text-gray-500 text2"
                        >• A "dead score" has been evaluted for each product
                        using the 
                        <button class="underline text-blue-500 inline cursor-pointer" on:click={() => setFormula = !setFormula}>formula</button>
                    </span>
                    <span class="text-sm text-gray-500 text2"
                        >• Clear out the products with highest dead score ASAP</span
                    >
                </div>
                <div class="flex flex-row gap-1 h-full w-1/2 mr-5">
                    <button
                        on:click={uploadXLSX}
                        class="flex flex-row items-center justify-center gap-5 transition-all w-full h-full transform duration-500 active:scale-95 hover:scale-102 hover:bg-gradient-to-r hover:from-green-600 hover:text-white hover:to-green-400 scale-100 bg-gray-200 rounded-xl border border-gray-300 shadow-md p-2 px-5"
                        class:translate-x-full={xlsxFile === null}
                        class:-translate-x-0={xlsxFile !== null}
                    >
                        Evaluate Dead Score
                    </button>
                    <input
                        type="file"
                        accept=".xlsx"
                        on:change={handleFileChange}
                        class="h-full w-full
                                text-transparent file:text-white
                                file:bg-gray-900 hover:file:bg-gray-700
                                file:w-full file:h-full
                                file:rounded-xl file:border-0
                                file:font-semibold file:text-xl z-100"
                    />
                </div>
            </div>
        </div>
        <!-- display table content and highlight item with greatest score  -->
        <div class="p-5 row-span-3 bg-white rounded-xl bxsdw h-full w-full">
            <div class="w-full flex flex-row justify-between">
                <button
                    class="my-2 px-4 py-2 bg-blue-300 rounded-lg bxsdw transition duration-150 active:scale-95 scale-100 ease-in-out"
                    on:click={toggleSort}
                >
                    {sortEnabled ? "Show original" : "Sort page by Dead Score"}
                </button>
                <div class="flex flex-row gap-1 h-full items-center">
                    <button
                        class="ml-auto my-2 px-4 py-2 bg-blue-300 rounded-lg bxsdw transition duration-150 active:scale-95 scale-100 ease-in-out"
                        on:click={toggleMonths}
                    >
                        {sortEnabled ? "Show original" : "Filter by Age"}
                    </button>
                    <select
                        bind:value={selectedMonths}
                        class="rounded-xl px-1 border bxsdw border-gray-300 h-[47px]"
                    >
                        <option value=""></option>
                        <option value="1">1 month</option>
                        <option value="3">3 months</option>
                        <option value="6">6 months</option>
                        <option value="12">12 months</option>
                    </select>
                </div>
            </div>
            <div class="text-white bg-gray-900 rounded-xl p-5 shadow-lg">
                <div
                    class="flex flex-row justify-between items-center w-full text-md"
                >
                    <span class="w-[150px]">Item Code</span>
                    <div class="w-[1px] h-[15px] bg-gray-400 rounded"></div>
                    <span class="w-[100px]">Mfg Date</span>
                    <div class="w-[1px] h-[15px] bg-gray-400 rounded"></div>
                    <span class="w-[100px]">Batch No</span>
                    <div class="w-[1px] h-[15px] bg-gray-400 rounded"></div>
                    <span class="w-[100px]">Loc. Bal Good</span>
                    <div class="w-[1px] h-[15px] bg-gray-400 rounded"></div>
                    <span class="w-[100px]">Item Description</span>
                    <div class="w-[1px] h-[15px] bg-gray-400 rounded"></div>
                    <span class="w-[100px]">Size</span>
                    <div class="w-[1px] h-[15px] bg-gray-400 rounded"></div>
                    <span class="w-[100px]">Age</span>
                    <div class="w-[1px] h-[15px] bg-gray-400 rounded"></div>
                    <span class="w-[100px]">deadScore</span>
                </div>
            </div>
            <div class="flex flex-col gap-3 w-full h-full overflow-y-auto">
                <!-- Before evaluation -->
                {#if data_with_deadScore.length === 0 && previewData.length > 0}
                    {#each previewData as row}
                        <div
                            class="border-b border-black text-black rounded-2xl shadow-sm flex flex-row justify-between p-5"
                        >
                            <span class="w-[100px]">{row["Item Code"]}</span>
                            <span class="w-[100px]">{row["Mfg Date"]}</span>
                            <span class="w-[100px]">{row["Batch No"]}</span>
                            <span class="w-[100px]">{row["Loc. Bal Good"]}</span
                            >
                            <span class="w-[100px]"
                                >{row["Item Description"]}</span
                            >
                            <span class="w-[100px]">{row["Size"]}</span>
                            <span class="w-[100px]">{row["Age"].toFixed(3)}</span>
                        </div>
                    {/each}
                {/if}

                <!-- After evaluation -->
                                 <!-- {#each sortEnabled ? sortedInventory : data_with_deadScore as order} -->
                {#if data_with_deadScore.length > 0}
                    {#each sortEnabled ? sortedInventory : sortMonths ? filterMonthly : data_with_deadScore as order}
                        <div
                            class="border-b border-black text-black rounded-2xl shadow-sm flex flex-row justify-between p-5"
                        >
                            <span class="w-[100px]">{order["Item Code"]}</span>
                            <span class="w-[100px]">{order["Mfg Date"]}</span>
                            <span class="w-[100px]">{order["Batch No"]}</span>
                            <span class="w-[100px]"
                                >{order["Loc. Bal Good"]}</span
                            >
                            <span class="w-[100px]"
                                >{order["Item Description"]}</span
                            >
                            <span class="w-[100px]">{order["Size"]}</span>
                            <span class="w-[100px]">{order["Age"]}</span>
                            <span
                                class="w-[100px] text-xl"
                                style="color:{getRiskColor(order.dead_score)}"
                            >
                                {order.deadScore}
                            </span>
                        </div>
                    {/each}
                {/if}
            </div>
        </div>
    </div>
</div>

<style>
</style>
