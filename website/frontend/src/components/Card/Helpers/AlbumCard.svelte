<!-- AlbumCard.svelte
A helper card that automagically fills out information for an album of the day or an album_list_item
based on its data. Since their cards are both very similar, I decided to combine them. -->
<script>
	import Card from '../Card.svelte';
	import CardBody from '../CardBody.svelte';
	import Image from '../../Generic/Image.svelte';
	import { dateDifferenceToHumanReadable } from '../../../lib/dates.js';
	import { generateSummaryText, NO_ALBUM_COVER_URL } from '../../../lib/utilities.js';
	export let data;
	export let cardType = 'album_of_the_day'; // Three possible types: "album_of_the_day", "album_list_item" or "album", since they are very similar
	export let skeleton = false; // Used to present a skeleton loader
	export let latest = null; // Used for latest cards
	export let compact = false; // Can be used to render a compact version of this card
	export let alwaysCompact = true; // See the Card component for more information
	$: typeIsAlbumOfTheDay = cardType === 'album_of_the_day';
	$: album = cardType === 'album' ? data : data.album; // The "album" type is for passing data directly, so album data is at the root
	$: cardText = !skeleton && (latest || cardType === 'album_list_item') ? data.comments : '';
	// We want the text inside a list item to be collapsible.
	$: albumCommentsIsCollapsible = !typeIsAlbumOfTheDay && cardText !== null && cardText.length > 0;
	$: cardSummary = albumCommentsIsCollapsible ? generateSummaryText(cardText, 64)[1] : cardText;
</script>

<Card {compact} {alwaysCompact} {skeleton} color={latest ? 'dark' : 'light'}>
	<svelte:fragment slot="title">
		{#if latest && typeIsAlbumOfTheDay}
			<h2 class="text-albumOfTheDay-text-foreground text-2xl flex flex-row items-center gap-x-2">
				<span class="font-bold">Senaste</span>
				<span class={`text-base${skeleton ? ' bg-albumOfTheDay-text-foreground m-3' : ''}`}
					>{!skeleton ? dateDifferenceToHumanReadable(data.date) : '20XX-XX-XX'}</span
				>
			</h2>
		{/if}
	</svelte:fragment>
	<svelte:fragment slot="image">
		<Image
			source={skeleton
				? null
				: album.cover_url !== null && album.cover_url.length > 0
				? album.cover_url
				: NO_ALBUM_COVER_URL}
			alt={`Albumomslagsbild för ${album.name}.`}
			dataSource={album.cover_source}
			{skeleton}
		/>
	</svelte:fragment>
	<svelte:fragment slot="body">
		<CardBody
			text={cardText}
			title={album.name}
			summary={cardSummary}
			{skeleton}
			collapsible={albumCommentsIsCollapsible}
		>
			<!-- Add artist information -->
			<svelte:fragment slot="subtitle">
				{#each album.artists as artist}
					<p>
						<a
							class={skeleton ? 'bg-albumOfTheDay-text-foreground m-3' : ''}
							href={!skeleton ? `/artists/${artist.id}` : null}
							>{!skeleton ? artist.name : 'Artist'}</a
						>
					</p>
				{/each}
				<!-- Add date if not latest -->
				{#if !latest && typeIsAlbumOfTheDay}
					<p class={skeleton ? 'bg-albumOfTheDay-text-foreground m-3' : ''}>
						{!skeleton ? dateDifferenceToHumanReadable(data.date) : 'x månad'}
					</p>
				{/if}
			</svelte:fragment>
		</CardBody>
		<slot name="body" />
		<a
			href={!skeleton
				? typeIsAlbumOfTheDay
					? `/album-of-the-days/${data.id}`
					: `/albums/${album.id}`
				: null}
			class={skeleton ? 'bg-albumOfTheDay-text-foreground m-3' : ''}
			>{typeIsAlbumOfTheDay ? 'Läs mer >>' : 'Till album >>>'}</a
		>
	</svelte:fragment>
</Card>
