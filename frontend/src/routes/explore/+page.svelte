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
            const res = await fetch(`${API_BASE}/explore`);
            if (!res.ok) throw new Error("Failed to fetch explore feed");
            const data = await res.json();
            projects = data.explore_feed || [];
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
    <title>Explore - Upcycle AI</title>
</svelte:head>

<!-- We need a larger container for the masonry grid if possible, 
     overriding the default max-w-4xl from layout for this specific page if we wished to, 
     but within max-w-4xl it looks like a nice centered feed too. -->
<div class="w-full">
    <!-- Header Area -->
    <div class="mb-10 text-center" in:fade={{ duration: 400 }}>
        <h1
            class="text-4xl font-bold bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent mb-4 inline-block"
        >
            Explore Inspire
        </h1>
        <p class="text-surface-950/60 dark:text-surface-50/60 max-w-lg mx-auto">
            Discover amazing upcycled creations from the community and get
            inspired for your next project.
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
                        class="w-full aspect-[4/3] bg-surface-500/20 rounded-xl mb-4"
                    ></div>
                    <div
                        class="h-6 bg-surface-500/20 rounded-md w-3/4 mb-3"
                    ></div>
                    <div class="h-4 bg-surface-500/20 rounded-md w-1/2"></div>
                </div>
            {/each}
        </div>
    {:else if projects.length === 0}
        <div class="text-center py-20 opacity-60" in:fade>
            <div class="text-6xl mb-4">🏜️</div>
            <h3 class="text-xl font-bold">No projects yet...</h3>
            <p>Be the first to scan an item and create a project!</p>
        </div>
    {:else}
        <!-- Masonry Grid Layout -->
        <!-- We use CSS columns for native CSS masonry. -->
        <div
            class="columns-1 sm:columns-2 gap-6 space-y-6"
            in:fade={{ duration: 400, delay: 100 }}
        >
            {#each projects as project}
                <button
                    onclick={() => openProject(project)}
                    class="glass group w-full text-left rounded-2xl overflow-hidden break-inside-avoid shadow-lg hover:shadow-2xl transition-all duration-300 hover:-translate-y-1 block border border-surface-500/10 focus:outline-none focus:ring-2 focus:ring-primary-500"
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
                            class="w-full aspect-[3/2] flex items-center justify-center bg-gradient-to-br from-primary-500/20 to-secondary-500/20 group-hover:scale-105 transition-transform duration-500"
                        >
                            <span class="text-5xl opacity-50">♻️</span>
                        </div>
                    {/if}

                    <div
                        class="p-5 bg-white/5 dark:bg-black/5 backdrop-blur-sm"
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
            class="absolute inset-0 bg-surface-950/80 backdrop-blur-sm cursor-pointer"
            in:fade={{ duration: 200 }}
            out:fade={{ duration: 200 }}
            onclick={closeModal}
        ></div>

        <!-- Modal Content container -->
        <div
            class="glass w-full max-w-3xl max-h-[90vh] flex flex-col rounded-3xl overflow-hidden relative z-10 shadow-2xl"
            in:slide={{ duration: 300, axis: "y" }}
            out:slide={{ duration: 200, axis: "y" }}
        >
            <!-- Modal Header / Image Area -->
            <div class="relative shrink-0 bg-surface-500/10">
                <!-- Close Button -->
                <button
                    onclick={closeModal}
                    class="absolute top-4 right-4 z-20 w-10 h-10 flex items-center justify-center rounded-full bg-black/40 text-white hover:bg-black/60 transition-colors backdrop-blur-md"
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
                        class="p-6 sm:p-8 bg-gradient-to-r from-primary-500/30 to-secondary-500/30"
                    >
                        <h2
                            class="text-2xl sm:text-3xl font-bold mb-2 leading-tight"
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
                class="p-6 sm:p-8 overflow-y-auto w-full prose prose-sm sm:prose-base prose-invert max-w-none prose-headings:text-primary-500 prose-a:text-secondary-500 prose-strong:text-opacity-90 leading-relaxed bg-surface-50 dark:bg-surface-950 pb-12"
            >
                {@html marked(selectedProject.recipe_text)}
            </div>
        </div>
    </div>
{/if}
