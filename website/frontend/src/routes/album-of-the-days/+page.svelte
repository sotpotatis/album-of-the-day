<!-- album-of-the-days.svelte
Shows a list of album of the days for a certain time period.
-->
<script>
	import Page from '../../components/Page.svelte';
	import { getNow, getStartAndEndOfMonth } from '../../lib/dates.js';
	import { DateTime } from 'luxon';
	import { onMount } from 'svelte';
	import { getAlbumOfTheDays } from '../../lib/apiClient.js';
	import AvailableMonthsPicker from '../../components/Generic/AvailableMonthsPicker.svelte';
	import HeadingDivider from '../../components/Generic/HeadingDivider.svelte';
	import { DUMMY_ALBUM_OF_THE_DAY_DATA } from '../../lib/dummyData.js';
	import AlbumCard from '../../components/Card/Helpers/AlbumCard.svelte';
	import Error from '../../components/Generic/Error.svelte';
	import { MANUAL_URLS_NOTICE } from '../../lib/utilities.js';
	const INITIAL_REQUEST_DATA = [null, [DUMMY_ALBUM_OF_THE_DAY_DATA]]; // success = null used to indicate loading, other data used for skeleton loader
	const now = getNow();
	let pickedTime = {
		// Use to set picked time
		year: now.year,
		month: now.month
	};
	let [success, responseData] = INITIAL_REQUEST_DATA;
	$: albumOfTheDaySkeleton = success === null;
	const updateAvailableMonths = () => {
		// Define function to perform request and update data
		console.log('Updating available months...');
		// Build datetime from month and year
		const month = pickedTime.month;
		const year = pickedTime.year;
		// If no values are set, use today
		let datetime = null;
		if (month === null && year === null) {
			datetime = getNow();
		} else {
			datetime = DateTime.fromObject({
				year: year,
				month: month
			});
		}
		[success, responseData] = INITIAL_REQUEST_DATA; // Reset request status
		// Get start and end of month, used for requests
		const startAndEndOfMonth = getStartAndEndOfMonth(datetime);
		// Get list of available months
		// Get album of the days
		const [startOfMonth, endOfMonth] = startAndEndOfMonth;
		getAlbumOfTheDays(null, {
			date__gte: startOfMonth.toISODate(),
			date__lte: endOfMonth.toISODate()
		}).then((result) => {
			[success, responseData] = result;
		});
	};
	// Since we use the AvailableMonthsPicker, we create a function that sets the picked time
	// once it has dispatched its iconic event!
	const setPickedTime = (newValue) => {
		pickedTime = newValue;
		updateAvailableMonths();
	};
	$: pickedTime, updateAvailableMonths();
</script>

<Page>
	<div slot="header" />
	<svelte:fragment slot="page">
		<HeadingDivider title="album of the day">
			<svelte:fragment slot="heading">
				<AvailableMonthsPicker
					itemType="album-of-the-days"
					{pickedTime}
					on:pickedtime={(event) => {
						setPickedTime(event.detail.pickedTime);
					}}
				/>
			</svelte:fragment>
		</HeadingDivider>
		{#if success !== false}
			<!-- Add all cards -->
			<div class="grid lg:grid-cols-3">
				{#each responseData as cardData}
					<AlbumCard data={cardData} skeleton={success === null} />
				{/each}
			</div>
		{:else}
			<Error
				description={`Misslyckades med att ladda in album of the days. ${MANUAL_URLS_NOTICE}`}
			/>
		{/if}
	</svelte:fragment>
</Page>
