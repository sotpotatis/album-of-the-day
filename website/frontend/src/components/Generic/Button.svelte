<!-- Button.svelte
Pretty self-explanatory - this is a button.
A clickable thing. -->
<script>
	export let text;
	export let buttonStyle = 'rounded';
	export let backgroundColor = 'albumOfTheDay-uiElements-darkBackground';
	export let textColor = 'black';
	export let extraClasses = null; // Pass any extra classes to apply
	export let height = null; // ...you can also pass a custom height
	export let width = null; // ...and a custom width if needed/wanted
	const STYLE_TO_CLASSES = {
		rounded: 'rounded-full px-3 py-1 m-3',
		big: 'rounded-xl text-xl px-3 py-1 m-3'
	};
	// Generate list with extra classes if height & width are set
	if (width !== null || height !== null) {
		if (extraClasses === null) {
			// Create extra classes
			extraClasses = '';
		}
		if (width !== null) {
			// Add width if specified
			extraClasses += ` ${width} `;
		}
		if (height != null) {
			// Add height if specified
			extraClasses += ` ${height} `;
		}
		extraClasses = extraClasses.trim(); // Trim some whitespace
	}
</script>

<button
	class={`${
		STYLE_TO_CLASSES[buttonStyle]
	}border-2 bg-${backgroundColor} border-${backgroundColor} text-${textColor} hover:underline font-semibold flex flex-row gap-x-2 items-center text-center w-fit${
		extraClasses !== null ? ` ${extraClasses}` : ''
	}`}
	on:click
>
	<slot name="icon" />
	{text}
</button>
