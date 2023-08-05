<!-- LetterGrouping.svelte
A container for items that are sorted/grouped by a specific letter.
See the groupItemsByName function from utilities.js for an helper function
and the genres/+page.svelte and artists/+page.svelte pages for information. -->
<script>
	import { TYPE_TO_GRID_CLASSES } from '../../lib/utilities.js';
	export let letter; // The letter, e.g. "A"
	export let itemType = 'genre'; // Types of items being rendered. "genre" or "artist".
	export let skeleton = false; // Used to set whether to show a skeleton loader or not.
</script>

<div
	class={`flex flex-row gap-x-8 py-12 border-b-[0.1em] border-b-gray-200 p-3${
		skeleton ? ' animate-pulse' : ''
	}`}
>
	<!-- The letter -->
	<h2 class={`text-2xl font-bold${skeleton ? ' m-6 bg-albumOfTheDay-text-foreground h-12' : ''}`}>
		{letter}
	</h2>
	<!-- Wrapper and slot for all the cards --->
	<div class={`${TYPE_TO_GRID_CLASSES[itemType]} gap-x-12 gap-y-12 items-center justify-center`}>
		<slot />
	</div>
</div>
