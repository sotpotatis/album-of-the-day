<!-- ArtistHeader.svelte
A header helper that shows details about an artist. -->
<script>
	export let artistName;
	export let skeleton = false; // Whether to show a skeleton loader or not
</script>

<div
	class={`flex flex-col gap-y-4 items-center justify-center ${skeleton ? ' animate-pulse' : ''}`}
>
	<h1 class={`text-2xl font-bold`}>artist</h1>
	<h2 class={`text-5xl font-bold${skeleton ? ' bg-white' : ''}`}>{artistName}</h2>
</div>
