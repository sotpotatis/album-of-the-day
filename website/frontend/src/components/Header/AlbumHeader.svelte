<!-- AlbumHeader.svelte
A header for presenting an album cover: complete with album name,
cover, genres, etc. -->
<script>
	import Image from '../Generic/Image.svelte';
	import GenreTag from '../Genres/GenreTag.svelte';
	import SpotifyButtons from '../Spotify/SpotifyButtons.svelte';
	import { NO_ALBUM_COVER_URL } from '../../lib/utilities.js';
	export let albumName;
	export let albumArtists; // Pass this as a dictionary so we can link to the artist page
	export let albumId; // The album's numerical ID
	// The album's Spotify UID (if any, if not, pass null or an empty string
	// (which will be what is returned by the server))
	export let albumSpotifyUID;
	export let albumSpotifyTrackURIs;
	export let coverURL;
	export let coverSource;
	export let genres; // Pass this as a list so we can link to the genre page
	export let date = null; // Optional: provide a date.
	export let skeleton = false; // Used to provide a skeleton loader.
</script>

<div class={`flex flex-col gap-y-2 items-center justify-center${skeleton ? ' animate-pulse' : ''}`}>
	<Image
		width="w-72"
		height="h-72"
		alt={!skeleton ? `Albumomslag för ${albumName}` : ''}
		source={skeleton
			? null
			: coverURL !== null && coverURL.length > 0
			? coverURL
			: NO_ALBUM_COVER_URL}
		dataSource={coverSource}
	/>
	{#if date}
		<p>{date}</p>
	{/if}
	<h1 class={`text-4xl font-bold${skeleton ? ' bg-white m-6' : ''}`}>{albumName}</h1>
	<div class="flex flex-col flex-wrap gap-x-2">
		{#each albumArtists as albumArtist, index}
			<!-- Render each artist. Add a comma if we have another artist to render. -->
			<h2 class={`text-lg font-bold${skeleton ? ' bg-white m-6' : ''}`}>
				<a href={!skeleton ? `/artists/${albumArtist.id}` : null}>{albumArtist.name}</a>
				{#if index + 1 < albumArtists.length}, {/if}
			</h2>
		{/each}
	</div>
	<!-- Render genre tags -->
	<div class="flex flex-row flex-wrap justify-center gap-x-2 gap-y-2">
		{#each genres as genre}
			<GenreTag name={genre.name} id={genre.id} color={genre.color} {skeleton} />
		{/each}
	</div>
	<!-- Render Spotify buttons -->
	<div class="grid grid-cols-1 md:grid-cols-2 gap-x-4 gap-y-4">
		<SpotifyButtons {albumId} {albumSpotifyUID} {albumSpotifyTrackURIs} {skeleton} />
	</div>
</div>
