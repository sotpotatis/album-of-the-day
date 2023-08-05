<!-- Image.svelte
Generic image class that applies rounding etc. -->
<script>
	export let source = null; // The URL/source to the image.
	export let alt = null; // Image alt text.
	// The things above can be a list! It will allow us
	// to do some really cool stuff - automatically generate thumbnails with less hassle. Nice!
	export let images = null;
	// Note: it is not recommended to override the width and height as long as you
	// don't need it for consistency.
	export let width = 'w-20 md:w-32';
	export let height = 'h-20 md:h-32';
	export let widthMultipleImages = 'w-18'; // Custom width for when multiple images are used
	export let heightMultipleImages = 'h-18'; // Custom width for when multiple images are used
	export let skeleton = false; // Used for skeleton loader
	export let dataSource = null; // Optional parameter used to attribute data source
	export let background = true; // Optional parameter which can be used to remove the background and border around images
	$: imageList = images !== null ? images : [{ source: source, alt: alt, dataSource: dataSource }]; // Create an image list if we do not already have done
	$: multipleImages = imageList.length > 1;
</script>

<div
	class={`${
		background ? `border-8 rounded-lg bg-albumOfTheDay-uiElements-darkBackground ` : ''
	}shadow-sm  shrink-0${multipleImages ? ' grid grid-cols-2' : ''}${
		skeleton && background ? ' border-albumOfTheDay-uiElements-darkBackground' : ''
	}`}
>
	<!-- Note: we set the alt text to null if the skeleton should be shown as some browser otherwise render the alt text
    to be visible to the client  -->
	{#each imageList as image}
		<img
			class={`${
				multipleImages ? `${widthMultipleImages} ${heightMultipleImages}` : `${width} ${height}`
			} border-1 rounded-lg border-albumOfTheDay-uiElements-darkBackground bg-border-albumOfTheDay-uiElements-darkBackground text-transparent`}
			src={image.source}
			alt={!skeleton ? image.alt : null}
		/>
	{/each}
	<!-- Present a slot to include any extra image content  -->
	<slot name="images" />
</div>
