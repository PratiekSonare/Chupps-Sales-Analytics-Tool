<script>
    import { activeView } from "../lib/stores/view";
    import "../app.css";
    import ChuppsButton from "./ChuppsButton.svelte";

    const point = [
        {
            title: "Data",
            content: "Edit and update analytics with the latest sales data.",
            svg: `<svg
                class="mx-auto w-8 h-8 text-gray-800 dark:text-white"
                aria-hidden="true"
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                fill="none"
                viewBox="0 0 24 24"
            >
                <path
                    stroke="currentColor"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M4 4v15a1 1 0 0 0 1 1h15M8 16l2.5-5.5 3 3L17.273 7 20 9.667"
                />
            </svg>`,
        },
        {
            title: "Forecast",
            content: "Get advanced AI-assisted forecasts on latest sales data.",
            svg: `<svg
                class="mx-auto w-8 h-8 text-gray-800 dark:text-white"
                aria-hidden="true"
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                fill="none"
                viewBox="0 0 24 24"
            >
                <path
                    stroke="currentColor"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M10 6.025A7.5 7.5 0 1 0 17.975 14H10V6.025Z"
                />
                <path
                    stroke="currentColor"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M13.5 3c-.169 0-.334.014-.5.025V11h7.975c.011-.166.025-.331.025-.5A7.5 7.5 0 0 0 13.5 3Z"
                />
            </svg>`,
        },
        {
            title: "Item & Shade",
            content:
                "Explore item and shade-wise analysis of entire catalogue.",
            svg: `<svg
                class="mx-auto w-8 h-8 text-white"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 640 512"
            >
                <path
                    fill="currentColor"
                    stroke="currentColor"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M416 0C352.3 0 256 32 256 32l0 128c48 0 76 16 104 32s56 32 104 32c56.4 0 176-16 176-96S512 0 416 0zM128 96c0 35.3 28.7 64 64 64l32 0 0-128-32 0c-35.3 0-64 28.7-64 64zM288 512c96 0 224-48 224-128s-119.6-96-176-96c-48 0-76 16-104 32s-56 32-104 32l0 128s96.3 32 160 32zM0 416c0 35.3 28.7 64 64 64l32 0 0-128-32 0c-35.3 0-64 28.7-64 64z"
                />
            </svg>`,
        },
        {
            title: "Regional",
            content:
                "Look at distribution of sales in India for any SKU of the catalogue.",
            svg: `<img
                src="/1856790.webp"
                alt="indiamap"
                class="invert w-[48px] h-[48px]"
            />`,
        },
        {
            title: "Risk Score",
            content:
                "Find if a particular transaction can get cancelled or not!",
            svg: `<svg
                class="mx-auto w-8 h-8 text-white invert"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 512 512"
                width="24"
                height="24"
            >
                <path
                    d="M313.4 32.9c26 5.2 42.9 30.5 37.7 56.5l-2.3 11.4c-5.3 26.7-15.1 52.1-28.8 75.2l144 0c26.5 0 48 21.5 48 48c0 18.5-10.5 34.6-25.9 42.6C497 275.4 504 288.9 504 304c0 23.4-16.8 42.9-38.9 47.1c4.4 7.3 6.9 15.8 6.9 24.9c0 21.3-13.9 39.4-33.1 45.6c.7 3.3 1.1 6.8 1.1 10.4c0 26.5-21.5 48-48 48l-97.5 0c-19 0-37.5-5.6-53.3-16.1l-38.5-25.7C176 420.4 160 390.4 160 358.3l0-38.3 0-48 0-24.9c0-29.2 13.3-56.7 36-75l7.4-5.9c26.5-21.2 44.6-51 51.2-84.2l2.3-11.4c5.2-26 30.5-42.9 56.5-37.7zM32 192l64 0c17.7 0 32 14.3 32 32l0 224c0 17.7-14.3 32-32 32l-64 0c-17.7 0-32-14.3-32-32L0 224c0-17.7 14.3-32 32-32z"
                />
            </svg>`,
        },
        {
            title: "RTO Orders",
            content:
                "Check and verify RTO orders with the highest risk scores!",
            svg: `<img
                src="/shopify-black.svg"
                alt="indiamap"
                class="invert w-[48px] h-[48px]"
            />`,
        },
        {
            title: "Dead Stock",
            content:
                "Push dead stock to flash sales and clear out inventory instantly!",
            svg: `<img
                src="/dead-stock.svg"
                alt="indiamap"
                class="invert w-[48px] h-[48px]"
            />`,
        },
    ];

    let imgSeen = false;
</script>

