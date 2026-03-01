<script lang="ts">
	import '../app.css';
	let { children } = $props();
</script>

<div class="h-screen w-screen overflow-x-hidden overflow-y-auto relative antialiased" data-theme="preset">
	<!-- Background Abstract Elements (Glassmorphism foundation) -->
	<div class="fixed inset-0 z-[-1] overflow-hidden pointer-events-none">
		<!-- Glowing Orbs -->
		<div class="absolute top-[-10%] left-[-10%] w-[40vw] h-[40vw] rounded-full bg-primary-500/20 blur-[120px] animate-float"></div>
		<div class="absolute bottom-[-10%] right-[-10%] w-[50vw] h-[50vw] rounded-full bg-secondary-500/20 blur-[120px] animate-float" style="animation-delay: -3s;"></div>
		
		<!-- Optional Particles Layer can go here later -->
	</div>

	<!-- Main Content -->
	<main class="container mx-auto p-4 md:p-8 min-h-screen flex flex-col items-center z-10">
		<!-- Header -->
		<header class="w-full max-w-4xl flex justify-between items-center mb-8 glass px-6 py-4 rounded-full">
			<div class="flex items-center gap-3">
				<span class="text-3xl">🌱</span>
				<h1 class="text-2xl font-bold bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent">
					Upcycle AI
				</h1>
			</div>
			
			<nav class="flex gap-4">
				<a href="/" class="text-sm font-medium hover:text-primary-500 transition-colors">Analyzer</a>
				<a href="/history" class="text-sm font-medium hover:text-primary-500 transition-colors">History</a>
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
