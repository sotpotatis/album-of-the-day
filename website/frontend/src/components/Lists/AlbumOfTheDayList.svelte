<!-- AlbumOfTheDayList.svelte
A list of album of the days for the home page. -->
<script>
	import { onMount } from 'svelte';
	import { getAlbumOfTheDays } from '../../lib/apiClient.js';
	import Card from '../Card/Card.svelte';
	import AlbumCard from '../Card/Helpers/AlbumCard.svelte';
	import Error from '../Generic/Error.svelte';
	import HeadingDivider from '../Generic/HeadingDivider.svelte';
	import { DUMMY_ALBUM_OF_THE_DAY_DATA } from '../../lib/dummyData.js';
	import { TYPE_TO_GRID_CLASSES } from '../../lib/utilities.js';
	export let includeLatest = false; // If true, "pins" the latest album of the day to the top
	export let title = 'Album'; // Title of the list
	export let startDate = null; // Allows specifying a start date for searching
	export let endDate = null; // Allows specifying an end date for searching
	export let limit = 5; // Allows specifying a limit of albums to display
	let [success, responseData] = [null, null]; // success == null means that we are loading
	onMount(() => {
		getAlbumOfTheDays(limit, startDate, endDate).then((result) => {
			[success, responseData] = result;
		});
	});
	// Fill out dummy data when loading
	if (success === null) {
		responseData = [
			DUMMY_ALBUM_OF_THE_DAY_DATA,
			DUMMY_ALBUM_OF_THE_DAY_DATA,
			DUMMY_ALBUM_OF_THE_DAY_DATA,
			DUMMY_ALBUM_OF_THE_DAY_DATA,
			DUMMY_ALBUM_OF_THE_DAY_DATA
		];
	}
	// Decide what to put on the latest card
	let latestCard = DUMMY_ALBUM_OF_THE_DAY_DATA;
	$: if (success && includeLatest) {
		latestCard = responseData[0];
		responseData = responseData.splice(1, responseData.length);
	}
</script>

<div id="album-of-the-day-list">
	{#if success !== false}
		<!-- Add latest card if included -->
		{#if includeLatest}
			<AlbumCard data={latestCard} latest={true} skeleton={success === null} />
		{/if}
		<HeadingDivider {title} />
		<!-- Add all cards -->
		<div class={TYPE_TO_GRID_CLASSES.album_of_the_day}>
			{#each responseData as cardData}
				<AlbumCard data={cardData} skeleton={success === null} />
			{/each}
		</div>
	{:else}
		<Error description="Misslyckades med att ladda album of the days. Försök igen senare." />
	{/if}
</div>
