<!-- Album of the day page
Retrieves an individual album of the day based on an ID.
-->
<script>
	import Page from '../../../components/Page.svelte';
	import { onMount } from 'svelte';
	import { getAlbumOfTheDay } from '../../../lib/apiClient.js';
	import HeaderTitle from '../../../components/Header/HeaderTitle.svelte';
	import HeadingDivider from '../../../components/Generic/HeadingDivider.svelte';
	import AlbumHeader from '../../../components/Header/AlbumHeader.svelte';
	import { DUMMY_ALBUM_OF_THE_DAY_DATA } from '../../../lib/dummyData.js';
	import { MANUAL_URLS_NOTICE } from '../../../lib/utilities.js';
	import Error from '../../../components/Generic/Error.svelte';
	import Notice from '../../../components/Generic/Notice.svelte';
	import Icon from '../../../components/Generic/Icon.svelte';
	export let data;
	$: requestedId = data.id; // The ID that was requested
	let [success, responseData] = [null, null]; // success = null means that we are loading
	onMount(() => {
		getAlbumOfTheDay(requestedId).then((result) => {
			[success, responseData] = result;
		});
	});
	$: skeleton = success !== true; //Whether to render a skeleton or not
	// Use dummy data if we're using a skeleton loader
	$: responseData = success === null ? DUMMY_ALBUM_OF_THE_DAY_DATA : responseData;
</script>

<Page>
	<div slot="header">
		<AlbumHeader
			albumName={responseData.album.name}
			albumId={responseData.album.id}
			albumSpotifyUID={responseData.album.spotify_uid}
			albumSpotifyTrackURIs={responseData.album.spotify_track_uris}
			albumArtists={responseData.album.artists}
			coverURL={responseData.album.cover_url}
			coverSource={responseData.album.cover_source}
			genres={responseData.album.genres}
			date={responseData.date}
			{skeleton}
		/>
	</div>
	<svelte:fragment slot="page">
		{#if success !== false}
			<!-- To get old albums (over 200!) into the platform, I used OCR. If you are viewing
            the source code (which I assume you are, because that is where comments can be found),
            check out the code in the root directory. Anyways, we add a little notice here about
            that the text can be inaccurate etc. -->
			{#if responseData.comments_source === 'ocr'}
				<Notice
					title="Heads-up: Kommentarer laddades in med OCR"
					description="Innan juli 2023 fanns album som jag skrivit om endast tillgängliga via min Snapchat-story i bildformat. för att få över de i textform har jag förlitat mig på en teknologi som kallas OCR, vilket enkelt förklarat innebär att en dator försöker läsa av text som finns i bilder. jag har försökt att fixa de felen jag kunde hitta, men enstaka stav- eller innehållsfel kan finnas i kommentarerna för detta album."
					includeIcon={true}
					backgroundColor="albumOfTheDay-uiElements-darkBackground"
					borderColor="albumOfTheDay-uiElements-text-background"
				>
					<svelte:fragment slot="icon">
						<Icon name="clarity:warning-solid" size="medium" color="albumOfTheDay-text-frontend" />
					</svelte:fragment>
				</Notice>
			{/if}
			<HeadingDivider title="Kommentarer" />
			<p class={skeleton ? 'bg-albumOfTheDay-text-foreground p-3' : ''}>
				{responseData.comments}
			</p>
		{:else}
			<Error
				description={`Misslyckades med att ladda in detta Album of the day. ${MANUAL_URLS_NOTICE}`}
			/>
		{/if}
	</svelte:fragment>
</Page>
