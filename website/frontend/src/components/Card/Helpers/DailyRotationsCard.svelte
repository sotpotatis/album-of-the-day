<!-- DailyRotationsCard.svelte
Shows information about a daily rotation. -->
<script>
	import Card from '../Card.svelte';
	import { getFirstAvailableAlbumImagesInList, openURL } from '../../../lib/utilities.js';
	import Image from '../../Generic/Image.svelte';
	import Badge from '../../Generic/Badge.svelte';
	import CardBody from '../CardBody.svelte';
	import DailyRotationImage from '../../Generic/Helpers/DailyRotationImage.svelte';
	import Button from '../../Generic/Button.svelte';
	export let data; // The data for the daily rotation
	export let skeleton = false; // Whether to show a skeleton loader or not
	// Read stuff from parameters
	$: albumCount = data.albums.length;
	$: genreCount = data.genres.length;
	$: genreCountText = `${genreCount} genrer`;
	$: albumImages = getFirstAvailableAlbumImagesInList({ items: data.albums }, 'daily_rotation');
</script>

<Card compact={true}>
	<!-- Add an image showing the played albums -->
	<svelte:fragment slot="image">
		<DailyRotationImage albumList={data.albums} {skeleton} />
	</svelte:fragment>
	<svelte:fragment slot="body">
		<!-- Render a card body with the number of albums and genres -->
		<CardBody
			title={`${albumCount} album`}
			text={genreCountText}
			summary={genreCountText}
			{skeleton}
		/>
		<Button
			text="Visa"
			backgroundColor="emerald-400"
			on:click={() => {
				openURL(`/daily-rotations/${data.id}`);
			}}
		/>
	</svelte:fragment>
</Card>
