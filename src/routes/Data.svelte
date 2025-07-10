<script>
    import { slide } from "svelte/transition";
    export let curr_max_data;

    let xlsxFile = null;
    let cleanedRows = [];
    let cleanedRowsAgg = [];
    let history = ["(insert db upload date, filename here)"];
    let max_date = curr_max_data[0].purDate;
    let input_min_date = "";
    let showLogs = true;
    let showHistory = false;
    let showDateCheck = false;

    console.log("max date object - ", curr_max_data);

    $: showLogs = prog1 === 1 ? true : false;
    $: showDateCheck = xlsxFile !== null ? true : false;

    function handleFileChange(event) {
        xlsxFile = event.target.files[0];
    }

    let prog1 = -1;
    let prog2 = -1;
    let prog3 = -1;
    let prog4 = -1;
    let prog5 = -1;

    $: if (xlsxFile) prog1 = 1;

    let dateCorrect = false;
    $: dateCorrect = input_min_date >= max_date ? true : false;

    $: if (cleanedRows && cleanedRows.length > 0) {
        const maxDate = cleanedRows.reduce(
            (latest, item) => {
                const date = new Date(item.purDate);
                return date < latest ? date : latest;
            },
            new Date(cleanedRows[0]?.purDate || 0),
        ); // safe fallback

        input_min_date = maxDate.toISOString().split("T")[0]; // format for input[type="date"]
    }

    async function clean({ input_xlsx }) {
        try {
            const formData = new FormData();
            formData.append("file", input_xlsx);

            prog2 = 0; //ghumao

            const res = await fetch("http://localhost:8000/input/clean/full", {
                method: "POST",
                body: formData,
            });

            const data = await res.json();
            cleanedRows = data;

            try {
                await cleanAgg({ input_xlsx: xlsxFile });
            } catch (error) {
                console.error("error in aggregating cleaning data: ", error);
            }
        } catch (error) {
            console.error("cleaning error: ", error);
        } finally {
            prog2 = 1; //complete
        }
    }

    async function cleanAgg({ input_xlsx }) {
        try {
            const formData = new FormData();
            formData.append("file", input_xlsx);

            prog5 = 0; //ghumao

            const res = await fetch("http://localhost:8000/input/clean/agg", {
                method: "POST",
                body: formData,
            });

            const data = await res.json();
            cleanedRowsAgg = data;
        } catch (error) {
            console.error("cleaning error: ", error);
        } finally {
            prog5 = 1; //complete
        }
    }

    async function uploadXLSX() {
        if (!xlsxFile) {
            alert("Please upload a file first.");
            return;
        } else {
            prog1 = 1; //complete
        }
        await clean({ input_xlsx: xlsxFile });
    }

    async function insertRows() {
        if (!cleanedRows.length) {
            console.error("No cleaned data available to insert.");
            return;
        }

        try {
            prog3 = 0;
            const res = await fetch("/data", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(cleanedRows),
            });

            const result = await res.json();
            if (result.success) {
                alert("Rows inserted successfully!");
            } else {
                alert("Insert failed: " + result.error.message);
                location.reload();
            }

            insertRowsAgg(cleanedRowsAgg);
        } catch (error) {
            console.error("error: ", error);
        } finally {
            prog3 = 1;
        }
    }

    async function insertRowsAgg() {
        if (!cleanedRows.length) {
            console.error("No cleaned data available to insert.");
            return;
        }

        try {
            prog5 = 0;
            const res = await fetch("/data-agg", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(cleanedRowsAgg),
            });

            const result = await res.json();
            if (result.success) {
                alert("AGG:Rows inserted successfully!");
            } else {
                alert("AGG:Insert failed: " + result.error.message);
                location.reload();
            }
        } catch (error) {
            console.error("error: ", error);
        } finally {
            prog5 = 1;
        }
    }

    $: svgprog1 =
        prog1 === -1
            ? "/chupps-gray.svg"
            : prog1 === 0
              ? "/chupps-black.svg"
              : "/chupps-green.svg";
    $: svgprog2 =
        prog2 === -1
            ? "/chupps-gray.svg"
            : prog2 === 0
              ? "/chupps-black.svg"
              : "/chupps-green.svg";
    $: svgprog3 =
        prog3 === -1
            ? "/chupps-gray.svg"
            : prog3 === 0
              ? "/chupps-black.svg"
              : "/chupps-green.svg";
    $: svgprog4 =
        prog4 === -1
            ? "/chupps-gray.svg"
            : prog4 === 0
              ? "/chupps-black.svg"
              : "/chupps-green.svg";
    $: svgprog5 =
        prog5 === -1
            ? "/chupps-gray.svg"
            : prog5 === 0
              ? "/chupps-black.svg"
              : "/chupps-green.svg";
</script>

