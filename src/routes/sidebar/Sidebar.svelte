<script>
    export let onSelect;
    export let activeView;
</script>

<aside class="w-full h-full bg-gray-900 shadow-2xl py-4 px-0 border-r">
    <ul class="space-y-2">
        <li>
            <img
                src="/chupps-white.svg"
                alt="chuppslogo"
                class="w-10 h-10 mx-auto mt-5 mb-10"
            />
        </li>

        <div class="w-10 h-[2px] bg-gray-400 mx-auto"></div>

        <button
            class="flex flex-col gap-1 items-center mb-0 hover:bg-gray-700 py-5 w-full"
            class:bg-gray-600={activeView == "home"}
            on:click={() => onSelect("home")}
        >
            <svg
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
                    d="m4 12 8-8 8 8M6 10.5V19a1 1 0 0 0 1 1h3v-3a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v3h3a1 1 0 0 0 1-1v-8.5"
                />
            </svg>

            <li><span class="text-blue-200 text1">Home</span></li>
        </button>

        <button
            class="flex flex-col gap-1 items-center mb-0 hover:bg-gray-700 py-5 w-full"
            class:bg-gray-600={activeView == "data"}
            on:click={() => onSelect("data")}
        >
            <svg
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
            </svg>

            <li><span class="text-blue-200">Data</span></li>
        </button>

        <button
            class="flex flex-col gap-1 items-center mb-0 hover:bg-gray-700 py-5 w-full"
            class:bg-gray-600={activeView == "forecast"}
            on:click={() => onSelect("forecast")}
        >
            <svg
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
            </svg>

            <li><span class="text-blue-200">Forecast</span></li>
        </button>

        <button
            class="flex flex-col gap-1 items-center mb-0 hover:bg-gray-700 py-5 w-full"
            class:bg-gray-600={activeView == "item-shade"}
            on:click={() => onSelect("item-shade")}
        >
            <svg
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
            </svg>

            <li><span class="text-blue-200">Item & Shade</span></li>
        </button>

        <button
            class="flex flex-col gap-1 items-center mb-0 hover:bg-gray-700 py-5 w-full"
            class:bg-gray-600={activeView == "regional"}
            on:click={() => onSelect("regional")}
        >
            <img src="/1856790.webp" alt="indiamap" class="invert w-[48px] h-[48px]">

            <li><span class="text-blue-200">Regional</span></li>
        </button>
    </ul>
</aside>
