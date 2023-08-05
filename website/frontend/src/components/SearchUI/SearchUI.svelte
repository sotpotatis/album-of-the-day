<!-- SearchUI.svelte
Shows a fullscreen search UI.
-->
<script>
	import UIBlur from '../Generic/UIBlur.svelte';
	import SearchBar from './SearchBar.svelte';
	import SearchUIHeader from './SearchUIHeader.svelte';
	import SearchResult from '../SearchResult/SearchResult.svelte';
	import SearchResults from './SearchResults.svelte';
	export let toggleSearch; // Function to toggle search
	let searchQuery = null;
</script>

<div class="fixed top-0 h-screen w-screen overflow-scroll p-8 z-10">
	<SearchUIHeader
		{toggleSearch}
		on:searchquery={(event) => {
			searchQuery = event.detail.query;
		}}
	/>
	<SearchResults {searchQuery} />
</div>
