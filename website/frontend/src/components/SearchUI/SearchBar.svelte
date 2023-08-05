<!-- SearchBar.svelte
Contains the search bar on the page. -->
<script>
	import { createEventDispatcher } from 'svelte';
	import Button from '../Generic/Button.svelte';
	import Icon from '../Generic/Icon.svelte';
	const dispatch = createEventDispatcher();
	// Function to run when the search query changes
	let onSearchQueryChange = (event) => {
		let searchQuery = document.getElementById('searchQueryBox').value;
		if (searchQuery.length > 0) {
			console.log(`Search query changed: ${searchQuery}.`);
			dispatch('searchquery', {
				query: searchQuery
			});
		}
	};
</script>

<div class="flex flex-row gap-x-4 p-3">
	<input
		id="searchQueryBox"
		type="text"
		class="bg-white rounded-full border-2 border-gray-300 px-8 py-4 text-gray-600 placeholder:text-gray-600"
		placeholder="Sök..."
		on:searchquery
		on:keyup={(event) => {
			if (event.key === 'Enter') {
				// Update search on enter key press
				onSearchQueryChange(event);
			}
		}}
	/>
	<Button text="" backgroundColor="blue-400" textColor="white" on:click={onSearchQueryChange}>
		<svelte:fragment slot="icon">
			<Icon name="material-symbols:search" />
		</svelte:fragment>
	</Button>
</div>
