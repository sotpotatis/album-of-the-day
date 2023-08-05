<!-- GenreHeader.svelte
A header that shows information about a certain genre. -->
<script>
	import { onMount } from 'svelte';
	import GenreTag from '../Genres/GenreTag.svelte';
	import { generateSummaryText, openURL } from '../../lib/utilities.js';
	import Button from '../Generic/Button.svelte';
	import Icon from '../Generic/Icon.svelte';
	export let genreName; // Name of the genre
	export let genreColor; // Genre color
	export let genreId; // ID of genre
	export let genreDescription; // Description of the genre - full version
	export let genreDescriptionSource;
	export let skeleton = false; // Whether to show a skeleton loader or not
	// Generate summary text if needed
	$: summaryData = generateSummaryText(genreDescription, 256);
	// The generateSummaryText returns a result list:
	// [<summary generated>, <summary text>], see the function
	// definition. Here we unpack it.
	$: summaryGenerated = summaryData[0];
	$: summaryText = summaryData[1];
	$: fullTextShown = !summaryGenerated; // Track whether to show full text or not
	// Note: for generating the URL, I first thought that I should add it as an attribute on the backend.
	// However, I checked the return from the Last.FM API, and unless I should source it with some kind of regex
	// from the description, they do not provide a URL to the tag in their tag API (at least not the endpoint I am calling).
	// So, I generate the link here since it seems to follow a certain format. I assume this will work in at least 9 out of 10 cases.
	$: genreLastFMURL = `https://last.fm/tag/${genreName.replace(' ', '+').toLowerCase()}`;
</script>

<div
	class={`flex flex-col gap-y-4 items-center justify-center ${skeleton ? ' animate-pulse' : ''}`}
>
	<GenreTag name={genreName} id={genreId} color={genreColor} size="big" link={false} {skeleton} />
	<!-- Add the genre description (if it exists) -->
	{#if genreDescription !== null && genreDescription.length > 0}
		<p class={`md:w-3/4 lg:w-4/6 leading-loose font-semibold${skeleton ? ' m-6 bg-white' : ''}`}>
			{!fullTextShown ? summaryText : genreDescription}
			<!-- Add "show more" button if a summary is shown -->
			{#if summaryGenerated}
				<button
					class="underline"
					on:click={() => {
						fullTextShown = !fullTextShown; // Invert whether full text is shown on click
					}}
				>
					{!fullTextShown ? 'Visa mer...' : 'Visa mindre...'}
				</button>
			{/if}
		</p>
	{/if}
	<!-- Add description disclaimer for different sources (currently the only used
    description source is Last.FM) -->
	{#if genreDescriptionSource === 'last_fm'}
		<Button
			on:click={() => {
				openURL(genreLastFMURL, true);
			}}
			text="Läs mer på Last.FM"
		>
			<svelte:fragment slot="icon">
				<Icon name="fa:lastfm-square" color="logos-lastFM" />
			</svelte:fragment>
		</Button>
		<p class="text-sm">
			<small>
				Genrebeskrivning från <a href="https://last.fm" target="_blank">Last.FM</a>, licenserad
				under
				<a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank">CC BY-SA 3.0</a>.
				Jag har ingen kontroll över innehållet i denna beskrivning då den automatiskt inhämtas från
				tredje part.
			</small>
		</p>
	{/if}
</div>
