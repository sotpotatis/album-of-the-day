<!-- Artists page
Lists all artists that are currently on the server. --->
<script>
	import { DUMMY_ARTIST_DATA } from '../../lib/dummyData.js';
	import Page from '../../components/Page.svelte';
	import HeaderTitle from '../../components/Header/HeaderTitle.svelte';
	import Error from '../../components/Generic/Error.svelte';
	import { onMount } from 'svelte';
	import { getArtists } from '../../lib/apiClient.js';
	import { groupItemsByName } from '../../lib/utilities.js';
	import ArtistTag from '../../components/Artists/ArtistTag.svelte';
	import LetterGrouping from '../../components/Generic/LetterGrouping.svelte';
	import HeadingDivider from '../../components/Generic/HeadingDivider.svelte';
	let [success, responseData] = [
		null,
		[DUMMY_ARTIST_DATA, DUMMY_ARTIST_DATA, DUMMY_ARTIST_DATA, DUMMY_ARTIST_DATA, DUMMY_ARTIST_DATA]
	]; // success = null to indicate skeleton loader, rest is dummy data
	onMount(() => {
		getArtists().then((result) => {
			[success, responseData] = result;
		});
	});
	$: sortedArtists = success !== false ? groupItemsByName(responseData, 'name') : {};
	$: skeleton = success !== true;
</script>

<Page>
	<svelte:fragment slot="header">
		<HeaderTitle
			title="artister"
			description="en komplett lista över alla artister som jag antingen lyssnat på eller skrivit om."
		/>
	</svelte:fragment>
	<svelte:fragment slot="page">
		<HeadingDivider title="Artister" />
		{#if success !== false}
			<!-- Render all artists -->
			{#each Object.entries(sortedArtists) as [letter, artistsData]}
				<LetterGrouping itemType="artist" {letter} {skeleton}>
					{#each artistsData as artistData}
						<ArtistTag artistName={artistData.name} artistId={artistData.id} {skeleton} />
					{/each}
				</LetterGrouping>
			{/each}
		{:else}
			<Error description="Kunde inte ladda lista av artister just nu. Försök igen lite senare." />
		{/if}
	</svelte:fragment>
</Page>
