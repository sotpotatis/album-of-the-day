<!-- ArtistTag.svelte
A small little tag showing information about an artist. -->

<script>
	import { openURL } from '../../lib/utilities.js';
	export let artistId; // ID of the artist
	export let artistName; // Name of the artist
	export let skeleton = false; // Whether to show skeleton loader or not.
</script>

<div>
	<button
		class={`font-bold bg-gray-200 border-2 text-black px-3 py-3 rounded-full hover:cursor-pointer hover:underline`}
		on:click={() => {
			openURL(`/artists/${artistId}`, false);
		}}><span class={`${skeleton ? ' bg-black animate-pulse' : ''}`}>{artistName}</span></button
	>
</div>
