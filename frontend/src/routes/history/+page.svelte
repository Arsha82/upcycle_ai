<script lang="ts">
    import { onMount } from "svelte";
    import { slide, fade } from "svelte/transition";
    import { marked } from "marked";

    type Project = {
        id: number;
        item_name: string;
        recipe_text: string;
        image_path: string | null;
        created_at: string;
    };

    let projects: Project[] = $state([]);
    let loading = $state(true);
    let errorMsg = $state("");

    // Modal State
    let selectedProject: Project | null = $state(null);
    let isModalOpen = $state(false);
    const API_BASE = "/api";
    const UPLOADS_BASE = ""; // proxy handles /uploads

    async function loadProjects() {
        loading = true;
        errorMsg = "";
        try {
            const res = await fetch(`${API_BASE}/history`);
            if (!res.ok) throw new Error("Failed to fetch history");
            const data = await res.json();
            projects = data.history || [];
        } catch (err: any) {
            errorMsg = err.message || "Error loading projects";
        } finally {
            loading = false;
        }
    }

    onMount(() => {
        loadProjects();
    });

    function getImageUrl(path: string | null) {
        if (!path) return "";
        // DB might store "images\file.jpg", "uploads/file.jpg", or "uploads\\file.jpg"
        const normalized = path.split("\\").join("/").split("//").join("/");
        // Extract the part starting with images/ or uploads/
        const match = normalized.match(/(images|uploads)\/[^/]+$/);
        if (match) {
            return `/${match[0]}`;
        }
        return normalized.startsWith("/") ? normalized : `/${normalized}`;
    }

    function openProject(project: Project) {
        selectedProject = project;
        isModalOpen = true;
    }

    function closeModal() {
        isModalOpen = false;
        setTimeout(() => {
            selectedProject = null;
        }, 300); // Wait for transition
    }

    function formatDate(dateString: string) {
        try {
            return new Date(dateString).toLocaleDateString("en-US", {
                month: "short",
                day: "numeric",
                year: "numeric",
            });
        } catch {
            return dateString;
        }
    }
</script>

<svelte:head>
    <title>History - Upcycle AI</title>
</svelte:head>

