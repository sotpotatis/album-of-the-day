<!-- Card.svelte
The Card is a versatile component: it can display an image, a title, and optional
other items. It is the fundamental of displaying many list items. It is simply awesome!
See all the components inside this subfolder for what's powering the magic,
because this is basically just a skeleton. -->
<script>
	export let color = 'light'; // Two options: light or dark
	export let compact = false; // Can be used to provide a more compact card view by allowing items to wrap onto a new line.
	// If true, will always wrap items on a new line. If false, will only wrap items onto a new line
	// if the screen size is small
	export let alwaysCompact = true;
	export let skeleton = false; // Used to provide a skeleton loader
	const colorClass =
		color === 'light'
			? 'albumOfTheDay-uiElements-lightBackground'
			: 'albumOfTheDay-uiElements-darkBackground';
</script>

<div
	class={`border-2 m-3 border-${colorClass} rounded-lg bg-${colorClass} text-albumOfTheDay-text-foreground p-3 break-all${
		skeleton ? ' animate-pulse' : ''
	}`}
>
	<!-- Any title items -->
	<div class="text-left">
		<slot name="title" />
	</div>
	<div
		class={`flex ${!compact ? 'flex-row' : 'flex-col flex-wrap'}${
			compact && !alwaysCompact ? ' md:flex-row md:flex-nowrap ' : ''
		} gap-x-12 md:gap-x-12 gap-y-2 text-left items-center md:p-3 py-3 px-1`}
	>
		<!-- Any image -->
		<slot name="image" />
		<!-- Any body items -->
		<div>
			<slot name="body" />
		</div>
	</div>
</div>
