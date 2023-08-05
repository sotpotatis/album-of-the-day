<!-- Badge.svelte
A circular badge.
-->
<script>
	export let text; // Badge text
	export let color = 'gray'; // Badge color
	export let skeleton = false; // Use for skeleton loader
	export let textSize = null; // Optional setting to set text size
	export let width = null; // Optional setting for width
	export let height = null; // Optional setting for height
</script>

<div
	class={`bg-albumOfTheDay-badge-${color} font-bold px-3 py-1 flex items-center justify-center rounded-full${
		width !== null ? ` ${width}` : ''
	}${height !== null ? ` ${height}` : ''}`}
>
	<span
		class={`${
			skeleton
				? ' animate-pulse bg-albumOfTheDay-text-foreground text-albumOfTheDay-text-foreground max-w-content'
				: ''
		}${textSize !== null ? ` ${textSize}` : ''}`}
	>
		{skeleton ? 'X' : text}
	</span>
</div>
