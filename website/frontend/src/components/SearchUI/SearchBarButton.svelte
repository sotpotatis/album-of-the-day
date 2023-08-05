<!-- SearchBarButton.svelte
Button to open the search bar. -->
<script>
	import Icon from '../Generic/Icon.svelte';
	export let toggleSearch; // Function to toggle search (when clicking on the search icon)
</script>

<button on:click={toggleSearch}>
	<Icon name="humbleicons:search" size="medium" color="white" />
</button>
