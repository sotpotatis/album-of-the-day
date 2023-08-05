<!-- SearchUIHeader.svelte
Contains the header of the search UI, which contains the search bar and a close button -->
<script>
	import SearchBar from './SearchBar.svelte';
	import Icon from '../Generic/Icon.svelte';
	export let toggleSearch;
</script>

<div id="search-header">
	<div class="flex justify-center p-3">
		<SearchBar on:searchquery />
	</div>
	<button on:click={toggleSearch} class="fixed top-0 right-0 p-6 md:p-12">
		<Icon name="iconamoon:close-fill" color="white" size="medium" />
	</button>
</div>
