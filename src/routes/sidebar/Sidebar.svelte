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
            <img
                src="/1856790.webp"
                alt="indiamap"
                class="invert w-[48px] h-[48px]"
            />

            <li><span class="text-blue-200">Regional</span></li>
        </button>

        <button
            class="flex flex-col gap-1 items-center mb-0 hover:bg-gray-700 py-5 w-full"
            class:bg-gray-600={activeView == "risk-score"}
            on:click={() => onSelect("risk-score")}
        >
            <svg
                class="mx-auto w-8 h-8 text-white invert" 
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 512 512"
                width="24"
                height="24"
            >
                <path
                    d="M313.4 32.9c26 5.2 42.9 30.5 37.7 56.5l-2.3 11.4c-5.3 26.7-15.1 52.1-28.8 75.2l144 0c26.5 0 48 21.5 48 48c0 18.5-10.5 34.6-25.9 42.6C497 275.4 504 288.9 504 304c0 23.4-16.8 42.9-38.9 47.1c4.4 7.3 6.9 15.8 6.9 24.9c0 21.3-13.9 39.4-33.1 45.6c.7 3.3 1.1 6.8 1.1 10.4c0 26.5-21.5 48-48 48l-97.5 0c-19 0-37.5-5.6-53.3-16.1l-38.5-25.7C176 420.4 160 390.4 160 358.3l0-38.3 0-48 0-24.9c0-29.2 13.3-56.7 36-75l7.4-5.9c26.5-21.2 44.6-51 51.2-84.2l2.3-11.4c5.2-26 30.5-42.9 56.5-37.7zM32 192l64 0c17.7 0 32 14.3 32 32l0 224c0 17.7-14.3 32-32 32l-64 0c-17.7 0-32-14.3-32-32L0 224c0-17.7 14.3-32 32-32z"
                />
            </svg>
            <li><span class="text-blue-200">Return Risk Score</span></li>
        </button>
    </ul>
</aside>
