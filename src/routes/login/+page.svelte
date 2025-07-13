<script lang="ts">
	import { supabase } from "$lib/supabaseClient";
	import { goto } from "$app/navigation";
	import ChuppsButton from "../ChuppsButton.svelte";

	let email = "";
	let password = "";
	let error = "";
	let loading = false;

	const handleLogin = async () => {
		loading = true;
		error = ""; // clear previous errors if any

		try {
			const { data, error: authError } =
				await supabase.auth.signInWithPassword({
					email,
					password,
				});

			if (authError) {
				error = authError.message;
			} else {
				goto("/");
			}
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	};
</script>

<div class="w-screen h-screen flex flex-col items-center justify-center p-44">
	<!-- <h1>Login</h1>
	<input bind:value={email} placeholder="Email" type="email" />
	<input bind:value={password} placeholder="Password" type="password" />
	<button on:click={handleLogin}>Login</button>

	{#if error}
		<p style="color: red;">{error}</p>
	{/if} -->
	<div class="grid grid-cols-2 gap-10 w-full h-full">
		<!-- logo -->
		<img
			class="scale-75 self-center bounce-custom"
			alt="chupps-analy logo"
			src="/chupps_header.svg"
		/>

		<div class="bg-white rounded-xl bxsdw w-full h-full p-5">
			<div
				class="border-4 border-gray-900 rounded-xl h-full w-full flex flex-col items-center py-5"
			>
				<div class="flex flex-row gap-3  mb-5">
					<span class="mt-5 text-center text-3xl text-black"
						>Welcome to the world of
					</span>
					<ChuppsButton />
				</div>
				<span class="text-xl underline">Please login to continue.</span>

				<div class="w-full mt-10">
					<span class="p-5 text-2xl">Email</span>
				</div>
				<input
					bind:value={email}
					placeholder="Enter your email here..."
					type="email"
					class="w-full p-5 bg-gray-900 text-white text2 tracking-widest border-y-4 border-gray-900"
				/>

				<div class="w-full mt-5">
					<span class="p-5 text-2xl">Password</span>
				</div>
				<input
					bind:value={password}
					placeholder="Enter your password here..."
					type="password"
					class="w-full p-5 bg-gray-900 text-white text2 border-y-4 border-gray-900"
				/>

				<button
					class="py-2 mt-10 w-full tracking-widest hover:bg-gradient-to-r hover:from-green-500 hover:to-green-300 transition transform active:scale-95 scale-100 border border-green-200 bg-amber-500 text-3xl duration-300 ease-in-out"
					on:click={handleLogin}
				>
					{#if !loading}
						<span>LOGIN</span>
					{:else}
						<div
							class="mx-auto w-10 h-10 border-4 border-white border-dashed rounded-full animate-spin"
						></div>
					{/if}
				</button>

				{#if error}
					<p
						style="color: red;"
						class="mt-5 p-2 px-5 bg-red-200 rounded-xl"
					>
						{error}
					</p>
				{/if}

				<div></div>
			</div>
		</div>
	</div>
</div>

<style>
	@reference "tailwindcss";
	@keyframes chupps-bounce {
		0%,
		100% {
			transform: translateY(0);
			animation-timing-function: ease-in-out;
		}
		50% {
			transform: translateY(-10%);
			animation-timing-function: ease-in-out;
		}
	}

	.bounce-custom {
		animation: chupps-bounce 1.8s infinite;
	}
</style>
