<!-- Individual artist page
Retrieves information about an individual artist.
-->
<script>
	import { DUMMY_ARTIST_DATA } from '../../../lib/dummyData.js';
	import { onMount } from 'svelte';
	import Page from '../../../components/Page.svelte';
	import { getArtist } from '../../../lib/apiClient.js';
	import SearchResult from '../../../components/SearchResult/SearchResult.svelte';
	import ArtistHeader from '../../../components/Header/ArtistHeader.svelte';
	import Error from '../../../components/Generic/Error.svelte';
	import { MANUAL_URLS_NOTICE } from '../../../lib/utilities.js';
	export let data; // Will be passed down from +page.js
	$: requestedId = data.id;
	let [success, responseData] = [null, DUMMY_ARTIST_DATA];
	$: skeleton = success !== true; // Whether to show skeleton loader or not
	onMount(() => {
		getArtist(requestedId).then((result) => {
			[success, responseData] = result;
		});
	});
</script>

<Page>
	<svelte:fragment slot="header">
		<ArtistHeader artistName={responseData.name} {skeleton} />
	</svelte:fragment>
	<svelte:fragment slot="page">
		{#if success !== false}
			<SearchResult searchType="albums" searchFilters={{ artists_id: requestedId }} />
		{:else}
			<Error
				description={`Information om den efterfrågade artisten kan inte laddas just nu. ${MANUAL_URLS_NOTICE}`}
			/>
		{/if}
	</svelte:fragment>
</Page>
