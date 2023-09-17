<!-- DailyRotationHeader.svelte
A header showing information about a daily rotation.
-->
<script>
	import GenreTag from '../Genres/GenreTag.svelte';
	import { getFirstAvailableAlbumImagesInList } from '../../lib/utilities.js';
	import DailyRotationImage from '../Generic/Helpers/DailyRotationImage.svelte';
	export let dailyRotationDate; // The date for the daily rotation as a luxon datetime
	export let dailyRotationGenres; // The genres included in the daily rotation
	export let dailyRotationAlbums; // The albums included in the daily rotation
	export let skeleton = false; // Whether to show a skeleton loader or not
	$: getFirstAvailableAlbumImagesInList({ items: dailyRotationAlbums }, 'daily_rotation');
	$: firstThreeGenres =
		dailyRotationGenres.length > 3 ? dailyRotationGenres.slice(0, 3) : dailyRotationGenres; // Get the first 3 genres
	$: numberOfAdditionalGenres = dailyRotationGenres.length > 3 ? dailyRotationGenres.length - 3 : 0; // Get the length of the additional genres - this is for a subtitle, see below.
	$: genresAreCollapsed = true;
</script>

<div id="header" class={`flex flex-col gap-y-8 items-center${skeleton ? ' animate-pulse' : ''}`}>
	<DailyRotationImage albumList={dailyRotationAlbums} size="big" {skeleton} />
	<h1 class="text-xl font-semibold">Daglig rotation</h1>
	<h1 class={`text-4xl font-bold${skeleton ? ' bg-white m-3' : ''}`}>
		{!skeleton ? dailyRotationDate.toISODate() : '20XX-XX-XX'}
	</h1>
	<!-- Add genre tags for each genre -->
	<div id="genre-tags" class="grid grid-cols-3 gap-x-8 gap-y-8">
		{#each genresAreCollapsed ? firstThreeGenres : dailyRotationGenres as genre}
			<GenreTag name={genre.name} id={genre.name} color={genre.color} {skeleton} size="small" />
		{/each}
	</div>
	<!-- Make genres collapsible if we can -->
	{#if numberOfAdditionalGenres > 0}
		{#if genresAreCollapsed}
			<p class={`text-xl font-bold${skeleton ? ' bg-white m-3' : ''}`}>
				+{numberOfAdditionalGenres}
				{numberOfAdditionalGenres !== 1 ? 'genrer' : 'genre'}
			</p>
		{/if}
		<button
			class={`underline text-white${skeleton ? ' bg-white m-3' : ''}`}
			on:click={() => {
				genresAreCollapsed = !genresAreCollapsed;
			}}>{genresAreCollapsed ? 'Visa alla' : 'Visa mindre'}</button
		>
	{/if}
</div>
