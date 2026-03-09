<script lang="ts">
	import "../app.css";
	let { children } = $props();
</script>

<div
	class="h-screen w-screen overflow-x-hidden overflow-y-auto relative antialiased"
	data-theme="preset"
>
	<!-- Removed glowing orbs for Neo-Brutalism design -->

	<!-- Main Content -->
	<main
		class="container mx-auto p-4 md:p-8 min-h-screen flex flex-col items-center z-10"
	>
		<!-- Header -->
		<header
			class="w-full max-w-4xl flex justify-between items-center mb-8 glass px-6 py-4 rounded-none"
		>
			<div class="flex items-center gap-3">
				<span class="text-3xl">🌱</span>
				<h1
					class="text-2xl font-black uppercase tracking-tighter text-surface-950 px-2 bg-primary-50"
				>
					Upcycle AI
				</h1>
			</div>

			<nav class="flex gap-4">
				<a
					href="/"
					class="text-sm font-medium hover:text-primary-500 transition-colors"
					>Analyzer</a
				>
				<a
					href="/explore"
					class="text-sm font-medium hover:text-primary-500 transition-colors"
					>Explore</a
				>
				<a
					href="/history"
					class="text-sm font-medium hover:text-primary-500 transition-colors"
					>History</a
				>
			</nav>
		</header>

		<!-- Page Content -->
		<div class="w-full max-w-4xl flex-grow">
			{@render children()}
		</div>

		<!-- Footer -->
		<footer class="mt-12 text-center text-sm opacity-50 py-4">
			Powered by Moondream & Qwen 2.5
		</footer>
	</main>
</div>
