<!-- ListList.svelte
A real tongue twiser - a list of lists! (lists as in album lists).
-->
<script>
	import { DUMMY_LIST_DATA } from '../../lib/dummyData.js';
	import { onMount } from 'svelte';
	import { getLists } from '../../lib/apiClient.js';
	import ListCard from '../Card/Helpers/ListCard.svelte';
	import Error from '../Generic/Error.svelte';
	let [success, responseData] = [
		null,
		[DUMMY_LIST_DATA, DUMMY_LIST_DATA, DUMMY_LIST_DATA, DUMMY_LIST_DATA, DUMMY_LIST_DATA]
	]; // success = null to indicate skeleton loader.
	onMount(() => {
		getLists().then((result) => {
			[success, responseData] = result;
		});
	});
	$: skeleton = success !== true; // Whether to show a skeleton loader or not.
</script>

{#if success !== false}
	<div class={`${skeleton ? ' animate-pulse' : ''}`}>
		{#each responseData as listData}
			<ListCard data={listData} {skeleton} />
		{/each}
	</div>
{:else}
	<Error description="Misslyckades att ladda in listor just nu. Försök igen lite senare." />
{/if}