<div class="w-full">
    <!-- Header Area -->
    <div class="mb-10 text-center" in:fade={{ duration: 400 }}>
        <h1
            class="text-4xl font-black uppercase tracking-tighter text-surface-950 px-4 py-2 bg-primary-50 inline-block border-[3px] border-surface-950 shadow-[6px_6px_0px_oklch(0.2_0.03_85)] mb-4"
        >
            Your History
        </h1>
        <p class="text-surface-950/80 font-medium text-lg max-w-lg mx-auto">
            Review the upcycling projects you've generated in the past.
        </p>
    </div>

    {#if errorMsg}
        <div
            class="bg-error-500/20 text-error-500 p-4 rounded-xl border border-error-500/50 mb-8"
            transition:slide
        >
            {errorMsg}
            <button onclick={loadProjects} class="ml-4 underline font-medium"
                >Try Again</button
            >
        </div>
    {/if}

    {#if loading}
        <!-- Loading Skeletons in a Grid -->
        <div class="columns-1 sm:columns-2 lg:columns-3 gap-6 space-y-6">
            {#each Array(6) as _, i}
                <div class="glass-card animate-pulse break-inside-avoid">
                    <div
                        class="w-full aspect-[4/3] bg-surface-500/20 mb-4"
                    ></div>
                    <div class="h-6 bg-surface-500/20 w-3/4 mb-3"></div>
                    <div class="h-4 bg-surface-500/20 w-1/2"></div>
                </div>
            {/each}
        </div>
    {:else if projects.length === 0}
        <div class="text-center py-20 opacity-60" in:fade>
            <div class="text-6xl mb-4">🏜️</div>
            <h3 class="text-xl font-bold">No history yet...</h3>
            <p>Scan an item on the Analyzer page to get started!</p>
        </div>
    {:else}
        <!-- Masonry Grid Layout -->
        <div
            class="columns-1 sm:columns-2 gap-6 space-y-6"
            in:fade={{ duration: 400, delay: 100 }}
        >
            {#each projects as project}
                <button
                    onclick={() => openProject(project)}
                    class="group w-full text-left bg-surface-50 border-[3px] border-surface-950 shadow-[6px_6px_0px_oklch(0.2_0.03_85)] overflow-hidden break-inside-avoid transition-transform duration-300 hover:-translate-y-1 hover:-translate-x-1 hover:shadow-[10px_10px_0px_oklch(0.2_0.03_85)] block focus:outline-none focus:ring-4 focus:ring-primary-500"
                >
                    <!-- Project Image Banner -->
                    {#if project.image_path}
                        <div
                            class="w-full relative bg-surface-500/10 overflow-hidden"
                        >
                            <!-- Image -->
                            <img
                                src={getImageUrl(project.image_path)}
                                alt={project.item_name}
                                class="w-full h-auto object-cover group-hover:scale-105 transition-transform duration-500"
                                loading="lazy"
                            />
                            <!-- Overlay Gradient -->
                            <div
                                class="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end p-4"
                            >
                                <span
                                    class="text-white font-medium flex items-center gap-2"
                                >
                                    <span class="text-xl">✨</span> View Details
                                </span>
                            </div>
                        </div>
                    {:else}
                        <!-- Fallback Pattern if no image -->
                        <div
                            class="w-full aspect-[3/2] flex items-center justify-center bg-primary-50 border-b-[3px] border-surface-950 group-hover:bg-secondary-50 transition-colors duration-500"
                        >
                            <span class="text-5xl opacity-80 mix-blend-multiply"
                                >♻️</span
                            >
                        </div>
                    {/if}

                    <div
                        class="p-5 bg-white border-t-[3px] border-surface-950 mt-[-3px]"
                    >
                        <h3
                            class="font-bold text-lg mb-2 line-clamp-2 leading-tight"
                        >
                            {project.item_name &&
                            project.item_name !== "" &&
                            !project.item_name.includes("\\")
                                ? project.item_name
                                : `Upcycled Item #${project.id}`}
                        </h3>
                        <div
                            class="flex items-center justify-between text-xs opacity-60 font-medium"
                        >
                            <span>#{project.id} Project</span>
                            <span>{formatDate(project.created_at)}</span>
                        </div>
                    </div>
                </button>
            {/each}
        </div>
    {/if}
</div>

<!-- Project Details Modal Override / Overlay -->
{#if isModalOpen && selectedProject}
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
        <!-- Backdrop -->
        <!-- svelte-ignore a11y_click_events_have_key_events -->
        <!-- svelte-ignore a11y_no_static_element_interactions -->
        <div
            class="absolute inset-0 bg-surface-950/90 cursor-pointer"
            in:fade={{ duration: 200 }}
            out:fade={{ duration: 200 }}
            onclick={closeModal}
        ></div>

        <!-- Modal Content container -->
        <div
            class="w-full max-w-3xl max-h-[90vh] flex flex-col bg-surface-50 border-[5px] border-surface-950 shadow-[12px_12px_0px_oklch(0.6_0.05_85)] overflow-hidden relative z-10"
            in:slide={{ duration: 300, axis: "y" }}
            out:slide={{ duration: 200, axis: "y" }}
        >
            <!-- Modal Header / Image Area -->
            <div class="relative shrink-0 bg-surface-500/10">
                <!-- Close Button -->
                <button
                    onclick={closeModal}
                    class="absolute top-4 right-4 z-20 w-12 h-12 flex items-center justify-center bg-white border-[3px] border-surface-950 text-surface-950 text-xl font-black hover:bg-primary-500 hover:text-white transition-colors shadow-[4px_4px_0px_oklch(0.2_0.03_85)]"
                >
                    ✕
                </button>

                {#if selectedProject.image_path}
                    <div
                        class="w-full h-48 sm:h-64 md:h-80 overflow-hidden relative"
                    >
                        <img
                            src={getImageUrl(selectedProject.image_path)}
                            alt={selectedProject.item_name}
                            class="w-full h-full object-cover"
                        />
                        <div
                            class="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent flex items-end p-6 sm:p-8"
                        >
                            <div>
                                <h2
                                    class="text-2xl sm:text-3xl font-bold text-white mb-2 leading-tight shadow-black drop-shadow-lg"
                                >
                                    {selectedProject.item_name &&
                                    selectedProject.item_name !== "" &&
                                    !selectedProject.item_name.includes("\\")
                                        ? selectedProject.item_name
                                        : `Upcycled Item #${selectedProject.id}`}
                                </h2>
                                <p class="text-white/70 text-sm font-medium">
                                    Generated on {formatDate(
                                        selectedProject.created_at,
                                    )}
                                </p>
                            </div>
                        </div>
                    </div>
                {:else}
                    <div
                        class="p-8 bg-primary-50 border-b-[3px] border-surface-950"
                    >
                        <h2
                            class="text-3xl sm:text-4xl font-black uppercase tracking-tighter mb-2 leading-tight text-surface-950"
                        >
                            {selectedProject.item_name &&
                            selectedProject.item_name !== "" &&
                            !selectedProject.item_name.includes("\\")
                                ? selectedProject.item_name
                                : `Upcycled Item #${selectedProject.id}`}
                        </h2>
                        <p class="opacity-70 text-sm font-medium">
                            Generated on {formatDate(
                                selectedProject.created_at,
                            )}
                        </p>
                    </div>
                {/if}
            </div>

            <!-- Modal Body (Markdown Markdown Scrollable) -->
            <div
                class="p-6 sm:p-10 overflow-y-auto w-full prose prose-lg max-w-none prose-headings:text-primary-500 prose-a:text-secondary-500 bg-white pb-12"
            >
                {@html marked(selectedProject.recipe_text)}
            </div>
        </div>
    </div>
{/if}
