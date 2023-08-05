<!-- Statistics.svelte
Offers a statistic view with an overview of how different entities on the website are doing.
Sample API response:
{"count":{"album_of_the_day":0,"album":6,"list":0,"genre":1,"artist":5,"daily_rotation":1}}
-->
<script>
	import Statistic from './Statistic.svelte';
	import { getStatistics } from '../../lib/apiClient.js';
	import { onMount } from 'svelte';
	import Error from '../Generic/Error.svelte';
	import HeadingDivider from '../Generic/HeadingDivider.svelte';
	const STATISTIC_TYPES_TO_STRING = {
		album_of_the_day: 'album',
		list: 'listor',
		artist: 'artister',
		genre: 'genrer'
	}; // Note that some attributes  from the API are excluded
	const STATISTIC_TYPES = Object.keys(STATISTIC_TYPES_TO_STRING);
	let [success, responseData] = [null, null]; // success == null means that we are loading
	onMount(() => {
		getStatistics().then((result) => {
			[success, responseData] = result;
		});
	});
</script>

<div>
	<HeadingDivider title="Statistik" />
	{#if success !== false}
		<div class="p-3 grid grid-cols-4 gap-x-12">
			{#each STATISTIC_TYPES as statisticType}
				<Statistic
					skeleton={success === null}
					title={STATISTIC_TYPES_TO_STRING[statisticType]}
					number={success ? responseData.count[statisticType] : null}
				/>
			{/each}
		</div>
	{:else}
		<Error description="Misslyckades med att ladda statistik. Försök igen lite senare." />
	{/if}
</div>
