<script>
    import "../app.css";
</script>

<main class="z-100 w-screen h-screen px-10">
    <div class="flex flex-col items-center gap-0">
        <img src="/chupps_header.svg" alt="" class="w-[30%]" />

        <div class="rounded-xl h-1 w-3/4 mgin mb-10"></div>

        <div class="text1 grid grid-cols-2 grid-rows-2 gap-10 w-full h-full">
            <div
                class="p-5 bg-white shadow-xl rounded-xl w-full h-full flex flex-col border border-gray-300"
            >
                <h1>Why to use?</h1>
                <ul class="text2 list-disc px-5 mt-5 text-base">
                    <li>
                        Get quick insights on latest sales data with year-long
                        forecasting for better planning.
                    </li>
                    <li>
                        Filter sales data item-wise and shade-wise demand to get
                        SKU based forecasting
                    </li>
                    <li>
                        Get advanced <span class="text2b"
                            >AI recommendations</span
                        > on a specific item/shade!
                    </li>
                </ul>
            </div>
            <div
                class="p-5 bg-white shadow-xl rounded-xl w-full h-full flex flex-col border border-gray-300"
            >
                <h1>How to use?</h1>
                <ul class="text2 list-decimal px-5 mt-5 text-base">
                    <li>Enter shade/item</li>
                    <li>
                        Filter sales data item-wise and shade-wise demand to get
                        SKU based forecasting
                    </li>
                    <li>
                        Get advanced <span class="text2b"
                            >AI recommendations</span
                        > on a specific item/shade!
                    </li>
                </ul>
            </div>

            <div
                class="p-5 bg-white shadow-xl col-span-2 rounded-xl w-full h-full flex flex-col border border-gray-300"
            >
                <h1>Versions and Bugs</h1>
            </div>
        </div>
    </div>
</main>

<style>
    .mgin {
        background: #020024;
        background: linear-gradient(
            90deg,
            rgba(2, 0, 36, 1) 0%,
            rgba(9, 9, 121, 1) 35%,
            rgba(0, 212, 255, 0.82) 100%
        );
    }
</style>
