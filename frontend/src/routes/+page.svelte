<script lang="ts">
    import { slide, fade } from "svelte/transition";
    import { marked } from "marked";

    // App State
    type Step = "upload" | "refining" | "generating" | "result";
    let currentStep: Step = $state("upload");

    // Data
    let imageFile: File | null = $state(null);
    let _imagePreviewUrl: string | null = $state(null);
    let visionItems: { name: string; selected: boolean }[] = $state([]);
    let toolsEquipment: string = $state("");

    let generatedProject: string = $state("");
    let errorMsg: string = $state("");

    // API Base
    const API_BASE = "http://localhost:8000/api";

    function handleFile(e: Event) {
        const target = e.target as HTMLInputElement;
        if (target.files && target.files.length > 0) {
            imageFile = target.files[0];
            _imagePreviewUrl = URL.createObjectURL(imageFile);
        }
    }

    async function runVision() {
        if (!imageFile) return;
        currentStep = "refining"; // Instantly show skeleton/spinner state
        errorMsg = "";

        try {
            const formData = new FormData();
            formData.append("file", imageFile);

            const res = await fetch(`${API_BASE}/vision`, {
                method: "POST",
                body: formData,
            });

            if (!res.ok) throw new Error("Vision API Failed");

            const data = await res.json();
            // Map to objects with 'selected' boolean
            visionItems = data.items.map((it: string) => ({
                name: it,
                selected: true,
            }));

            // If empty, add a default fallback
            if (visionItems.length === 0) {
                visionItems.push({ name: "Unknown Object", selected: true });
            }
        } catch (err: any) {
            errorMsg = err.message || "Failed to analyze image";
            currentStep = "upload"; // Revert on fail
        }
    }

    async function runGeneration() {
        const selected = visionItems
            .filter((v) => v.selected)
            .map((v) => v.name);
        if (selected.length === 0) {
            errorMsg = "Please select at least one item.";
            return;
        }

        currentStep = "generating";
        errorMsg = "";

        try {
            const res = await fetch(`${API_BASE}/generate`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    selected_items: selected,
                    equipment: toolsEquipment,
                    // pass image_path if we want to save it to DB, but omitting for now
                }),
            });

            if (!res.ok) throw new Error("Generation API Failed");

            const data = await res.json();
            generatedProject = data.project_markdown;

            currentStep = "result";
        } catch (err: any) {
            errorMsg = err.message || "Failed to brainstorm project";
            currentStep = "refining"; // Revert to refine step
        }
    }

    function reset() {
        imageFile = null;
        _imagePreviewUrl = null;
        visionItems = [];
        toolsEquipment = "";
        generatedProject = "";
        errorMsg = "";
        currentStep = "upload";
    }
</script>

<svelte:head>
    <title>New Scan - Upcycle AI</title>
</svelte:head>

