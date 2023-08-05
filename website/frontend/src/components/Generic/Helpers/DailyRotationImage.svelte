<!-- DailyRotationImage.svelte
A daily rotation image includes a special layout and some additional calculations.
This is a helper that does it for us! -->
<script>
	import Image from '../Image.svelte';
	import { getFirstAvailableAlbumImagesInList } from '../../../lib/utilities.js';
	import Badge from '../Badge.svelte';
	export let albumList; // A list of all the albums in the daily rotation
	export let skeleton = false; // Whether to show a skeleton loader or not
	export let size = 'small'; // "small" or "big"
	$: albumCount = albumList.length;
	$: albumImages = getFirstAvailableAlbumImagesInList({ items: albumList }, 'daily_rotation');
	$: albumImagesFound = albumImages.length > 0;
	$: sizeIsBig = size === 'big';
</script>

<!-- We render a backgroundless image, so we can place a circular thing at the end
         that shows how many albums that were played -->
<Image
	{skeleton}
	images={albumImages}
	background={sizeIsBig}
	width={sizeIsBig ? 'w-48' : undefined}
	height={sizeIsBig ? 'h-48' : undefined}
	heightMultipleImages={sizeIsBig ? 'h-auto' : undefined}
	widthMultipleImages={sizeIsBig ? 'w-auto' : undefined}
>
	<svelte:fragment slot="images">
		{#if albumCount > albumImages.length}
			<!-- Note: numbers below here are sourced from: the default image sizes (of the Image components).
            The text sizes have been retrieved by looking up the width -> rem and height to rem in the Tailwind
            documentation and dividing it in half. -->
			<Badge
				text={`${albumImagesFound ? '+' : ''}${albumCount - albumImages.length}`}
				color="lime_2"
				{skeleton}
				width={albumImagesFound ? null : sizeIsBig ? 'w-48' : 'w-20 md:w-32'}
				height={albumImagesFound ? null : sizeIsBig ? 'h-auto' : 'h-20 md:h-32'}
				textSize={albumImagesFound
					? 'md:text-4xl'
					: sizeIsBig
					? 'text-[6rem]'
					: 'text-[2.5rem] md:text-[4.5rem]'}
			/>
		{/if}
	</svelte:fragment>
</Image>