<main class="p-5 w-full h-full">
    <div class="grid grid-cols-2 grid-rows-3 gap-5 h-full w-full">
        <div
            class="p-5 border border-gray-500 bg-gray-800 rounded-xl bxsdw col-span-2 w-full h-full flex justify-center items-center"
        >
            <div class="flex flex-col items-center">
                <span class="text-5xl dm-serif-text-regular text-cyan-400"
                    >Data is important!</span
                >
                <span class="text-2xl dm-serif-text-regular text-cyan-800"
                    >Please upload the correct datasets to continue.</span
                >
            </div>
        </div>

        <div
            class="p-5 border border-gray-300 bg-white rounded-xl bxsdw row-span-2 group"
        >
            <div
                class="flex p-5 flex-col items-center justify-center rounded-xl border-3 border-gray-400 h-full w-full group-hover:border-gray-900 duration-300 ease-in-out border-dashed"
            >
                <div
                    class="flex flex-col items-center justify-start w-full h-full"
                >
                    <div
                        class="flex flex-row gap-2 items-center justify-center mb-10 bg-green-500 text-green-700 rounded-full p-2 px-10"
                    >
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            x="0px"
                            y="0px"
                            width="24"
                            height="24"
                            class="fill-current"
                            viewBox="0 0 24 24"
                        >
                            <path
                                d="M 12 2 C 6.4889971 2 2 6.4889971 2 12 C 2 17.511003 6.4889971 22 12 22 C 17.511003 22 22 17.511003 22 12 C 22 6.4889971 17.511003 2 12 2 z M 12 4 C 16.430123 4 20 7.5698774 20 12 C 20 16.430123 16.430123 20 12 20 C 7.5698774 20 4 16.430123 4 12 C 4 7.5698774 7.5698774 4 12 4 z M 11 7 L 11 9 L 13 9 L 13 7 L 11 7 z M 11 11 L 11 17 L 13 17 L 13 11 L 11 11 z"
                            ></path>
                        </svg>

                        <span class=""
                            >Please ensure that you're uploading the correct
                            data, match the dates!</span
                        >
                    </div>

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

                    {#if prog2 !== 1}
                        <button
                            on:click={uploadXLSX}
                            class="flex flex-row items-center justify-center gap-5 transition-all w-full h-full transform duration-500 active:scale-95 hover:scale-102 hover:bg-gradient-to-r hover:from-green-600 hover:text-white hover:to-green-400 scale-100 bg-gray-200 rounded-xl border border-gray-300 shadow-md p-2 px-5"
                            class:-translate-y-full={xlsxFile === null}
                            class:translate-y-0={xlsxFile !== null}
                            class:bg-gradient-to-r={prog2 === 0}
                            class:from-green-600={prog2 === 0}
                            class:to-green-400={prog2 === 0}
                        >
                            {#if prog2 === 0}
                                <div
                                    class="w-12 h-12 border-4 border-white border-dashed rounded-full animate-spin"
                                ></div>
                            {:else}
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    viewBox="0 0 384 512"
                                    width="48"
                                    height="48"
                                    class="fill-current"
                                >
                                    <path
                                        d="M64 0C28.7 0 0 28.7 0 64L0 448c0 35.3 28.7 64 64 64l256 0c35.3 0 64-28.7 64-64l0-288-128 0c-17.7 0-32-14.3-32-32L224 0 64 0zM256 0l0 128 128 0L256 0zM80 64l64 0c8.8 0 16 7.2 16 16s-7.2 16-16 16L80 96c-8.8 0-16-7.2-16-16s7.2-16 16-16zm0 64l64 0c8.8 0 16 7.2 16 16s-7.2 16-16 16l-64 0c-8.8 0-16-7.2-16-16s7.2-16 16-16zm54.2 253.8c-6.1 20.3-24.8 34.2-46 34.2L80 416c-8.8 0-16-7.2-16-16s7.2-16 16-16l8.2 0c7.1 0 13.3-4.6 15.3-11.4l14.9-49.5c3.4-11.3 13.8-19.1 25.6-19.1s22.2 7.7 25.6 19.1l11.6 38.6c7.4-6.2 16.8-9.7 26.8-9.7c15.9 0 30.4 9 37.5 23.2l4.4 8.8 54.1 0c8.8 0 16 7.2 16 16s-7.2 16-16 16l-64 0c-6.1 0-11.6-3.4-14.3-8.8l-8.8-17.7c-1.7-3.4-5.1-5.5-8.8-5.5s-7.2 2.1-8.8 5.5l-8.8 17.7c-2.9 5.9-9.2 9.4-15.7 8.8s-12.1-5.1-13.9-11.3L144 349l-9.8 32.8z"
                                    />
                                </svg>

                                <span class="text-2xl"
                                    >Clean Data & Check Dates</span
                                >
                            {/if}
                        </button>
                    {:else}
                        <button
                            on:click={() => insertRows()}
                            class="flex flex-row items-center justify-center gap-5 transition-all w-full h-full transform duration-500 active:scale-95 hover:scale-102 hover:bg-gradient-to-r hover:from-blue-600 hover:text-white hover:to-gray-900 scale-100 bg-gray-200 rounded-xl border border-gray-300 shadow-md p-2 px-5"
                            disabled={!dateCorrect}
                            class:-translate-y-full={xlsxFile === null}
                            class:translate-y-0={xlsxFile !== null}
                            class:bg-gradient-to-r={prog3 === 0}
                            class:from-blue-600={prog3 === 0}
                            class:to-gray-900={prog3 === 0}
                        >
                            {#if prog3 === 0}
                                <div
                                    class="w-12 h-12 border-4 border-white border-dashed rounded-full animate-spin"
                                ></div>
                            {:else if dateCorrect}
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    viewBox="0 0 448 512"
                                    width="48"
                                    height="48"
                                    class="fill-current"
                                >
                                    <path
                                        d="M448 80l0 48c0 44.2-100.3 80-224 80S0 172.2 0 128L0 80C0 35.8 100.3 0 224 0S448 35.8 448 80zM393.2 214.7c20.8-7.4 39.9-16.9 54.8-28.6L448 288c0 44.2-100.3 80-224 80S0 332.2 0 288L0 186.1c14.9 11.8 34 21.2 54.8 28.6C99.7 230.7 159.5 240 224 240s124.3-9.3 169.2-25.3zM0 346.1c14.9 11.8 34 21.2 54.8 28.6C99.7 390.7 159.5 400 224 400s124.3-9.3 169.2-25.3c20.8-7.4 39.9-16.9 54.8-28.6l0 85.9c0 44.2-100.3 80-224 80S0 476.2 0 432l0-85.9z"
                                    /></svg
                                >
                                <span class="text-2xl">Upload to Server</span>
                            {:else}
                                <span class="text-2xl text-red-500">X</span>
                            {/if}
                        </button>
                    {/if}
                </div>
            </div>
        </div>

        <div
            class="p-5 border border-gray-300 bg-white rounded-xl bxsdw row-span-2 group"
        >
            <div
                class="flex flex-col py-5 rounded-xl border-3 border-gray-400 h-full w-full group-hover:border-gray-900 duration-300 ease-in-out border-dashed"
            >
                <!-- Accordion Item 3: Date Check -->
                <div
                    class="pb-5 border-b border-gray-300 rounded-b-4xl shadow-xl w-full"
                >
                    <button
                        class="flex justify-between items-center px-10 text-2xl font-semibold focus:outline-none w-full"
                        on:click={() => (showDateCheck = !showDateCheck)}
                    >
                        Date Check:
                        <span>{showDateCheck ? "▲" : "▼"}</span>
                    </button>

                    {#if showDateCheck}
                        <div
                            transition:slide
                            class="flex flex-col justify-start w-full px-10 mt-2"
                        >
                            <div
                                class="flex flex-row items-center gap-5 text-gray-900"
                            >
                                <span class="text-lg">•</span>
                                <div class="w-full flex justify-between">
                                    <span
                                        class="text-base tracking-tight block textlight"
                                    >
                                        Min date in your data:
                                    </span>
                                    {#if prog2 === 1}
                                        <span class="text-lg"
                                            >{input_min_date}</span
                                        >
                                    {:else if prog2 === 0}
                                        <div
                                            class="w-4 h-4 border-4 border-green-500 border-dashed rounded-full animate-spin"
                                        ></div>
                                    {:else}
                                        <span class="text-lg text-green-700"
                                            >Click on "Clean Data & Check Dates"</span
                                        >
                                    {/if}
                                </div>
                            </div>
                            <div
                                class="flex flex-row items-center gap-5 text-gray-900"
                            >
                                <span class="text-lg">•</span>
                                <div class="w-full flex justify-between">
                                    <span
                                        class="text-base tracking-tight block textlight"
                                    >
                                        Current max date:
                                    </span>
                                    <span class="text-lg">{max_date}</span>
                                </div>
                            </div>

                            {#if prog2 === 1}
                                {#if dateCorrect}
                                    <span
                                        class="text-center text-2xl text-green-600"
                                        >CHANGES APPROVED!</span
                                    >

                                    <span
                                        class="text-center text-xs text-green-800 underline"
                                        >[ min date in your data &GreaterEqual;
                                        current max date ]
                                    </span>
                                {:else}
                                    <span
                                        class="text-center text-2xl text-red-500"
                                        >Dates don't match, please check data again.</span
                                    >
                                    <span
                                        class="text-center text-sm text-red-800 underline"
                                        >if, min date in your data &LessSlantEqual;
                                        current max date &rArr; no need to upload data!
                                    </span>
                                {/if}
                            {:else}
                                <span class="text-center text-2xl text-gray-500"
                                    >---</span
                                >
                            {/if}
                        </div>
                    {/if}
                </div>

                <!-- Accordion Item 1: Logs -->
                <div
                    transition:slide
                    class="pb-5 border-b border-gray-300 rounded-b-4xl shadow-xl w-full overflow-hidden"
                >
                    <button
                        class="flex justify-between items-center mt-6 px-10 text-2xl font-semibold focus:outline-none w-full"
                        on:click={() => (showLogs = !showLogs)}
                    >
                        Logs:
                        <span>{showLogs ? "▲" : "▼"}</span>
                    </button>

                    {#if showLogs}
                        <div
                            transition:slide
                            class="z-0 relative mt-4 transition-all duration-300 ease-in-out"
                        >
                            {#if xlsxFile === null}
                                <div
                                    class="absolute flex items-center px-10 rounded-md justify-end w-full h-40 bg-gradient-to-t from-stone-300 to-white opacity-80"
                                >
                                    <span class="text-green-800 text-2xl">
                                        Upload a file first!
                                    </span>
                                </div>
                            {/if}

                            <div
                                class="flex flex-row items-center gap-2 mt-2 mb-1 px-10"
                            >
                                <img
                                    src={svgprog1}
                                    alt="chupps-gray"
                                    class="w-4 h-4"
                                    class:animate-spin={prog1 === 0}
                                />
                                <span
                                    class="text-gray-500"
                                    class:text-black={prog1 === 0}
                                    class:text-green-500={prog1 === 1}
                                >
                                    Checking file validity...
                                </span>
                            </div>

                            <div
                                class="flex flex-row items-center gap-2 my-1 px-10"
                            >
                                <img
                                    src={svgprog2}
                                    alt="chupps-gray"
                                    class="w-4 h-4"
                                    class:animate-spin={prog2 === 0}
                                />
                                <span
                                    class="text-gray-500"
                                    class:text-black={prog2 === 0}
                                    class:text-green-500={prog2 === 1}
                                >
                                    Cleaning the input file...
                                </span>
                            </div>

                            <div
                                class="flex flex-row items-center gap-2 my-1 px-10"
                            >
                                <img
                                    src={svgprog5}
                                    alt="chupps-gray"
                                    class="w-4 h-4"
                                    class:animate-spin={prog5 === 0}
                                />
                                <span
                                    class="text-gray-500"
                                    class:text-black={prog5 === 0}
                                    class:text-green-500={prog5 === 1}
                                >
                                    Aggregating data day-wise...
                                </span>
                            </div>

                            <div
                                class="flex flex-row items-center gap-2 my-1 px-10"
                            >
                                <img
                                    src={svgprog3}
                                    alt="chupps-gray"
                                    class="w-4 h-4"
                                    class:animate-spin={prog3 === 0}
                                />
                                <span
                                    class="text-gray-500"
                                    class:text-black={prog3 === 0}
                                    class:text-green-500={prog3 === 1}
                                >
                                    Uploading the latest database to server...
                                </span>
                            </div>

                            <div
                                class="flex flex-row items-center gap-2 my-1 px-10"
                            >
                                <img
                                    src={svgprog4}
                                    alt="chupps-gray"
                                    class="w-4 h-4"
                                    class:animate-spin={prog4 === 0}
                                />
                                <span
                                    class="text-gray-500"
                                    class:text-black={prog4 === 0}
                                    class:text-green-500={prog4 === 1}
                                >
                                    Fetching appropriate data from the server...
                                </span>
                            </div>
                        </div>
                    {/if}
                </div>

                <!-- Accordion Item 2: History -->
                <div
                    class="pb-5 border-b border-gray-300 rounded-b-4xl shadow-xl w-full"
                >
                    <button
                        class="flex justify-between items-center px-10 mt-6 text-2xl font-semibold focus:outline-none w-full"
                        on:click={() => (showHistory = !showHistory)}
                    >
                        History:
                        <span>{showHistory ? "▲" : "▼"}</span>
                    </button>

                    {#if showHistory}
                        <div
                            transition:slide
                            class="flex flex-col justify-start w-full px-10 mt-2"
                        >
                            {#each history as c}
                                <div
                                    class="flex flex-row items-center gap-5 text-gray-900"
                                >
                                    <span class="text-lg">•</span>
                                    <span
                                        class="text-base tracking-tight block textlight"
                                    >
                                        {c}
                                    </span>
                                </div>
                            {/each}
                        </div>
                    {/if}
                </div>
            </div>
        </div>
    </div>
</main>
