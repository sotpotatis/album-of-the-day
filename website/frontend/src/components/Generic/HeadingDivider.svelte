<!-- HeadingDivider.svelte
A heading divider is a subheading on a page with a horizontal ruler underneath it. -->
<script>
	import Icon from './Icon.svelte';
	export let title;
	export let collapsible = false; // Set to true to allow collapsing (hiding/showing) content via a button.'
	export let defaultCollapsed = false;
	export let skeleton = false; // Allows showing a skeleton loader
	$: collapsed = defaultCollapsed;
</script>

<h2
	class={`text-2xl text-left font-bold text-albumOfTheDay-text-foreground p-3 flex flex-row items-center gap-x-2${
		skeleton ? ' animate-pulse bg-albumOfTheDay-text-foreground m-6' : ''
	}`}
>
	{title}
	<slot name="heading" />
	{#if collapsible}
		<button
			on:click={() => {
				collapsed = !collapsed;
			}}
		>
			<Icon
				color="albumOfTheDay-text-foreground"
				size="medium"
				name={collapsed ? 'fa-solid:chevron-up' : 'fa-solid:chevron-down'}
			/>
		</button>
	{/if}
</h2>
<hr />
{#if !collapsed}
	<slot name="collapsible" />
{/if}
