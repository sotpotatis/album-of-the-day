<!-- ListHeader.svelte
Header information for a list. -->
<script>
	import Icon from '../Generic/Icon.svelte';
	import Image from '../Generic/Image.svelte';
	import { getAlbumsInList, getFirstAvailableAlbumImagesInList } from '../../lib/utilities.js';
	export let listName; // The list name
	export let listDescription; // A description in the list
	export let listItems; // All items in the list
	export let listCreationDate; // When the list was created.
	export let skeleton = false; // Whether to show a skeleton loader or not.
	// Work a little with the list items: filter out text entries
	$: listAlbumEntries = getAlbumsInList({ items: listItems !== undefined ? listItems : [] });
	// Generate list metadata icons
	$: listMetadata = [
		{
			icon: 'fa-solid:compact-disc',
			text: `${listAlbumEntries.length} album`
		},
		{
			icon: 'fa6-solid:calendar-days',
			text: `${!skeleton ? listCreationDate.toISODate() : 'YYYY-MM-DD'}`
		}
	];
</script>

<div
	class={`flex flex-wrap flex-row items-evenly justify-evenly ${
		skeleton ? ' animate-pulse' : ''
	} py-3`}
>
	<div id="list-metadata text-center md:text-left">
		<!-- List name and description -->
		<h1 class={`text-4xl font-bold py-3${skeleton ? ' bg-white p-3 m-3' : ''}`}>{listName}</h1>
		<p class={`${skeleton ? 'bg-white p-3 m-3' : ''}`}>{listDescription}</p>
		<!-- Add list metadata -->
		{#each listMetadata as metadataEntry}
			<p class={`font-semibold flex gap-x-2 py-3${skeleton ? ' bg-white p-3 m-3' : ''}`}>
				<Icon name={metadataEntry.icon} color="white" />
				{metadataEntry.text}
			</p>
		{/each}
	</div>
	<div id="list-image" class="order-first md:order-nome">
		<Image images={getFirstAvailableAlbumImagesInList({ items: listItems }, 'album_list')} />
	</div>
</div>
