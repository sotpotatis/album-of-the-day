<!-- Genres page
Lists all the genres that are in the database.
-->
<script>
	import Page from '../../components/Page.svelte';
	import HeaderTitle from '../../components/Header/HeaderTitle.svelte';
	import { DUMMY_GENRE_DATA } from '../../lib/dummyData.js';
	import { onMount } from 'svelte';
	import { getGenres } from '../../lib/apiClient.js';
	import GenreTag from '../../components/Genres/GenreTag.svelte';
	import HeadingDivider from '../../components/Generic/HeadingDivider.svelte';
	import Badge from '../../components/Generic/Badge.svelte';
	import { GENRE_BADGE_COLOR, groupItemsByName } from '../../lib/utilities.js';
	import Error from '../../components/Generic/Error.svelte';
	import LetterGrouping from '../../components/Generic/LetterGrouping.svelte';
	let [success, responseData] = [
		null,
		[DUMMY_GENRE_DATA, DUMMY_GENRE_DATA, DUMMY_GENRE_DATA, DUMMY_GENRE_DATA]
	]; // success = null used to indicate loading, other is dummy data for skeleton loader
	$: currentPage = 1;
	$: totalEntries = null;
	$: loadedEntries = null;
	onMount(() => {
		// Get genres on mount
		getGenres(null, null, (page, loaded, total) => {
			currentPage = page;
			loadedEntries = loaded;
			totalEntries = total;
		}).then((result) => {
			[success, responseData] = result;
		});
	});
	// Sort genres by name and create a dictionary with all genres for each letter
	$: sortedGenres = success !== false ? groupItemsByName(responseData, 'name') : {};
	$: skeleton = success !== true; // Whether to show skeleton loader or not
	$: loading = success === null; // Whether genres are loading or not
</script>

<Page>
	<div slot="header">
		<HeaderTitle
			title="genrer"
			description="en lista över alla genrer med album som jag har skrivit om. (denna sida kommer ta en halv evighet att ladda, då det är så pass många genrer!)"
		/>
	</div>
	<svelte:fragment slot="page">
		<HeadingDivider title="Genrer">
			<svelte:fragment slot="heading">
				<Badge text={responseData.length} color={GENRE_BADGE_COLOR} {skeleton} />
				{#if loading && loadedEntries !== null}
					<p class="text-base">Laddat {loadedEntries} genrer, {currentPage - 1} sidor</p>
				{/if}
			</svelte:fragment>
		</HeadingDivider>
		{#if success !== false}
			{#each Object.entries(sortedGenres) as [letter, genresData]}
				<LetterGrouping {letter} {skeleton}>
					{#each genresData as genreData}
						<GenreTag
							size="big"
							id={genreData.id}
							name={genreData.name}
							color={genreData.color}
							details={`${genreData.album_count} album`}
							{skeleton}
						/>
					{/each}
				</LetterGrouping>
			{/each}
		{:else}
			<Error
				description={`Kunde inte ladda in en lista av genrer just nu. Testa att komma tillbaka lite senare!`}
			/>
		{/if}
	</svelte:fragment>
</Page>
