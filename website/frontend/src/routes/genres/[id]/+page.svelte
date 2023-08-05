<!-- Specific genre page
 Page that shows data for a specific genre. -->
<script>
	import Page from '../../../components/Page.svelte';
	import HeaderTitle from '../../../components/Header/HeaderTitle.svelte';
	import { onMount } from 'svelte';
	import { getGenre } from '../../../lib/apiClient.js';
	import { DUMMY_GENRE_DATA } from '../../../lib/dummyData.js';
	import GenreHeader from '../../../components/Header/GenreHeader.svelte';
	import SearchResult from '../../../components/SearchResult/SearchResult.svelte';
	import Error from '../../../components/Generic/Error.svelte';
	import { MANUAL_URLS_NOTICE } from '../../../lib/utilities.js';
	export let data;
	$: requestedId = data.id; // Get the requested ID from the URL (see +page.js for the one-liner magic that does this :))
	let [success, responseData] = [null, DUMMY_GENRE_DATA]; // success = null is used to show skeleton loader
	onMount(() => {
		getGenre(requestedId).then((result) => {
			[success, responseData] = result;
		});
	});
	$: skeleton = success !== true;
</script>

<Page>
	<svelte:fragment slot="header">
		<GenreHeader
			genreName={responseData.name}
			genreColor={responseData.color}
			genreDescription={responseData.description}
			genreDescriptionSource={responseData.description_source}
			{skeleton}
		/>
	</svelte:fragment>
	<svelte:fragment slot="page">
		{#if success !== false}
			<SearchResult
				searchType="album_of_the_days"
				searchFilters={{
					album_genres_id: data.id
				}}
				title="Album"
			/>
		{:else}
			<Error description={`Kunde inte ladda in efterfrågad genre. ${MANUAL_URLS_NOTICE}`} />
		{/if}
	</svelte:fragment>
</Page>
