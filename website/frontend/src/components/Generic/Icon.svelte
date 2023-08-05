<!-- Icon.svelte
An icon with a customizable size and custom colors. -->
<script>
	// Define constants: valid sizes
	import Icon from '@iconify/svelte';
	const iconSizes = {
		// Mapping: size name --> class(es) to apply
		small: 'text-2xl', // Used on the list page, on the menu and on (small) buttons
		medium: 'text-4xl', // Used on collapse/show buttons and on (medium) buttons
		big: 'text-7xl', // Used on the loading screen on the Spotify dialog
		huge: 'text-[4em]', // Used on the Spotify authentication screen
		gigantic: 'text-[7em]', // Used on the Spotify authentication confirmation page
		max: 'h-max w-max'
	};
	export let name;
	export let size = 'small';
	export let color = 'white';
</script>

<span class={`${iconSizes[size]} text-${color}`}>
	<Icon icon={name} />
</span>
