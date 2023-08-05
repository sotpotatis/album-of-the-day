<!-- CardBody.svelte
Holds card text content.
-->
<script>
	import Icon from '../Generic/Icon.svelte';
	import { onMount } from 'svelte';
	export let title; // Card title text
	export let text; // Card body text
	// The "collapsible" function adds a "Read more" icon to the text
	export let collapsible = false;
	export let summary;
	export let collapsed = true;
	export let skeleton = false; // Used to add a skeleton loader
</script>

<h3
	class={`font-bold text-albumOfTheDay-text-foreground text-xl${
		skeleton ? ' bg-albumOfTheDay-text-foreground p-3 m-3' : ''
	}`}
>
	{!skeleton ? title : 'Lorem ipsum...'}
</h3>
<!-- Allow subtitle elements to be added -->
<slot name="subtitle" />
<p
	class={`text-albumOfTheDay-text-foreground${!collapsible ? ' line-clamp-2' : ''}${
		skeleton ? ' bg-albumOfTheDay-text-foreground p-3 m-3' : ''
	}`}
>
	<!-- Render some dummy, invisible skeleton text. -->
	{#if skeleton}
		Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus pharetra diam non posuere
		tincidunt. Suspendisse pellentesque nibh mauris. Praesent ac accumsan elit, ut eleifend metus.
		Nullam blandit scelerisque magna, non sagittis neque euismod eget. Nam ultricies luctus erat,
		accumsan vehicula ex ultricies ac.
		<!-- Render summary text  -->
	{:else if (collapsible && collapsed) || !collapsible}
		{summary}
	{:else}
		{text}
	{/if}
	<!-- Add collapsible button -->
	{#if collapsible && summary !== text}
		<button
			class=""
			on:click={() => {
				// Toggle if the text is collapsed on click
				collapsed = !collapsed;
			}}
		>
			<Icon
				size="small"
				name={collapsed ? 'fa-solid:chevron-up' : 'fa-solid:chevron-down'}
				color="albumOfTheDay-text-foreground"
			/>
		</button>
	{/if}
</p>
