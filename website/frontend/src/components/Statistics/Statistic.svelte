<!-- Statistic.svelte
Renders an individual statistic on the statistics view.
-->
<script>
	export let number; // The number to render
	export let title; // The title of the statistic
	export let skeleton; // Whether to render as a skeleton loader or not
</script>

<div class={`text-albumOfTheDay-text-foreground${skeleton ? ' animate-pulse' : ' '}`}>
	<p class={`text-3xl font-bold${skeleton ? ' bg-albumOfTheDay-text-foreground m-3 my-1' : ''}`}>
		{!skeleton ? number : '--'}
	</p>
	<h3 class={skeleton ? 'bg-albumOfTheDay-text-foreground mx-3 my-1' : ''}>
		{!skeleton ? title : '--'}
	</h3>
</div>
