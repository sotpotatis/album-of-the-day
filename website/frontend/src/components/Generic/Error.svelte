<!-- Error.svelte
An error to show in case a request (or something else) failed. -->
<script>
	import Icon from '../Generic/Icon.svelte';
	export let title = 'Fel';
	export let color = 'albumOfTheDay-text-foreground';
	export let description;
	export let size = 'medium';
	const SIZE_TO_TEXT_CLASS = {
		small: {
			title: 'text-sm font-bold',
			description: 'text-sm'
		},
		medium: {
			title: 'text-xl',
			description: ''
		}
	};
	$: isSmall = size === 'small';
</script>

<div
	class={`text-${color} flex ${
		!isSmall ? 'flex-col' : 'flex-row'
	} gap-y-2 gap-x-2 items-center justify-center p-3`}
>
	<Icon {size} name="material-symbols:warning" {color} />
	<h3 class={`${SIZE_TO_TEXT_CLASS[size].title} font-bold`}>{title}</h3>
	<p class={`${SIZE_TO_TEXT_CLASS[size].description}`}>{description}</p>
</div>
