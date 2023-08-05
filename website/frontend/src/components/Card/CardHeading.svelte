<!-- CardHeading.svelte
A card heading/title -->
<script>
	export let title; // The main heading
	export let subHeading = null; // An optional subheading to add next to the title
</script>

<h3 class={`text-2xl font-bold break-word${subHeading !== null ? ' flex flex-col gap-x-2' : ''}`}>
	{title}
	{#if subHeading !== null}
		{subHeading}
	{/if}
</h3>
