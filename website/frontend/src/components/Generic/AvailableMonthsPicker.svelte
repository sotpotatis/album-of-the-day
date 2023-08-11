<!-- AvailableMonths.svelte
Element that functions as a list for available months to retrieve different items
as well as a picker to pick the month. -->
<script>
	import { createEventDispatcher, onMount } from 'svelte';
	import { getAvailableMonths } from '../../lib/apiClient.js';
	import { DateTime } from 'luxon';
	import { getNow } from '../../lib/dates.js';
	export let itemType; // Either "album-of-the-days" or "daily-rotations"
	// Getter and setter for the current month and year
	export let pickedTime;
	const dispatch = createEventDispatcher(); // Create an event dispatcher
	const now = getNow(); // Use for skeleton data
	let skeletonData = {};
	skeletonData[now.year.toString()] = [now.month.toString()];
	let [success, responseData] = [null, skeletonData]; // success = null used to indicate loading, other is dummy data for skeleton loader
	onMount(() => {
		getAvailableMonths(itemType).then((result) => {
			[success, responseData] = result;
		});
	});
	// Check skeleton loader
	$: skeleton = success !== true;
	// Create a function for when the current month and year is changed
	const onYearMonthChange = (event) => {
		// Note: month and year is stored in the dataset of each option
		// We first get the <option> element that is the target
		const optionTarget = event.target.options[event.target.selectedIndex];
		const targetYear = Number(optionTarget.dataset.year);
		const targetMonth = Number(optionTarget.dataset.month);
		if (targetYear !== null && targetMonth !== null) {
			dispatch('pickedtime', {
				pickedTime: {
					year: targetYear,
					month: targetMonth
				}
			});
		} else {
			console.warn('Missing target year and target month!');
		}
	};
	// Also create a function that takes a month and a year and converts it into a human-readable string
	const yearAndMonthToReadable = (year, month) => {
		return DateTime.fromObject({ year: year, month: month })
			.setLocale('sv')
			.toFormat('MMMM yyyy')
			.toLowerCase();
	};
	$: selectedOption = `${pickedTime.year}-${pickedTime.month}`;
</script>

<select
	class={`p-3 border-1 rounded-lg bg-white border-gray-100 text-base${
		skeleton ? ' animate-pulse bg-albumOfTheDay-text-foreground m-3' : ''
	}`}
	bind:value={selectedOption}
	on:change={onYearMonthChange}
	data-selected-option={selectedOption}
>
	<!-- Response from the server looks like this:
    {
        ...
        "2023": [available_months],
        "2022": [available_months]
        ...
    }.
    It is sorted from the server, but I figured that it also must be sorted here somehow.
    -->
	{#each Object.keys(responseData).sort((key) => key) as availableYear}
		{#each responseData[availableYear].sort((key) => key) as availableMonth}
			<!-- No idea why this makes the list sorted, but it does.. -->
			<p>{availableYear}-{availableMonth}</p>
			<option
				value={`${availableYear}-${availableMonth}`}
				data-year={availableYear}
				data-month={availableMonth}
			>
				{yearAndMonthToReadable(availableYear, availableMonth)}
			</option>
		{/each}
	{/each}
</select>