<main class="z-100 w-screen h-screen">
    <div class="flex flex-col items-center gap-0">
        <button class="transition active:scale-95 scale-100 duration-200 ease-in-out w-[30%] my-20">
            <!-- <img src="/chupps-ai.svg" alt="" class="w-[30%] my-20" /> -->
            <img src="/chupps-ai.svg" alt="" class="w-full" />
        </button>

        <div
            class="text1 grid grid-cols-5 grid-rows-2 gap-5 w-full h-full px-10"
        >
            {#each point as p}
                <button
                    on:click={() => activeView.set(p.title)}
                    class="overflow-hidden bg-gray-900 hover:bg-gradient-to-b hover:from-gray-900 hover:to-gray-600 shadow-xl rounded-xl w-full h-full flex flex-col items-center justify-center border border-gray-700 group active:scale-90 scale-100 transition-all transform duration-500 ease-in-out"
                >
                    <div
                        class="flex-11/12 flex flex-col items-center justify-center mt-5 px-5 scale-105 group-hover:scale-95"
                    >
                        {@html p.svg}
                        <h1 class="text-white text1 mb-3">{p.title}</h1>

                        <span class="text-gray-300 text2 text-center"
                            >{p.content}</span
                        >
                    </div>

                    <div
                        class="flex-1/12 flex flex-row items-center justify-between px-5 py-2 bg-transparent translate-y-[150px] group-hover:translate-y-0 transition-all duration-100 ease-in-out transform text-white w-full h-full"
                    >
                        <span>Explore now!</span>
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 448 512"
                            width="20"
                            height="20"
                            class="fill-current"
                        >
                            <path
                                d="M438.6 278.6c12.5-12.5 12.5-32.8 0-45.3l-160-160c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3L338.8 224 32 224c-17.7 0-32 14.3-32 32s14.3 32 32 32l306.7 0L233.4 393.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0l160-160z"
                            />
                        </svg>
                    </div>
                </button>
            {/each}

            <div
                class="py-5 px-10 bg-gradient-to-t from-gray-300 to-white text-white col-span-2 rounded-xl w-full h-full flex flex-col version-sdw border border-gray-900"
            >
                <h1 class="mb-5 text1 text-gray-900">Versions and Bugs</h1>

                <div
                    class="flex flex-col gap-2 justify-center w-full mb-0 text-xs"
                >
                    <ul class="list-disc text-gray-800">
                        <li class="text2">
                            "Forecast" complete with Deepseek V03 0324
                            integration for meta-data analysis <span
                                class="text-red-600">(16-06)</span
                            >
                        </li>
                        <li class="text2">
                            "Item & Shade" complete with Google Gemma 3
                            integration for shade analysis of an item <span
                                class="text-red-600">(24-06)</span
                            >
                        </li>
                        <li class="text2">
                            "Regional" complete with map integration integration
                            for qualitative analysis of item sales <span
                                class="text-red-600">(24-06)</span
                            >
                        </li>
                        <li class="text2">
                            "Risk Score" complete with backend fastapi NN
                            endpoint and train_data filtering <span
                                class="text-red-600">(03-07)</span
                            >
                        </li>
                        <li class="text2">
                            "Data" page ongoing, complete supabase connection
                            with backend fastapi NN endpoint and train_data
                            filtering <span class="text-red-600">(03-07)</span>
                        </li>
                        <li class="text2">
                            Dynamic data upgradation completed! "Data" page
                            fully accessible. Only need to fix reloading of the
                            tool to update with latest dataset! <span
                                class="text-red-600">(10-07)</span
                            >
                        </li>
                    </ul>
                </div>
            </div>

            <div
                class="relative overflow-hidden flex flex-col rounded-xl pratiek-sdw group bg-transparent pt-0 border border-gray-900"
            >
                {#if imgSeen}
                    <span class="absolute bottom-14 right-4 text-xl text-blue-500"
                        >+91-9326014954</span
                    >
                {/if}
                
                <div
                    class="flex flex-col flex-11/12 items-center justify-center group-hover:scale-110 duration-100 ease-in-out"
                >
                    <ChuppsButton />
                    <span class="text-sm mt-5">Need help?</span>
                    <span class="text-black text-xl">Facing trouble?</span>
                </div>

                <div
                    class="flex-1/12 flex flex-row items-center justify-between px-5 py-2 bg-transparent translate-y-[150px] group-hover:translate-y-0 transition-all duration-100 ease-in-out transform text-white w-full h-full"
                >
                    <span class="text-black">Contact the intern!</span>
                    <div
                        class="flex flex-row gap-1 items-center justify-center"
                    >
                        <a href="https://www.linkedin.com/in/pratiek-sonare/"
                            ><img
                                src="/linkedin.svg"
                                class="w-10 h-10 hover:scale-120"
                                alt="linkedin"
                            /></a
                        >
                        <button on:click={() => (imgSeen = !imgSeen)}>
                            <img
                                src="/call.svg"
                                class="w-6 h-6 hover:scale-120"
                                alt="linkedin"
                            />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</main>

<style>
    @reference "tailwindcss";

    .pratiek-sdw {
        box-shadow:
            rgba(6, 24, 44, 0.4) 0px 0px 0px 2px,
            rgba(6, 24, 44, 0.65) 0px 4px 6px -1px,
            rgba(255, 255, 255, 0.08) 0px 1px 0px inset;
    }

    .version-sdw {
        box-shadow: rgba(50, 50, 93, 0.25) 0px 30px 60px -12px inset, rgba(0, 0, 0, 0.3) 0px 18px 36px -18px inset;
    }
</style>