<div class="w-full flex flex-col gap-8">
    {#if errorMsg}
        <div
            transition:slide
            class="bg-red-500/20 border border-red-500/50 text-red-200 p-4 rounded-xl backdrop-blur-md"
        >
            {errorMsg}
        </div>
    {/if}

    <!-- STEP 1: UPLOAD -->
    {#if currentStep === "upload"}
        <div
            in:fade={{ duration: 300, delay: 300 }}
            out:fade={{ duration: 200 }}
            class="glass-card flex flex-col items-center justify-center p-12 text-center min-h-[50vh]"
        >
            <span class="text-6xl mb-6">♻️</span>
            <h2 class="text-3xl font-bold mb-2">Scan Your Waste</h2>
            <p
                class="text-surface-950/60 dark:text-surface-50/60 mb-8 max-w-md"
            >
                Upload a picture of items you want to throw away, and our vision
                engine will identify them for upcycling.
            </p>

            <label class="relative cursor-pointer group">
                <input
                    type="file"
                    accept="image/jpeg, image/png, image/webp"
                    class="fixed -top-[1000px]"
                    onchange={handleFile}
                />
                <div
                    class="px-8 py-4 bg-primary-500 hover:bg-primary-600 text-white rounded-full font-bold shadow-lg shadow-primary-500/30 transition-all group-hover:scale-105 flex items-center gap-3"
                >
                    <span class="text-xl">📸</span> Upload Image
                </div>
            </label>

            {#if _imagePreviewUrl}
                <div
                    class="mt-8 flex flex-col items-center gap-4"
                    transition:slide
                >
                    <img
                        src={_imagePreviewUrl}
                        alt="Preview"
                        class="w-48 h-48 object-cover rounded-xl shadow-lg border-2 border-primary-500/30"
                    />
                    <button
                        onclick={runVision}
                        class="px-6 py-2 bg-secondary-500 hover:bg-secondary-600 text-white rounded-full font-bold transition-transform hover:-translate-y-1"
                    >
                        ✨ Analyze Image
                    </button>
                </div>
            {/if}
        </div>
    {/if}

    <!-- STEP 2: REFINE -->
    {#if currentStep === "refining"}
        <div
            in:fade={{ duration: 300, delay: 200 }}
            out:fade={{ duration: 200 }}
            class="grid md:grid-cols-[1fr_2fr] gap-8"
        >
            <!-- Image Context -->
            <div class="glass-card flex flex-col gap-4">
                <h3 class="text-xl font-bold opacity-80">Reference</h3>
                {#if _imagePreviewUrl}
                    <img
                        src={_imagePreviewUrl}
                        alt="Preview"
                        class="w-full aspect-square object-cover rounded-xl"
                    />
                {/if}
            </div>

            <!-- Refinement Form -->
            <div class="glass-card flex flex-col gap-8">
                <div>
                    <h2 class="text-2xl font-bold mb-2 flex items-center gap-3">
                        <span
                            class="bg-primary-500 rounded-full w-8 h-8 flex items-center justify-center text-sm text-white"
                            >1</span
                        >
                        Select Items
                    </h2>
                    <p class="opacity-70 mb-6 font-medium text-sm">
                        Our vision model detected these items. Uncheck the
                        background noise.
                    </p>

                    {#if visionItems.length === 0}
                        <!-- Loading Skeleton -->
                        <div class="flex flex-col gap-3">
                            <div
                                class="w-full h-12 bg-surface-500/20 animate-pulse rounded-lg"
                            ></div>
                            <div
                                class="w-3/4 h-12 bg-surface-500/20 animate-pulse rounded-lg"
                            ></div>
                            <div
                                class="w-5/6 h-12 bg-surface-500/20 animate-pulse rounded-lg"
                            ></div>
                        </div>
                    {:else}
                        <div class="flex flex-col gap-3" transition:slide>
                            {#each visionItems as item}
                                <label
                                    class="flex items-center gap-4 p-4 rounded-xl bg-surface-500/5 hover:bg-surface-500/10 border border-surface-500/10 cursor-pointer transition-colors"
                                >
                                    <!-- Custom minimalist checkbox logic -->
                                    <input
                                        type="checkbox"
                                        bind:checked={item.selected}
                                        class="w-6 h-6 rounded-md accent-primary-500"
                                    />
                                    <span class="text-lg font-medium capitalize"
                                        >{item.name}</span
                                    >
                                </label>
                            {/each}
                        </div>
                    {/if}
                </div>

                <hr class="border-surface-500/20" />

                <div>
                    <h2 class="text-2xl font-bold mb-2 flex items-center gap-3">
                        <span
                            class="bg-secondary-500 rounded-full w-8 h-8 flex items-center justify-center text-sm text-white"
                            >2</span
                        >
                        Available Tools
                    </h2>
                    <p class="opacity-70 mb-4 font-medium text-sm">
                        What tools or extra materials do you have? (Leave blank
                        for basics)
                    </p>

                    <input
                        type="text"
                        bind:value={toolsEquipment}
                        placeholder="e.g. Hot glue gun, exacto knife, paint..."
                        class="w-full px-5 py-4 rounded-xl bg-surface-500/10 border border-surface-500/20 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500 transition-all font-medium"
                        disabled={visionItems.length === 0}
                    />
                </div>

                <div class="flex justify-end gap-4 mt-4">
                    <button
                        onclick={() => (currentStep = "upload")}
                        class="px-6 py-3 rounded-full opacity-70 hover:opacity-100 transition-opacity font-medium"
                    >
                        Back
                    </button>
                    <button
                        onclick={runGeneration}
                        disabled={visionItems.length === 0}
                        class="px-8 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-full font-bold shadow-lg transition-transform hover:-translate-y-1 disabled:opacity-50 disabled:hover:translate-y-0"
                    >
                        ✨ Brainstorm Projects
                    </button>
                </div>
            </div>
        </div>
    {/if}

    <!-- STEP 3: GENERATING -->
    {#if currentStep === "generating"}
        <div
            in:fade
            out:fade
            class="glass-card flex flex-col items-center justify-center p-16 min-h-[50vh] text-center"
        >
            <div class="relative w-24 h-24 mb-8">
                <div
                    class="absolute inset-0 border-4 border-surface-500/20 rounded-full"
                ></div>
                <div
                    class="absolute inset-0 border-4 border-t-primary-500 border-r-secondary-500 border-b-transparent border-l-transparent rounded-full animate-spin"
                ></div>
            </div>

            <h2
                class="text-3xl font-bold mb-4 bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent animate-pulse"
            >
                Consulting Knowledge Base...
            </h2>
            <p class="opacity-70 max-w-sm">
                Our custom RAG database is searching through 767 curated
                projects to find the perfect match for your tools.
            </p>
        </div>
    {/if}

    <!-- STEP 4: RESULT -->
    {#if currentStep === "result"}
        <div
            in:fade={{ duration: 400 }}
            class="glass-card flex flex-col gap-8 print:shadow-none print:border-none print:bg-transparent"
        >
            <div class="flex justify-between items-start print:hidden">
                <h2 class="text-3xl font-bold tracking-tight">
                    Your Upcycle Project
                </h2>
                <div class="flex gap-3">
                    <button
                        onclick={() => window.print()}
                        class="px-4 py-2 bg-surface-500/10 hover:bg-surface-500/20 rounded-lg flex items-center gap-2 font-medium transition-colors"
                    >
                        📄 Export PDF
                    </button>
                    <button
                        onclick={reset}
                        class="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg flex items-center gap-2 font-bold transition-colors shadow-md shadow-primary-500/20"
                    >
                        ♻️ New Scan
                    </button>
                </div>
            </div>

            <!-- Render Markdown -->
            <article
                class="prose prose-invert max-w-none prose-headings:text-primary-500 prose-a:text-secondary-500 prose-strong:text-opacity-90 leading-relaxed bg-surface-500/5 p-8 rounded-2xl border border-surface-500/10 print:bg-white print:text-black print:p-0 print:prose-invert:false"
            >
                {@html marked(generatedProject)}
            </article>
        </div>
    {/if}
</div>
