<script>
    export let onSelect;
</script>

<aside
    class="w-32 bg-gray-900 shadow-2xl py-4 px-0 border-r absolute left-0 top-0 h-full items-stretch"
>
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
            on:click={()=>onSelect('home')}
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
            on:click={()=>onSelect('data')}
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
            class="flex flex-col gap-1 items-center mb-5 hover:bg-gray-700 py-5 w-full"
            on:click={()=>onSelect('forecast')}
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
    </ul>
</aside>
