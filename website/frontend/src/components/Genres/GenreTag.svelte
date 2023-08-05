<!-- GenreTag.svelte
Renders a genre in a tag format.
Tag colors are provided by the backend. -->
<script>
	import { openURL } from '../../lib/utilities.js';
	export let name;
	export let id;
	export let color;
	export let skeleton = false; // Use to provide a skeleton loader
	export let size = 'small';
	export let details = null; // Allows setting a details text
	export let link = true; // Allows disabling the link on the button
	export let borderStyle = 'regular'; // "regular" or "pill"
	$: isPillBorder = borderStyle === 'pill';
	const sizeToClasses = {
		// Mapping: size setting --> classes to apply
		smaller: 'text-sm text-white font-semibold px-3 py-1',
		small: 'text-white font-bold px-3 py-1',
		medium: 'text-xl font-bold px-3 py-1',
		big: 'text-3xl font-bold px-6 py-3'
	};
	// Figure out border color based on the primary color
	$: colorName = color.split('-')[0];
	$: colorNumber = Number(color.split('-')[1]);
	$: borderColor = `${colorName}-${
		// Subtract 100 from the base color if possible
		colorNumber > 100 ? colorNumber - 100 : colorNumber
	}`;
</script>

<button
	class={`${sizeToClasses[size]}
bg-${color} border-2 ${
		!isPillBorder ? `rounded-xl` : 'rounded-full'
	} border-${borderColor} text-white ${link ? ' hover:underline' : ''}`}
	disabled={!link}
	on:click={!skeleton && link
		? () => {
				// Open genre page on click
				openURL(`/genres/${id}`, false);
		  }
		: null}
>
	<span
		class={`line-clamp-1 text-ellipsis
    ${skeleton ? ' bg-white' : ''}
    `}>{name}</span
	>
	<!-- Add details text if set.
     This is only available on the big button size. -->
	{#if size === 'big' && details !== null}
		<br />
		<span class={`text-base${skeleton ? ' bg-white' : ''}`}>{details}</span>
	{/if}
</button>
