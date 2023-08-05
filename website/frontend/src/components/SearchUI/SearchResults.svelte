<!--SearchResults.svelte
Shows search results for every searchable parameter.
Made for rendering inside SearchUI.-->
<script>
	import SearchResult from '../SearchResult/SearchResult.svelte';
	export let searchQuery;
	const TYPES_TO_SEARCH_FOR = [
		'album_of_the_days',
		'artists',
		'genres',
		'lists',
		'daily_rotations'
	];
</script>

<div class="flex flex-col gap-y-6">
	{#if searchQuery !== null}
		{#each TYPES_TO_SEARCH_FOR as searchType}
			<SearchResult
				{searchType}
				searchFilters={{
					search: searchQuery
				}}
				defaultCollapsed={true}
				inline={false}
			/>
		{/each}
	{/if}
</div>
