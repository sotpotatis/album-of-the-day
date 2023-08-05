<!-- DailyRotationsList.svelte
Contains a list of daily rotations. -->
<script>
	import HeadingDivider from '../Generic/HeadingDivider.svelte';
	import Badge from '../Generic/Badge.svelte';
	import { TYPE_TO_BADGE_COLOR } from '../../lib/utilities.js';
	import { onMount } from 'svelte';
	import { getDailyRotations } from '../../lib/apiClient.js';
	import Error from '../Generic/Error.svelte';
	import { DUMMY_DAILY_ROTATION_DATA } from '../../lib/dummyData.js';
	import AvailableMonthsPicker from '../Generic/AvailableMonthsPicker.svelte';
	import { getNow, getStartAndEndOfMonth } from '../../lib/dates.js';
	import { DateTime } from 'luxon';
	import DailyRotationsCard from '../Card/Helpers/DailyRotationsCard.svelte';
	import { TYPE_TO_GRID_CLASSES } from '../../lib/utilities.js';
	const INITIAL_REQUEST_DATA = [
		null,
		[
			DUMMY_DAILY_ROTATION_DATA,
			DUMMY_DAILY_ROTATION_DATA,
			DUMMY_DAILY_ROTATION_DATA,
			DUMMY_DAILY_ROTATION_DATA,
			DUMMY_DAILY_ROTATION_DATA
		]
	];
	// success = null to indicate skeleton loader, other is dummy data
	let [success, responseData] = INITIAL_REQUEST_DATA;
	const now = getNow();
	let pickedTime = { month: now.month, year: now.year };
	$: skeleton = success !== true; // Whether to show skeleton loader or not.
	const updateAvailableMonths = () => {
		// Create function for sending API request
		[success, responseData] = INITIAL_REQUEST_DATA;
		// Get DateTimes for the request
		const month = pickedTime.month;
		const year = pickedTime.year;
		let dateTime = null;
		if (month === null && year === null) {
			dateTime = getNow(); // Use today's time if nothing else is specified
		} else {
			dateTime = DateTime.fromObject({
				year: year,
				month: month
			});
		}
		// Calculate limits to work with
		const startAndEndOfMonth = getStartAndEndOfMonth(dateTime);
		const [startOfMonth, endOfMonth] = startAndEndOfMonth;
		getDailyRotations(null, {
			day__gte: startOfMonth.toISODate(),
			day__lte: endOfMonth.toISODate()
		}).then((result) => {
			[success, responseData] = result;
		});
	};
	const setPickedTime = (newValue) => {
		// Create function to set picked Time
		pickedTime = newValue;
		updateAvailableMonths();
	};
	onMount(updateAvailableMonths);
</script>

<HeadingDivider title="Dagliga rotationer">
	<svelte:fragment slot="heading">
		<Badge {skeleton} text={responseData.length} color={TYPE_TO_BADGE_COLOR.daily_rotation} />
		<AvailableMonthsPicker
			itemType="daily-rotations"
			{pickedTime}
			on:pickedtime={(event) => {
				setPickedTime(event.detail.pickedTime);
			}}
		/>
	</svelte:fragment>
</HeadingDivider>
{#if success !== false}
	<div id="daily-rotations" class={`${TYPE_TO_GRID_CLASSES.daily_rotation}`}>
		<!-- Render all daily rotations -->
		{#each responseData as dailyRotationData}
			<DailyRotationsCard data={dailyRotationData} {skeleton} />
		{/each}
	</div>
{:else}
	<Error description="Kunde inte ladda dagliga rotationer just nu. Kom tillbaka lite senare!" />
{/if}
