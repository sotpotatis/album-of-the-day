<!-- Individual album page
A page showing an individual album.
Almost identical to the page showing an album of the day in the header.
Shows where you can find the album in the body. -->
<script>
	import Page from '../../../components/Page.svelte';
	import { DUMMY_ALBUM_DATA } from '../../../lib/dummyData.js';
	import { onMount } from 'svelte';
	import { getAlbum } from '../../../lib/apiClient.js';
	import AlbumHeader from '../../../components/Header/AlbumHeader.svelte';
	import SearchResult from '../../../components/SearchResult/SearchResult.svelte';
	import Error from '../../../components/Generic/Error.svelte';
	import { MANUAL_URLS_NOTICE } from '../../../lib/utilities.js';
	export let data; // We will get the album ID here
	$: requestedAlbumId = data.id;
	let [success, responseData] = [null, DUMMY_ALBUM_DATA]; // success = null to indicate a skeleton loader, and some dummy data by default
	onMount(() => {
		getAlbum(requestedAlbumId).then((result) => {
			[success, responseData] = result;
		});
	});
	$: skeleton = success !== true; // Whether to show skeleton loader or not.
</script>

<Page>
	<svelte:fragment slot="header">
		<AlbumHeader
			albumName={responseData.name}
			albumId={responseData.id}
			albumSpotifyUID={responseData.spotify_uid}
			albumSpotifyTrackURIs={responseData.spotify_track_uris}
			albumArtists={responseData.artists}
			coverURL={responseData.cover_url}
			coverSource={responseData.cover_source}
			genres={responseData.genres}
			{skeleton}
		/>
	</svelte:fragment>
	<svelte:fragment slot="page">
		{#if success !== false}
			<SearchResult
				searchType="album_of_the_days"
				searchFilters={{
					album_id: responseData.id
				}}
				title="Album of the day"
				defaultCollapsed={true}
			/>
			<SearchResult
				searchType="lists"
				searchFilters={{ items_album_id: responseData.id }}
				title="Listor"
				defaultCollapsed={true}
			/>
			<SearchResult
				searchType="daily_rotations"
				searchFilters={{
					albums_id: responseData.id
				}}
				title="Dagliga rotationer"
				defaultCollapsed={true}
			/>
		{:else}
			<Error
				description={`Misslyckades med att ladda in efterfrågat album. ${MANUAL_URLS_NOTICE}`}
			/>
		{/if}
	</svelte:fragment>
</Page>
